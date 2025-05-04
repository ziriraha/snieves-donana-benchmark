from utils import calculate_iou, calculate_metrics, save_metrics_to_txt
import os

os.system("rm -rf train_test_megadetector")
os.mkdir("train_test_megadetector")
os.chdir("train_test_megadetector")

print("Downloading MegaDetector model...")
os.mkdir("models")
os.chdir("models/")
os.system("wget https://github.com/agentmorris/MegaDetector/releases/download/v5.0/md_v5a.0.0.pt")

print("Downloading YOLOv5...")
os.chdir("..")
os.system("git clone https://github.com/ultralytics/yolov5.git")
os.chdir("yolov5")
os.system("pip install -qr requirements.txt")

print("Training MegaDetector model...")
os.system("python train.py --data ../../dataset/dataset.yaml --weights ../models/md_v5a.0.0.pt --epochs 20 --batch-size 16 --imgsz 640 --freeze 20 --save-period 1")
print("Training finished")

true_val = []
pred_val = []
iou = []

for label in os.listdir(f'../dataset/test/labels'):
    try:
        with open(f'../dataset/test/labels/{label}', 'r') as f:
            si = f.readline().split(" ")
            true = int(si[0])
            true_box = [float(si[1]), float(si[2]), float(si[3]), float(si[4])]

        with open(f'yolov5/runs/detect/exp/labels/{label}', 'r') as f:
            si = f.readline().split(" ")
            pred = int(si[0])
            pred_box = [float(si[1]), float(si[2]), float(si[3]), float(si[4])]

        iou.append(calculate_iou(pred_box, true_box))
        true_val.append(true)
        pred_val.append(pred)
    except Exception as e: print(e)

with open(f"results_test_megadetector.txt", "w") as file:
    file.write("True vals: " + str(true_val) + " \n")
    file.write("Pred vals: " + str(pred_val) + " \n")
    file.write("IoU vals: " + str(iou) + " \n")

metrics = calculate_metrics(true_val, pred_val, iou)
print(metrics)

save_metrics_to_txt(metrics, "test_results_megadetector")