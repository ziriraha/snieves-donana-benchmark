from flask import Blueprint, request, jsonify, after_this_request, send_file
from .models import Park, Species, Image
import os
from .tasks import generate_zip
from .utils import verify_date, verify_num_files
from .constants import ERROR_DATE_FORMAT, ERROR_LIMIT_FORMAT, ERROR_PARK_NOT_FOUND, ERROR_SPECIES_NOT_FOUND, ERROR_NO_IMAGES_FOUND

api_bp = Blueprint('api', __name__) 
# TODO: use date range?
# TODO: use limit + offset in all of them

@api_bp.route('/datasets/<set>', methods=['GET'])
def get_dataset(dataset_name):
    # TODO: Implement dataset retrieval logic
    return jsonify({'message': f'Dataset {dataset_name} is not implemented yet.'}), 501

@api_bp.route('/parks/<pcode>', methods=['GET'])
def get_park_images(pcode): 
    park = Park.query.filter_by(code=pcode).first()
    if not park: return jsonify({'error': ERROR_PARK_NOT_FOUND}), 404
    date = request.args.get('date')
    if not verify_date(date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = request.args.get('limit')
    if not verify_num_files(limit): return jsonify({'error': ERROR_LIMIT_FORMAT}), 400

    images = Image.query.filter_by(park_id=park.id, date=date).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404
    
    task = generate_zip(images)
    zip_file = task.get()

    @after_this_request
    def remove_zip(response):
        os.remove(zip_file)
        return response

    return send_file(zip_file, as_attachment=True, download_name=f'{park.code}_images.zip')

@api_bp.route('/parks/<pcode>/species/<scode>', methods=['GET'])
def get_park_species_images(pcode, scode):
    park = Park.query.filter_by(code=pcode).first()
    if not park: return jsonify({'error': ERROR_PARK_NOT_FOUND}), 404
    species = Species.query.filter_by(code=scode).first()
    if not species: return jsonify({'error': ERROR_SPECIES_NOT_FOUND}), 404
    date = request.args.get('date')
    if not verify_date(date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = request.args.get('limit')
    if not verify_num_files(limit): return jsonify({'error': ERROR_LIMIT_FORMAT}), 400

    images = Image.query.filter_by(park_id=park.id, species_id=species.id, date=date).limit(limit).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404
    
    task = generate_zip(images)
    zip_file = task.get()

    @after_this_request
    def remove_zip(response):
        os.remove(zip_file)
        return response
    
    return send_file(zip_file, as_attachment=True, download_name=f'{park.code}_{species.code}_images.zip', mimetype='application/zip')

@api_bp.route('/species/<scode>', methods=['GET'])
def get_species_images(scode):
    # ERROR HANDLING
    species = Species.query.filter_by(code=scode).first()
    if not species: return jsonify({'error': ERROR_SPECIES_NOT_FOUND}), 404
    date = request.args.get('date')
    if not verify_date(date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = request.args.get('limit')
    if not verify_num_files(limit): return jsonify({'error': ERROR_LIMIT_FORMAT}), 400
    
    images = Image.query.filter_by(species_id=species.id, date=date).limit(limit).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404
    
    task = generate_zip(images)
    zip_file = task.get()

    @after_this_request
    def remove_zip(response):
        os.remove(zip_file)
        return response

    return send_file(zip_file, as_attachment=True, download_name=f'{species.code}_images.zip', mimetype='application/zip')
