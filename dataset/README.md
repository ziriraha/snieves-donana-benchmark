# Dataset
In this directory there will be files for the analysis and processing of the dataset and the creation of the traininig split.
The scripts were tested and written for Python 3.9.6.

The `confi_dataset.yaml` and `dataset.yaml` files are the ones needed by the models to function.

## Classes provided
| Label | Scientific name          | Name                                     |
|-------|--------------------------|------------------------------------------|
| equ   | Equus ferus              | horse                                    |
| cer   | Cervus elaphus           | red deer                                 |
| dam   | Dama dama                | fallow deer                              |
| caca  | Capreolus capreolus      | roe deer                                 |
| bos   | Bos primigenius          | cow                                      |
| capi  | Capra pyrenaica          | Spanish ibex                             |
| caae  | Capra aegagrus hircus    | domestic goat                            |
| ovor  | Ovis orientalis musimon  | mouflon                                  |
| ovar  | Ovis orientalis aries    | sheep                                    |
| sus   | Sus scrofa               | wild boar                                |
| fel   | Felis catus              | domestic cat                             |
| fsi   | Felis silvestris         | wildcat                                  |
| lyn   | Lynx pardinus            | Iberian lynx                             |
| can   | Canis lupus familiaris   | domestic dog                             |
| calu  | Canis lupus              | wolf                                     |
| vul   | Vulpes vulpes            | red fox                                  |
| lut   | Lutra lutra              | otter                                    |
| mel   | Meles meles              | badger                                   |
| mafo  | Martes foina             | beech marten                             |
| mupu  | Mustela putorius         | European polecat                         |
| her   | Herpestes ichneumon      | Egyptian mongoose                        |
| muni  | Mustela nivalis          | weasel                                   |
| gen   | Genetta genetta          | common genet                             |
| elqu  | Elyomis quercinus        | garden dormouse                          |
| ory   | Oryctolagus cuniculus    | rabbit                                   |
| lep   | Lepus granatensis        | Iberian hare                             |
| mus   | Mus o apodemus           | mouse (likely wood mouse)                |
| rara  | Rattus rattus            | black rat                                |
| tile  | Timon lepidus            | ocellated lizard                         |
| liz   | lizard                   | lizard                                   |
| tur   | Testudo graeca           | spur-thighed tortoise                    |
| sna   | snake                    | snake                                    |
| bird  | bird                     | bird                                     |
| hom   | Homo sapiens             | human                                    |
| car   | any vehicle              | any vehicle                              |
| ani   | animal non identified    | animal not identified                    |
| carni | non identified carnivore | non-identified carnivore                 |
| cerni | red or fallow deer       | red or fallow deer (unidentified cervid) |
| emp   | empty                    | empty                                    |

## CSVs
In the releases section of the repository are all the csvs of the project (`csv.zip`):
- `raw`: all the images provided.
- `full`: all the images with datetime information.
- `full-interested`: Only the images we are interested in.
- `clean`: images taken in the same minute are all discarded but one. The goal is to remove duplicate images.
- `train`, `val`, `test`: splits for the training dataset.

## Scripts
### Processing Scripts
- `get_datetime.py`: Retrieves the datetime of the images in a csv and generates a new csv with the datetime information.
- `clear_bursts.py`: Removes images taken in the same minute, keeping only one image per minute to avoid duplicates.
- `splitter.py`: Splits the dataset into train, validation, and test sets.

### Special Scripts
- `change_shape.py`: Converts the dataset directory structure from `dataset/split/park/species/images|labels/image.jpg|txt` to `dataset/split/images|labels/image.jpg|txt` for compatibility with the models.
- `add_xml_annotation.py`: Converts the .txt annotations to .xml format for FasterRCNN compatibility.

### Downloader
The `downloader.py` script needs a .env with Minio access information, similar to the one needed for the app. Make sure to have the yolov5 repository in the same directory and to set PYTHONPATH to the working directory and to the yolov5 directory. This is needed for Megadetector.

## Analysis
In the `analysis/` folder is available the notebook used to analyze the dataset. In the `analysis/images/` folder is where the graphs generated were saved. The script needs the `csv` files in the same directory to work.