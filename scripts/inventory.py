import abc

import pygame
from scripts.gui import Text

class InventoryItem:
    def __init__(self, image):
        self.image = image
        self.count = 1

class Item(abc.ABC):
    def __init__(self, x, y, width, height, image, image_name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.image_name = image_name
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def collision_check(self, game):
        if self.rect.colliderect(game.player.get_rect()):
            for i, slot in enumerate(game.inventory):
                if slot is None:
                    game.inventory[game.inventory.index(slot)] = [self.image_name, self.image, 1, None]
                    game.gui_manager.add_element(Text(19+i*12, 17, str(game.inventory[i][2]), 4))
                    game.inventory[i][3] = game.gui_manager.get_element(-1)
                    break
                else:
                    if self.image_name in slot:
                        game.inventory[i][2] += 1
                        game.inventory[i][3].update_text(str(game.inventory[i][2]))
                        break

            game.items.remove(self)
            
    @abc.abstractmethod
    def draw(self, display):
        pass

class Iron(Item):
    def __init__(self, x, y, width, height, image, image_name):
        super().__init__(x, y, width, height, image, image_name)

    def draw(self, game):
        self.rect = pygame.Rect(self.x-game.player.camera.x, self.y-game.player.camera.y, self.width, self.height)
        self.collision_check(game)
        game.display.blit(self.image, self.rect)