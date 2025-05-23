from dotenv import load_dotenv
from flask import Flask
import os
from api import api_bp
import logging

load_dotenv()

app = Flask(__name__)

app.register_blueprint(api_bp)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Verifying if the dataset zip files exist
    # If they don't exist, they are created
    if os.path.exists(ZIP_DIRECTORY):
        for dataset in DATASET_NAMES:
            if not os.path.exists(ZIP_DIRECTORY + dataset + '.zip'):
                make_dataset_zip(dataset)
    else: 
        os.makedirs(ZIP_DIRECTORY)
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #    executor.map(make_dataset_zip, DATASET_NAMES)
        for dataset in DATASET_NAMES:
            make_dataset_zip(dataset)

    # Creating the custom datasets directory if it doesn't exists
    os.makedirs(CUSTOM_DIRECTORY, exist_ok=True)

    logger.info('App started')
    app.run(debug=True)
