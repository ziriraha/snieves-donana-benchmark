# Dataset
In this directory there will be files for the analysis and processing of the dataset and the creation of the traininig split.

The `confi_dataset.yaml` and `dataset.yaml` files are the ones needed by the models to function.

## Classes provided
| Label | Scientific name          | Name (English)                           |
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
In the releases section of the repository are all the csvs of the project:
- `raw`: all the images provided.
- `full`: only the images from the species we are interested in. Also contains date and time information of the image. Discards non existant image paths too.
- `clean`: images taken in the same minute are all discarded but one. The goal is to remove duplicate images.
- `train`, `val`, `test`: splits for the training dataset.

## Processing
The `raw.csv` was the dataset provided. First, some species were excluded and the timestamp (`get_datetime.py`) of the images was added to generate `full.csv`. The `clear_bursts.py` script was used to remove images from the same burst (this was done to remove duplicates), the result is the `clean.csv`. Finally, the `dataset_splitter.py` script was run to generate the `train.csv`, `val.csv`, `test.csv`.

### Special Datasets
The dataset downloader may download the data in the following directory structure: `dataset/split/park/species/images|labels/image.jpg|txt` to convert from this to a compatible format for the models (`dataset/split/images|labels/image.jpg|txt`) use the `change_shape.py` script.

FasterRCNN expects xml files instead of .txt. For this, the `add_xml_annotation.py` script can be used on a dataset directory with `images` and `labels` folder to create a `xml_labels` folder.