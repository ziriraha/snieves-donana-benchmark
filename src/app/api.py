import os

from celery.result import AsyncResult
from flask import Blueprint, after_this_request, jsonify, request, send_file, current_app
import json

from .constants import (
    DEFAULT_LIMIT,
    ERROR_DATE_FORMAT,
    ERROR_NO_IMAGES_FOUND,
    ERROR_PARK_NOT_FOUND,
    ERROR_SPECIES_NOT_FOUND,
    ERROR_GENERATE_ZIP,
    DATASETS,
    MAX_LIMIT,
)
from .models import Image, Park, Species
from .tasks import generate_zip
from .utils import verify_date
from .extensions import redis_client
import logging
logger = logging.getLogger(__name__)


api_bp = Blueprint('api', __name__)

@api_bp.route('/datasets/<set_name>', methods=['GET'])
async def get_dataset(set_name):
    if set_name not in DATASETS: return jsonify({'error': f"Dataset {set_name} not found. Available datasets are: {', '.join(DATASETS)}"}), 404

    dataset_path = os.path.join(current_app.config['API_DATA_DIRECTORY'], f"{set_name}.zip")
    if not os.path.exists(dataset_path):
        return jsonify({'error': f"Dataset {set_name} not found but should exist."}), 500
    
    return send_file(dataset_path, as_attachment=True, download_name=f"{set_name}.zip"), 200

@api_bp.route('/species', methods=['GET'])
async def get_species():
    species = Species.query.all()
    if not species: return jsonify({'error': ERROR_SPECIES_NOT_FOUND}), 404
    return jsonify([s.to_json() for s in species]), 200

@api_bp.route('/species/<scode>', methods=['GET'])
async def get_species_by_code(scode):
    species = Species.query.filter_by(code=scode).first()
    if not species: return jsonify({'error': ERROR_SPECIES_NOT_FOUND}), 404
    return jsonify(species.to_json()), 200

@api_bp.route('/parks', methods=['GET'])
async def get_parks():
    parks = Park.query.all()
    if not parks: return jsonify({'error': ERROR_PARK_NOT_FOUND}), 404
    return jsonify([p.to_json() for p in parks]), 200

@api_bp.route('/parks/<pcode>', methods=['GET'])
async def get_park_by_code(pcode):
    park = Park.query.filter_by(code=pcode).first()
    if not park: return jsonify({'error': ERROR_PARK_NOT_FOUND}), 404
    return jsonify(park.to_json()), 200

@api_bp.route('/images', methods=['GET'])
async def get_images():
    parks = request.args.get('parks', default=None, type=str)
    species = request.args.get('species', default=None, type=str)
    start_date = request.args.get('start_date', default=None, type=str)
    end_date = request.args.get('end_date', default=None, type=str)
    if not verify_date(start_date) and not verify_date(end_date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = min(request.args.get('limit', default=DEFAULT_LIMIT, type=int), MAX_LIMIT)
    offset = request.args.get('offset', default=0, type=int)

    query = Image.query
    if parks: query = query.filter(Image.park.has(Park.code.in_(parks.split(','))))
    if species: query = query.filter(Image.species.has(Species.code.in_(species.split(','))))
    if start_date: query = query.filter(Image.date >= start_date)
    if end_date: query = query.filter(Image.date <= end_date)
    images = query.order_by(Image.id).offset(offset).limit(limit).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404

    return jsonify([img.to_json() for img in images]), 200

@api_bp.route('/queries', methods=['POST'])
async def create_job():
    parks = request.form.getlist('parks', type=str)
    species = request.form.getlist('species', type=str)
    start_date = request.form.get('start_date', type=str)
    end_date = request.form.get('end_date', type=str)
    if not verify_date(start_date) and not verify_date(end_date): return jsonify({'error': ERROR_DATE_FORMAT}), 400
    limit = min(request.form.get('limit', DEFAULT_LIMIT, type=int), MAX_LIMIT)
    offset = request.form.get('offset', default=0, type=int)

    parks = [p.strip() for p in parks if p.strip()]
    species = [s.strip() for s in species if s.strip()]

    query = Image.query
    if parks: query = query.filter(Image.park.has(Park.code.in_(parks)))
    if species: query = query.filter(Image.species.has(Species.code.in_(species)))
    if start_date: query = query.filter(Image.date >= start_date)
    if end_date: query = query.filter(Image.date <= end_date)
    images = query.order_by(Image.id).offset(offset).limit(limit).all()
    if not images: return jsonify({'error': ERROR_NO_IMAGES_FOUND}), 404

    task = generate_zip.delay([img.to_dict() for img in images])

    redis_client.set(f'status:{task.id}', json.dumps({
        'status': 'Dispatched job... Waiting for it to start.',
        'progress': 0,
        'total': len(images)
    }))

    return jsonify({'query_id': task.id}), 202

@api_bp.route('/queries/<query_id>', methods=['GET'])
async def get_job_status(query_id):
    task = redis_client.get(f'status:{query_id}')
    async_task = AsyncResult(query_id)
    if not (task and async_task): return jsonify({'error': 'Query information not found.'}), 404

    task_status = json.loads(task)
    response = {
        "query_id": query_id,
        "status": task_status['status'],
        "progress": round(task_status['progress'] / task_status['total'] * 100)
    }

    if async_task.failed():
        redis_client.delete(f'status:{query_id}')
        response['failed'] = True
        response['error'] = async_task.result if async_task.result else 'An error occurred while processing the request.'
    elif async_task.successful():
        redis_client.delete(f'status:{query_id}')
        response['completed'] = True

    return jsonify(response), 200

@api_bp.route('/queries/<query_id>/download', methods=['GET'])
async def get_job_result(query_id):
    task = AsyncResult(query_id)
    zip_file = task.get()
    if not zip_file: return jsonify({'error': ERROR_GENERATE_ZIP}), 500

    @after_this_request
    def remove_zip(response):
        os.remove(zip_file)
        redis_client.delete(f'status:{query_id}')
        return response

    return send_file(zip_file, as_attachment=True, download_name=f'{query_id}.zip'), 200
