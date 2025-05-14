import os
import shutil
import argparse

from utils import Tester, prepare_environment, DATASET_YAML, IMAGES_PATH

MODEL = 'megadetector'
WEIGHTS_PATH = "yolov5/runs/train/exp/weights/best.pt"
SAVE_PATH = "./"
RUN_PATH = "yolov5/runs/detect/exp/labels"

def prepare():
    prepare_environment(MODEL)

    print("Downloading MegaDetector model...")
    os.system("wget https://github.com/agentmorris/MegaDetector/releases/download/v5.0/md_v5a.0.0.pt")

    print("Downloading YOLOv5...")
    os.system("git clone https://github.com/ultralytics/yolov5.git")
    os.system("pip install -qr yolov5/requirements.txt")

def train(save_path=SAVE_PATH):
    print("Training MegaDetector model...")
    os.system(f"python yolov5/train.py --data {DATASET_YAML} --weights ./md_v5a.0.0.pt --epochs 20 --batch-size 16 --imgsz 640 --freeze 20 --save-period 1")
    print("Training finished")

    print("Saving model...")
    destination = os.path.join(save_path, "megadetector.pt")
    shutil.copy(WEIGHTS_PATH, destination)
    print("Model saved to ", destination)

def test(save_path=SAVE_PATH):
    print("Initializing Tester...")
    tester = Tester(MODEL)

    print("Running inference on test images")
    os.system(f"python3 detect.py --weights {WEIGHTS_PATH} --source {IMAGES_PATH} --max-det 1 --device 0 --save-txt --nosave")

    def get_pred(img_name):
        label = os.path.join(RUN_PATH, f'{img_name}.txt')
        if not os.path.exists(label): return -1, None

        with open(label, 'r') as f:
            clas, *bbox = f.readline().split()
            pcls = int(clas)
            pbbox = list(map(float, bbox))

        return pcls, pbbox

    print("Running tester (validation of the results)")
    tester.run(get_pred)

    print("Tester finished\nSaving results...")
    destination = os.path.join(save_path, "megadetector_values.txt")
    tester.save_vals_to_txt(destination)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Train and test MegaDetector model")
    argparser.add_argument('--train', action='store_true', help="Only train the model (no testing)")
    argparser.add_argument('--save-dir', type=str, default=SAVE_PATH, help="Directory to save the model and/or values")
    args = argparser.parse_args()

    prepare()
    train(args.save_dir)
    if not args.train:
        test(args.save_dir)
    print("Done.")