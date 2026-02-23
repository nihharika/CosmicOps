from core.network import send_request

for i in range(5):
    response = send_request("127.0.0.1", 9001, {
        "type": "write",
        "value": float(i * 10)
    })
    print(response)