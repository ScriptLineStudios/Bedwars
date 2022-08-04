import pygame
import json

from scripts.gui import Button, GuiManager

class Editor:
    def __init__(self):
        self.display = pygame.display.set_mode((700, 700))
        self.clock = pygame.time.Clock()

        self.blocks = {"map": []}
        with open("assets/map/map.json", "r") as f:
            json_string = json.load(f)
            self.blocks = json_string
        
        self.block_images = []

        for block in self.blocks["map"]:
            self.block_images.append(block[4])
            block.remove(block[4])

        self.tiles = ["assets/images/player_walk1.png"]

        self.clicking = False
        self.select_image = None

        def select_image(button):
            self.select_image = button.image_name

        self.gui_manager = GuiManager([])
        for i, tile_type in enumerate(self.tiles):
            self.gui_manager.gui_elements.append(Button(i*30, 10, tile_type, select_image))

        self.events = None
        self.removing = False

        self.offset_x = 0
        self.offset_y = 0


    def main(self):
        while True:
            self.display.fill((0, 0, 0))
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    with open("assets/map/map.json", "w") as f:
                        for index, block in enumerate(self.blocks["map"]):
                            block.append(self.block_images[index])
                        json_string = json.dumps(self.blocks)
                        f.write(json_string)
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True

                    if event.button == 3:
                        self.removing = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.removing = False


            self.offset_x -= pygame.key.get_pressed()[pygame.K_a] * 10
            self.offset_x += pygame.key.get_pressed()[pygame.K_d] * 10
            self.offset_y += pygame.key.get_pressed()[pygame.K_s] * 10
            self.offset_y -= pygame.key.get_pressed()[pygame.K_w] * 10

            mx, my = pygame.mouse.get_pos()
            mx += self.offset_x
            my += self.offset_y

            if my > 30:
                if self.clicking:
                    should_place = False
                    print( [((mx)//16)*16, ((my)//16)*16, 16, 16])
                    if not [((mx)//16)*16, ((my)//16)*16, 16, 16] in self.blocks["map"]:
                        self.blocks["map"].append([((mx) // 16)*16, ((my) //16)*16, 16, 16])
                        self.block_images.append(self.select_image)

                if self.removing:
                    for idx, block in enumerate(self.blocks["map"]):
                        if self.blocks["map"][idx] == [((mx) // 16) * 16, ((my) // 16) * 16, 16, 16]:
                            self.blocks["map"].pop(idx)
                            self.block_images.pop(idx)

            self.gui_manager.draw_gui_elements(self.display, self.events)

            for index, block in enumerate(self.blocks["map"]):
                self.display.blit(pygame.image.load(self.block_images[index]), (block[0]-self.offset_x, block[1]-self.offset_y, block[2], block[3]))

            pygame.display.update()
            self.clock.tick(60)