from flask import Flask, after_this_request, request, jsonify, send_from_directory, Blueprint
from constants import CSV_DIRECTORY, SPECIES_NAMES, CUSTOM_DIRECTORY, ERROR_MESSAGES
from make_datasets import make_custom_zip
from utils import verify_date, verify_num_files
import os
import logger
import pandas as pd

species = Blueprint('species', __name__)

# Obtener datos por especie, fecha y número de ficheros (ambos opcionales si no se indica se devuelven todos) (zip)
@species.route('/species/<species_name>', methods=['GET'])
def get_species_images(species_name):
    # ERROR HANDLING
    if species_name not in SPECIES_NAMES:
        logger.log_error(f'Species not found: {species_name}')
        return jsonify({'error': ERROR_MESSAGES['species']}), 404
    date = request.args.get('date')
    if date and not verify_date(date):
        logger.log_error(f'Invalid date: {date}')
        return jsonify({'error': ERROR_MESSAGES['date']}), 400
    num_files = request.args.get('num_files')
    if num_files and not verify_num_files(num_files):
        logger.log_error(f'Invalid number of files: {num_files}')
        return jsonify({'error': ERROR_MESSAGES['num_files']}), 400
    
    zip_name = species_name

    # Selecting data
    all_data = pd.concat([pd.read_csv(CSV_DIRECTORY + 'all_data_0.csv'),
                          pd.read_csv(CSV_DIRECTORY + 'all_data_1.csv')], ignore_index=True)
    data = all_data[all_data['species'] == species_name]
    if date:
        zip_name += f'_{date}'
        data = data[data['datetime'].str.contains(date, na=False)]
    if num_files:
        zip_name += f'_{num_files}'
        data = data.sample(n=int(num_files), random_state=1)

    if len(data) == 0:
        logger.log_error(f'No data found for {species_name} at {date} max {num_files}')
        return jsonify({'error': ERROR_MESSAGES['no_data']}), 404

    logger.log_message(f'SPECIES_REQUEST: {species_name} at {date} max {num_files} ({zip_name}), total of {len(data)} images.')

    # Creating zip
    make_custom_zip(data, zip_name)
    
    # Removing zip after request
    @after_this_request
    def remove_zip(response):
        os.remove(CUSTOM_DIRECTORY + zip_name + '.zip')
        return response
    
    # Sending zip
    return send_from_directory(CUSTOM_DIRECTORY, zip_name + '.zip')
    