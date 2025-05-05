import os
import shutil
from utils import Tester
import pandas as pd
from PIL import Image

DATASET_YAML = "/home/usuario/Documentos/ziri/dataset/confi_dataset.yaml"
TEST_PATH = "/home/usuario/Documentos/ziri/dataset/test"
IMAGES_PATH = os.path.join(TEST_PATH, 'images')

WEIGHTS_PATH = "fastercnn/outputs/training/res_1/best_model.pth"
SAVE_PATH = "./fasterrcnn_trained.pt"
RUN_PATH = "fastercnn/outputs/inference/res_1/boxes.csv"

CLASSES = ['_background_', 'mus', 'rara', 'ory', 'fsi', 'lyn', 'lut', 'sus', 'mel', 'vul', 'lep', 'equ', 'cer', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'ovar', 'mafo', 'capi', 'caae', 'ovor', 'caca']

print("Preparing environment...")
os.system("rm -rf train_test_fasterrcnn")
os.mkdir("train_test_fasterrcnn")
os.chdir("train_test_fasterrcnn")

os.system("git clone https://github.com/sovit-123/fastercnn-pytorch-training-pipeline.git fasterrcnn")
os.system("pip install -r fasterrcnn/requirements.txt")

print("Training FasterRCNN model...")
os.system(f"python fasterrcnn/train.py --data {DATASET_YAML} --model fasterrcnn_resnet50_fpn_v2 --epochs 20 --batch 4")
print("Training finished")

print("Saving model...")
shutil.copy(WEIGHTS_PATH, SAVE_PATH)

print("Initializing Tester...")
tester = Tester("fasterrcnn", TEST_PATH)

print("Running inference on test images")
os.system(f"python inference.py --input {IMAGES_PATH} --weights {WEIGHTS_PATH} --table --data {DATASET_YAML}")

print("Processing results...")
results = {}
with open("/home/usuario/Documentos/ziri/train_test_fasterrcnn/fastercnn-pytorch-training-pipeline/outputs/inference/res_1/boxes.csv", "r") as file:
    for line in file.readlines()[1:]:
        img_name, pred_label, pred_xmin, pred_xmax, pred_ymin, pred_ymax, pred_width, pred_height, _ = line.split()
        with Image.open(os.path.join(IMAGES_PATH, f'{img_name}.jpg')) as img:
            size_x, size_y = img.size
        px = (float(pred_xmin) / size_x + float(pred_xmax) / size_x) / 2
        py = (float(pred_ymin) / size_y + float(pred_ymax) / size_y) / 2
        pw = float(pred_width) / size_x
        ph = float(pred_height) / size_y
        results[img_name] = (CLASSES.index(pred_label)-1, [px, py, pw, ph])


def get_pred(img_name):
    pcls, pbbox = -1, None
    if img_name in results:
        pcls, pbbox = results[img_name]
    return pcls, pbbox

print("Running tester (validation of the results)")
tester.run(get_pred)

print("Tester finished\nSaving results...")
tester.calculate_metrics()
tester.save_metrics_to_txt()
tester.save_vals_to_txt()

print("Done.")