import os
import cv2
from datetime import datetime
from typing import List, Tuple


# Absolute folder path
DATA_FOLDER = "/Users/niharikabordoloi/CosmicOps/data/images"


def extract_timestamp(filename: str) -> datetime:
    """
    Extract date from filename like:
    LANDSAT19072004.jpg

    Date format: DDMMYYYY
    """
    name, _ = os.path.splitext(filename)

    # Remove prefix "LANDSAT"
    date_part = name.replace("LANDSAT", "")

    try:
        return datetime.strptime(date_part, "%d%m%Y")
    except ValueError:
        raise ValueError(f"Invalid date format in filename: {filename}")


def load_images(folder: str = DATA_FOLDER) -> List[Tuple[datetime, any]]:
    """
    Loads images with timestamps.
    Returns a sorted list of (timestamp, image).
    """

    if not os.path.exists(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    data = []

    for file in os.listdir(folder):
        if not file.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        path = os.path.join(folder, file)
        img = cv2.imread(path)

        if img is None:
            print(f"[WARNING] Could not read image: {file}")
            continue

        try:
            timestamp = extract_timestamp(file)
        except ValueError as e:
            print(f"[SKIPPED] {e}")
            continue

        data.append((timestamp, img))

    # Sort images by timestamp
    data.sort(key=lambda x: x[0])

    print(f"[INFO] Loaded {len(data)} images successfully.")

    return data