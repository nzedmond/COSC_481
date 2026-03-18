from raylib import *
from pyray import *
from settings import *


class Snake:
    def __init__(self):
        self.length = SNAKE_LENGTH
        self.size = SNAKE_SIZE
        self.speed = SNAKE_SIZE  # Always move exactly one cell per tick to stay grid-aligned
        self.color = SNAKE_COLOR
        self.direction = Vector2(1, 0)  # Initial direction: right
        self.allow_move = True
        self.frames_counter = 0
        self.move_interval = SNAKE_MOVE_INTERVAL
        self.body = [Vector2(100 - i * self.size, 100) for i in range(self.length)]

    def handle_input(self):
        if is_key_pressed(KEY_RIGHT) and self.direction.x == 0 and self.allow_move:
            self.direction = Vector2(1, 0)
            self.allow_move = False
        if is_key_pressed(KEY_LEFT) and self.direction.x == 0 and self.allow_move:
            self.direction = Vector2(-1, 0)
            self.allow_move = False
        if is_key_pressed(KEY_UP) and self.direction.y == 0 and self.allow_move:
            self.direction = Vector2(0, -1)
            self.allow_move = False
        if is_key_pressed(KEY_DOWN) and self.direction.y == 0 and self.allow_move:
            self.direction = Vector2(0, 1)
            self.allow_move = False
        if is_key_pressed(KEY_RIGHT_BRACKET):
            self.move_interval = max(1, self.move_interval - 1)   # speed up
        if is_key_pressed(KEY_LEFT_BRACKET):
            self.move_interval = min(20, self.move_interval + 1)  # slow down

    def draw(self):
        for segment in self.body:
            draw_rectangle(int(segment.x), int(segment.y), self.size, self.size, self.color)

    def update(self):
        self.frames_counter += 1
        if (self.frames_counter % self.move_interval) != 0:
            return False  # Skip movement until the next interval

        # Move the snake's body segments
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i] = Vector2(self.body[i - 1].x, self.body[i - 1].y)

        # Move the head of the snake in the current direction
        self.body[0].x += self.direction.x * self.speed
        self.body[0].y += self.direction.y * self.speed
        self.allow_move = True
        self.frames_counter = 0  # Reset to avoid unbounded growth
        return True  # Indicate that the snake has moved this frame
