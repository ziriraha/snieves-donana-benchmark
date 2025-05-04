import PIL.Image as Image
import os

classes = ['mus', 'rara', 'ory', 'fsi', 'lyn', 'lut', 'sus', 'mel', 'vul', 'lep', 'equ', 'cer', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'ovar', 'mafo', 'capi', 'caae', 'ovor', 'caca']

def getAnnotationXML(txt, size_x, size_y):
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

for dataset in ["train", "val"]:
    os.makedirs(f"dataset/{dataset}/xml_labels", exist_ok=True)
    for img in os.listdir(f"dataset/{dataset}/images"):
        if img.endswith(".jpg"):
            try:
                img_name = img.split(".")[0]
                with Image.open(f"dataset/{dataset}/images/{img}") as image:
                    size_x, size_y = image.size
                with open(f"dataset/{dataset}/labels/{img_name}.txt", "r") as f:
                    txt = f.read()
                xml = getAnnotationXML(txt, size_x, size_y)
                with open(f"dataset/{dataset}/xml_labels/{img_name}.xml", "w") as f:
                    f.write(xml)
            except FileNotFoundError as fr:
                pass
print("Done!")