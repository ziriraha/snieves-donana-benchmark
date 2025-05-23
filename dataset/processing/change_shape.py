import argparse
import os

IMAGES_PATH = 'images'
LABELS_PATH = 'labels'

def change_shape(path):
    def move_file(file_path, filename):
        if filename.endswith(".jpg"): target = IMAGES_PATH
        elif filename.endswith(".txt"): target = LABELS_PATH
        else: return
        os.rename(file_path, os.path.join(path, target, filename))

    for park in os.listdir(path):
        park_path = os.path.join(path, park)
        if not os.path.isdir(park_path): continue

        for species in os.listdir(park_path):
            species_path = os.path.join(park_path, species)
            if not os.path.isdir(species_path): continue

            for filename in os.listdir(species_path):
                file_path = os.path.join(species_path, filename)                
                move_file(file_path, filename)

def main(dataset_path):
    for subset in os.listdir(dataset_path):
        subset_path = os.path.join(dataset_path, subset)
        if not os.path.isdir(subset_path): continue

        change_shape(subset_path)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Change shape of dataset from <set>/<park>/<species>/<image>.jpg|txt to <set>/images|labels/<image>.jpg|txt")
    argparser.add_argument("dataset_path", type=str, help="Path to the dataset folder")

    args = argparser.parse_args()

    if not os.path.isdir(args.dataset_path):
        raise ValueError(f"Dataset path {args.dataset_path} is not a directory")
    
    main(args.dataset_path)