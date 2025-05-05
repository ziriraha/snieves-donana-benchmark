from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import numpy as np
import os

DATASET_YAML = '/home/usuario/Documentos/ziri/dataset/dataset.yaml'
CONFI_DATASET_YAML = '/home/usuario/Documentos/ziri/dataset/confi_dataset.yaml'
TEST_PATH = '/home/usuario/Documentos/ziri/dataset/test'
IMAGES_PATH = os.path.join(TEST_PATH, 'images')


class Tester:
    def __init__(self, name):
        self.model_name = name
        if not os.path.exists(TEST_PATH): raise Exception("Test directory doesn't exist")
        self.images_folder = os.path.join(TEST_PATH, 'images')
        self.labels_folder = os.path.join(TEST_PATH, 'labels')
        self.reset_vals()

    def reset_vals(self):
        self.true = []
        self.pred = []
        self.iou = []

    def get_real(self, img_name):
        lbl_path = os.path.join(self.labels_folder, img_name + '.txt')
        if not os.path.exists(lbl_path): # Empty image
            real_cls = -1 # -1 will represent an empty image
            real_box = None
        else: # Non-empty
            with open(lbl_path, 'r') as f:
                clas, *bbox = f.readline().split()
                real_cls = int(clas)
                real_box = list(map(float, bbox))
        return real_cls, real_box

    def run(self, get_pred):
        images = os.listdir(self.images_folder)
        for img in images:
            if not img.endswith('.jpg'): continue
            img_name = img.split('.')[0]
            rcls, rbbox = self.get_real(img_name)
            pcls, pbbox = get_pred(img_name)
            
            self.true.append(rcls)
            self.pred.append(pcls)
            # No IOU if empty image
            if rbbox and pbbox: self.iou.append(self.calculate_iou(pbbox, rbbox))

    def calculate_metrics(self):
        self.metrics = {
            "precision": precision_score(self.true, self.pred, average='weighted'),
            "recall": recall_score(self.true, self.pred, average='weighted'),
            "f1": f1_score(self.true, self.pred, average='weighted'),
            "iou_avg": sum(self.iou) / len(self.iou) if self.iou else 0,
            "conf_matrix": confusion_matrix(self.true, self.pred)
        }
        return self.metrics

    def save_metrics_to_txt(self, filename = None):
        if not filename: filename = f"{self.model_name}_metrics"
        with open(f"{filename}.txt", "w") as file:
            file.write("Precision: " + str(self.metrics['precision']) + "\n")
            file.write("Recall: " + str(self.metrics['recall']) + "\n")
            file.write("F1-score: " + str(self.metrics['f1']) + "\n")
            file.write("IoU: " + str(self.metrics['iou_avg']) + "\n")
            file.write("Confusion Matrix:\n")
            np.savetxt(file, self.metrics['conf_matrix'], fmt='%d')
            file.write("\n\n")
    
    def save_vals_to_txt(self, filename = None):
        if not filename: filename = f"{self.model_name}_values"
        with open(f"{filename}.txt", "w") as file:
            file.write("True vals: " + str(self.true) + " \n")
            file.write("Pred vals: " + str(self.pred) + " \n")
            file.write("IoU vals: " + str(self.iou) + " \n")

    def calculate_iou(cls, box1, box2):
        x1 = max(box1[0], box2[0]); x2 = min(box1[2], box2[2])
        y1 = max(box1[1], box2[1]); y2 = min(box1[3], box2[3])
        
        intersection_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)
        
        box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
        box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
        
        return intersection_area / (box1_area + box2_area - intersection_area)