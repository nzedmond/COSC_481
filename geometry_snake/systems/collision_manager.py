from config.settings import *

class CollisionManager:
    def __init__(self, player, trail):
        self.player = player
        self.trail = trail
        
    def check_all(self):
        return self.check_self_collision()
    
    def check_self_collision(self):
        head = self.player.pos
        for i, segment in enumerate(list(self.trail.points)[5:]):
            dx = head.x - segment.X
            dy = head.y - segment.y
            
            if (dx*dx + dy*dy) ** 0.5 < COLLISION_RADIUS:
                return True
            
            return False