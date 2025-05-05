from ultralytics import YOLO
from utils import Tester
import os

DATASET = '/home/usuario/Documentos/ziri/dataset/dataset.yaml'
TEST = '/home/usuario/Documentos/ziri/dataset/test'
SAVE_LOCATION = '/home/usuario/Documentos/ziri/models/yolo_trained.pt'

# Training
model = YOLO('yolov8s')
print('Training model...')
results = model.train(data=DATASET, epochs=20, imgsz=640, batch=16, save_period=1)
print('Training finished\nSaving model...')
model.save(SAVE_LOCATION)

# Testing
print("Initializing Tester...")
tester = Tester('yolo', TEST)

print("Importing model...")
model = YOLO(SAVE_LOCATION)
def get_pred(img_name):
    pcls, pbbox = -1, None
    img_path = os.path.join(tester.images_folder, f'{img_name}.jpg')
    for result in model(img_path):
        if len(result.boxes) != 0:
            pcls = int(result.boxes.cls[0].item())
            pbbox = result.boxes.xywhn[0].tolist()
        break
    return pcls, pbbox

print("Running tester")
tester.run(get_pred)

print("Tester finished\nSaving results...")
tester.calculate_metrics()
tester.save_metrics_to_txt()
tester.save_vals_to_txt()

print("Done.")