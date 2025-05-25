from app import create_app, setup_logging
setup_logging()

flask_app = create_app()
celery_app = flask_app.extensions["celery"]