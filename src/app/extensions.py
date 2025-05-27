from flask_sqlalchemy import SQLAlchemy
from celery import Celery, Task
from minio import Minio
from megadetector.detection import run_detector
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

minio_client = None
def initialize_minio_client(app):
    global minio_client
    minio_client = Minio(
        app.config['MINIO_URL'],
        access_key=app.config['MINIO_ACCESS_KEY'],
        secret_key=app.config['MINIO_SECRET_KEY']
    )

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

redis_client = None
def initialize_redis_client(app):
    global redis_client
    redis_client = redis.Redis.from_url(app.config['REDIS_APP_URL'])