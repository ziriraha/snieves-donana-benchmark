import pandas as pd
from minio import Minio
from tokens import TOKEN_MINIO
from md_visualization import visualization_utils as vis_utils
import uuid
from detection import run_detector
import pandas as pd
from PIL.ExifTags import TAGS
from pathlib import Path
import concurrent.futures
import PIL.Image as Image
import os
import numpy as np

data = pd.read_csv('raw.csv')

def get_datetime(image):
    ret = "nan"
    exifdata = image.getexif()
    try:
        # iterating over all EXIF data fields
        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes 
            if isinstance(data, bytes):
                data = data.decode('latin1', errors='ignore')  # Or any other suitable encoding
            if tag == 'DateTime':
                # print(f"{tag:5}: {data}")
                datetime = str(data)
                if datetime == 'nan':
                    return 'nan'
                date, time = datetime.split(' ')
                year, month, day = date.split(':')
                hour, minute, second = time.split(':')
                ret = f'{day}{month}{year} {hour}{minute}{second}'
                break
    except Exception as err:
        print(err)
    return ret

MINIO_URL= '192.168.219.2:9000'
MINIO_BUCKET= 'fauna-data'
MINIO_ACCESS_KEY= 'fauna-reader'
MINIO_SECRET_KEY= TOKEN_MINIO


def process_bbox_datetime(df_setname):
    df_set, name = df_setname
    df_set.reset_index(drop=True, inplace=True)

    mi_client = Minio(
            MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        )

    def get_image_from_minio(image: Path, path_to_save: Path):
        mi_client.fget_object(
            bucket_name=MINIO_BUCKET,
            object_name=image.as_posix(),
            file_path=path_to_save.as_posix())

    save_path = f"temp_images_{name}/"
    #model = run_detector.load_detector('MDV5A')
    print("")

    for index, row in df_set.iterrows():
        print(f"\r{name}: {index}/{len(df_set)}", end="")
        dire = save_path + str(uuid.uuid4())
        bbox = 'none'
        datetime = 'nan'
        try:
            get_image_from_minio(Path(row.path),Path(dire + '.jpg'))
            with Image.open(dire + '.jpg') as image:
                #pred = model.generate_detections_one_image(image)['detections'][-1]
                #p = pred['bbox']
                #bbox = f'{p[0] + p[2]/2} {p[1] + p[3]/2} {p[2]} {p[3]}'
                datetime = get_datetime(image)
        except Exception as e:
            print(e)
        df_set.at[index, 'bbox'] = bbox
        df_set.at[index, 'datetime'] = datetime
        os.remove(dire + '.jpg')
    print("DONE")
    df_set.to_csv(f'{name}.csv', index=False)

quant = 6
with concurrent.futures.ThreadPoolExecutor() as executor:
    for index, dataframe in enumerate(np.array_split(data, quant)):
        executor.submit(process_bbox_datetime, (dataframe, f"data{index}"))

all_data = pd.read_csv('data0.csv')
for i in range(1, quant):
    dataq = pd.read_csv(f'data{i}.csv')
    all_data = pd.concat([all_data, dataq])
all_data.to_csv('full.csv', index=False)
