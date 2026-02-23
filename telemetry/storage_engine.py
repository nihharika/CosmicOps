import os
import struct
import zlib
import numpy as np

from telemetry.cache import LRUCache


BLOCK_SIZE = 1024  # rows per block


class StorageEngine:
    def __init__(self, path="data/tsdb"):
        self.cache = LRUCache(100)
        self.path = path
        os.makedirs(self.path, exist_ok=True)

        self.data_file = os.path.join(self.path, "data.bin")
        self.index_file = os.path.join(self.path, "index.bin")

        self.buffer = []

        # Create files if they don’t exist
        if not os.path.exists(self.data_file):
            open(self.data_file, "wb").close()

        if not os.path.exists(self.index_file):
            open(self.index_file, "wb").close()

    # ---------------------------------
    # Insert
    # ---------------------------------

    def insert(self, timestamp, value):
        self.buffer.append((timestamp, value))

        if len(self.buffer) >= BLOCK_SIZE:
            self.flush_block()

    def flush_block(self):
        if not self.buffer:
            return

        timestamps = np.array([x[0] for x in self.buffer], dtype=np.float64)
        values = np.array([x[1] for x in self.buffer], dtype=np.float32)

        raw = timestamps.tobytes() + values.tobytes()
        compressed = zlib.compress(raw)

        with open(self.data_file, "ab") as df:
            offset = df.tell()
            df.write(struct.pack("I", len(compressed)))
            df.write(compressed)

        start_ts = timestamps[0]
        end_ts = timestamps[-1]

        with open(self.index_file, "ab") as idx:
            idx.write(struct.pack("d d Q", start_ts, end_ts, offset))

        self.buffer = []

    # ---------------------------------
    # Query
    # ---------------------------------

    def query_range(self, start_ts, end_ts):
        results = []

        with open(self.index_file, "rb") as idx:
            while True:
                chunk = idx.read(24)  # 8 + 8 + 8 bytes
                if not chunk:
                    break

                block_start, block_end, offset = struct.unpack("d d Q", chunk)

                if block_end < start_ts or block_start > end_ts:
                    continue

                # Check cache first
                if offset in self.cache:
                    timestamps, values = self.cache[offset]
                else:
                    with open(self.data_file, "rb") as df:
                        df.seek(offset)
                        size = struct.unpack("I", df.read(4))[0]
                        compressed = df.read(size)

                    raw = zlib.decompress(compressed)

                    half = len(raw) // 2
                    timestamps = np.frombuffer(raw[:half], dtype=np.float64)
                    values = np.frombuffer(raw[half:], dtype=np.float32)

                    self.cache[offset] = (timestamps, values)

                mask = (timestamps >= start_ts) & (timestamps <= end_ts)

                for t, v in zip(timestamps[mask], values[mask]):
                    results.append((float(t), float(v)))

        return results

    # ---------------------------------
    # Graceful shutdown
    # ---------------------------------

    def close(self):
        self.flush_block()