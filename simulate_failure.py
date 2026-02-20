import time
from core.network import send_request

for i in range(5):
    r = send_request("127.0.0.1", 9001, {
        "type": "write",
        "value": i
    })
    print(r)
    time.sleep(1)