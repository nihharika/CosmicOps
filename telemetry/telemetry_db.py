from telemetry.storage_engine import StorageEngine
from telemetry.anomaly import detect_anomaly

class TelemetryDB:

    def __init__(self, path):
        self.engine = StorageEngine(path)

    def insert(self, timestamp, value):
        self.engine.insert(timestamp, value)

        if detect_anomaly(value):
            print(f"[ANOMALY] at {timestamp}")