# Models
The models trained are:
- YOLO
- Megadetector
- FasterRCNN

On this folder scripts are provided that run the training and testing of a model. Each script wil create a folder that contains all the files from the operation.

The `utils.py` file contains helper functions used on each of the scripts. When using a specific train-test script please add the `utils.py` in the same directory.

## Datasets
For training some models expect a specific format for the dataset. Megadetector and YOLO use the same format (`dataset.yaml`). Faster RCNN takes a different format (`confi_dataset.yaml`). More information about these datasets in the _dataset_ directory.

## Running the Training-Testing
1. Add the `utils.py` in the same directory as the train-test script.
2. Modify the constant in the `utils.py` file:
    - DATASET_YAML: the absolute path to the dataset.yaml file.
    - CONFI_DATASET_YAML: the absolute path to the confi_dataset.yaml file.
    - TEST_PATH: the absolute path to the downloaded test dataset split.

3. Install the required python modules (some are used for the study of the model in the `analysis/study.ipynb` notebook):
```bash
pip install -r requirements.txt
```
It's recommended to use a virtual environment.

3. Run the train-test scripts (or individual script):
```bash
python3 train_test_*.py
```

## Analysis
In the `analysis/` folder is available the notebook used to analyze the models. In the `analysis/images/` folder is where the graphs generated were saved manually.

To use the `study.ipynb` notebook just add the model's values text file in the same directory and modify the model names in the notebook (you also have to choose a color for each model).