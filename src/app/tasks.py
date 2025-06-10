import concurrent.futures
import logging
import os
import shutil
import tempfile
import zipfile

import pandas as pd
from flask import current_app as app
from tqdm import tqdm
from celery import shared_task
import json

from .extensions import db, redis_client
from .constants import DATASETS
from .models import Image, Park, Species
from .utils import download_image_from_minio, calculate_bbox
import base64

logger = logging.getLogger(__name__)

# from app.tasks import import_data_from_zip; import_data_from_zip.delay(app.config['DEFAULT_DATA_ZIP_PATH'])
@shared_task
def import_data_from_zip(file_path):
    species, parks, images = None, None, None

    with zipfile.ZipFile(file_path, 'r') as file:
        species = pd.read_csv(file.open('species.csv'))
        parks = pd.read_csv(file.open('parks.csv'))
        images = pd.read_csv(file.open('images.csv'))

    existing_species = {code for (code,) in Species.query.with_entities(Species.code).all()}
    created_species = set()
    for _, row in tqdm(species.iterrows(), total=len(species), desc='Importing species'):
        if row['code'] in existing_species: continue
        created_species.add(Species(code=row['code'], scientific_name=row['scientific'], name=row['name']))
    db.session.bulk_save_objects(created_species)
    db.session.commit()

    existing_parks = {code for (code,) in Park.query.with_entities(Park.code).all()}
    created_parks = set()
    for _, row in tqdm(parks.iterrows(), total=len(parks), desc='Importing parks'):
        if row['code'] in existing_parks: continue
        created_parks.add(Park(code=row['code'], name=row['name']))
    db.session.bulk_save_objects(created_parks)
    db.session.commit()

    existing_images = {path for (path,) in Image.query.with_entities(Image.path).all()}
    parks_dict = {p.code: p.id for p in Park.query.all()}
    species_dict = {s.code: s.id for s in Species.query.all()}
    created_images = set()
    for _, row in tqdm(images.iterrows(), total=len(images), desc='Importing images'):
        if row['path'] in existing_images: continue
        dt = pd.to_datetime(row['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        dt = None if pd.isna(dt) else dt
        created_images.add(Image(path=row['path'], date=dt, species_id=species_dict[row['species']], park_id=parks_dict[row['park']]))
    db.session.bulk_save_objects(created_images)
    db.session.commit()

@shared_task
def download_dataset_zips(file_path):
    sets = {}

    with zipfile.ZipFile(file_path, 'r') as file:
        for set_name in DATASETS: 
            sets[set_name] = pd.read_csv(file.open(f"{set_name}.csv"))
    for set_name, df in sets.items():
        with tempfile.TemporaryDirectory() as temp_dir:
            images_path = os.path.join(temp_dir, 'images')
            labels_path = os.path.join(temp_dir, 'labels')
            os.makedirs(images_path, exist_ok=True)
            os.makedirs(labels_path, exist_ok=True)

            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=app.config['MAX_CELERY_THREADS']) as executor:
                for _, row in df.iterrows():
                    image = Image.query.filter_by(path=row['path']).first()
                    if not image: logger.warning(f"Image with path {row['path']} not found in database."); continue

                    image_path = os.path.join(images_path, f'{image.id}.jpg')
                    label_path = os.path.join(labels_path, f'{image.id}.txt')
                    futures.append(executor.submit(download_image, image.to_dict(), image_path, label_path))

            for future in concurrent.futures.as_completed(futures):
                iid, bbox = future.result()
                if bbox:
                    img = Image.query.get(iid)
                    img.bbox = bbox
            db.session.commit()

            archive_file = os.path.join(app.config['API_DATA_DIRECTORY'], set_name)
            shutil.make_archive(archive_file, 'zip', temp_dir)
    

@shared_task
def calculate_bbox_wrapper(base64_image):
    bytes_image = base64.b64decode(base64_image.encode('utf-8'))
    return calculate_bbox(bytes_image)

def download_image(image, image_path, label_path, job_id=None):
    new_bbox = None
    try:
        bytes_image = download_image_from_minio(image['path'], image_path)
        if image['species']['code'] != 'emp':
            if not image['bbox']:
                base64_image = base64.b64encode(bytes_image).decode('utf-8')
                new_bbox_task = calculate_bbox_wrapper.delay(base64_image)
                new_bbox = new_bbox_task.get(disable_sync_subtasks=False)
                image['bbox'] = new_bbox
            with open(label_path, 'w') as file:
                annotation_text = f"{image['species']['id']} {image['bbox']['x']} {image['bbox']['y']} {image['bbox']['width']} {image['bbox']['height']}"
                file.write(annotation_text)

    except Exception as e:
        logger.error(f"Error downloading image {image['id']}: {str(e)}")
        if os.path.exists(image_path): os.remove(image_path)
        if os.path.exists(label_path): os.remove(label_path)

    if job_id:
        progress = json.loads(redis_client.get(f'status:{job_id}'))
        progress['progress'] += 1
        redis_client.set(f'status:{job_id}', json.dumps(progress))
    return image['id'], new_bbox

@shared_task
def download_images(images, destination, job_id=None):
    futures = []
    if job_id: redis_client.set(f'status:{job_id}', json.dumps({'status': 'Downloading images...', 'progress': 0, 'total': len(images)}))

    with concurrent.futures.ThreadPoolExecutor(max_workers=app.config['MAX_CELERY_THREADS']) as executor:
        for image in images:
            save_path = os.path.join(destination, image['park']['code'], image['species']['code'])
            os.makedirs(save_path, exist_ok=True)

            filename = str(image['id'])
            image_path = os.path.join(save_path, f'{filename}.jpg')
            label_path = os.path.join(save_path, f'{filename}.txt')

            futures.append(executor.submit(download_image, image, image_path, label_path, job_id))

    for future in concurrent.futures.as_completed(futures):
        iid, bbox = future.result()
        if bbox:
            img = Image.query.get(iid)
            img.bbox = bbox
    db.session.commit()

@shared_task(bind=True)
def generate_zip(self, images):
    output_zip_file = None
    job_id = self.request.id
    redis_client.set(f'status:{job_id}', json.dumps({'status': 'Starting...', 'progress': 0, 'total': len(images)}))
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            download_images(images, temp_dir, job_id)
            redis_client.set(f'status:{job_id}', json.dumps({'status': 'Creating zip file...', 'progress': len(images), 'total': len(images)}))
            archive_file = os.path.join(app.config['API_DATA_DIRECTORY'],  str(job_id))
            output_zip_file = shutil.make_archive(archive_file, 'zip', temp_dir)
    except Exception as e:
        logger.error(f"Error generating zip file: {e}")
        raise e
    redis_client.set(f'status:{job_id}', json.dumps({'status': 'Completed', 'progress': len(images), 'total': len(images)}))
    return output_zip_file