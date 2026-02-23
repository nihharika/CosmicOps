import time
import random
from telemetry.storage_engine import StorageEngine

db = StorageEngine()

print("Inserting 100k rows...")

start = time.time()

base = time.time()

for i in range(100000):
    db.insert(base + i, random.random())

db.flush_block()

end = time.time()

print("Insert time:", end - start, "seconds")

print("Query test...")

start_q = time.time()
res = db.query_range(base + 1000, base + 5000)
end_q = time.time()

print("Query results:", len(res))
print("Query time:", end_q - start_q, "seconds")