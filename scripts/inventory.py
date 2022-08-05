import abc

import pygame

class InventoryItem:
    def __init__(self, image):
        self.image = image
        self.count = 1

class Item(abc.ABC):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def collision_check(self, game):
        if self.rect.colliderect(game.player.get_rect()):
            for slot in game.inventory:
                if slot is not None:
                    if 

            game.items.remove(self)
            
    @abc.abstractmethod
    def draw(self, display):
        pass

class Iron(Item):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def draw(self, game):
        self.rect = pygame.Rect(self.x-game.player.camera.x, self.y-game.player.camera.y, self.width, self.height)
        self.collision_check(game)
        pygame.draw.rect(game.display, (255, 0, 0), self.rect, 2)