
from datetime import datetime
from ultralytics import YOLO



class Detector:
    """
    YOLOv8-based object detector for CosmicOps satellite imagery.
    Returns structured detection results with timestamp.
    """

    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect(self, image):
        """
        Run inference on an image and return structured detections.
        """
        results = self.model(image)
        detections = []

        timestamp = datetime.utcnow().isoformat()

        for r in results:
            for box in r.boxes:
                detections.append({
                    "timestamp": timestamp,
                    "class": int(box.cls),
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()[0]
                })

        return detections