from pathlib import Path

import cv2
import matplotlib.pyplot as plt

# Find the project and dataset folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_DIR / "Dataaset" / "DeepGlobe"
TRAIN_DIR = DATASET_DIR / "train"

# Find satellite images
images = sorted(TRAIN_DIR.glob("*_sat.jpg"))

if not images:
    print("No satellite images found.")
    print("Dataset folder:", TRAIN_DIR)
else:
    image_path = images[0]
    print("Satellite image:", image_path.name)
    image_id = image_path.stem.replace("_sat", "")
    mask_path = TRAIN_DIR / f"{image_id}_mask.png"
    print("Segmentation mask:", mask_path.name)

    if not mask_path.exists():
        print("Matching mask not found:", mask_path)
    else:
        satellite = cv2.imread(str(image_path))
        satellite = cv2.cvtColor(satellite, cv2.COLOR_BGR2RGB)

        mask = cv2.imread(str(mask_path))
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(satellite)
        plt.title("Satellite Image")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(mask)
        plt.title("Segmentation Mask")
        plt.axis("off")

        plt.tight_layout()
        plt.show()