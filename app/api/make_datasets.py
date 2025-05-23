from app.utils.constants import CUSTOM_DIRECTORY, DATASET_NAMES, CSV_DIRECTORY, ZIP_DIRECTORY
from utils import download_images
import os
import pandas as pd
import datetime
import shutil
import logging

logger = logging.getLogger(__name__)

# Will create a zip full of images from dataset.
def make_dataset_zip(dataset_name):
    if dataset_name not in DATASET_NAMES:
        raise ValueError('Invalid dataset name')
    if not os.path.exists(CSV_DIRECTORY + dataset_name + '.csv'):
        raise ValueError('Dataset CSV not found')
    
    if os.path.exists(ZIP_DIRECTORY + dataset_name + '.zip'):
        os.remove(ZIP_DIRECTORY + dataset_name + '.zip')
    if os.path.exists(ZIP_DIRECTORY + 'temp/' + dataset_name):
        os.remove(ZIP_DIRECTORY + 'temp/' + dataset_name)

    os.makedirs(ZIP_DIRECTORY + 'temp/' + dataset_name, exist_ok=True)

    data = pd.read_csv(CSV_DIRECTORY + dataset_name + '.csv')

    # Download images
    res = download_images(ZIP_DIRECTORY + 'temp/', data, dataset_name)
    # If new bboxes are added, update the dataset csv file
    if not res:
        os.rename(CSV_DIRECTORY + dataset_name + '.csv', 
                  CSV_DIRECTORY + dataset_name + f'_old{datetime.datetime.now()}.csv')
        res.to_csv(CSV_DIRECTORY + dataset_name + '.csv', index=False)

    #os.system(f'zip -r {ZIP_DIRECTORY + dataset_name}.zip {ZIP_DIRECTORY + "temp/" + dataset_name}')
    shutil.make_archive(ZIP_DIRECTORY + dataset_name, 'zip', ZIP_DIRECTORY + "temp/" + dataset_name)
    os.system(f'rm -rf {ZIP_DIRECTORY + "temp/" + dataset_name}')

# Will create a zip full of images from dataframe.
def make_custom_zip(dataframe, name):
    if os.path.exists(CUSTOM_DIRECTORY + name + '.zip'):
        return
    os.makedirs(CUSTOM_DIRECTORY + 'temp/' + name, exist_ok=True)

    # Download images
    res = download_images(CUSTOM_DIRECTORY + 'temp/', dataframe, name)
    # If new bboxes are added, update the all_data.csv file
    if not res:
        logger.info(f'All data updated with new bboxes from {name}')
        all_data = pd.read_csv(CSV_DIRECTORY + 'all_data.csv', ignore_index=True)
        for _, row in res.iterrows():
            all_data.loc[all_data['path'] == row['path']] = row

        os.rename(CSV_DIRECTORY + 'all_data.csv',
                  CSV_DIRECTORY + f'all_data_old{datetime.datetime.now()}.csv')
        all_data.to_csv(CSV_DIRECTORY + 'all_data.csv', index=False)

    shutil.make_archive(CUSTOM_DIRECTORY + name, 'zip', CUSTOM_DIRECTORY + "temp/" + name)
    #os.system(f'zip -r {name}.zip {name}')
    os.system(f'rm -rf {CUSTOM_DIRECTORY + "temp/" + name}')