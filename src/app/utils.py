from flask import current_app as app
from .extensions import minio_client, get_bbox_model
from megadetector.visualization import visualization_utils as vis_utils

def get_image_from_minio(image_path, save_path):
    minio_client.fget_object(
        bucket_name=app.config['MINIO_BUCKET'],
        object_name=image_path,
        file_path=save_path
    )

def calculate_bbox(image_path):
    pred = [0, 0, 0, 0]
    with vis_utils.load_image(image_path) as image:
        pred = get_bbox_model.generate_detections_one_image(image)['detections'][-1]['bbox']
    return {
        'x': pred[0] + pred[2]/2,
        'y': pred[1] + pred[3]/2,
        'width': pred[2],
        'height': pred[3]
    }