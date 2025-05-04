# Dataset
In this directory there will be files for the analysis and processing of the dataset and the creation of the traininig split.

The confi_dataset.yaml and dataset.yaml files are the ones needed by the models to function.

## Processing
The api_alldata.py script makes the csv for all the data. (full.csv)

Inside the dataset-creation/ folder are available the scripts used to generate the train test val split. The train_set.ipynb is the script that generates the split, it is used twice, once to generate the train and test, another to split train into train and val.

The get_times.py script fetches the datetime of when the photos were taken and the clear_rafagas.py discards the pictures taken within a second of each other based on the previous information.

image_downloader.py is the class used to download the images from a csv into the park/species/img format and generate the .txt with the Megadetector bbox.

### Special Datasets
FasterRCNN expects xml files instead of .txt. For this, the script called "add_xml_annotation.py" was used on a dataset with the shape: images/labels folder. To convert to that shape, the script "chage_shape.py" was used.