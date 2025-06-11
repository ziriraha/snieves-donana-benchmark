# How to run the Web App
Create a `.env` file with the following variables (see example.env):
- MINIO_URL
- MINIO_ACCESS_KEY
- MINIO_SECRET_KEY
- MINIO_BUCKET

To run the app execute the following command in the `src` directory with docker and docker-compose installed:
```bash
docker compose up --build -d
```
Optionally, you can use `--scale celery=3` to scale the celery to use 3 workers, which can help with performance when processing large datasets. And the `config.toml` file can be modified to add more workers for the flask app. These actions will consume more resources.

To populate the database, open a shell in the flask app container and run the init-db command:
```bash
docker compose exec -it app /bin/bash
flask init-db
```
This will run the data importation task, it may take up to 5 minutes for the data to appear on the database.

For generating the train, val and test dataset zip:
```bash
flask download-datasets
```
This will start a celery task to download the datasets, to view the progress take a look at the celery logs. This action may take several hours to complete. And 200 GBs of storage are needed.

In case you ever need to delete custom datasets:
```bash
flask delete-custom-datasets
```

Once the app is running, you can access it at `http://localhost:4000/`.

# Files needed
The `db-data.zip` file contains all the information the app needs. The `inference.pt` file is necessary for the inference.

# How to use the API
Inside the web page `/api/` you may find API documentation on how to use the endpoints.