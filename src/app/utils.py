from io import BytesIO

from .extensions import minio_client, get_bbox_model
from .config import MINIO_BUCKET
from datetime import datetime
from megadetector.visualization import visualization_utils as vis_utils
import logging
logger = logging.getLogger(__name__)

class DetectionError(Exception):
    pass

def verify_date(date_str):
    if date_str:
        try: datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError: return False
    return True

def get_image_from_minio(object_path):
    return minio_client.get_object(
        bucket_name=MINIO_BUCKET, 
        object_name=object_path)

def download_image_from_minio(object_path, save_path):
    bytes_image = get_image_from_minio(object_path).data
    with vis_utils.load_image(BytesIO(bytes_image)) as image:
        image.save(save_path, format='JPEG', quality='keep' if image.format == 'JPEG' else 95)

def calculate_bbox(image):
    detection = get_bbox_model().generate_detections_one_image(image)
    bbox = sorted(detection['detections'], key=lambda x: x['conf'], reverse=True)[0]['bbox']
    return {
        'x': bbox[0] + bbox[2]/2,
        'y': bbox[1] + bbox[3]/2,
        'width': bbox[2],
        'height': bbox[3]
    }
    
def generate_annotation(image, image_path, label_path):
    new_bbox = None
    if not image['bbox']:
        with vis_utils.load_image(image_path) as image_obj:
            new_bbox = calculate_bbox(image_obj)
        image['bbox'] = new_bbox
    with open(label_path, 'w') as file: 
        file.write(f"{image['species']['id']} {image['bbox']['x']} {image['bbox']['y']} {image['bbox']['width']} {image['bbox']['height']}")
    return new_bbox
