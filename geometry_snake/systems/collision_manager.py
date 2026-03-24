from config.settings import *

class CollisionManager:
    def __init__(self, player, trail, obstacles):
        self.player = player
        self.trail = trail
        self.obstacles = obstacles
        
    def check_all(self):
        return (
            self.check_wall_collision()
            or self.check_self_collision()
            or self.check_obstacle_collision()
            )
    
    def check_wall_collision(self):
        return (
            self.player.pos.y < 0 or
            self.player.pos.y > SCREEN_HEIGHT
        )
        
    def check_self_collision(self):
        head = self.player.pos

        for segment in list(self.trail.points)[5:]:
            dx = head.x - segment.x
            dy = head.y - segment.y

            if (dx * dx + dy * dy) ** 0.5 < COLLISION_RADIUS:
                return True

        return False

    def check_obstacle_collision(self):
        head = self.player.pos

        for obs in self.obstacles:
            if obs.collides(head):
                return True

        return False