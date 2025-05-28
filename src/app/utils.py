from io import BytesIO
import os
from flask import current_app as app
from .extensions import minio_client, get_bbox_model, db
from megadetector.visualization import visualization_utils as vis_utils
import logging
logger = logging.getLogger(__name__)

class DetectionError(Exception):
    pass

def verify_date(date_str):
    from datetime import datetime
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
def verify_num_files(limit_str):
    try:
        limit = int(limit_str)
        return limit > 0
    except (ValueError, TypeError):
        return False

def get_image_from_minio(object_path):
    return minio_client.get_object(
        bucket_name=app.config['MINIO_BUCKET'], 
        object_name=object_path)

def download_image_from_minio(object_path, save_path):
    image = None
    try:
        bytes_image = get_image_from_minio(object_path)
        image = vis_utils.load_image(BytesIO(bytes_image))
        image.save(save_path, format='JPEG', quality='keep' if image.format == 'JPEG' else 95)
    except Exception as e: 
        logger.error(f"Error retrieving and saving image {image}: {str(e)}")
        if os.path.exists(save_path): os.remove(save_path)
    return image

def calculate_bbox(image):
    detection = get_bbox_model().generate_detections_one_image(image)
    if detection['failure']: raise DetectionError("Detection failed: " + detection['failure'])
    bbox = sorted(detection['detections'], key=lambda x: x['conf'], reverse=True)[0]['bbox']
    return {
        'x': bbox[0] + bbox[2]/2,
        'y': bbox[1] + bbox[3]/2,
        'width': bbox[2],
        'height': bbox[3]
    }
    
def generate_annotation(image_obj, image, save_path):
    success = True
    try:
        if not image.bbox: image.bbox = calculate_bbox(image_obj)
        with open(save_path, 'w') as file: 
            file.write(f'{image.species.id} {image.bbox["x"]} {image.bbox["y"]} {image.bbox["width"]} {image.bbox["height"]}')
    except Exception as e:
        logger.error(f"Error generating annotation for image {image}: {str(e)}")
        db.session.delete(image)
        success = False
    finally: db.session.commit()
    return success