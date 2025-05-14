import os
import shutil
import argparse

from PIL import Image

from utils import Tester, prepare_environment, CONFI_DATASET_YAML, IMAGES_PATH

MODEL = 'fasterrcnn'
WEIGHTS_PATH = "fastercnn/outputs/training/res_1/best_model.pth"
SAVE_PATH = "./"
RUN_PATH = "fastercnn/outputs/inference/res_1/boxes.csv"

CLASSES = ['_background_', 'mus', 'rara', 'ory', 'fsi', 'lyn', 'lut', 'sus', 'mel', 'vul', 'lep', 'equ', 'cer', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'ovar', 'mafo', 'capi', 'caae', 'ovor', 'caca']

def prepare():
    prepare_environment(MODEL)
    os.system("git clone https://github.com/sovit-123/fastercnn-pytorch-training-pipeline.git fasterrcnn")
    os.system("pip install -r fasterrcnn/requirements.txt")

def train(save_path=SAVE_PATH):
    print("Training FasterRCNN model...")
    os.system(f"python fasterrcnn/train.py --data {CONFI_DATASET_YAML} --model fasterrcnn_resnet50_fpn_v2 --epochs 20 --batch 4")
    print("Training finished")

    destination = os.path.join(save_path, "fastercnn.pth")
    shutil.copy(WEIGHTS_PATH, destination)
    print("Model saved to ", destination)

def test(save_path=SAVE_PATH):
    print("Initializing Tester...")
    tester = Tester(MODEL)

    print("Running inference on test images")
    os.system(f"python inference.py --input {IMAGES_PATH} --weights {WEIGHTS_PATH} --table --data {CONFI_DATASET_YAML}")

    print("Processing results...")
    results = {}
    with open(RUN_PATH, "r") as file:
        for line in file.readlines()[1:]:
            img_name, pred_label, pred_xmin, pred_xmax, pred_ymin, pred_ymax, pred_width, pred_height, _ = line.split(',')
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
    destination = os.path.join(save_path, "fastercnn_values.txt")
    tester.save_vals_to_txt(destination)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Train and test FasterRCNN model")
    argparser.add_argument('--train', action='store_true', help="Only train the model (no testing)")
    argparser.add_argument('--save-dir', type=str, default=SAVE_PATH, help="Directory to save the model and/or values")
    args = argparser.parse_args()

    prepare()
    train(args.save_dir)
    if not args.train:
        test(args.save_dir)
    print("Done.")