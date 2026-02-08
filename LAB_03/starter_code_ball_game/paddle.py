from pyray import *
from os.path import join
from settings import *

class Paddle:
    def __init__(self, position):
        self.position = position
        self.score = 0
        self.color = BLUE
        self.width = 20
        self.height = 100
        self.speed = 200  # pixels per second
        self.rect = Rectangle(
            self.position.x, self.position.y, self.width, self.height)

    def draw(self):
        draw_rectangle_rec(self.rect, self.color)

    def update(self):
        '''Handles user input to move the paddle up and down'''
        motion = Vector2(0, 0)
        if is_key_down(KeyboardKey.KEY_UP):
            motion.y -= 1
        elif is_key_down(KeyboardKey.KEY_DOWN):
            motion.y += 1

        motion_this_frame = vector2_scale(
            motion, get_frame_time() * self.speed)
        self.position = vector2_add(self.position, motion_this_frame)

        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y + self.height > WINDOW_HEIGHT:
            self.position.y = WINDOW_HEIGHT - self.height

        # Update rectangle position
        self.rect.y = self.position.y