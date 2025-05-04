import os
from utils import calculate_iou, calculate_metrics, save_metrics_to_txt

os.system("rm -rf train_test_fasterrcnn")
os.mkdir("train_test_fasterrcnn")
os.chdir("train_test_fasterrcnn")

os.system("git clone https://github.com/sovit-123/fastercnn-pytorch-training-pipeline.git")

os.chdir("fastercnn-pytorch-training-pipeline")

os.system("pip install -r requirements.txt")

os.system("python train.py --data /home/usuario/Documentos/ziri/dataset/confi_dataset.yaml --model fasterrcnn_resnet50_fpn_v2 --epochs 20 --batch 4")

os.system("python inference.py --input /home/usuario/Documentos/ziri/dataset/test/images/ --weights /home/usuario/Documentos/ziri/train_test_fasterrcnn/fastercnn-pytorch-training-pipeline/outputs/training/res_1/best_model.pth --table --data /home/usuario/Documentos/ziri/dataset/confi_dataset.yaml")

CLASSES = ['_background_', 'mus', 'rara', 'ory', 'fsi', 'lyn', 'lut', 'sus', 'mel', 'vul', 'lep', 'equ', 'cer', 'bos', 'gen', 'her', 'dam', 'fel', 'can', 'ovar', 'mafo', 'capi', 'caae', 'ovor', 'caca']

true = []
pred = []
iou = []

import PIL.Image as Image

with open("/home/usuario/Documentos/ziri/train_test_fasterrcnn/fastercnn-pytorch-training-pipeline/outputs/inference/res_7/boxes.csv", "r") as file:
    lines = file.readlines()[1:]
for line in lines:
    try:
        image, pred_label, pred_xmin, pred_xmax, pred_ymin, pred_ymax, pred_width, pred_height, pred_area = line.split(" ")
        if (pred_label not in CLASSES):
            continue
        with Image.open("/home/usuario/Documentos/ziri/dataset/test/images/" + image + ".jpg") as img:
            size_x, size_y = img.size
        with open("/home/usuario/Documentos/ziri/dataset/test/labels/" + image + ".txt", "r") as label_file:
            true_label, true_x, true_y, true_width, true_height = label_file.readline().split(" ")
        pred_x = (float(pred_xmin) / size_x + float(pred_xmax) / size_x) / 2
        pred_y = (float(pred_ymin) / size_y + float(pred_ymax) / size_y) / 2
        pred_w = float(pred_width) / size_x
        pred_h = float(pred_height) / size_y

        iou.append(calculate_iou([float(true_x), float(true_y), float(true_width), float(true_height)], [pred_x, pred_y, pred_w, pred_h]))
        
        true.append(int(true_label))
        pred.append(CLASSES.index(pred_label)-1)
    except Exception as e:
        print(e)
        continue

metrics = calculate_metrics(true, pred, iou)
print(metrics)

save_metrics_to_txt(metrics, "test_results_fasterrcnn")