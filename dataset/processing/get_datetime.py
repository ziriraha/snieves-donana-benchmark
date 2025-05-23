import argparse
import concurrent.futures
import os
from datetime import datetime
from io import BytesIO

import pandas as pd
from PIL import Image

from image_downloader import Downloader

MAX_THREADS = 5 * (os.cpu_count() or 4)
SAVE_PATH = './output.csv'

def get_datetime_for_image(image_path):
    date = "nan"
    try:
        response = Downloader.get_image_from_minio(image_path)
        with Image.open(BytesIO(response.data)) as image:
            exifdata = image.getexif().get(306, None) or image.getexif().get(36867, None)
            decoded_exif = str(exifdata.decode('utf-8', errors='ignore') if isinstance(exifdata, bytes) else exifdata)
            date = datetime.strptime(decoded_exif, '%Y:%m:%d %H:%M:%S') if decoded_exif else None
            date = date.strftime('%Y-%m-%d %H:%M:%S') if date else "nan"
    except Exception as err: 
        print(f"Error processing image {image_path}: {err}")
    finally:
        response.close()
        response.release_conn()
    return date

def get_datetime_for_row(row):
    row['datetime'] = get_datetime_for_image(row.path)
    return row

def main(dataframe, output=SAVE_PATH):
    print("Processing images in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        rows = list(executor.map(get_datetime_for_row, [row for _, row in dataframe.iterrows()]))
    dataframe = pd.DataFrame(rows)
    print(f"Done\nWriting output to file {output}")
    dataframe.to_csv(output, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract datetime from images in a CSV file.")
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument("--output", type=str, default=SAVE_PATH, help=f"Path to the output CSV file (default: {SAVE_PATH})")
    parser.add_argument("--max-threads", type=int, default=MAX_THREADS, help=f"Number of threads to use. (default: {MAX_THREADS})")

    args = parser.parse_args()
    MAX_THREADS = args.max_threads

    main(pd.read_csv(args.input_csv), args.output)
