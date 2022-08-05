import pygame
import json

from scripts.gui import Button, GuiManager

TILE_SIZE = 8

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

        self.tiles = ["assets/images/tiles/grass.png", "assets/images/tiles/dirt.png", "assets/images/bed.png"]

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

        self.highlighting = False
        self.highlight_rect = None

        self.click_pos = (0, 0)

        self.copied_blocks = []
        self.copied_block_images = []
        
        while True:

            mx, my = pygame.mouse.get_pos()
            mx += self.offset_x
            my += self.offset_y
            self.display.fill((0, 0, 0))

            for index, block in enumerate(self.blocks["map"]):
                self.display.blit(pygame.image.load(self.block_images[index]), (block[0]-self.offset_x, block[1]-self.offset_y, block[2], block[3]))
            
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

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.highlighting = not self.highlighting       

                    if event.key == pygame.K_q and self.highlighting:
                        x_lower_bound = self.highlight_rect.topright[0] + self.offset_x
                        x_upper_bound = self.highlight_rect.topleft[0] + self.offset_x

                        y_lower_bound = self.highlight_rect.bottomright[1] + self.offset_y
                        y_upper_bound = self.highlight_rect.topleft[1] + self.offset_y
                        
                        for idx, block in enumerate(self.blocks["map"]):
                            if (block[0] < x_lower_bound and block[0] > x_upper_bound and block[1] < y_lower_bound and block[1] > y_upper_bound):
                                self.blocks["map"].pop(idx)
                                self.block_images.pop(idx)

                    if event.key == pygame.K_c and self.highlighting:
                        self.copied_blocks = []
                        self.copied_block_images = []

                        x_lower_bound = self.highlight_rect.topright[0] + self.offset_x
                        x_upper_bound = self.highlight_rect.topleft[0] + self.offset_x

                        y_lower_bound = self.highlight_rect.bottomright[1] + self.offset_y
                        y_upper_bound = self.highlight_rect.topleft[1] + self.offset_y

                        for i, block in enumerate(self.blocks["map"]):
                            
                            if (block[0] < x_lower_bound and block[0] > x_upper_bound and 
                                block[1] < y_lower_bound and block[1] > y_upper_bound):
                                if block not in self.copied_blocks:
                                    self.copied_blocks.append(block)    
                                    self.copied_block_images.append(self.block_images[i])          
                                #pygame.draw.rect(self.display, (255, 0, 0), (block[0]-self.offset_x, block[1]-self.offset_y, block[2], block[3]), 1) 
                        
                        print("Copied!")

                    if event.key == pygame.K_v and self.highlighting:
                        for i, block in enumerate(self.copied_blocks):
                            self.blocks["map"].append([((mx+block[0]) // TILE_SIZE)*TILE_SIZE, 
                            ((block[1]+self.offset_y) //TILE_SIZE)*TILE_SIZE, block[2], block[3]])
                            self.block_images.append(self.copied_block_images[i])

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        self.click_pos = (mx -self.offset_x, my -self.offset_y)
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


            if not self.highlighting:
                if my > 30:
                    if self.clicking:
                        should_place = False
                        if not [((mx)//TILE_SIZE)*TILE_SIZE, ((my)//TILE_SIZE)*TILE_SIZE, TILE_SIZE, TILE_SIZE] in self.blocks["map"]:
                            self.blocks["map"].append([((mx) // TILE_SIZE)*TILE_SIZE, ((my) //TILE_SIZE)*TILE_SIZE, pygame.image.load(self.select_image).get_width(), 
                            pygame.image.load(self.select_image).get_height()])
                            self.block_images.append(self.select_image)

                    if self.removing:
                        for idx, block in enumerate(self.blocks["map"]):
                            if self.blocks["map"][idx] == [((mx) // TILE_SIZE) * TILE_SIZE, ((my) // TILE_SIZE) * TILE_SIZE, block[2], block[3]]:
                                self.blocks["map"].pop(idx)
                                self.block_images.pop(idx)
            else:
                if self.clicking:
                    self.highlight_rect = pygame.Rect(self.click_pos[0], self.click_pos[1], abs(self.click_pos[0] - (mx - self.offset_x)), abs(self.click_pos[1] - (my - self.offset_y )))
                if self.highlight_rect is not None:
                    pygame.draw.rect(self.display, (255, 255, 255), self.highlight_rect, 1)

            self.gui_manager.draw_gui_elements(self.display, self.events)

            

            pygame.display.update()
            self.clock.tick(60)