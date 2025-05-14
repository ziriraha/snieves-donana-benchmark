import os
import argparse

import pandas as pd

SAVE_DIR = './'
PROPORTION = 0.8
RANDOM_STATE = 42
MEAN_WEIGHT = 1
OVERRIDE_TOP = 0

def rounded_mean(x, weight=MEAN_WEIGHT):
    mean_images = x[x['species'] != 'emp'].groupby('species')['path'].count().mean()
    rounded = ((mean_images + 999) // 1000) * 1000
    return rounded * weight

def get_even_parks_for_species(images, top=float('inf')):
    top = int(top) if OVERRIDE_TOP == 0 else OVERRIDE_TOP
    total_images_in_parks = images.groupby('park').size().to_dict()
    num_parks = len(total_images_in_parks)
    if num_parks <= 1: return images.head(top).reset_index(drop=True)
    images_per_park = {park: min(top//num_parks, total_images_in_parks[park]) 
                       for park in total_images_in_parks}
    images_per_park = sorted(images_per_park.items(), key=lambda item: item[1])
    next_is_taking = top//num_parks
    for park, _ in images_per_park:
        images_per_park[park] = images[images['park'] == park].head(next_is_taking)
        next_is_taking = top - images_per_park[park].shape[0]
    return pd.concat(images_per_park.values()).reset_index(drop=True)

def get_even_images_per_species(dataset, top=float('inf')):
    species_images = {species: dataset[dataset['species'] == species] 
                       for species in dataset['species'].unique()}
    for species, images in species_images.items():
        species_images[species] = get_even_parks_for_species(images, top)
    return pd.concat(species_images.values()).reset_index(drop=True)

def split_dataset(dataset, proportion=PROPORTION, random_state=RANDOM_STATE):
    first_split = dataset.groupby(['species', 'park']).apply(lambda x: x.sample(frac=proportion, random_state=random_state)).reset_index(drop=True)
    second_split = dataset[~dataset.index.isin(first_split.index)]
    return first_split, second_split

def split_even_dataset(dataset, proportion=PROPORTION, random_state=RANDOM_STATE):
    first_split, second_split = split_dataset(dataset, proportion=proportion, random_state=random_state)
    first_split = get_even_images_per_species(first_split, rounded_mean(first_split))
    second_split = get_even_images_per_species(second_split, rounded_mean(second_split))
    return first_split, second_split

def main(dataset_path, save_dir=SAVE_DIR):
    print("Importing dataset...")
    original = pd.read_csv(dataset_path)
    original = original.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True) # Shuffle

    print("Splitting dataset (train-val and test)...")
    train_val_dataset, test_dataset = split_even_dataset(original)
    print("Splitting train-val dataset...")
    train_dataset, val_dataset = split_even_dataset(train_val_dataset)

    print("Train dataset size: ", train_dataset.shape[0])
    print("Validation dataset size: ", val_dataset.shape[0])
    print("Test dataset size: ", test_dataset.shape[0])

    print("Saving datasets to " + save_dir)
    train_dataset.to_csv(os.path.join(save_dir, 'train.csv'), index=False)
    val_dataset.to_csv(os.path.join(save_dir, 'val.csv'), index=False)
    test_dataset.to_csv(os.path.join(save_dir, 'test.csv'), index=False)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Split dataset into train, validation and test sets.")
    argparser.add_argument('dataset', type=str, required=True, help="Path to the dataset CSV file.")
    argparser.add_argument('--save', type=str, default=SAVE_DIR, help="Directory to save the split datasets.")
    argparser.add_argument('--proportion', type=float, default=PROPORTION, help="Proportion of the dataset to use for training.")
    argparser.add_argument('--random_state', type=int, default=RANDOM_STATE, help="Random state for reproducibility.")
    argparser.add_argument('--mean_weight', type=int, default=MEAN_WEIGHT, help="Weight for the mean calculation.")
    argparser.add_argument('--override_top', type=int, default=OVERRIDE_TOP, help="Override the top value for even splits.")
    args = argparser.parse_args()

    # Update global variables with command line arguments
    PROPORTION = args.proportion
    RANDOM_STATE = args.random_state
    MEAN_WEIGHT = args.mean_weight
    OVERRIDE_TOP = args.override_top

    main(args.dataset, args.save)