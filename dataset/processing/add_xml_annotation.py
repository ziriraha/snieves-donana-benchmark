import os
import argparse

import PIL.Image as Image
from tqdm import tqdm

CLASSES = ['bos', 'caae', 'caca', 'can', 'capi', 'cer', 'dam', 'equ', 'fel', 'fsi', 'gen', 'her', 'lep', 'lut', 'lyn', 'mafo', 'mel', 'mus', 'ory', 'ovar', 'ovor', 'rara', 'sus', 'vul']
SPLITS = ['train', 'val']
XML_NAME = 'xml_labels'

def get_xml_annotation(txt, size_x, size_y, classes=CLASSES):
    txt = txt.split(" ")
    cls = int(txt[0])
    bbox = [int(float(txt[1])*size_x), 
            int(float(txt[2])*size_y), 
            int(float(txt[3])*size_x), 
            int(float(txt[4])*size_y)]
    return f"""<annotation>
    <object>
        <name>{classes[cls]}</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <occluded>0</occluded>
        <bndbox>
            <xmin>{bbox[0] - bbox[2]//2}</xmin>
            <xmax>{bbox[0] + bbox[2]//2}</xmax>
            <ymin>{bbox[1] - bbox[3]//2}</ymin>
            <ymax>{bbox[1] + bbox[3]//2}</ymax>
        </bndbox>
    </object>
</annotation>"""

def main(dataset, splits=SPLITS, folder_name=XML_NAME):
    for split in splits:
        images_dir = os.path.join(dataset, split, 'images')
        labels_dir = os.path.join(dataset, split, 'labels')
        xml_labels_dir = os.path.join(dataset, split, folder_name)

        os.makedirs(xml_labels_dir, exist_ok=True)

        for image_file in tqdm(os.listdir(images_dir), desc=f"Processing {split} labels", unit="labels"):
            if not image_file.endswith(".jpg"): continue
            img_name = ''.join(image_file.split(".")[:-1])

            annotation = "<annotation>\n</annotation>"

            label_path = os.path.join(labels_dir, f'{img_name}.txt')
            if os.path.exists(label_path):
                with Image.open(os.path.join(images_dir, f'{img_name}.jpg')) as image:
                    size_x, size_y = image.size
                with open(label_path, "r") as file: txt = file.read()
                annotation = get_xml_annotation(txt, size_x, size_y)

            with open(os.path.join(xml_labels_dir, f'{img_name}.xml'), "w") as file:
                file.write(annotation)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add XML annotation to dataset.")
    parser.add_argument("dataset", help="Path to the dataset directory")
    parser.add_argument("--name", type=str, default=XML_NAME, help=f"Folder name for xml labels (default: {XML_NAME})")
    parser.add_argument("--splits", type=str, default=SPLITS, help=f"Splits to process (default: {str(SPLITS)})")
    parser.add_argument("--classes", nargs='+', default=CLASSES, help=f"List of classes (default: {str(CLASSES)})")
    args = parser.parse_args()

    XML_NAME = args.name
    SPLITS = args.splits
    CLASSES = args.classes
    
    main(args.dataset)