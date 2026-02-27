from raylib import *
from pyray import *
from settings import *


class Food:
    def __init__(self):
        self.size = FOOD_SIZE
        self.color = FOOD_COLOR
        self.position = Vector2(200, 200)  # Initial position of the food
    
    def draw(self):
        draw_rectangle(int(self.position.x), int(self.position.y), self.size, self.size, self.color)