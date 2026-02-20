import time
from telemetry.telemetry_db import TelemetryDB

db = TelemetryDB()

now = time.time()

db.insert(now, 100.0)
db.insert(now + 1, 200.0)
db.insert(now + 2, 300.0)

results = db.query_range(now, now + 2)
print(results)