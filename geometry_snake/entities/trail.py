from collections import deque
from pyray import *
from config.settings import *

class Trail:
    def __init__(self):
        self.points = deque()
        
    def update(self, head_pos):
        if not self.points:
            self.points.appendleft(Vector2(head_pos.x, head_pos.y))
            return
        
        last = self.points[0]
        
        if ((head_pos.x - last.x) ** 2 + (head_pos.y - last.y) ** 2) ** 0.5 >= TRAIL_MIN_STEP:  # write a helper for this
            self.points.appendleft(Vector2(head_pos.x, head_pos.y))
            
            if len(self.points) > TRAIL_MAX_LENGTH:
                self.points.pop()