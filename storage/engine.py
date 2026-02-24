from storage.compression import compress
from storage.index import add
import os

class StorageEngine:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def insert(self, timestamp, value):
        record = f"{timestamp},{value}\n".encode()
        compressed = compress(record)

        with open(self.path, "ab") as f:
            offset = f.tell()
            f.write(compressed)

        add(timestamp, offset)