class Obstacle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def collides(self, point):
        return (
            self.x <= point.x <= self.x + self.w and
            self.y <= point.y <= self.y + self.h
        )