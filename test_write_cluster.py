from core.network import send_request

response = send_request("127.0.0.1", 9001, {
    "type": "write",
    "value": 123
})

print(response)