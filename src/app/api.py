import os

# from celery.result import AsyncResult
from flask import Blueprint, after_this_request, jsonify, request, send_file

from .constants import (
    DEFAULT_LIMIT,
    ERROR_DATE_FORMAT,
    ERROR_NO_IMAGES_FOUND,
    ERROR_PARK_NOT_FOUND,
    ERROR_SPECIES_NOT_FOUND,
    ERROR_GENERATE_ZIP,
    MAX_LIMIT,
)
from .models import Image, Park, Species
from .tasks import generate_zip
from .utils import verify_date

api_bp = Blueprint('api', __name__) 

@api_bp.route('/datasets/<set>', methods=['GET'])
def get_dataset(dataset_name):
    # TODO: Implement dataset retrieval logic
    return jsonify({'message': f'Dataset {dataset_name} is not implemented yet.'}), 501

@api_bp.route('/queries/parks/<pcode>', methods=['GET', 'POST'])
def get_park_images(pcode):
    park = Park.query.filter_by(code=pcode).first()
    if not park: return jsonify({'error': ERROR_PARK_NOT_FOUND}), 404

    start_date = request.args.get('start_date', default=None, type=str)
    end_date = request.args.get('end_date', default=None, type=str)
    if not verify_date(start_date) and not verify_date(end_date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = min(request.args.get('limit', default=DEFAULT_LIMIT, type=int), MAX_LIMIT)
    offset = request.args.get('offset', default=0, type=int)

    query = Image.query.filter_by(park_id=park.id)
    if start_date: query = query.filter(Image.date >= start_date)
    if end_date: query = query.filter(Image.date <= end_date)
    images = query.order_by(Image.id).offset(offset).limit(limit).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404

    if request.method == 'GET':
        return jsonify([img.to_json() for img in images]), 200
    
    task = generate_zip.delay([img.to_dict() for img in images])
    zip_file = task.get()
    if not zip_file: return jsonify({'error': ERROR_GENERATE_ZIP}), 500

    @after_this_request
    def remove_zip(response):
        os.remove(zip_file)
        return response

    return send_file(zip_file, as_attachment=True, download_name=f'{park.code}_{offset}_to_{offset+limit}.zip')

@api_bp.route('/queries/parks/<pcode>/species/<scode>', methods=['GET', 'POST'])
def get_park_species_images(pcode, scode):
    park = Park.query.filter_by(code=pcode).first()
    if not park: return jsonify({'error': ERROR_PARK_NOT_FOUND}), 404
    species = Species.query.filter_by(code=scode).first()
    if not species: return jsonify({'error': ERROR_SPECIES_NOT_FOUND}), 404
    
    start_date = request.args.get('start_date', default=None, type=str)
    end_date = request.args.get('end_date', default=None, type=str)
    if not verify_date(start_date) and not verify_date(end_date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = min(request.args.get('limit', default=DEFAULT_LIMIT, type=int), MAX_LIMIT)
    offset = request.args.get('offset', default=0, type=int)

    query = Image.query.filter_by(park_id=park.id, species_id=species.id)
    if start_date: query = query.filter(Image.date >= start_date)
    if end_date: query = query.filter(Image.date <= end_date)
    images = query.order_by(Image.id).offset(offset).limit(limit).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404

    if request.method == 'GET':
        return jsonify([img.to_json() for img in images]), 200
    
    task = generate_zip.delay([img.to_dict() for img in images])
    zip_file = task.get()
    if not zip_file: return jsonify({'error': ERROR_GENERATE_ZIP}), 500

    @after_this_request
    def remove_zip(response):
        os.remove(zip_file)
        return response
    
    return send_file(zip_file, as_attachment=True, download_name=f'{park.code}_{species.code}_{offset}_to_{offset+limit}.zip'), 200

@api_bp.route('/queries/species/<scode>', methods=['GET', 'POST'])
def get_species_images(scode):
    species = Species.query.filter_by(code=scode).first()
    if not species: return jsonify({'error': ERROR_SPECIES_NOT_FOUND}), 404
    
    start_date = request.args.get('start_date', default=None, type=str)
    end_date = request.args.get('end_date', default=None, type=str)
    if not verify_date(start_date) and not verify_date(end_date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = min(request.args.get('limit', default=DEFAULT_LIMIT, type=int), MAX_LIMIT)
    offset = request.args.get('offset', default=0, type=int)
    
    query = Image.query.filter_by(species_id=species.id)
    if start_date: query = query.filter(Image.date >= start_date)
    if end_date: query = query.filter(Image.date <= end_date)
    images = query.order_by(Image.id).offset(offset).limit(limit).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404
    
    if request.method == 'GET':
        return jsonify([img.to_json() for img in images]), 200

    task = generate_zip.delay([img.to_dict() for img in images])
    zip_file = task.get()
    if not zip_file: return jsonify({'error': ERROR_GENERATE_ZIP}), 500

    @after_this_request
    def remove_zip(response):
        os.remove(zip_file)
        return response

    return send_file(zip_file, as_attachment=True, download_name=f'{species.code}_{offset}_to_{offset+limit}.zip'), 200

# @api_bp.route('/jobs/<job_id>', methods=['GET'])
# def get_job_status(job_id):
#     task = AsyncResult(job_id)
#     return jsonify({
#         'job_id': job_id,
#         'status': task.status,
#         'progress': task.info.get('progress', 0),
#     }), 200

# @api_bp.route('/jobs/<job_id>/result', methods=['GET'])
# def get_job_result(job_id):
#     task = AsyncResult(job_id)
#     zip_file = task.get()
#     if not zip_file: return jsonify({'error': ERROR_GENERATE_ZIP}), 500
#     return send_file(zip_file, as_attachment=True, download_name=f'{job_id}.zip'), 200
