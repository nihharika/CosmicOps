def extract_value(detections):
    # Example: count detected ships (class 8 placeholder)
    ship_count = sum(1 for d in detections if d["class"] == 8)
    return ship_count