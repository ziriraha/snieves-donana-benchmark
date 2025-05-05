from utils import Tester, DATASET_YAML, IMAGES_PATH
import shutil
import os

WEIGHTS_PATH = "yolov5/runs/train/exp/weights/best.pt"
SAVE_PATH = "./megadetector_trained.pt"
RUN_PATH = "yolov5/runs/detect/exp/labels"

print("Preparing environment...")
os.system("rm -rf train_test_megadetector")
os.mkdir("train_test_megadetector")
os.chdir("train_test_megadetector")

print("Downloading MegaDetector model...")
os.system("wget https://github.com/agentmorris/MegaDetector/releases/download/v5.0/md_v5a.0.0.pt")

print("Downloading YOLOv5...")
os.system("git clone https://github.com/ultralytics/yolov5.git")
os.system("pip install -qr yolov5/requirements.txt")

print("Training MegaDetector model...")
os.system(f"python yolov5/train.py --data {DATASET_YAML} --weights ./md_v5a.0.0.pt --epochs 20 --batch-size 16 --imgsz 640 --freeze 20 --save-period 1")
print("Training finished")

print("Saving model...")
shutil.copy(WEIGHTS_PATH, SAVE_PATH)

print("Initializing Tester...")
tester = Tester('megadetector')

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
tester.calculate_metrics()
tester.save_metrics_to_txt()
tester.save_vals_to_txt()

print("Done.")