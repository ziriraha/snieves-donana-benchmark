import os
import argparse
import concurrent.futures
import pandas as pd

DEFAULT_CPU = 2

MAX_CPU = 8
EXCLUDE = ['mus', 'rara', 'ory', 'fsi', 'lyn', 'lut', 'mel', 'lep', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'mafo', 'capi', 'caae', 'ovor', 'caca']
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
    return pd.DataFrame(filtered)

def main(dataframe, output=SAVE_PATH, max_cpu=MAX_CPU):
    dataframe = dataframe.reset_index(drop=True)
    
    keep = pd.concat([dataframe[pd.isnull(dataframe['date'])], 
                        dataframe[dataframe['species'].isin(EXCLUDE)]], ignore_index=True)
    
    to_filter = dataframe.loc[~dataframe.index.isin(keep.index)]
    to_filter['date'] = pd.to_datetime(to_filter['date'], format='%Y-%m-%d %H:%M:%S')

    groups = [group for _, group in to_filter.groupby('species', group_keys=False)]

    n = min(os.cpu_count() or DEFAULT_CPU, max_cpu)
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        futures = [executor.submit(process_group, group) for group in groups]

    results = [future.result() for future in futures] + [keep]
    out = pd.concat(results, ignore_index=True)
    out.to_csv(output, index=False, escapechar='\\')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and process a CSV file.")
    parser.add_argument("input", help="Path to the input CSV file")
    parser.add_argument("--output", type=str, default=SAVE_PATH, help=f"Path to the output CSV file (default: {SAVE_PATH})")
    parser.add_argument("--time-interval", type=int, default=TIME_INTERVAL, help=f"Time interval threshold in seconds (default: {TIME_INTERVAL})")
    parser.add_argument("--max-cpu", type=int, default=MAX_CPU, help=f"Maximum number of CPUs to use (default: {MAX_CPU})")
    parser.add_argument("--exclude", nargs='+', default=EXCLUDE, help=f"List of species to exclude (default: {str(EXCLUDE)})")

    args = parser.parse_args()

    SAVE_PATH = args.output
    TIME_INTERVAL = args.time_interval
    MAX_CPU = args.max_cpu
    EXCLUDE = args.exclude

    main(pd.read_csv(args.input))