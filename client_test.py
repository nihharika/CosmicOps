import requests

for i in range(5):
    requests.post("http://localhost:8000/write", json={"value": i})