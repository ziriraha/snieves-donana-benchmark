from .extensions import db
from .models import Image, Park, Species
import pandas as pd
from celery import shared_task
import os
import logging
logger = logging.getLogger(__name__)

from .utils import get_image_from_minio, calculate_bbox

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

            dt = pd.to_datetime(row['date'], format='%Y:%m:%d %H:%M:%S', errors='coerce')
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
    except Exception as e:
        return f"Error importing data: {str(e)}"
    
@shared_task
def download_images(images, destination): # TODO: Paralelize this task to speed up the process
    for image in images:
        try:
            # Get the image
            save_path = os.path.join(destination, image.park.name, image.species.name)
            os.makedirs(save_path, exist_ok=True)
            image_path = os.path.join(save_path, f"{image.id}.jpg")
            get_image_from_minio(image.path, image_path)

            # Generate the annotation
            if not image.bbox:
                image.bbox = calculate_bbox(image_path)
                db.session.commit()

            with open(os.path.join(save_path, f"{image.id}.txt"), 'w') as file:
                file.write(f'{image.species.id} {image.bbox["x"]} {image.bbox["y"]} {image.bbox["width"]} {image.bbox["height"]}')
        except Exception as e:
            logger.error(f"Error downloading image {image}: {str(e)}")