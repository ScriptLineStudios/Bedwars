
import pygame
import os

def load_img(path, color=(255,255,255)):
    img = pygame.image.load(os.path.join("assets", "font", f"{path}.png"))
    img.set_colorkey(color)
    return img

alphabet = {
    "a": load_img("a", (0,0,0)),
    "b": load_img("b", (0,0,0)),
    "c": load_img("c", (0,0,0)),
    "d": load_img("d", (0,0,0)),
    "e": load_img("e", (0,0,0)),
    "f": load_img("f", (0,0,0)),
    "g": load_img("g", (0,0,0)),
    "h": load_img("h", (0,0,0)),
    "i": load_img("i", (0,0,0)),
    "j": load_img("j", (0,0,0)),
    "k": load_img("k", (0,0,0)),
    "l": load_img("l", (0,0,0)),
    "m": load_img("m", (0,0,0)),
    "n": load_img("n", (0,0,0)),
    "o": load_img("o", (0,0,0)),
    "p": load_img("p", (0,0,0)),
    "q": load_img("q", (0,0,0)),
    "r": load_img("r", (0,0,0)),
    "s": load_img("s", (0,0,0)),
    "t": load_img("t", (0,0,0)),
    "u": load_img("u", (0,0,0)),
    "v": load_img("v", (0,0,0)),
    "w": load_img("w", (0,0,0)),
    "x": load_img("x", (0,0,0)),
    "y": load_img("y", (0,0,0)),
    "z": load_img("z", (0,0,0)),
    " ": load_img("space", (0,0,0)),
    "0": load_img("0", (0,0,0)),
    "1": load_img("1", (0,0,0)),
    "2": load_img("2", (0,0,0)),
    "3": load_img("3", (0,0,0)),
    "4": load_img("4", (0,0,0)),
    "5": load_img("5", (0,0,0)),
    "6": load_img("6", (0,0,0)),
    "7": load_img("7", (0,0,0)),
    "8": load_img("8", (0,0,0)),
    "9": load_img("9", (0,0,0)),
    "/": load_img("tick", (0,0,0)),
}