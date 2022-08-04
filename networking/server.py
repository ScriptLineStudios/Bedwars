import socket
import json
from pymongo import MongoClient

class Server:
    def __init__(self, ip: str, port: int, player_data: list):
        self.ip = ip
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (self.ip, self.port)
        self.buffer_size = 65527

        self.server.bind(self.address)
        self.data = {}
        self.data_type = None

        self.cluster = MongoClient("mongodb+srv://scriptline:VwuyimDwh81IVaqE@cluster0.2gjvk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.db = self.cluster["pygame-sockets"]
        self.collection = self.db["user-data"]
        self.collection.delete_many({});

        self.request_types = {
            "login": "login",
            "sign up": "sign up",
            "data": "data",
            "disconnect": "disconnect"
        }

        self.active_connections = []
        self.users = {

        }
        self.player_data = player_data

    def sign_up_user(self, payload: dict, address: tuple) -> None:
        '''
            Method for allowing the creation of a new user on the database
            and posting the login details to the MongoDB database
        '''

        username = payload["username"]
        password = payload["password"]
        print("Incoming connection...")
        self.active_connections.append(address) 
        self.collection.insert_one({ "name": username, "password": password, "user_data": {}})
        player_data = [
        200, 200, 0, 0, 0, 0, 0, 0, 0, True, 0, 0 #rect_x, rect_y, scroll x, scroll y, movement x,
            # movement y, vertical momentum, air timer, animation index, 
            # facing right, prev x, prev y
        ]
        self.users[username] = player_data #Construct a new user

    def login_user(self, payload: dict, address: tuple) -> None:
        '''
            Method from retrived data from the MongoDB database
        '''

        username = payload["username"]
        password = payload["password"]
        self.active_connections.append(address)
        for document in self.collection.find():
            if document["name"] == username:
                print("Match Found! logging in")
                print(document["user_data"])
                self.users[username] = document["user_data"]

    def receive_data(self) -> None:
        msg = self.server.recvfrom(self.buffer_size)
        self.data = json.loads(msg[0].decode())
        address = msg[1]
        self.data_type = self.data["type"]
        payload = self.data["payload"]
        if self.data_type == "sign up":
            self.sign_up_user(payload, address)
        elif self.data_type == "login":
            self.login_user(payload, address)
        elif self.data_type == "disconnect":
            client_name = payload["username"]
            print(f"Disconneting client {client_name}")
            self.collection.update_one({"name": client_name}, {"$set":{"user_data": self.users[client_name]}})
            self.active_connections.remove(address)
            del self.users[client_name]

    def distribute_data(self) -> None:
        for connection in self.active_connections:
            self.server.sendto(json.dumps(self.users).encode(), connection)
        