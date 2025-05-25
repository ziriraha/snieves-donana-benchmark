from . import celery, db
import pandas as pd

@celery.task
def import_csv_task(file_path):
    pass