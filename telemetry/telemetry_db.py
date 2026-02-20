import os
import numpy as np

class TelemetryDB:

    def __init__(self, path="data/telemetry"):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

        self.timestamps_file = os.path.join(self.path, "timestamps.bin")
        self.values_file = os.path.join(self.path, "values.bin")

    def insert(self, timestamp, value):
        with open(self.timestamps_file, "ab") as tf:
            tf.write(np.array([timestamp], dtype=np.float64).tobytes())

        with open(self.values_file, "ab") as vf:
            vf.write(np.array([value], dtype=np.float32).tobytes())

    def query_range(self, start_ts, end_ts):
        timestamps = np.fromfile(self.timestamps_file, dtype=np.float64)
        values = np.fromfile(self.values_file, dtype=np.float32)

        mask = (timestamps >= start_ts) & (timestamps <= end_ts)
        return list(zip(timestamps[mask], values[mask]))