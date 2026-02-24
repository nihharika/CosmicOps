import os
from datetime import datetime

import cv2 


def extract_timestamp(filename: str) -> datetime:
    """
    Extract timestamp from filename formatted as LANDSAT_YYYYMMDD.jpg
    """
    parts = filename.split("_")
    date_part = parts[1].split(".")[0]
    return datetime.strptime(date_part, "%Y%m%d")


def load_images(folder: str):
    """
    Load all JPG and PNG images from folder.
    Returns list of (timestamp, image).
    """
    data = []

    for file in os.listdir(folder):
        if file.endswith((".jpg", ".png")):
            path = os.path.join(folder, file)
            img = cv2.imread(path)
            timestamp = extract_timestamp(file)
            data.append((timestamp, img))

    return data

## Images must be named like: LANDSAT_20240101.jpg
