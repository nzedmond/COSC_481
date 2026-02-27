from raylib import *
from pyray import *
from settings import *



class Snake:
    def __init__(self):
        self.length = SNAKE_LENGTH
        self.size = SNAKE_SIZE
        self.speed = SNAKE_SPEED
        self.color = SNAKE_COLOR
        self.direction = Vector2(1, 0)  # Initial direction: right
        self.body = [Vector2(100 - i * self.size, 100) for i in range(self.length)]  # Initial position of the snake's body segments
    
    def draw(self):
        for segment in self.body:
            draw_rectangle(int(segment.x), int(segment.y), self.size, self.size, self.color)
    
    def update(self):
        pass