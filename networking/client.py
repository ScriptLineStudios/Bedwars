import socket
import json

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (self.ip, self.port)
        self.buffer_size = 65527

        self.request_types = {
            "login": "login",
            "sign up": "sign up",
            "data": "data",
            "disconnect": "disconnect"
        }
        self.data = {}

        self.buffer = {
            
        }

    def create_json_object(self, json_data: dict) -> object:
        return json.dumps(json_data)

    def send_data(self, data: dict) -> None:
        self.client.sendto(data, self.address)

    def receive_data(self) -> None:
        while True:
            msg = self.client.recvfrom(self.buffer_size)
            self.data = json.loads(msg[0].decode())

    def add_to_buffer(self, username, data):
        if username not in self.buffer:
            self.buffer[username] = []
            self.buffer[username].append(data)
        else:
            self.buffer[username].append(data)