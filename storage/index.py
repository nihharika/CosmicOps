import bisect

timestamps = []
offsets = []

def add(timestamp, offset):
    idx = bisect.bisect_left(timestamps, timestamp)
    timestamps.insert(idx, timestamp)
    offsets.insert(idx, offset)

def range_query(start, end):
    s = bisect.bisect_left(timestamps, start)
    e = bisect.bisect_right(timestamps, end)
    return offsets[s:e]