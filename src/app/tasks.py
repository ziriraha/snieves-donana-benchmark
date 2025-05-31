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

from .extensions import db
from .constants import DATASETS
from .models import Image, Park, Species
from .utils import download_image_from_minio, generate_annotation

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

            for future in tqdm(futures, total=len(futures), desc=f'Downloading images for {set_name}'):
                iid, bbox = future.result()
                if bbox:
                    img = Image.query.get(iid)
                    img.bbox = bbox
            db.session.commit()

            archive_file = os.path.join(app.config['API_DATA_DIRECTORY'], set_name)
            shutil.make_archive(archive_file, 'zip', temp_dir)
    

@shared_task
def annotation_task_wrapper(image, image_path, label_path):
    return generate_annotation(image, image_path, label_path)

def download_image(image, image_path, label_path):
    new_bbox = None
    try:
        download_image_from_minio(image['path'], image_path)
        if image['species']['code'] != 'emp':
            annotation_job = annotation_task_wrapper.delay(image, image_path, label_path)
            new_bbox = annotation_job.get(disable_sync_subtasks=False)
    except Exception as e:
        logger.error(f"Error downloading image {image['id']}: {str(e)}")
        if os.path.exists(image_path): os.remove(image_path)
        if os.path.exists(label_path): os.remove(label_path)
    return image['id'], new_bbox

@shared_task
def download_images(job, images, destination):
    futures = []
    job.update_state(state='PROGRESS', meta={'status': 'Downloading images...', 'progress': 0})
    with concurrent.futures.ThreadPoolExecutor(max_workers=app.config['MAX_CELERY_THREADS']) as executor:
        for image in images:
            save_path = os.path.join(destination, image['park']['code'], image['species']['code'])
            os.makedirs(save_path, exist_ok=True)

            filename = str(image['id'])
            image_path = os.path.join(save_path, f'{filename}.jpg')
            label_path = os.path.join(save_path, f'{filename}.txt')

            futures.append(executor.submit(download_image, image, image_path, label_path))
    progress = 0
    total = len(futures)
    for future in futures:
        iid, bbox = future.result()
        if bbox:
            img = Image.query.get(iid)
            img.bbox = bbox
        job.update_state(state='PROGRESS', meta={'status': 'Downloading images...', 'progress': progress / total * 100})
    db.session.commit()

@shared_task(bind=True)
def generate_zip(self, images):
    output_zip_file = None
    self.update_state(state='PROGRESS', meta={'status': 'Starting...', 'progress': 0})
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            download_images(self, images, temp_dir)
            self.update_state(state='PROGRESS', meta={'status': 'Creating zip file...', 'progress': 100})
            archive_file = os.path.join(app.config['API_DATA_DIRECTORY'],  str(self.request.id))
            output_zip_file = shutil.make_archive(archive_file, 'zip', temp_dir)
    except Exception as e:
        logger.error(f"Error generating zip file: {e}")
        raise e
    self.update_state(state='SUCCESS', meta={'status': 'Completed', 'progress': 100})
    return output_zip_file