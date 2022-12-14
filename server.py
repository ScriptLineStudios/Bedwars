from networking.server import Server
from scripts.tile import Tile

from scripts.inventory import Iron

import pygame
import json
import random

import threading

clock = pygame.time.Clock()

server = Server("127.0.0.1", 4444, [
            200, 200, 0, 0, #X, Y, camX, camY
            0, 0, #moveX, moveY
            False, 3, #isOnGround, yVelocity
            0, False # animation_index, moving
        ])

server.users["WORLD_DATA"] = {
    "items": []
}


def animate(image_list, animation_index, time_to_show_image_on_screen):
    if animation_index+1 >= len(image_list)*time_to_show_image_on_screen:
        animation_index = 0
    animation_index += 1

    return animation_index

def get_colliding_tiles(tiles, player_rect: pygame.Rect):
    """
    Returns a list of tiles the player is currently colliding with
    """
    return_tiles = []
    for tile in tiles:
        if tile.rect.colliderect(player_rect):
            return_tiles.append(tile)

    return return_tiles

def calculate_rect(
    movement: dict, player_rect: pygame.Rect, map_tiles, player
) -> pygame.Rect:
    """
    Calculates the Rect of the player based on their movement and the surrounding tiles
    """
    player_rect.x += player["moveX"]
    tiles = get_colliding_tiles(map_tiles, player_rect)
    for tile in tiles:
        if player["moveX"] > 0:
            player_rect.right = tile.rect.left
        if player["moveX"] < 0:
            player_rect.left = tile.rect.right

    player_rect.y += player["yVelocity"]
    player["isOnGround"] = False
    tiles = get_colliding_tiles(map_tiles, player_rect)
    for tile in tiles:
        if player["yVelocity"] > 0:
            player_rect.bottom = tile.rect.top
            player["isOnGround"] = True
        if player["yVelocity"] < 0:
            player_rect.top = tile.rect.bottom

    return player_rect

with open("assets/map/map.json", "rb") as file:
    map_data = json.load(file)

player_spawn_points = []
resource_spawn_points = []
tiles = []

for tile in map_data["map"]:
    rect = pygame.Rect(tile[0], tile[1], tile[2], tile[3])
    
    tile_name = tile[4].split("/")[-1].split(".")[0]
            
    if tile_name == "marker1": #Player_spawn_marker
        player_spawn_points.append([tile[0], tile[1]])
    elif tile_name == "marker2":
        resource_spawn_points.append([tile[0], tile[1]])
    else:
        tiles.append(Tile(rect=rect, color=(100, 100, 100), image=tile[4]))

server.spawn_points = player_spawn_points
server.resource_spawn_points = resource_spawn_points

resource_spawn_cooldown = 0

buffer_time = 0

def receive_data():
    while True:
        data = server.receive_data()
        
        if data == {}:
            continue

        payload = data["payload"]

        if server.data_type == "data":
            username = payload["username"] #Get the username of the sender
            server.users[username]["X"] = payload["X"]
            server.users[username]["Y"] = payload["Y"]

thread = threading.Thread(target = receive_data).start()

while True:
    if resource_spawn_cooldown <= 0:
        for point in resource_spawn_points:
            server.users["WORLD_DATA"]["items"].append([point[0], point[1], 8, 8, "iron.png", "iron"])
        resource_spawn_cooldown = 500
    else:
        resource_spawn_cooldown -= 1

    for i, item in enumerate(server.users["WORLD_DATA"]["items"]):
        server.users["WORLD_DATA"]["items"][i][3] += 1

    if buffer_time <= 0:
        server.distribute_data() #Distribute the updated user packet to all connected clients
        buffer_time = 1000
    else:
        buffer_time -= 1