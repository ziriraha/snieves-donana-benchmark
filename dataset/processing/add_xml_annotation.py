import os
import argparse

import PIL.Image as Image

CLASSES = ['mus', 'rara', 'ory', 'fsi', 'lyn', 'lut', 'sus', 'mel', 'vul', 'lep', 'equ', 'cer', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'ovar', 'mafo', 'capi', 'caae', 'ovor', 'caca']
SPLITS = ['train', 'val']

def getAnnotationXML(txt, size_x, size_y):
    txt = txt.split(" ")
    cls = int(txt[0])
    bbox = [int(float(txt[1])*size_x), 
            int(float(txt[2])*size_y), 
            int(float(txt[3])*size_x), 
            int(float(txt[4])*size_y)]
    return f"""<annotation>
            <object>
                    <name>{CLASSES[cls]}</name>
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

def main(dataset):
    for split in SPLITS:
        images_dir = os.path.join(dataset, split, 'images')
        labels_dir = os.path.join(dataset, split, 'labels')
        xml_labels_dir = os.path.join(dataset, split, 'xml_labels')

        os.makedirs(xml_labels_dir, exist_ok=True)

        for img in os.listdir(images_dir):
            if not img.endswith(".jpg"): continue

            with Image.open(os.path.join(images_dir, img)) as image:
                size_x, size_y = image.size

            img_name = img.split(".")[:-1]
            label_path = os.path.join(labels_dir, f'{img_name}.txt')
            if os.path.exists(label_path):
                with open(label_path, "r") as f: txt = f.read()
                with open(os.path.join(xml_labels_dir, f'{img_name}.xml'), "w") as f:
                    f.write(getAnnotationXML(txt, size_x, size_y))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add XML annotation to dataset.")
    parser.add_argument("dataset", help="Path to the dataset directory")
    args = parser.parse_args()
    
    main(args.dataset)