from core.network import send_request

response = send_request("127.0.0.1", 9001, {"type": "ping"})
print(response)