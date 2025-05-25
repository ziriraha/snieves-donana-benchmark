from flask import Flask
from dotenv import load_dotenv
import logging

from .extensions import db, celery_init_app
from .views import views_bp

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    with app.app_context():
        db.create_all()
        
    celery_init_app(app)

    # app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(views_bp, url_prefix='/')
    return app

