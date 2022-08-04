import math
from typing import Tuple

import pygame


class Vector2:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def move_towards(self, dst_x, dst_y, speed) -> Tuple[float, float]:
        """
        Returns the sine and cosine needed to move the vector towards the target at the given speed.
        """

        dy, dx = dst_y - self.y, dst_x - self.x
        angle = math.atan2(dy, dx)

        if dx and dy:
            return math.cos(angle) * speed, math.sin(angle) * speed
        return 0, 0