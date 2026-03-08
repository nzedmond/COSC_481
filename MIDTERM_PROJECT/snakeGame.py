from raylib import *
from food import Food
from snake import Snake
from pyray import *
from settings import *


class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.pause = False
        self.cell_size = SNAKE_SIZE
        self.offset_x = WINDOW_WIDTH % self.cell_size
        self.offset_y = WINDOW_HEIGHT % self.cell_size
    
    def update(self):
        if self.game_over:
            if is_key_pressed(KEY_ENTER):
                self.reset()
        else:
            if is_key_pressed(KEY_P):
                self.pause = not self.pause

            if not self.pause:
                self.snake.handle_input()
                self.snake.update()
                self.check_wall_collision()
                self.food.update(self.snake)

    def check_wall_collision(self):
        head = self.snake.body[0]

        if (
            head.x > (WINDOW_WIDTH - self.offset_x)
            or head.y > (WINDOW_HEIGHT - self.offset_y)
            or head.x < 0
            or head.y < 0
        ):
            self.game_over = True
    
    def draw(self):
        self.draw_grid()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()

        if self.game_over:
            draw_text("GAME OVER!", WINDOW_WIDTH//4, WINDOW_HEIGHT//2, 50, DARKBROWN)
            draw_text("Press ENTER to restart", WINDOW_WIDTH//4, WINDOW_HEIGHT//2 + 60, 24, BLACK)
        elif self.pause:
            draw_text("GAME PAUSED!", WINDOW_WIDTH//4, WINDOW_HEIGHT//2, 50, BLACK)

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

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.pause = False
    
    def shutdown(self):
        pass
