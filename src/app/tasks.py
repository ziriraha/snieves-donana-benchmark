from .extensions import db, redis_client
from flask import current_app as app
from .models import Image, Park, Species
import pandas as pd
from celery import shared_task
import os
import logging
import json
import concurrent.futures
logger = logging.getLogger(__name__)

from .utils import download_image_from_minio, generate_annotation

# TODO: Should add a species.csv and a parks.csv file to the import for the full names
@shared_task
def import_csv_data(file_path):
    try:
        df = pd.read_csv(file_path)
        parks = {}
        for park in df['park'].unique():
            park_obj = Park.query.filter_by(name=park).first()
            if not park_obj:
                park_obj = Park(name=park)
                db.session.add(park_obj)
                db.session.commit()
            parks[park] = park_obj

        species = {}
        for species_name in df['species'].unique():
            species_obj = Species.query.filter_by(name=species_name).first()
            if not species_obj:
                species_obj = Species(name=species_name)
                db.session.add(species_obj)
                db.session.commit()
            species[species_name] = species_obj

        for _, row in df.iterrows():
            image_exists = Image.query.filter_by(path=row['path']).first()
            if image_exists: continue

            dt = pd.to_datetime(row['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            dt = None if pd.isna(dt) else dt

            image = Image(
                path=row['path'],
                date=dt,
                species=species[row['species']],
                park=parks[row['park']]
            )
            db.session.add(image)
            db.session.commit()

        return "Data imported successfully"
    except Exception as err:
        return f"Error importing data: {str(err)}"

@shared_task
def annotation_task_wrapper(image_object, image, label_path):
    return generate_annotation(image_object, image, label_path)

def download_image(image, image_path, label_path):
    image_object = download_image_from_minio(image.path, image_path)
    if not image_object:
        logger.error(f"Failed to download image {image.path}")
        if os.path.exists(image_path): os.remove(image_path)
        return (image.id, False)

    if image.species.name != 'emp':
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
    
@shared_task(bind=True)
def download_images(self, images, destination):
    job_id = self.request.id
    progress = {'Done': False, 'success': 0, 'failed': 0, 'total': len(images)}
    redis_client.set(f"progress:{job_id}", json.dumps(progress))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=app.config['MAX_CELERY_THREADS']) as executor:
        futures = []
        for image in images:
            save_path = os.path.join(destination, image.park.name, image.species.name)
            os.makedirs(save_path, exist_ok=True)

            image_path = os.path.join(save_path, f'{image.id}.jpg')
            label_path = os.path.join(save_path, f'{image.id}.txt')

            futures.append(executor.submit(download_image, image, image_path, label_path))

        for future in concurrent.futures.as_completed(futures):
            progress['success' if future.result()[1] else 'failed'] += 1
            redis_client.set(f"progress:{job_id}", json.dumps(progress))
            results.append(future.result())

    progress['Done'] = True
    redis_client.set(f"progress:{job_id}", json.dumps(progress))
    logger.info(f"Download task {job_id} completed with {progress['success']} successes and {progress['failed']} failures.")
    return {
        'success': [image_id for image_id, success in results if success],
        'failed': [image_id for image_id, success in results if not success],
    }