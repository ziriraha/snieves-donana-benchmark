import os

DATA_ZIP_PATH = './csv/archive.zip'

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False

REDIS_URL = os.getenv('REDIS_URL')
REDIS_CELERY_URL = REDIS_URL + '/0'

CELERY = {
    'broker_url': REDIS_CELERY_URL,
    'result_backend': REDIS_CELERY_URL,
}
MAX_CELERY_THREADS = (os.cpu_count() or 4) * 2

API_DATA_DIR = os.getenv('API_DATA_DIR', './api_data/')

MINIO_URL = os.getenv('MINIO_URL')
MINIO_BUCKET = os.getenv('MINIO_BUCKET')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')

DATASET_DIRECTORY = './api_data/'
