from flask import jsonify, send_from_directory
import logging

logger = logging.getLogger(__name__)

def get_dataset(dataset_name):
    return send_from_directory(ZIP_DIRECTORY, dataset_name + '.zip')