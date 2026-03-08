import random

from raylib import *
from pyray import *
from settings import *


class Food:
    def __init__(self):
        self.size = FOOD_SIZE
        self.color = FOOD_COLOR
        self.position = Vector2(200, 200)  # Initial position of the food
        self.isActive = True  # Indicates whether the food is active (not eaten)
    
    def draw(self):
        draw_rectangle(int(self.position.x), int(self.position.y), self.size, self.size, self.color)
        
    def update(self, snake):
        if not self.isActive:
            return
        
        # Check for collision with the snake's head
        head = snake.body[0]
        if (head.x < self.position.x + self.size and
            head.x + snake.size > self.position.x and
            head.y < self.position.y + self.size and
            head.y + snake.size > self.position.y):
            self.isActive = False  # Deactivate the food after being eaten
            snake.length += 1  # Increase the snake's length when food is eaten
            snake.body.append(Vector2(snake.body[-1].x, snake.body[-1].y))  # Add a new segment to the snake's body

            # Generate a new food position that does not overlap snake segments.
            while True:
                candidate = Vector2(
                    random.randint(0, (WINDOW_WIDTH - self.size) // snake.size)
                    * snake.size,
                    random.randint(0, (WINDOW_HEIGHT - self.size) // snake.size)
                    * snake.size,
                )

                overlaps_snake = any(
                    segment.x == candidate.x and segment.y == candidate.y
                    for segment in snake.body
                )

                if not overlaps_snake:
                    self.position = candidate
                    break

            self.isActive = True  # Reactivate the food at the new position