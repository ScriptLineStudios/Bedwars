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

        # self.cluster = MongoClient("ok")
        # self.db = self.cluster["pygame-sockets"]
        # self.collection = self.db["user-data"]
        # self.collection.delete_many({});

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

        print("Server created and listening...")

        self.number_users = 0
        self.spawn_points = []
        self.resource_spawn_points = []

    def sign_up_user(self, payload: dict, address: tuple) -> None:
        '''
            Method for allowing the creation of a new user on the database
            and posting the login details to the MongoDB database
        '''

        username = payload["username"]
        password = payload["password"]
        print("Incoming connection...")
        self.active_connections.append(address) 
       # self.collection.insert_one({ "name": username, "password": password, "user_data": {}})

        player_data = {
            "X": 40,           #0
            "Y": 200,           #1
            "camX": 0, 
            "camY": 0,
            "moveX": 0, 
            "moveY": 0, 
            "isOnGround": False,
            "yVelocity": 3, 
            "animationIndex": 0, 
            "moving": False, 
            
            "numberPlayers": 0
        }

        self.users[username] = player_data #Construct a new user
        self.number_users += 1

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

    def receive_data(self) -> object:
        msg = self.server.recvfrom(self.buffer_size)
        data = json.loads(msg[0].decode())
        address = msg[1]
        self.data_type = data["type"]
        payload = data["payload"]
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

        return data 

    def distribute_data(self) -> None:
        for name in iter(self.users):
            self.users[name]["numberPlayers"] = self.number_users

        for connection in self.active_connections:
            self.server.sendto(json.dumps(self.users).encode(), connection)
        
