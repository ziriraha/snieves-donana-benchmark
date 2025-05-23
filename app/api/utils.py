from minio import Minio
from megadetector.visualization import visualization_utils as vis_utils
import uuid
from megadetector.detection import run_detector
from pathlib import Path
import os

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


# Will download images from dataframe df and save them into download_path + folder. 
# If bbox is not present, it will be generated and saved into the dataframe.
def download_images(download_path, df, folder):
    aux = download_path
    download_path += folder + '/'
    os.system(f'mkdir -p {download_path}')
    for park in df['park'].unique():
        os.system(f'mkdir -p {download_path + park}')
        for species in df[df['park'] == park]['species'].unique():
            os.system(f'mkdir -p {download_path + park + "/" + species}')

    change = False
    classes = []

    for _, row in df.iterrows():
        dire = download_path + row['park'] + '/' + row['species'] + '/' + str(uuid.uuid4())
        get_image_from_minio(Path(row['path']), Path(dire + '.jpg'))

        # get bbox if not exists
        if row['bbox'] == 'none' and row['species'] != 'emp':
            try:
                with vis_utils.load_image(dire + '.jpg') as image:
                    p = MODEL.generate_detections_one_image(image)['detections'][-1]['bbox']
                    row['bbox'] = f' {p[0] + p[2]/2} {p[1] + p[3]/2} {p[2]} {p[3]}'
                    change = True
            except Exception:
                os.remove(dire + '.jpg')
                try:
                    os.remove(dire + '.txt')
                except Exception: pass

        # write bbox if exists
        if row['bbox'] != 'none':

            # get species index
            if row['species'] not in classes:
                classes.append(row['species'])
            with open(dire + '.txt', 'w') as f:
                f.write(str(classes.index(row['species'])) + " " + row['bbox'])

    # save species indexes
    with open(download_path + 'classes.txt', 'w') as f:
        f.write(str(classes))

    download_path = aux
    return df if change else None