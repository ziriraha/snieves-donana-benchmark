import os

# CSV_DIRECTORY is 'csv/'
# ZIP_DIRECTORY = 'files/dataset_zip/'
# CUSTOM_DIRECTORY = 'files/custom_datasets/'
# DATASET_NAMES are ['train', 'test', 'val']
# PARK_NAMES are ['snieves', 'donana']
# SPECIES_NAMES are ["equ", "cer", "dam", "caca", "bos", "capi", "caae", "ovor", "ovar", "sus",
#                  "fel", "fsi", "lyn", "can", "calu", "vul", "lut", "mel", "mafo", "mupu",
#                  "her", "muni", "gen", "elqu", "ory", "lep", "mus", "rara", "tile", "liz",
#                  "tur", "sna", "bird", "hom", "car", "ani", "carni", "cerni", "emp", "others"]
# ERROR_MESSAGES
#     'dataset': 'Dataset not found. Available datasets: ' + ', '.join(DATASET_NAMES),
#     'park': 'Park not found. Available parks: ' + ', '.join(PARK_NAMES),
#     'species': 'Species not found. Available species: ' + ', '.join(SPECIES_NAMES),
#     'date': 'Invalid date. Date format: DDMMYYYY',
#     'num_files': 'Invalid number of files. Must be a positive integer',
#     'no_data': 'No images found for the specified parameters'
# 

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False

MINIO_URL = os.environ.get('MINIO_URL')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')


REDIS_URL = os.environ.get('REDIS_URL')
CELERY = {
    'broker_url': REDIS_URL,
    'result_backend': REDIS_URL,
}

MAX_REQUEST_ROWS = 10000
