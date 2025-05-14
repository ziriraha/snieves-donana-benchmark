import os

DATASET_YAML = '/home/usuario/Documentos/ziri/dataset/dataset.yaml'
CONFI_DATASET_YAML = '/home/usuario/Documentos/ziri/dataset/confi_dataset.yaml'
TEST_PATH = '/home/usuario/Documentos/ziri/dataset/test'
IMAGES_PATH = os.path.join(TEST_PATH, 'images')

def prepare_environment(model_name, delete=True):
    env_name = f"train_test_{model_name}"
    if delete: os.system(f"rm -rf {env_name}")
    os.makedirs(env_name, exist_ok=True)
    os.chdir(env_name)

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
        for img in os.listdir(self.images_folder):
            if not img.endswith('.jpg'): continue
            img_name = img.split('.')[0]
            rcls, rbbox = self.get_real(img_name)
            pcls, pbbox = get_pred(img_name)
            
            self.true.append(rcls)
            self.pred.append(pcls)
            # No IOU if empty image
            if rbbox and pbbox: self.iou.append(self.calculate_iou(pbbox, rbbox))

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