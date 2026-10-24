from pathlib import Path
import cv2
import matplotlib.pyplot as plt

# Dataset folder location
DATASET_DIR = Path(__file__).resolve().parent.parent / "Dataset" / "DeepGlobe"

# Training images folder
TRAIN_DIR = DATASET_DIR / "train"

# Find satellite images
satellite_images = sorted(TRAIN_DIR.glob("*_sat.jpg"))

if not satellite_images:
    print("No satellite images found!")
    print("Please check the dataset folder path and image filenames.")
else:
    # Select the first satellite image
    image_path = satellite_images[0]

    # Find the matching segmentation mask
    mask_path = TRAIN_DIR / f"{image_path.stem.replace('_sat', '')}_mask.png"

    if not mask_path.exists():
        print(f"Matching mask not found: {mask_path}")
    else:
        # Read satellite image
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Read segmentation mask
        mask = cv2.imread(str(mask_path))
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

        # Display both images
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(image)
        plt.title("Original Satellite Image")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(mask)
        plt.title("Segmentation Mask")
        plt.axis("off")

        plt.tight_layout()
        plt.show()