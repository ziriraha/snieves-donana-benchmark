from flask import Blueprint, render_template

from .models import Species, Park
from .constants import INFERENCE_CLASSES

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
async def home():
    return render_template('home.html')

@views_bp.route('/dataset/')
async def dataset():
    to_json = lambda x: x.to_json()
    species_list = map(to_json, Species.query.all())
    parks_list = map(to_json, Park.query.all())
    return render_template('dataset.html', 
                           species_list=species_list,
                           parks_list=parks_list)

@views_bp.route('/inference/')
async def inference():
    inference_species = Species.query.filter(Species.code.in_(INFERENCE_CLASSES)).order_by(Species.scientific_name).all()
    return render_template('inference.html', species_list=[s.to_json() for s in inference_species])

@views_bp.route('/benchmark/')
async def benchmark():
    return render_template('benchmark.html')

@views_bp.route('/api/')
async def api():
    return render_template('api.html')