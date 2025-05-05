# Models
The models trained are:
- YOLO
- Megadetector
- FasterRCNN

On each folder a script is provided that runs the training and testing of a model. Each script wil create a folder that contains all the files from the operation.

The `utils.py` file contains helper functions used on each of the scripts. When using a specific train-test script please add the `utils.py` in the same directory.

## Datasets
For training some models expect a specific format for the dataset. Megadetector and YOLO use the same format (`dataset.yaml`). Faster RCNN takes a different format (`confi_dataset.yaml`). More information about these datasets in the _dataset_ directory.

## Environment definition
Modify the constant in the `utils.py` file:
- DATASET_YAML: the absolute path to the dataset.yaml file.
- CONFI_DATASET_YAML: the absolute path to the confi_dataset.yaml file.
- TEST_PATH: the absolute path to the downloaded test dataset split.