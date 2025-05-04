from ultralytics import YOLO
import os
from utils import calculate_iou, calculate_metrics, save_metrics_to_txt

dataset = 'dataset'
model = YOLO('yolov8s')
# Training

print('Training model...')
results = model.train(data=f'/home/usuario/Documentos/ziri/dataset/{dataset}.yaml', epochs=20, imgsz=640, batch=16, save_period=1)
model.save(f'models/yolo_trained_on_{dataset}.pt')
print('Training finished')
with open(f'train_results_{dataset}.txt', 'w') as f:
    print(results, file=f)

true_val = []
pred_val = []
iou = []

for img in os.listdir(f'{dataset}/test/images/'):
    path = f'{dataset}/test/images/' + img
    results = model(path)
    for result in results:
        if len(result.boxes) != 0:
            try:
                with open(path.replace('images', 'labels').replace('jpg', 'txt'), 'r') as f:
                    si = f.readline().split(" ")

                    true_val.append(int(si[0]))
                    pred_val.append(int(result.boxes.cls[0].item()))

                    true_box = [float(si[1]), float(si[2]), float(si[3]), float(si[4])]
                    pred_box = result.boxes.xywhn[0].tolist()
                    iou.append(calculate_iou(pred_box, true_box))
            except Exception as e: print(e)
        break

with open(f"results_test_yolo.txt", "w") as file:
    file.write("True vals: " + str(true_val) + " \n")
    file.write("Pred vals: " + str(pred_val) + " \n")
    file.write("IoU vals: " + str(iou) + " \n")

metrics = calculate_metrics(true_val, pred_val, iou)
print(metrics)

save_metrics_to_txt(metrics, "test_results_yolo")