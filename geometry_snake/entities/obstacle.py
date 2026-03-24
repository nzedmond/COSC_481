class Obstacle:
    def __init__(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)
        
    def collides(self, point):
        return (
            self.x <= point.x <= self.x + self.w and
            self.y <= point.y <= self.y + self.h
        )