from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import numpy as np

def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)
    
    box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
    
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    return iou

def calculate_metrics(true, pred, iou):
    return {
        "precision": precision_score(true, pred, average='weighted'),
        "recall": recall_score(true, pred, average='weighted'),
        "f1": f1_score(true, pred, average='weighted'),
        "iou_avg": sum(iou) / len(iou),
        "conf_matrix": confusion_matrix(true, pred)
    }

def save_metrix_to_txt(metrics, filename):
    with open(f"{filename}.txt", "w") as file:
        file.write("Precision: " + str(metrics['precision']) + "\n")
        file.write("Recall: " + str(metrics['recall']) + "\n")
        file.write("F1-score: " + str(metrics['f1']) + "\n")
        file.write("IoU: " + str(metrics['iou_avg']) + "\n")
        file.write("Confusion Matrix:\n")
        np.savetxt(file, metrics['conf_matrix'], fmt='%d')
        file.write("\n\n")

