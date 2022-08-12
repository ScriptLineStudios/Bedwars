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

screen = pygame.display.set_mode((1000, 800))

inventory_slot = pygame.transform.scale(pygame.image.load("assets/images/slot.png").convert(), (12, 12))

iron_img = pygame.image.load("assets/images/iron.png").convert()
iron_img.set_colorkey((255, 255, 255))

class Game:
    FPS = 60
    def __init__(self):
        self.client = Client("178.128.43.84", 4444)
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
            "X": 40,
            "Y": 200
        }

        self.camera = [0, 0]
        self.screen = screen

        self.display = pygame.Surface((200, 150))
        self.minimap = pygame.Surface((500, 400))

        self.clock = pygame.time.Clock()

        self.running = True
        pygame.display.set_caption("Bedwars!")

        self.events = None

        self.key_presses = {"a": False, "d": False}

        self.inventory = [None, None, None, None, None]
        self.items = []
        self.handled_items = []

        with open("assets/map/map.json", "rb") as file:
            map_data = json.load(file)
        self.tiles = []
        for tile in map_data["map"]:
            rect = pygame.Rect(tile[0], tile[1], tile[2], tile[3])
            tile_name = tile[4].split("/")[-1].split(".")[0]
            
            if tile_name == "marker1" or tile_name == "marker2": #Player_spawn_marker
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

    def lerp(self, number, lerp_to, speed):
        return number + (lerp_to-number)* speed

    def main(self):
        receive_thread = threading.Thread(target=self.client.receive_data)
        receive_thread.start()

        while self.running:

            self.display.fill((125, 233, 255))
            self.minimap.fill(pygame.Color("black"))
            pygame.display.set_caption(f"{self.clock.get_fps()}")

            for i, slot in enumerate(self.inventory):
                self.display.blit(inventory_slot, (10+i*12, 10))
                if slot is not None:
                    self.display.blit(pygame.transform.scale(
                        slot[1], (slot[1].get_width()/2, slot[1].get_height()/2)), 
                            ((10+i*12)+slot[1].get_width()/4 - 2, 10+slot[1].get_height()/8))


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
                        print(self.client.buffer)


            keys = pygame.key.get_pressed()
            self.key_presses["a"] = keys[pygame.K_a]
            self.key_presses["d"] = keys[pygame.K_d]

            self.payload["X"] = self.player.rect.x
            self.payload["Y"] = self.player.rect.y

            json = {
                "type": self.client.request_types["data"],
                "payload": self.payload
            }
            request_json = self.client.create_json_object(json).encode()
            self.client.send_data(request_json)


            for name, packet in self.client.data.items(): #Handles incoming packets
                if name == self.username:
                    pass
                elif name == "WORLD_DATA":
                    pass

                    
                    #for item in packet["items"]:
                        # if item[4] not in self.handled_items:
                        #     if item[-1] == "iron":
                        #         self.items.append(Iron(item[0], item[1], 
                        #             item[2], item[3], iron_img, 
                        #             "iron")) #ngl this solution kinda sucks, but it will do for now...                                

                        #     self.handled_items.append(item[4])
                else:
                    self.client.add_to_buffer(str(name), packet)
                    for packet in self.client.buffer[str(name)]:
                        pygame.draw.circle(
                            self.display,
                            (255, 100, 40),
                            (packet["X"]-self.player.camera.x, packet["Y"]-self.player.camera.y),
                            2
                        )
                    if len(self.client.buffer[str(name)]) > 50:
                        packet = self.client.buffer[str(name)][1]
                        prev_packet = self.client.buffer[str(name)][0]

                        x = self.lerp(prev_packet["X"], packet["X"], 1)
                        y = self.lerp(prev_packet["Y"], packet["Y"], 1)

                        self.display.blit(self.player.idle_images[0], (x-self.player.camera.x, 
                            y-self.player.camera.y))
                        self.client.buffer[str(name)].remove(prev_packet)



            for item in self.items:
                item.draw(self)

            self.player.handle_movement(self.key_presses, self.tiles)
            self.player.draw(self.display)

            pygame.draw.circle(self.minimap, (255, 0, 0), (self.player.rect.x-self.player.camera.x, self.player.rect.y-self.player.camera.y + 255), 4)

            self.render_map(self.display, self.tiles)
            self.gui_manager.draw_gui_elements(self.display, self.events)

            self.screen.blit(pygame.transform.scale(self.display, (1000, 800)), (0, 0))
            self.screen.blit(pygame.transform.scale(self.minimap, (200,  150)), (700, 0))

            pygame.display.flip()
            self.clock.tick(self.FPS)

    @staticmethod
    def run(self):
        self.main()
