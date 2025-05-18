from minio import Minio
from constants import TOKEN_MINIO
from md_visualization import visualization_utils as vis_utils
import uuid
from detection import run_detector
from pathlib import Path
import os

# Verify if the date provided is valid
def verify_date(date_str):
    try:
        if len(date_str) != 8:
            return False
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:])
        if day < 1 or day > 31 or month < 1 or month > 12 or year < 1000:
            return False
        return True
    except ValueError:
        return False

# Verify if the number of files provided is valid
def verify_num_files(num_files_str):
    try:
        num_files = int(num_files_str)
        return num_files > 0
    except ValueError:
        return False

MINIO_URL = os.getenv('MINIO_URL')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET = os.getenv('MINIO_BUCKET')

mi_client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

def get_image_from_minio(image: Path, path_to_save: Path):
    mi_client.fget_object(
        bucket_name=MINIO_BUCKET,
        object_name=image.as_posix(),
        file_path=path_to_save.as_posix())

if not os.path.exists("yolov5"):
    os.system("git clone https://github.com/ultralytics/yolov5")    

MODEL = run_detector.load_detector('MDV5A')


# Will download images from dataframe df and save them into DOWNLOAD_PATH + folder. 
# If bbox is not present, it will be generated and saved into the dataframe.
def download_images(DOWNLOAD_PATH, df, folder):
    aux = DOWNLOAD_PATH
    DOWNLOAD_PATH += folder + '/'
    os.system(f'mkdir -p {DOWNLOAD_PATH}')
    for park in df['park'].unique():
        os.system(f'mkdir -p {DOWNLOAD_PATH + park}')
        for species in df[df['park'] == park]['species'].unique():
            os.system(f'mkdir -p {DOWNLOAD_PATH + park + "/" + species}')

    change = False
    classes = []

    for _, row in df.iterrows():
        dire = DOWNLOAD_PATH + row['park'] + '/' + row['species'] + '/' + str(uuid.uuid4())
        get_image_from_minio(Path(row['path']), Path(dire + '.jpg'))

        # get bbox if not exists
        if row['bbox'] == 'none' and row['species'] != 'emp':
            try:
                with vis_utils.load_image(dire + '.jpg') as image:
                    p = MODEL.generate_detections_one_image(image)['detections'][-1]['bbox']
                    row['bbox'] = f' {p[0] + p[2]/2} {p[1] + p[3]/2} {p[2]} {p[3]}'
                    change = True
            except Exception as e:
                os.remove(dire + '.jpg')
                try:
                    os.remove(dire + '.txt')
                except: pass

        # write bbox if exists
        if row['bbox'] != 'none':

            # get species index
            if row['species'] not in classes:
                classes.append(row['species'])
            with open(dire + '.txt', 'w') as f:
                f.write(str(classes.index(row['species'])) + " " + row['bbox'])

    # save species indexes
    with open(DOWNLOAD_PATH + 'classes.txt', 'w') as f:
        f.write(str(classes))

    DOWNLOAD_PATH = aux
    return df if change else None