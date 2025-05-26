import os
import uuid
import argparse
from tqdm import tqdm
import concurrent.futures
import multiprocessing as mp

from dotenv import load_dotenv
from detection import run_detector
from md_visualization import visualization_utils as vis_utils
from minio import Minio
import pandas as pd

load_dotenv()

MAX_THREADS = min(64, 4 * (os.cpu_count() or 4))
MAX_PROCESSES = 2

MINIO_URL = os.environ.get('MINIO_URL')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')

class Downloader:
    MINIO_CLIENT = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    CLASSES = ['bos', 'caae', 'caca', 'can', 'capi', 'cer', 'dam', 'equ', 'fel', 'fsi', 'gen', 'her', 'lep', 'lut', 'lyn', 'mafo', 'mel', 'mus', 'ory', 'ovar', 'ovor', 'rara', 'sus', 'vul']
    MULTIPROCESSING_CONTEXT = mp.get_context("spawn")

    def __init__(self, download_path = 'dataset/', detection = True):
        self.errors = {}
        self.ctx = mp.get_context("spawn")
        self.inference_queue = self.MULTIPROCESSING_CONTEXT.Queue(maxsize=MAX_THREADS * 2)
        self.progress_queue = self.MULTIPROCESSING_CONTEXT.Queue()

        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path, exist_ok=True)

        self.detection = detection

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

    @staticmethod
    def get_bbox(model, image):
        pred = model.generate_detections_one_image(image)['detections'][-1]['bbox']
        return f'{pred[0] + pred[2]/2} {pred[1] + pred[3]/2} {pred[2]} {pred[3]}'

    def process_image(self, model, image_path, label_path, species):
        try:
            image = vis_utils.load_image(image_path)
            image.save(image_path, format='JPEG', quality=100)

            if self.detection and species != "emp":
                with open(label_path, 'w') as file:
                    file.write(f'{self.CLASSES.index(species)} {self.get_bbox(model, image)}')
        except Exception as err:
            self.errors[image_path] = str(err)
            if os.path.exists(image_path): os.remove(image_path)
            if os.path.exists(label_path): os.remove(label_path)


    def get_image(self, image_folder, label_folder, image):
        filename = str(uuid.uuid4())
        image_path = os.path.join(image_folder, f'{filename}.jpg')
        label_path = os.path.join(label_folder, f'{filename}.txt')

        try:
            self.download_image_from_minio(image['path'], image_path)
            self.inference_queue.put((image_path, label_path, image['species']))
        except Exception as err:
            self.errors[image['path']] = str(err)
            if os.path.exists(image_path): os.remove(image_path)

    def inference_worker(self):
        model = run_detector.load_detector('MDV5A') if self.detection else None
        while True:
            item = self.inference_queue.get()
            if item is None: break
            self.process_image(model, *item)
            self.progress_queue.put(1)

    def progress_worker(self, total):
        with tqdm(total=total, desc="Downloading and processing images", unit="images") as progress_bar:
            while True:
                item = self.progress_queue.get()
                if item is None: break
                progress_bar.update(item)

    def download_images(self, df, folder):
        save_directory = os.path.join(self.download_path, folder, '')
        image_folder = os.path.join(save_directory, 'images', '')
        label_folder = os.path.join(save_directory, 'labels', '')
        os.makedirs(image_folder, exist_ok=True)
        os.makedirs(label_folder, exist_ok=True)

        progress = self.MULTIPROCESSING_CONTEXT.Process(target=self.progress_worker, args=(len(df),))
        progress.start()

        inference = [self.MULTIPROCESSING_CONTEXT.Process(target=self.inference_worker) for _ in range(MAX_PROCESSES)]
        for proc in inference: proc.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            for _, row in df.iterrows():
                image = {'path': row['path'], 'species': row['species']}
                executor.submit(self.get_image, image_folder, label_folder, image)

        for _ in range(MAX_PROCESSES): self.inference_queue.put(None)
        for proc in inference: proc.join()

        self.progress_queue.put(None)
        progress.join()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Download images from MinIO and process their bbox.")
    argparser.add_argument('dataset', type=str, help='Path to the dataset CSV file containing image paths and species')
    argparser.add_argument('--folder', type=str, default='./', help='Folder name to save images (default: ./)')
    argparser.add_argument('--path', type=str, default='dataset/', help='Path to save downloaded images (default: dataset/)')
    argparser.add_argument('--no-detection', action='store_true', help='Disable detection for bounding boxes')
    argparser.add_argument('--max-threads', type=int, default=MAX_THREADS, help=f'Maximum number of threads to use (default: {MAX_THREADS})')
    argparser.add_argument('--max-processes', type=int, default=MAX_PROCESSES, help=f'Maximum number of processes to use (default: {MAX_PROCESSES})')

    args = argparser.parse_args()
    MAX_THREADS = args.max_threads
    MAX_PROCESSES = args.max_processes

    downloader = Downloader(download_path=args.path, detection=not args.no_detection)
    downloader.download_images(pd.read_csv(args.dataset), args.folder)