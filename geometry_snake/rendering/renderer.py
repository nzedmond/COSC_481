from pyray import *

class Renderer:
    def __init__(self, player, trail):
        self.player = player
        self.trail = trail
        
    def draw(self):
        self.draw_trail()
        self.draw_player()
        
    def draw_player(self):
        draw_circle(int(self.player.pos.x), int(self.player.pos.y), 6, WHITE)
        
    def draw_trail(self):
        for point in self.trail.points:
            draw_circle(int(point.x), int(point.y), 3, GRAY)