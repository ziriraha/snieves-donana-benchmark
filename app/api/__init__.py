from flask import Blueprint

from park import get_park_images
from parkspecies import get_park_species_images
from species import get_species_images
from datasets import get_dataset

api_bp = Blueprint('api', __name__, url_prefix='/api')

api_bp.add_url_rule('/dataset/<dataset_name>', view_func=get_dataset, methods=['GET'])
api_bp.add_url_rule('/park/<park_name>', view_func=get_park_images, methods=['GET'])
api_bp.add_url_rule('/park/<park_name>/species/<species_name>', view_func=get_park_species_images, methods=['GET'])
api_bp.add_url_rule('/species/<species_name>', view_func=get_species_images, methods=['GET'])
