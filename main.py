import pygame

from scripts.player import Player
from scripts.tile import Tile
from scripts.gui import Text, GuiManager
from scripts.images import *
from scripts.inventory import Iron

from networking.client import Client

import random
from typing import List
import json
import threading

class Game:
    FPS = 60
    def __init__(self):
        self.client = Client("127.0.0.1", 4444)
        self.username = str(random.random())

        sign_up_request_data = {
            "type": "sign up",
            "payload": {
                "username": self.username,
                "password": str(random.random())
            }
        }

        request = self.client.create_json_object(sign_up_request_data).encode()
        self.client.send_data(request)

        self.payload = {
            "username": self.username,
            "left": False, 
            "right": False,
            "jumping": False
        }

        self.camera = [0, 0]
        self.screen = pygame.display.set_mode((1000, 800))

        self.display = pygame.Surface((200, 150))
        self.minimap = pygame.Surface((500, 400))

        self.clock = pygame.time.Clock()

        self.running = True
        pygame.display.set_caption("Bedwars!")

        self.events = None

        self.key_presses = {"a": False, "d": False}

        self.inventory = [None, None, None, None, None]
        self.items = [Iron(-88, 404, 8, 8)]

        with open("assets/map/map.json", "rb") as file:
            map_data = json.load(file)
        self.tiles = []
        for tile in map_data["map"]:
            rect = pygame.Rect(tile[0], tile[1], tile[2], tile[3])
            tile_name = tile[4].split("/")[-1].split(".")[0]
            
            if tile_name == "marker1": #Player_spawn_marker
                pass
            else:
                self.tiles.append(Tile(rect=rect, color=(100, 100, 100), image=tile[4]))

        self.player = Player(40, 200)

        self.gui_manager = GuiManager([])  

    def render_map(self, display: pygame.Surface, tiles: List[Tile]) -> None:
        """
        Renders the games tiles
        """

        for tile in tiles:
            display.blit(tile.image, (tile.rect.x-self.player.camera.x, tile.rect.y-self.player.camera.y))
            self.minimap.blit(tile.image, (tile.rect.x-self.player.camera.x, tile.rect.y-self.player.camera.y + 255))


    def main(self):
        receive_thread = threading.Thread(target=self.client.receive_data)
        receive_thread.start()

        inventory_slot = pygame.transform.scale(pygame.image.load("assets/images/slot.png").convert(), (12, 12))

        iron_img = pygame.image.load("assets/images/iron.png").convert()
        iron_img.set_colorkey((255, 255, 255))

        while self.running:
            self.display.fill((125, 233, 255))
            self.minimap.fill(pygame.Color("black"))
            pygame.display.set_caption(f"{self.clock.get_fps()}")

            for i, slot in enumerate(self.inventory):
                self.display.blit(inventory_slot, (10+i*12, 10))

            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.payload["jumping"] = True
                        if self.player.is_on_ground:
                            self.player.y_velocity -= self.player.JUMP_HEIGHT

                    if event.key == pygame.K_o:
                        self.player.rect.x += 200
                        self.player.rect.y += 200


            keys = pygame.key.get_pressed()
            self.key_presses["a"] = keys[pygame.K_a]
            self.key_presses["d"] = keys[pygame.K_d]

            self.payload["left"] = keys[pygame.K_a]
            self.payload["right"] = keys[pygame.K_d]

            json = {
                "type": self.client.request_types["data"],
                "payload": self.payload
            }
            request_json = self.client.create_json_object(json).encode()
            self.client.send_data(request_json)

            for name, packet in self.client.data.items(): #Handles incoming packets
                if name == self.username:
                    pygame.draw.rect(self.display, (255, 0, 0), (packet["X"]-packet["camX"], packet["Y"]-packet["camY"], 16, 16), 1)
                    if abs(packet["X"] - self.player.rect.x) > 75:
                        print(f"Adju X: Predicted: {self.player.rect.x}, actual: {packet['X']}")
                        self.player.rect.x = packet["X"]
                        self.player.camera.x = packet["camX"]
                    
                    if abs(packet["Y"] - self.player.rect.y) > 175:
                        print(f"Adju Y: Predicted: {self.player.rect.y}, actual: {packet['Y']}")
                        self.player.rect.y = packet["Y"]
                        self.player.camera.y = packet["camY"]             
                else:
                    self.display.blit(self.player.idle_images[0], (packet["X"]-self.player.camera.x, packet["Y"]-self.player.camera.y))

            for item in self.items:
                item.draw(self)

            self.player.handle_movement(self.key_presses, self.tiles)
            self.player.draw(self.display)

            pygame.draw.circle(self.minimap, (255, 0, 0), (self.player.rect.x-self.player.camera.x, self.player.rect.y-self.player.camera.y + 255), 4)

            self.render_map(self.display, self.tiles)
            self.gui_manager.draw_gui_elements(self.display, self.events)

            self.payload["jumping"] = False

            self.screen.blit(pygame.transform.scale(self.display, (1000, 800)), (0, 0))
            self.screen.blit(pygame.transform.scale(self.minimap, (200,  150)), (700, 0))

            pygame.display.flip()
            self.clock.tick(self.FPS)

    @staticmethod
    def run(self):
        self.main()
