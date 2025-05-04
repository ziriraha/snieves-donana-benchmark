import pandas as pd
import concurrent.futures

CSV_DIR = 'csv/big_csv/'
YOUR_TIME_INTERVAL_THRESHOLD = 1

EXCLUDE = ['mus',
            'rara',
            'ory',
            'fsi',
            'lyn',
            'lut',
            'mel',
            'lep',
            'bos',
            'gen',
            'her',
            'dam',
            'fel',
            'can',
            'mafo',
            'capi',
            'caae',
            'ovor',
            'caca']

def process_group(group):
    group_df = group[1]
    if group[0] in EXCLUDE:
        return group_df
    
    group_df = group_df.sort_values(by='date').reset_index(drop=True)
    prev_time = None
    filtered_data_local = []
    for index, row in group_df.iterrows():
        if prev_time is not None:
            time_diff = row['date'] - prev_time
            if time_diff.total_seconds() > YOUR_TIME_INTERVAL_THRESHOLD:
                filtered_data_local.append(row)
        prev_time = row['date']
    return pd.DataFrame(filtered_data_local)

# Load the CSV file
print("Preprocessing CSV file...")
df = pd.read_csv(CSV_DIR + "datetime_data.csv").reset_index(drop=True)
print("Original CSV: ", df.shape[0])

filtered_data = df[pd.isnull(df['date'])]
df = df.dropna(subset=['date'])
df = df.reset_index(drop=True)

df['date'] = pd.to_datetime(df['date'], format='%Y:%m:%d %H:%M:%S')
df.head(10)
a = df.shape[0]
print("After clearing N/A: ", a)

print("Sorting data...")
grouped = df.groupby('species')

print("Filtering data...")
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(process_group, grouped))

print("Process complete, results:")
for result in results:
    print(result.shape[0])

filtered_data = pd.concat([filtered_data, pd.concat(results, ignore_index=True)], ignore_index=True)

print("Filtered result: ", filtered_data.shape[0], "\nSaving...")

filtered_data.to_csv(CSV_DIR + 'filtered_datetime.csv', index=False, escapechar='\\')

print("Results saved!")