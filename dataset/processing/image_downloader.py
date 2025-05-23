from minio import Minio
from md_visualization import visualization_utils as vis_utils
import uuid
from detection import run_detector
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

MINIO_URL = os.environ.get('MINIO_URL')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')

classes = ['mus', 'rara', 'ory', 'emp', 'fsi', 'lyn', 'lut', 'sus', 'mel', 'vul', 'lep', 'equ', 'cer', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'ovar', 'mafo', 'capi', 'caae', 'ovor', 'caca'] # class names

MINIO_CLIENT = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

def get_image_from_minio(image):
    return MINIO_CLIENT.get_object(
        bucket_name=MINIO_BUCKET,
        object_name=image)

def download_image_from_minio(image: Path, path_to_save: Path):
    MINIO_CLIENT.fget_object(
        bucket_name=MINIO_BUCKET,
        object_name=image.as_posix(),
        file_path=path_to_save.as_posix())

parks = {
    'donana': ['donana penelope final', 'TAGGED_UMA_DONANA', 'donana tagges daphne y alejandro', 'CamptrapD', 'donana TAG76jun2019', 'CamtrapF', 'first images she reviewed 4dec2018 tagged', '6_8_may_2019 tagged', 'CamtrapB'],
    'snieves': ['IAcitizens_tagged_NO SHARE', 'fotos etiquetadas Snieves', 'Snieves', 'IAcitizens_tagged', 'SNieves revisiones 1-4']
}

class DOWNLOADER:
    def __init__(self, DOWNLOAD_PATH = 'dataset/', OBJECT_DETECTION = True, VERBOSE = False, DEBUG_IMG = False) -> None:
        self.ERROR_IMAGES = []
        self.OBJECT_DETECTION = OBJECT_DETECTION
        self.DEBUG_IMG = DEBUG_IMG
        self.VERBOSE = VERBOSE
        self.DOWNLOAD_PATH = DOWNLOAD_PATH
        if OBJECT_DETECTION:
            self.MODEL = run_detector.load_detector('MDV5A')

    # Returns the park where the image is located based on the path of the image on MinIO
    def get_park(self, path):
        if any(subf in parks['donana'] for subf in path.split('/')): return 'donana'
        elif any(subf in parks['snieves'] for subf in path.split('/')): return 'snieves'
        else: return 'other'

    # Uses Megadetector to calculate the bbox of the animal in the image.
    def get_annotations(self, img, dire, clase, model="YOLO"):
        #img = vis_utils.load_image(dire + '.jpg')
        pred = self.MODEL.generate_detections_one_image(img)['detections'][-1]
        if self.DEBUG_IMG:
            vis_utils.render_detection_bounding_boxes([pred], img)
            img.save(dire + '_annotated.jpg')
        with open(dire + '.txt', 'w') as f:
            p = pred['bbox']
            f.write(str(classes.index(clase)) + f' {p[0] + p[2]/2} {p[1] + p[3]/2} {p[2]} {p[3]}')

    # Downloads the image from MinIO and saves it in the DOWNLOAD_PATH folder
    # with the format park/species/uuid.jpg and annotation is saved in park/species/uuid.txt
    def get_image(self, path, clase, park="NOPARK"):
        if park == "NOPARK":
            park = self.get_park(path)
        dire = self.DOWNLOAD_PATH + park + '/' + clase + '/' + str(uuid.uuid4())
        download_image_from_minio(Path(path), Path(dire + '.jpg'))
        try:
            image = vis_utils.load_image(dire + '.jpg')
            image.save(dire + '.jpg', format='JPEG', quality=100)
            if self.OBJECT_DETECTION:
                if clase != "emp":
                    self.get_annotations(image, dire, clase)
        except Exception as e:
            self.ERROR_IMAGES.append((path, clase, e))
            os.remove(dire + '.jpg')
            try:
                os.remove(dire + '.txt')
            except: pass

    # Downloads the image from a row.
    def get_image_from_row(self, row):
        self.get_image(row['path'], row['species'], row['park'])

    def get_error_images(self):
        return self.ERROR_IMAGES
    
    # Downloads a single image and returns the path where it was saved.
    def download_image(self, path):
        res_path = self.DOWNLOAD_PATH + str(uuid.uuid4()) + '.jpg'
        download_image_from_minio(Path(path), Path(res_path))
        return res_path
    
    # Downloads all the images from a dataframe and saves them in the folder specified.
    def download_images(self, df, folder):
        aux = self.DOWNLOAD_PATH
        self.DOWNLOAD_PATH += folder + '/'
        df = df.reset_index(drop=True)
        m = df.shape[0]
        for i, row in df.iterrows():
            if self.VERBOSE: print(f'\rDownloaded {i/m*100:.2f}%   ', end='')
            self.get_image_from_row(row)
        if self.VERBOSE: print('\rCOMPLETE                       ')
        self.DOWNLOAD_PATH = aux
    
    def reset_error_count(self):
        self.ERROR_IMAGES = []
    
    def clear_directory(self, folder=""):
        os.system(f'rm -rf {self.DOWNLOAD_PATH + folder}')