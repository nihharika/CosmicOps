"""
Main orchestration entry point.
"""

from ingestion.loader import load_images
from detection import detect
from telemetry.extractor import extract_value
from telemetry.anomaly import detect_anomaly
from telemetry.storage_engine import StorageEngine
from observability.tracing import tracer
from observability.metrics import images_processed, anomalies_detected
import config


db = StorageEngine(config.DB_FILE)


def process_image(timestamp, image):
    """
    Process a single image and store telemetry.
    """
    with tracer.start_as_current_span("process_image"):

        detections = detect(image)
        value = extract_value(detections)

        db.insert(timestamp, value)
        images_processed.add(1)

        if detect_anomaly(value):
            anomalies_detected.add(1)
            print("Anomaly detected at", timestamp)


def main():
    """
    Main entry point.
    """
    images = load_images(config.DATA_FOLDER)

    for timestamp, img in images:
        process_image(timestamp, img)


if __name__ == "__main__":
    main()