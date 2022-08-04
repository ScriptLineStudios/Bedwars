from abc import ABC, abstractmethod
from typing import List
from scripts.images import alphabet

import pygame

pygame.font.init()


class UIElement(ABC):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def handle_events(self, events: list) -> None:
        pass

    @abstractmethod
    def draw(self, display: pygame.Surface) -> None:
        pass


class GuiManager:
    def __init__(self, gui_elements: List[UIElement]) -> None:
        self.gui_elements = gui_elements

    def get_element(self, index: int) -> UIElement:
        """
        Returns the element at the given index
        """

        return self.gui_elements[index]

    def draw_gui_elements(self, display: pygame.Surface, events: list) -> None:
        """
        Draws each ui element
        """

        for element in self.gui_elements:
            element.handle_events(events)
            element.draw(display)

class Button(UIElement):
    def __init__(self, x: int, y: int, image: str, function):
        super().__init__(x, y)

        self.pressing_button = False
        self.function = function

        self.image_name = image
        self.image = pygame.image.load(image)

    def handle_events(self, events: list) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height()).collidepoint((mx, my)):
                        self.pressing_button = True
                        self.function(self)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.pressing_button = True

    def draw(self, display: pygame.Surface) -> None:
        display.blit(self.image, (self.x, self.y))


class Text(UIElement):
    def __init__(self, x: int, y: int, text: str, size: int) -> None:
        super().__init__(x, y)
        self.size = size

        self.text = text


    def render_text(self, display, word, pos):
        for index, letter in enumerate(word):
                img = alphabet[letter]
                if letter == " ":
                    display.blit(img, ((pos[0]+index*32), pos[1]))
                else:
                    display.blit(img, ((pos[0]+index*7), pos[1]))      

    def draw(self, display: pygame.Surface) -> None:
        """
        Renders text
        """
        self.render_text(display, self.text, (self.x, self.y))


class Slider(UIElement):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        self.pointer_x = x
        self.pointer_y = y

        self.clicking = False
        self.clicked_mouse_x = 0

    def handle_events(self, events: list) -> None:
        """
        Handles movement of slider
        """

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if pygame.Rect(
                        self.pointer_x - 5, self.pointer_y, 10, 10
                    ).collidepoint(pygame.mouse.get_pos()):
                        self.clicking = True
                        self.clicked_mouse_x = pygame.mouse.get_pos()[0]

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicking = False

    def get_value(self) -> float:
        clamp = lambda smallest, n, largest: sorted([smallest, n, largest])[1]
        return clamp(-1.0, ((self.pointer_x - self.x) / 100) - 1, 1.0)

    def draw(self, display: pygame.Surface) -> None:
        current_mouse_x = pygame.mouse.get_pos()[0]
        if self.clicking:
            if (
                self.pointer_x < self.x + 99
                and self.clicked_mouse_x - current_mouse_x < 0
                or self.pointer_x > self.x - 1
                and self.clicked_mouse_x - current_mouse_x > 0
            ):
                self.pointer_x -= (self.clicked_mouse_x - current_mouse_x) / 25
        pygame.draw.rect(display, (100, 100, 100), (self.x, self.y, 100, 8))
        pygame.draw.circle(
            display, (255, 0, 0), (self.pointer_x, self.pointer_y + 4), 5
        )