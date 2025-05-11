import concurrent.futures
import os
import tempfile
from pathlib import Path
import argparse

import numpy as np
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS

from image_downloader import get_image_from_minio

DEFAULT_CPU = 2

def get_datetime_for_image(image):
    datetime = "nan"
    exifdata = image.getexif()
    try:
        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTime':
                raw = exifdata.get(tag_id)
                datetime = str(raw.decode('utf-8', errors='ignore') if isinstance(raw, bytes) else raw)
                break
    except Exception as err: print(err)
    return datetime

def get_datetime_for_dataframe(data):
    data.reset_index(drop=True, inplace=True)
    for index, row in data.iterrows():
        with tempfile.NamedTemporaryFile(suffix='.jpg') as file:
            if get_image_from_minio(Path(row.path), Path(file)):
                with Image.open(file) as image:
                    data.at[index, 'datetime'] = get_datetime_for_image(image)
    return data

def main(dataframe, output='./output.csv', max_cpu=8):
    n = min(os.cpu_count() or DEFAULT_CPU, max_cpu)
    splits = np.array_split(dataframe, n)

    with concurrent.futures.ProcessPoolExecutor(max_workers=n) as executor:
        futures = [executor.submit(get_datetime_for_dataframe, split) for split in splits]
    
    dataframe = pd.concat([future.result() for future in futures], ignore_index=True)
    dataframe.to_csv(output, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract datetime from images in a CSV file.")
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument("output_csv", type=str, default='./output.csv', help="Path to the output CSV file (default: ./output.csv)")
    parser.add_argument("--max_cpu", type=int, default=8, help="Maximum number of CPUs to use (default: 8)")

    args = parser.parse_args()

    main(pd.read_csv(args.input_csv), args.output_csv, max_cpu=args.max_cpu)
