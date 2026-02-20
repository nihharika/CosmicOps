import time
from core.wal import WriteAheadLog

wal = WriteAheadLog()

wal.append(1, 1, time.time(), 42.5)
wal.append(1, 2, time.time(), 55.1)

entries = wal.replay()
print(entries)