import os
import shutil
import uuid

from dotenv import load_dotenv
from megadetector.detection import run_detector
from megadetector.visualization import visualization_utils as vis_utils
from minio import Minio

load_dotenv()

MINIO_URL = os.environ.get('MINIO_URL')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')

class Downloader:
    MINIO_CLIENT = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    CLASSES = ['mus', 'rara', 'ory', 'emp', 'fsi', 'lyn', 'lut', 'sus', 'mel', 'vul', 'lep', 'equ', 'cer', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'ovar', 'mafo', 'capi', 'caae', 'ovor', 'caca'] # class names

    def __init__(self, download_path = 'dataset/', detection = True):
        self.errors = {}

        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path, exist_ok=True)

        self.detection = detection
        if detection:
            self.MODEL = run_detector.load_detector('MDV5A')

    @classmethod
    def download_image_from_minio(cls, image, save_file):
        cls.MINIO_CLIENT.fget_object(
            bucket_name=MINIO_BUCKET,
            object_name=image,
            file_path=save_file)
        
    @classmethod
    def get_image_from_minio(cls, image):
        return cls.MINIO_CLIENT.get_object(
            bucket_name=MINIO_BUCKET,
            object_name=image)

    def get_bbox(self, image):
        pred = self.MODEL.generate_detections_one_image(image)['detections'][-1]['bbox']
        return f'{pred[0] + pred[2]/2} {pred[1] + pred[3]/2} {pred[2]} {pred[3]}'

    def get_image(self, object_path, save_path, species):
        filename = str(uuid.uuid4())
        image_path = os.path.join(save_path, f'{filename}.jpg')
        label_path = os.path.join(save_path, f'{filename}.txt')
        
        try:
            self.download_image_from_minio(object_path, image_path)
            image = vis_utils.load_image(image_path)
            image.save(image_path, format='JPEG', quality=100)

            if self.detection and species != "emp":
                with open(label_path, 'w') as file:
                    file.write(f'{self.CLASSES.index(species)} {self.get_bbox(image)}')

        except Exception as err:
            self.errors[object_path] = str(err)
            if os.path.exists(image_path):
                os.remove(image_path)
            if os.path.exists(label_path):
                os.remove(label_path)
    
    def download_images(self, df, folder):
        save_directory = os.path.join(self.download_path, folder)

        for _, row in df.reset_index(drop=True).iterrows():
            save_path = os.path.join(save_directory, row['park'], row['species'])
            os.makedirs(save_path, exist_ok=True)
            self.get_image(row['path'], save_path, row['species'])
    
    def clear_download_path(self, folder=""):
        path = os.path.join(self.download_path, folder)
        shutil.rmtree(path, ignore_errors=True)