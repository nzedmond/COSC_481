
from pyray import *
import random

# ------------------- DEFINE CONSTANTS/GLOBALS -------------------------
# Window settings
screen_width = 800
screen_height = 600

# -------------------- DEFINE GLOBAL FUNCTIONS -------------------------


# create the player

class Player:
    def __init__(self):
        self.width = 100
        self.height = 20
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 40
        self.speed = 7
        self.score = 0
        
    def draw(self):
        draw_rectangle(self.x, self.y, self.width, self.height, BLUE)
        
# create falling objects
class FallingObject:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(0, screen_width - self.width)
        self.y = 0
        self.speed = 5
    
    def draw(self):
        draw_rectangle(self.x, self.y, self.width, self.height, RED)

# Game loop

class Game:
    def __init__(self):
        self.player = Player()
        self.falling_object = FallingObject()
        
    def update(self):
        if is_key_down(KEY_LEFT) and self.player.x > 0:
            self.player.x -= self.player.speed
        
        if is_key_down(KEY_RIGHT) and self.player.x < screen_width - self.player.width:
            self.player.x += self.player.speed
            
        self.falling_object.y += self.falling_object.speed  # move the falling object
        
        # check for collision
        
        if (self.falling_object.y + self.falling_object.height >= self.player.y and self.falling_object.x + self.falling_object.width >= self.player.x and self.falling_object.x <= self.player.x + self.player.width):
            self.player.score += 1
            self.falling_object.y = 0
            self.falling_object.x = random.randint(0, screen_width - self.falling_object.width)
            
        # reset is missed
        if self.falling_object.y > screen_height:
            self.falling_object.y = 0
            self.falling_object.x = random.randint(0, screen_width - self.falling_object.width)
            
    def draw(self):
        self.player.draw()
        self.falling_object.draw()
        draw_text(f"Score: {self.player.score}", 10, 10, 20, BLACK)
        
    def shutdown(self):
        pass

