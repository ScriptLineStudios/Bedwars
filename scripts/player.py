from typing import List

import pygame

from scripts.entity import Entity
from scripts.tile import Tile

class Player(Entity):
    SPEED = 2
    JUMP_HEIGHT = 7

    def __init__(self, x, y) -> None:
        super().__init__(x, y)

        self.y_velocity = 3
        self.is_on_ground = False
        self.rect = pygame.Rect(self.x, self.y, 16, 16)

        self.walk_images = [self.load_image("player_walk1"), self.load_image("player_walk2"), self.load_image("player_walk3"), 
        self.load_image("player_walk4")]
        
        self.idle_images = [self.load_image("player_idle1"), self.load_image("player_idle2")]
        

        self.animation_index = 0
        
        self.camera = pygame.math.Vector2()

        self.player_movement = {"horizontal": 0, "vertical": self.y_velocity}
        self.facing_right = True
        self.moving = False


    def get_colliding_tiles(
        self, tiles: List[Tile], player_rect: pygame.Rect
    ) -> List[Tile]:
        """
        Returns a list of tiles the player is currently colliding with
        """
        return_tiles = []
        for tile in tiles:
            if tile.rect.colliderect(player_rect):
                return_tiles.append(tile)

        return return_tiles

    def calculate_rect(
        self, movement: dict, player_rect: pygame.Rect, map_tiles: List[Tile]
    ) -> pygame.Rect:
        """
        Calculates the Rect of the player based on their movement and the surrounding tiles
        """
        player_rect.x += movement["horizontal"]
        tiles = self.get_colliding_tiles(map_tiles, player_rect)
        for tile in tiles:
            if tile.collision(player_rect):
                if movement["horizontal"] > 0:
                    player_rect.right = tile.rect.left
                if movement["horizontal"] < 0:
                    player_rect.left = tile.rect.right

        self.is_on_ground = False
        player_rect.y += movement["vertical"]
        tiles = self.get_colliding_tiles(map_tiles, player_rect)
        for tile in tiles:
            if tile.collision(player_rect):
                if movement["vertical"] > 0:
                    player_rect.bottom = tile.rect.top
                    self.is_on_ground = True
                if movement["vertical"] < 0:
                    player_rect.top = tile.rect.bottom

        return player_rect

    def handle_movement(self, key_presses: dict, tiles) -> pygame.Rect:
        """
        Handles all code relating to the movement of the player
        """

        self.player_movement = {"horizontal": 0, "vertical": self.y_velocity}

        if key_presses["a"]:
            self.player_movement["horizontal"] -= self.SPEED
            self.facing_right = False
        if key_presses["d"]:
            self.player_movement["horizontal"] += self.SPEED
            self.facing_right = True

        self.moving = bool(self.player_movement["horizontal"])

        if self.y_velocity < 3:
            self.y_velocity += 0.2

        self.rect = self.calculate_rect(self.player_movement, self.rect, tiles)
        
    def draw(self, display) -> None:
        """
        Draws the player at the rect position
        """
        mx, my = pygame.mouse.get_pos()
        self.camera.x += (self.rect.x-self.camera.x-100+mx/200)/7
        self.camera.y += (self.rect.y-self.camera.y-75+my/200)/7

        if self.moving:    
            self.animation_index = self.animate(self.walk_images, self.animation_index, 15)
            display.blit(
                pygame.transform.flip(self.walk_images[self.animation_index//15], not self.facing_right, False), 
                (self.rect.x-self.camera.x, self.rect.y-self.camera.y))
        else:
            self.animation_index = self.animate(self.idle_images, self.animation_index, 15)
            display.blit(
                pygame.transform.flip(self.idle_images[self.animation_index//15], not self.facing_right, False), 
                (self.rect.x-self.camera.x, self.rect.y-self.camera.y))