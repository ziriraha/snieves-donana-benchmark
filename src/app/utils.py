from io import BytesIO

from .extensions import minio_client, get_bbox_model, get_detection_model
from .constants import INFERENCE_CLASSES
from .config import MINIO_BUCKET
from datetime import datetime
from megadetector.visualization import visualization_utils as vis_utils
import logging

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
    response = get_image_from_minio(object_path)
    bytes_image = response.data
    response.close()
    response.release_conn()
    with vis_utils.load_image(BytesIO(bytes_image)) as image:
        image.save(save_path, format='JPEG', quality='keep' if image.format == 'JPEG' else 95)
    return bytes_image

def calculate_bbox(bytes_image):
    with vis_utils.load_image(BytesIO(bytes_image)) as image:
        detection = get_bbox_model().generate_detections_one_image(image)
        bbox = sorted(detection['detections'], key=lambda x: x['conf'], reverse=True)[0]['bbox']
        return {
            'x': bbox[0] + bbox[2]/2,
            'y': bbox[1] + bbox[3]/2,
            'width': bbox[2],
            'height': bbox[3]
        }

def get_inference_calculation(bytes_image):
    model, pcls, pbbox, bbox_image = get_detection_model(), -1, None, BytesIO()
    with vis_utils.load_image(BytesIO(bytes_image)) as image:
        for result in model(image):
            if len(result.boxes) != 0:
                pcls = int(result.boxes.cls[0].item())
                pbbox = result.boxes.xywhn[0].tolist()
                dbbox = result.boxes.xyxy[0].tolist()
            break
        if pbbox:
            vis_utils.draw_bounding_box_on_image(image, dbbox[1], dbbox[0], dbbox[3], dbbox[2], use_normalized_coordinates=False)
            image.save(bbox_image, format='JPEG', quality='keep' if image.format == 'JPEG' else 95)
        else: bbox_image = None
    return INFERENCE_CLASSES[pcls] if pcls != -1 else 'emp', pbbox, bbox_image.getvalue()