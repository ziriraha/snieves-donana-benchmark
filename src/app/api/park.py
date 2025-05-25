from flask import after_this_request, request, jsonify, send_from_directory
from app.utils.constants import CSV_DIRECTORY, PARK_NAMES, CUSTOM_DIRECTORY, ERROR_MESSAGES
from make_datasets import make_custom_zip
from utils import verify_date
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Obtener datos por parque natural y fecha (es opcional si no se indica se devuelven todos) (zip)
# Date: DDMMYYYY
def get_park_images(park_name):
    # ERROR HANDLING
    if park_name not in PARK_NAMES:
        logger.error(f'Park not found: {park_name}')
        return jsonify({'error': ERROR_MESSAGES['park']}), 404
    date = request.args.get('date')
    if not verify_date(date):
        logger.error(f'Invalid date: {date}')
        return jsonify({'error': ERROR_MESSAGES['date']}), 400
    
    zip_name = park_name

    # Selecting data
    all_data = pd.concat([pd.read_csv(CSV_DIRECTORY + 'all_data_0.csv'),
                          pd.read_csv(CSV_DIRECTORY + 'all_data_1.csv')])
    data = all_data[all_data['park'] == park_name]
    if date:
        zip_name += f'_{date}'
        data = data[data['datetime'].str.contains(date, na=False)]

    if len(data) == 0:
        logger.error(f'No data found for {park_name} at {date}')
        return jsonify({'error': ERROR_MESSAGES['no_data']}), 404

    logger.info(f'PARK_REQUEST: {park_name} at {date} ({zip_name}), total of {len(data)} images.')
    
    # Creating zip
    make_custom_zip(data, zip_name)

    # Removing zip after request
    @after_this_request
    def remove_zip(response):
        os.remove(CUSTOM_DIRECTORY + zip_name + '.zip')
        return response

    # Sending zip
    return send_from_directory(CUSTOM_DIRECTORY, zip_name + '.zip')
