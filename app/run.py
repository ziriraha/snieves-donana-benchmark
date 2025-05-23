from dotenv import load_dotenv
from flask import Flask
import os
import logging

from api.make_datasets import make_dataset_zip

from api import api_bp
from views import views_bp

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

app.config.from_pyfile('config.py')

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(views_bp, url_prefix='/')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # # Verifying if the dataset zip files exist
    # # If they don't exist, they are created
    # if os.path.exists(ZIP_DIRECTORY):
    #     for dataset in DATASET_NAMES:
    #         if not os.path.exists(ZIP_DIRECTORY + dataset + '.zip'):
    #             make_dataset_zip(dataset)
    # else: 
    #     os.makedirs(ZIP_DIRECTORY)
    #     for dataset in DATASET_NAMES:
    #         make_dataset_zip(dataset)

    # # Creating the custom datasets directory if it doesn't exists
    # os.makedirs(CUSTOM_DIRECTORY, exist_ok=True)

    logger.info('App started')
    app.run(debug=True)
