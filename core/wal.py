import os
import struct


class WriteAheadLog:

    def __init__(self, path="data/wal.log"):
        self.path = path
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "wb").close()

    def append(self, term, index, timestamp, value):
        with open(self.path, "ab") as f:
            entry = struct.pack("i i d f", term, index, timestamp, value)
            f.write(entry)

    def replay(self):
        entries = []
        with open(self.path, "rb") as f:
            while True:
                chunk = f.read(20)
                if not chunk:
                    break
                term, index, timestamp, value = struct.unpack("i i d f", chunk)
                entries.append((term, index, timestamp, value))
        return entries