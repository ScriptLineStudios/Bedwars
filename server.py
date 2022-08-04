from networking.server import Server
from scripts.player import Player
from main import Game
from scripts.tile import Tile

import pygame
import json

clock = pygame.time.Clock()

server = Server("127.0.0.1", 4444, [
            200, 200, 0, 0, #X, Y, camX, camY
            0, 0, #moveX, moveY
            False, 3, #isOnGround, yVelocity
            0, False # animation_index, moving
        ])

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
    player_rect.x += player[4]
    tiles = get_colliding_tiles(map_tiles, player_rect)
    for tile in tiles:
        if player[4] > 0:
            player_rect.right = tile.rect.left
        if player[4] < 0:
            player_rect.left = tile.rect.right

    player[6] = False
    player_rect.y += player[7]
    tiles = get_colliding_tiles(map_tiles, player_rect)
    for tile in tiles:
        if player[7] > 0:
            player_rect.bottom = tile.rect.top
            player[6] = True
        if player[7] < 0:
            player_rect.top = tile.rect.bottom

    return player_rect

with open("assets/map/map.json", "rb") as file:
    map_data = json.load(file)
tiles = []
for tile in map_data["map"]:
    rect = pygame.Rect(tile[0], tile[1], tile[2], tile[3])
    tiles.append(Tile(rect=rect, color=(100, 100, 100), image=tile[4]))

while True:
    server.receive_data()
    data = server.data
    payload = data["payload"]
    '''
        The following section details the calculations that take place when the sever receives a data packet. These include changing the
        player position, peforming physics calculations, animations, jumping etc.
    '''

    
    if server.data_type == "data":
        username = payload["username"] #Get the username of the sender
        server.users[username][4] = 0
        server.users[username][5] = 0

        if payload["left"]:
            server.users[username][4] -= 2
        if payload["right"]:
            server.users[username][4] += 2
        if payload["jumping"]:
            if server.users[username][6]:
                server.users[username][7] -= 7

        if server.users[username][7] < 3:
            server.users[username][7] += 0.2

        rect = calculate_rect([server.users[username][4], server.users[username][5]], 
            pygame.Rect(server.users[username][0], server.users[username][1], 16, 16), tiles, 
            server.users[username])
            
        server.users[username][2] += (rect.x-server.users[username][2]-100) / 7
        server.users[username][3] += (rect.y-server.users[username][3]-75) / 7

        server.users[username][0] = rect.x
        server.users[username][1] = rect.y

        server.users[username][9] = bool(server.users[username][4]) #moving = is player moving

    server.distribute_data() #Distribute the updated user packet to all connected clients