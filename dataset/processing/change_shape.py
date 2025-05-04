import os

# files are in <train,test,val>/<park>/<species>/<image>.jpg and <train,test,val>/<park>/<species>/<image>.txt
# change to <train,test,val>/images/<image>.jpg and <train,test,val>/labels/<image>.txt
for subset in os.listdir("dataset"):
    if subset == "dataset.yaml":
        continue
    os.makedirs(f"dataset/{subset}/images", exist_ok=True)
    os.makedirs(f"dataset/{subset}/labels", exist_ok=True)
    for park in os.listdir(f"dataset/{subset}"):
        if park == "images" or park == "labels":
                continue
        for species in os.listdir(f"dataset/{subset}/{park}"):
            if species.endswith(".cache"):
                continue
            for image in os.listdir(f"dataset/{subset}/{park}/{species}"):
                if image.endswith(".jpg"):
                    os.rename(f"dataset/{subset}/{park}/{species}/{image}", f"dataset/{subset}/images/{image}")
                elif image.endswith(".txt"):
                    os.rename(f"dataset/{subset}/{park}/{species}/{image}", f"dataset/{subset}/labels/{image}")