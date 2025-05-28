from .extensions import db, redis_client
from flask import current_app as app
from .models import Image, Park, Species
import pandas as pd
from celery import shared_task
import tempfile
import shutil
import os
import logging
import json
import zipfile
import concurrent.futures
logger = logging.getLogger(__name__)

from .utils import download_image_from_minio, generate_annotation

# from app.tasks import import_data_from_zip; import_data_from_zip.delay(app.config['DATA_ZIP_PATH'])
@shared_task
def import_data_from_zip(file_path):
    species, parks, images = None, None, None

    with zipfile.ZipFile(file_path, 'r') as file:
        species = pd.read_csv(file.open('species.csv'))
        parks = pd.read_csv(file.open('parks.csv'))
        images = pd.read_csv(file.open('images.csv'))

    existing_species = {code for (code,) in Species.query.with_entities(Species.code).all()}
    created_species = set()
    for _, row in species.iterrows():
        if row['code'] in existing_species: continue
        created_species.add(Species(code=row['code'], scientific_name=row['scientific'], name=row['name']))
    db.session.bulk_save_objects(created_species)
    db.session.commit()

    existing_parks = {code for (code,) in Park.query.with_entities(Park.code).all()}
    created_parks = set()
    for _, row in parks.iterrows():
        if row['code'] in existing_parks: continue
        created_parks.add(Park(code=row['code'], name=row['name']))
    db.session.bulk_save_objects(created_parks)
    db.session.commit()

    existing_images = {path for (path,) in Image.query.with_entities(Image.path).all()}
    parks_dict = {p.code: p.id for p in Park.query.all()}
    species_dict = {s.code: s.id for s in Species.query.all()}
    created_images = set()
    for _, row in images.iterrows():
        if row['path'] in existing_images: continue
        dt = pd.to_datetime(row['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        dt = None if pd.isna(dt) else dt
        created_images.add(Image(path=row['path'], date=dt, species_id=species_dict[row['species']], park_id=parks_dict[row['park']]))
    db.session.bulk_save_objects(created_images)
    db.session.commit()

    return "Data imported successfully"

@shared_task
def annotation_task_wrapper(image_object, image, label_path):
    return generate_annotation(image_object, image, label_path)

def download_image(image, image_path, label_path):
    image_object = download_image_from_minio(image.path, image_path)
    if not image_object:
        logger.error(f"Failed to download image {image.path}")
        if os.path.exists(image_path): os.remove(image_path)
        return (image.id, False)

    if image.species.code != 'emp':
        detection_result = True
        try:
            detection_task = annotation_task_wrapper.delay(image_object, image, label_path)
            detection_result = detection_task.get()
        except Exception as e:
            logger.error(f"Error during annotation task for image {image.id}: {str(e)}")
            detection_result = False
        if not detection_result:
            logger.error(f"Annotation task failed for image {image.id}")
            if os.path.exists(image_path): os.remove(image_path)
            if os.path.exists(label_path): os.remove(label_path)
            return (image.id, False)
    return (image.id, True)
    
@shared_task()
def download_images(job_id, images, destination):
    progress = {'downloaded': 0, 'failed': 0, 'total': len(images), 'status': 'Downloading'}
    redis_client.set(f"progress:{job_id}", json.dumps(progress))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=app.config['MAX_CELERY_THREADS']) as executor:
        futures = []
        for image in images:
            save_path = os.path.join(destination, image.park.code, image.species.code)
            os.makedirs(save_path, exist_ok=True)

            filename = str(image.id)
            image_path = os.path.join(save_path, f'{filename}.jpg')
            label_path = os.path.join(save_path, f'{filename}.txt')

            futures.append(executor.submit(download_image, image, image_path, label_path))

        for future in concurrent.futures.as_completed(futures):
            progress['success' if future.result()[1] else 'failed'] += 1
            redis_client.set(f"progress:{job_id}", json.dumps(progress))
            results.append(future.result())

    redis_client.set(f"progress:{job_id}", json.dumps(progress))
    logger.info(f"Download task {job_id} completed with {progress['success']} successes and {progress['failed']} failures.")
    return {
        'success': [image_id for image_id, success in results if success],
        'failed': [image_id for image_id, success in results if not success],
    }

@shared_task(bind=True)
def generate_zip(self, images):
    job_id = self.request.id
    output_zip_file = None
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = download_images(job_id, images, temp_dir)

            result['status'] = 'Zipping'
            redis_client.set(f"progress:{job_id}", json.dumps(result))

            archive_file = os.path.join(app.config['API_DATA_DIR'],  f"dataset_{job_id}")
            output_zip_file = shutil.make_archive(archive_file, 'zip', temp_dir)
            
            result['status'] = 'Completed'
            redis_client.set(f"progress:{job_id}", json.dumps(result))
    except Exception as e:
        logger.error(f"Error generating zip file for job {job_id}: {e}")
        if output_zip_file and os.path.exists(output_zip_file): os.remove(output_zip_file)
        redis_client.delete(f"progress:{job_id}")
        return {'error': str(e)}

    return {'file': output_zip_file}