import logging

from flask import Flask
import click
from flask.cli import with_appcontext

from .extensions import db, celery_init_app
from .tasks import import_data_from_zip, download_dataset_zips

from .views import views_bp
from .api import api_bp

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
        handlers=[
            # logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Populates db with default data. This action may take several minutes to complete."""
    from flask import current_app as app
    click.echo('Importing default data from zip...')
    import_data_from_zip(app.config['DEFAULT_DATA_ZIP_PATH'])
    click.echo('Default data imported successfully.')

@click.command('download-datasets')
@click.option('--background', is_flag=True, default=False, help='Run download in the background.')
@with_appcontext
def download_datasets_command(background):
    """Download datasets to the configured API data directory. This action may take several hours to complete."""
    from flask import current_app as app
    click.echo('Downloading datasets...')
    task = download_dataset_zips.delay(app.config['DEFAULT_DATA_ZIP_PATH'])
    click.echo(f"Download started in the background with id {task.id}. This will take several hours to complete.")
    if not background:
        click.echo('Waiting for download to complete...')
        task.get()
        click.echo('Datasets downloaded successfully.')

@click.command('delete-custom-datasets')
@with_appcontext
def delete_custom_datasets_command():
    """Deletes all custom datasets from the API data directory."""
    from flask import current_app as app
    import os
    api_data_dir = app.config['API_DATA_DIRECTORY']
    if not os.path.exists(api_data_dir):
        click.echo('API data directory does not exist.')
        return

    for filename in os.listdir(api_data_dir):
        if filename.endswith('.zip') and filename not in app.config['DATASETS']:
            file_path = os.path.join(api_data_dir, filename)
            os.remove(file_path)
            click.echo(f'Deleted custom dataset: {filename}')
    click.echo('Custom datasets deleted successfully.')

def create_app():
    setup_logging()

    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    with app.app_context():
        db.create_all()
        
    celery_init_app(app)

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(views_bp, url_prefix='/')

    app.cli.add_command(init_db_command)
    app.cli.add_command(download_datasets_command)
    app.cli.add_command(delete_custom_datasets_command)
    return app