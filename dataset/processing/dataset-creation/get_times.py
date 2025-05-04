import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS
import os
from utils_testing.image_downloader import DOWNLOADER
import concurrent.futures

dw = DOWNLOADER(DOWNLOAD_PATH='temp_images/', OBJECT_DETECTION=False)

def get_datetime(image_path: str):
    path = dw.download_image(image_path)
    ret = ""
    image = Image.open(path)
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
                ret = data
                break
    except OSError as err:
        print("OS error:", err)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    image.close()
    os.remove(path)
    return ret

dataset = pd.read_csv('csv/big_csv/filtered_data.csv').reset_index(drop=True)
#correct = dataset.head(1000)

# call get_datetime for each image
# save the result in a new column

paths = dataset['path']

def apply_get_datetime_parallel(paths):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(get_datetime, paths))
    return pd.Series(results)

dataset.loc[:, 'date'] = apply_get_datetime_parallel(dataset['path'])

dataset.to_csv('csv/big_csv/datetime_data.csv', index=False, escapechar='\\')

#correct['date'] = correct['path'].apply(get_datetime)

# check if the test and correct are the same
#print(test.equals(correct))
