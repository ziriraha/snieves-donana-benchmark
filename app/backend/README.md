# How to run the API
Create a `.env` file with the following variables:
- MINIO_URL
- MINIO_ACCESS_KEY
- MINIO_SECRET_KEY
- MINIO_BUCKET

To run the app execute the following commands in the `backend` directory:
```bash
pip install -r requirements.txt
git clone https://github.com/ultralytics/yolov5
python app.py
``` 
It is recommended to create a virtual enviroment.

# Files needed
The `train.csv`, `test.csv` and `val.csv` files in the csv/ folder will be needed to create the initial dataset zips. Also the `full.csv` file will be needed to fulfill user requests.

# How to use the API
To download the datasets make a GET request to the `/dataset/<set>` URL, where set is `train`, `test` or `val`.

To download all images from a park (and optionally a datetime) use `/park/<park_name>?date=<datetime>`. The park names we have available are `snieves` for Sierra de las Nieves and `donana` for Doñana. Datetime will be provided in the following format: DDMMYYYY.

To download all images for a species (optionally a datetime and a number of files) use `species/<species_name>?date=<datetime>?nfiles=<number_of_files>`. The number of files must be an integer greater than zero.

To download all images from a park and a species (optionally a datetime and a number of files) use `/park/<park_name>/species/<species_name>?date=<datetime>?nfiles=<number_of_files>`. The available species names are:

## Dataset labels

| Label | Scientific name          | Name (Spanish)                          |
|-------|--------------------------|-----------------------------------------|
| equ   | Equus ferus              | caballo                                 |
| cer   | Cervus elaphus           | ciervo                                  |
| dam   | Dama dama                | gamo                                    |
| caca  | Capreolus capreolus      | corzo                                   |
| bos   | Bos primigenius          | vaca                                    |
| capi  | Capra pyrenaica          | cabra montés                            |
| caae  | Capra aegagrus hircus    | cabra doméstica                         |
| ovor  | Ovis orientalis musimon  | muflón                                  |
| ovar  | Ovis orientalis aries    | oveja                                   |
| sus   | Sus scrofa               | jabalí                                  |
| fel   | Felis catus              | gato doméstico                          |
| fsi   | Felis silvestris         | gato montés                             |
| lyn   | Lynx pardinus            | lince ibérico                           |
| can   | Canis lupus familiaris   | perro                                   |
| calu  | Canis lupus              | lobo                                    |
| vul   | Vulpes vulpes            | zorro                                   |
| lut   | Lutra lutra              | nutria                                  |
| mel   | Meles meles              | tejón                                   |
| mafo  | Martes foina             | garduña                                 |
| mupu  | Mustela putorius         | turón                                   |
| her   | Herpestes ichneumon      | meloncillo                              |
| muni  | Mustela nivalis          | comadreja                               |
| gen   | Genetta genetta          | gineta                                  |
| elqu  | Elyomis quercinus        | lirón careto                            |
| ory   | Oryctolagus cuniculus    | conejo                                  |
| lep   | Lepus granatensis        | liebre                                  |
| mus   | Mus o apodemus           | ratón                                   |
| rara  | Rattus rattus            | rata negra                              |
| tile  | Timon lepidus            | lagarto ocelado                         |
| liz   | lizard                   | lagartija                               |
| tur   | Testudo graeca           | tortuga mora                            |
| sna   | snake                    | serpiente                               |
| bird  | bird                     | ave                                     |
| hom   | Homo sapiens             | humano                                  |
| car   | any vehicle              | vehículo motorizado                     |
| ani   | animal non identified    | animal no identificado                  |
| carni | non identified carnivore | carnívoro no identificado               |
| cerni | red or fallow deer       | ciervo o gamo (cérvido no identificado) |
| emp   | empty                    | vacío                                   |

Labels on the .txt file will be the index on the classes.txt file provided on the zip. Bboxes provided on those .txt files will be in YOLOv8 format: (center x, center y, width, height) normalized to image size.