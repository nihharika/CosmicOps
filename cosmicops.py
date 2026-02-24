"""
CosmicOps main orchestration module.
"""

from core.raft import RaftNode
from detection.loader import Detector
from telemetry.telemetry_loader import load_images
from telemetry.telemetry_db import TelemetryDB
from observability.tracing import tracer
from observability.metrics import images_processed


# Initialize components
detector = Detector()

raft = RaftNode(
    node_id="node-1",
    peers=[]
)

db = TelemetryDB("data/telemetry/tsdb.db")


def extract_value(detections):
    """
    Extract telemetry value from detection results.
    """
    return sum(1 for d in detections if d.get("class") == 8)


def process_image(timestamp, image):
    """
    Process a single image.
    """
    with tracer.start_as_current_span("process_image"):

        detections = detector.detect(image)
        value = extract_value(detections)

        # Change this to actual method in raft.py
        raft.append_entry({
            "type": "telemetry_insert",
            "timestamp": timestamp,
            "value": value,
        })

        images_processed.add(1)


def main():
    """
    Entry point.
    """
    images = load_images("data/images")

    for timestamp, img in images:
        process_image(timestamp, img)


if __name__ == "__main__":
    main()