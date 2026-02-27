from raylib import *
from food import Food
from snake import Snake
from pyray import *
from settings import *


class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.pause = False
        self.cell_size = SNAKE_SIZE
        self.offset_x = WINDOW_WIDTH % self.cell_size
        self.offset_y = WINDOW_HEIGHT % self.cell_size
    
    def update(self):
        if is_key_pressed(KEY_P):
            self.pause = not self.pause

        if self.pause:
            return

        self.snake.handle_input()
        self.snake.update()
        self.food.update()
    
    def draw(self):
        self.draw_grid()
        self.snake.draw()
        self.food.draw()

    def draw_grid(self):
        for i in range(WINDOW_WIDTH // self.cell_size + 1):
            x = int(self.cell_size * i + self.offset_x / 2)
            draw_line(
                x,
                int(self.offset_y / 2),
                x,
                int(WINDOW_HEIGHT - self.offset_y / 2),
                LIGHTGRAY,
            )

        for i in range(WINDOW_HEIGHT // self.cell_size + 1):
            y = int(self.cell_size * i + self.offset_y / 2)
            draw_line(
                int(self.offset_x / 2),
                y,
                int(WINDOW_WIDTH - self.offset_x / 2),
                y,
                LIGHTGRAY,
            )
    
    def startup(self):
        pass
    
    def shutdown(self):
        pass
