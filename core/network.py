import socket
import threading
import json


class NodeServer:
    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port

    def start(self, handler):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)

        print(f"[NETWORK] Listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server.accept()
            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, handler)
            )
            thread.start()

    def handle_client(self, client_socket, handler):
        try:
            data = client_socket.recv(4096).decode()
            request = json.loads(data)
            response = handler(request)
            client_socket.send(json.dumps(response).encode())
        except Exception as e:
            client_socket.send(json.dumps({"error": str(e)}).encode())
        finally:
            client_socket.close()


def send_request(host, port, payload):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send(json.dumps(payload).encode())
    response = json.loads(client.recv(4096).decode())
    client.close()
    return response