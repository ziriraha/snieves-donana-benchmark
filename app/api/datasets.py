from flask import jsonify, send_from_directory
from app.utils.constants import DATASET_NAMES, ERROR_MESSAGES, ZIP_DIRECTORY
import logging

logger = logging.getLogger(__name__)

def get_dataset(dataset_name):
    if dataset_name not in DATASET_NAMES:
        logger.error(f'Dataset not found: {dataset_name}')
        return jsonify({'error': ERROR_MESSAGES['dataset']}), 404
    logger.info(f'Dataset requested: {dataset_name}')
    return send_from_directory(ZIP_DIRECTORY, dataset_name + '.zip')