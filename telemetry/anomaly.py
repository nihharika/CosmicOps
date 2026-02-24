from collections import deque
import statistics

window = deque(maxlen=50)

def detect_anomaly(value):
    window.append(value)

    if len(window) < 10:
        return False

    mean = statistics.mean(window)
    std = statistics.stdev(window)

    if std == 0:
        return False

    z = (value - mean) / std
    return abs(z) > 3
