import os
import argparse
import concurrent.futures

import pandas as pd
from tqdm import tqdm

MAX_PROCESSES = os.cpu_count() or 4

TIME_INTERVAL = 1
SAVE_PATH = './output.csv'

def process_group(group, time_interval=TIME_INTERVAL):
    dataframe = group.sort_values(by='date').reset_index(drop=True)
    
    prev_time = dataframe.loc[0, 'date']
    filtered = [dataframe.loc[0]]
    for _, row in dataframe.iterrows():
        time_diff = row['date'] - prev_time
        if time_diff.total_seconds() > time_interval:
            filtered.append(row)
            prev_time = row['date']
    return filtered

def main(dataframe, output=SAVE_PATH, exclude=False):
    dataframe = dataframe.reset_index(drop=True)
    dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    to_exclude = []

    if exclude:
        species_counts = dataframe['species'].value_counts()
        median = round(species_counts.median(), -3)
        to_exclude = species_counts[species_counts < median].index.tolist()
        print(f"Excluding from filtering species with less than the {median} images:\n{', '.join(to_exclude)}")

    print("Filtering data...")
    keep = pd.concat([dataframe[pd.isna(dataframe['date'])], 
                      dataframe[dataframe['species'].isin(to_exclude)]]) \
             .drop_duplicates(subset=['path', 'species'])
    
    to_filter = dataframe.drop(keep.index)

    groups = [group for _, group in to_filter.groupby('species', group_keys=False)]
    print(f"Processing {len(groups)} species groups in parallel using {MAX_PROCESSES} processes...")

    with tqdm(total=len(groups), desc="Filtering", unit="groups") as progress_bar:
        filtered = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROCESSES) as executor:
            futures = [executor.submit(process_group, group) for group in groups]
            for future in concurrent.futures.as_completed(futures):
                progress_bar.update(1)
                filtered.extend(future.result())

    print("Finished. Compiling results...")
    results = pd.DataFrame(filtered).reset_index(drop=True)
    out = pd.concat([results, keep], ignore_index=True).drop_duplicates(subset=['path', 'species'])
    print(f"Total images discarded: {len(dataframe) - len(out)}")
    out.to_csv(output, index=False, escapechar='\\')
    print(f"Output written to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and process a CSV file.")
    parser.add_argument("input", help="Path to the input CSV file")
    parser.add_argument("--output", type=str, default=SAVE_PATH, help=f"Path to the output CSV file (default: {SAVE_PATH})")
    parser.add_argument("--time-interval", type=int, default=TIME_INTERVAL, help=f"Time interval threshold in seconds (default: {TIME_INTERVAL})")
    parser.add_argument("--exclude", action="store_true", help="Exclude from filtering all species with less than the median number of images.")
    parser.add_argument("--max-processes", type=int, default=MAX_PROCESSES, help=f"Maximum number of processes to use (default: {MAX_PROCESSES})")

    args = parser.parse_args()

    TIME_INTERVAL = args.time_interval
    MAX_PROCESSES = args.max_processes

    main(pd.read_csv(args.input), args.output, args.exclude)