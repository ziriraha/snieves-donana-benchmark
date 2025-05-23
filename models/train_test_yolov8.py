import os
import argparse

from ultralytics import YOLO

from utils import Tester, prepare_environment, DATASET_YAML

MODEL = 'yolo'
SAVE_PATH = './'

def prepare():
    print("Downloading YOLOv8...")
    return YOLO('yolov8s')

def train(model, save_path=SAVE_PATH):
    print('Training model...')
    model.train(data=DATASET_YAML, epochs=20, imgsz=640, batch=16, save_period=1)
    print('Training finished\nSaving model...')
    destination = os.path.join(save_path, "yolo.pt")
    model.save(destination)
    print('Model saved to ', destination)
    return model

def test(model, save_path=SAVE_PATH):
    print("Initializing Tester...")
    tester = Tester()

    print("Importing model...")
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
    destination = os.path.join(save_path, "yolo_values.txt")
    tester.save_vals_to_txt(destination)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Train and test YOLOv8 model")
    argparser.add_argument('--train', action='store_true', help="Only train the model (no testing)")
    argparser.add_argument('--save-dir', type=str, default=SAVE_PATH, help="Directory to save the model and/or values")
    args = argparser.parse_args()

    prepare_environment(MODEL)
    model = prepare()
    model = train(model, args.save_dir)
    if not args.train:
        test(model, args.save_dir)
    print("Done.")