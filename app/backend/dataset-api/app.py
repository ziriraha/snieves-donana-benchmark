from flask import Flask
import logger
import os
from dotenv import load_dotenv

load_dotenv()

from park import park
from parkspecies import parkspecies
from species import species
from datasets import dataset

from make_datasets import make_dataset_zip

from constants import CUSTOM_DIRECTORY, ZIP_DIRECTORY, DATASET_NAMES

app = Flask(__name__)

# Obtener subconjunto de datos de entrenamiento (zip)
# Obtener subconjunto de datos de validación (zip)
# Obtener subconjunto de datos de test (zip)
app.register_blueprint(dataset)

# Obtener datos por parque natural y fecha (es opcional si no se indica se devuelven todos) (zip)
# /park/<park_name>
app.register_blueprint(park)

# Obtener datos por especie, fecha y número de ficheros (ambos opcionales si no se indica se devuelven todos) (zip)
# /species/<species_name>
app.register_blueprint(species)

# Obtener datos por parque natural, especie, fecha y número de ficheros (ambos opcionales si no se indica se devuelven todos) (zip)
# /park/<park_name>/species/<species_name>
app.register_blueprint(parkspecies)
    

if __name__ == '__main__':
    load_dotenv()

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

    logger.start_log()
    app.run() #you can add debug. True if you want to debug the app
