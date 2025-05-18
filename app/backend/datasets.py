from flask import jsonify, send_from_directory, Blueprint
from constants import DATASET_NAMES, ERROR_MESSAGES, ZIP_DIRECTORY
import logger

dataset = Blueprint('dataset', __name__)

@dataset.route(f'/dataset/<dataset_name>', methods=['GET'])
def get_dataset(dataset_name):
    if dataset_name not in DATASET_NAMES:
        logger.log_error(f'Dataset not found: {dataset_name}')
        return jsonify({'error': ERROR_MESSAGES['dataset']}), 404
    logger.log_message(f'Dataset requested: {dataset_name}')
    return send_from_directory(ZIP_DIRECTORY, dataset_name + '.zip')