from celery import Celery, Task
from flask_sqlalchemy import SQLAlchemy
from megadetector.detection import run_detector
from .config import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, REDIS_APP_URL
from minio import Minio
import redis

db = SQLAlchemy()

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_config = app.config["CELERY"]
    celery_app.config_from_object(celery_config)
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

minio_client = Minio(MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

redis_client = redis.from_url(REDIS_APP_URL)

bbox_model = None
def get_bbox_model():
    global bbox_model
    if bbox_model is None:
        bbox_model = run_detector.load_detector('MDV5A')
    return bbox_model

detection_model = None
def get_detection_model():
    global detection_model
    if detection_model is None:
        pass # Load my model here
    return detection_model