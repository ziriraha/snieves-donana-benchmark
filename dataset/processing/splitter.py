import os
import argparse

import pandas as pd

SAVE_DIR = './'
PROPORTION = 0.8
RANDOM_STATE = 2975

rounded_mean = lambda x: int(round(x[x['species'] != 'emp'].groupby('species')['path'].count().mean(), -3))

def get_even_parks_for_species(images, top):
    total_images_in_parks = images.groupby('park').size().to_dict()
    num_parks = len(total_images_in_parks)
    if num_parks <= 1: return images.head(top)
    images_per_park = {park: min(top//num_parks, total_images_in_parks[park]) 
                       for park in total_images_in_parks}
    sorted_image_quantity = sorted(images_per_park.items(), key=lambda item: item[1])
    next_is_taking = top//num_parks
    for park, _ in sorted_image_quantity:
        images_per_park[park] = images[images['park'] == park].head(next_is_taking)
        next_is_taking = top - images_per_park[park].shape[0]
    return pd.concat(images_per_park.values(), ignore_index=True)

def get_even_images_per_species(dataset, top):
    species_images = {species: dataset[dataset['species'] == species] 
                       for species in dataset['species'].unique()}
    for species, images in species_images.items():
        species_images[species] = get_even_parks_for_species(images, top)
    return pd.concat(species_images.values(), ignore_index=True)

def split_dataset(dataset, proportion=PROPORTION, random_state=RANDOM_STATE):
    first_split = dataset.groupby(['species', 'park']).sample(frac=proportion, random_state=random_state)
    second_split = dataset.drop(first_split.index)
    return first_split, second_split

def main(dataset_path, save_dir=SAVE_DIR):
    print("Importing dataset...")
    original = pd.read_csv(dataset_path).sample(frac=1, random_state=RANDOM_STATE).reset_index()

    print("Splitting datasets (train, val and test)...")
    train_val_dataset, test_dataset = split_dataset(original)
    train_dataset, val_dataset = split_dataset(train_val_dataset)

    print("Getting even images per species...")
    train_dataset = get_even_images_per_species(train_dataset, top=rounded_mean(train_dataset))
    val_dataset = get_even_images_per_species(val_dataset, top=rounded_mean(val_dataset))
    test_dataset = get_even_images_per_species(test_dataset, top=rounded_mean(test_dataset))

    print("Train dataset size: ", train_dataset.shape[0])
    print("Validation dataset size: ", val_dataset.shape[0])
    print("Test dataset size: ", test_dataset.shape[0])

    print("Saving datasets to " + save_dir)
    train_dataset.to_csv(os.path.join(save_dir, 'train.csv'), index=False)
    val_dataset.to_csv(os.path.join(save_dir, 'val.csv'), index=False)
    test_dataset.to_csv(os.path.join(save_dir, 'test.csv'), index=False)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Split dataset into train, validation and test sets.")
    argparser.add_argument('dataset', type=str, help="Path to the dataset CSV file.")
    argparser.add_argument('--save', type=str, default=SAVE_DIR, help="Directory to save the split datasets.")
    argparser.add_argument('--proportion', type=float, default=PROPORTION, help="Proportion of the dataset to use for training.")
    argparser.add_argument('--random-state', type=int, default=RANDOM_STATE, help="Random state for reproducibility.")
    args = argparser.parse_args()

    PROPORTION = args.proportion
    RANDOM_STATE = args.random_state

    main(args.dataset, args.save)