import pyray as rl
import math
import random


# gemini translation of 
#  https://github.com/alexeykarnachev/raylib_platforms_demo/blob/master/src/main.c

# --- Constants ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024
GRAVITY = 50.0
PLAYER_MAX_HEALTH = 100.0
MAX_SAFE_SPEED = 30.0

# Colors
BACKGROUND_COLOR = rl.Color(20, 20, 20, 255)
OBSTACLE_COLOR = rl.Color(80, 80, 80, 255)
UI_BG_COLOR = rl.Color(40, 40, 40, 255)

class Utils:
    @staticmethod
    def get_aabb_mtv(r1: rl.Rectangle, r2: rl.Rectangle) -> rl.Vector2:
        """Calculates Minimum Translation Vector to push r1 out of r2."""
        mtv = rl.Vector2(0, 0)
        if not rl.check_collision_recs(r1, r2):
            return mtv

        x_west = r2.x - r1.x - r1.width
        x_east = r2.x + r2.width - r1.x
        mtv.x = x_west if abs(x_west) < abs(x_east) else x_east

        y_south = r2.y + r2.height - r1.y
        y_north = r2.y - r1.y - r1.height
        mtv.y = y_south if abs(y_south) < abs(y_north) else y_north

        if abs(mtv.x) > abs(mtv.y):
            mtv.x = 0.0
        else:
            mtv.y = 0.0
        return mtv

    @staticmethod
    def lerp_color(c1: rl.Color, c2: rl.Color, ratio: float) -> rl.Color:
        return rl.Color(
            int((1.0 - ratio) * c1.r + ratio * c2.r),
            int((1.0 - ratio) * c1.g + ratio * c2.g),
            int((1.0 - ratio) * c1.b + ratio * c2.b),
            255)

class Obstacle:
    def __init__(self, rect: rl.Rectangle, end_pos: rl.Vector2 = None, speed: float = 0.0):
        self.rect = rect
        self.start_pos = rl.Vector2(rect.x, rect.y)
        self.end_pos = end_pos if end_pos else self.start_pos
        self.speed = speed
        self.is_moving_to_start = False
        self.is_player_attached = False

    def update(self, dt: float, player):
        if self.speed <= 0:
            return

        # Movement Logic
        direction = rl.vector2_normalize(rl.vector2_subtract(self.end_pos, self.start_pos))
        if self.is_moving_to_start:
            direction = rl.vector2_negate(direction)

        step = rl.vector2_scale(direction, self.speed * dt)
        self.rect.x += step.x
        self.rect.y += step.y

        if self.is_player_attached:
            player.position = rl.vector2_add(player.position, step)

        # Reached target check
        target = self.start_pos if self.is_moving_to_start else self.end_pos
        to_target = rl.vector2_subtract(target, rl.Vector2(self.rect.x, self.rect.y))
        
        if rl.vector2_dot_product(direction, to_target) <= 0:
            self.rect.x, self.rect.y = target.x, target.y
            self.is_moving_to_start = not self.is_moving_to_start

    def draw(self):
        rl.draw_rectangle_rec(self.rect, OBSTACLE_COLOR)

class Player:
    def __init__(self):
        self.position = rl.Vector2(0, 0)
        self.velocity = rl.Vector2(0, 0)
        self.size = rl.Vector2(1.0, 2.0)
        self.speed = 15.0
        self.jump_impulse = 30.0
        self.health = PLAYER_MAX_HEALTH
        self.is_grounded = False

    @property
    def rect(self) -> rl.Rectangle:
        return rl.Rectangle(
            self.position.x + 0.5 * self.size.x,
            self.position.y + self.size.y,
            self.size.x,
            self.size.y
        )

    def update(self, dt: float):
        # Gravity
        self.velocity.y += GRAVITY * dt

        # Horizontal Input
        move_dir = 0.0
        if rl.is_key_down(rl.KeyboardKey.KEY_A): move_dir -= 1.0
        if rl.is_key_down(rl.KeyboardKey.KEY_D): move_dir += 1.0
        
        h_move = rl.vector2_scale(rl.vector2_normalize(rl.Vector2(move_dir, 0)), self.speed * dt)

        # Jump
        if rl.is_key_pressed(rl.KeyboardKey.KEY_W) and self.is_grounded:
            self.velocity.y -= self.jump_impulse

        # Apply Velocity
        total_step = rl.vector2_add(h_move, rl.vector2_scale(self.velocity, dt))
        self.position = rl.vector2_add(self.position, total_step)

    def resolve_collisions(self, obstacles: list[Obstacle]):
        mtv_final = rl.Vector2(0, 0)
        
        for obs in obstacles:
            mtv = Utils.get_aabb_mtv(self.rect, obs.rect)
            
            # Combine MTVs (simplification of the C logic)
            if abs(mtv.x) > abs(mtv_final.x): mtv_final.x = mtv.x
            if abs(mtv.y) > abs(mtv_final.y): mtv_final.y = mtv.y

            # Platform attachment
            obs.is_player_attached = (mtv.y < 0.0 and obs.speed > 0.0)

        self.position = rl.vector2_add(self.position, mtv_final)

        # Grounded and Damage logic
        if mtv_final.y < 0.0 and self.velocity.y > 0.0:
            impact_speed = rl.vector2_length(self.velocity)
            damage = max(0.0, impact_speed - MAX_SAFE_SPEED)
            self.health -= damage
            
            self.velocity = rl.Vector2(0, 0)
            self.is_grounded = True
        elif mtv_final.y > 0.0 and self.velocity.y < 0.0:
            self.velocity.y = 0.0
        else:
            # Note: This is a simple ground check; 
            # in a real game, you'd check if mtv.y was exactly 0 or just below
            if mtv_final.y == 0:
                self.is_grounded = False

    def draw(self):
        rl.draw_rectangle_rec(self.rect, rl.ORANGE)

class Game:
    def __init__(self):
        rl.set_config_flags(rl.ConfigFlags.FLAG_MSAA_4X_HINT)
        rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Platforms - Python OOP")
        rl.set_target_fps(60)

        self.camera = rl.Camera2D(
            rl.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
            rl.Vector2(0, 0), 0.0, 20.0
        )
        self.health_view = PLAYER_MAX_HEALTH
        self.load_level()

    def load_level(self):
        self.player = Player()
        self.obstacles = [
            # Ground
            Obstacle(rl.Rectangle(-20.0, 20.0, 40.0, 2.5)),
            # Left Wall
            Obstacle(rl.Rectangle(-20.0, -100.0, 2.5, 120.0)),
            # Left Stair
            Obstacle(rl.Rectangle(-17.5, 15.0, 2.5, 5.0)),
            # Right Wall
            Obstacle(rl.Rectangle(17.5, -100.0, 2.5, 120.0)),
        ]

        # Random Moving Platforms
        for i in range(10):
            y = 8.0 - i * 8.0
            x = random.uniform(-15.0, 5.0)
            speed = random.uniform(5.0, 9.0)
            self.obstacles.append(
                Obstacle(
                    rl.Rectangle(x, y, 10.0, 2.5),
                    rl.Vector2(5.0, y), # End X
                    speed
                )
            )

    def update(self):
        if rl.is_key_pressed(rl.KeyboardKey.KEY_R):
            self.load_level()

        dt = rl.get_frame_time()

        self.player.update(dt)
        for obs in self.obstacles:
            obs.update(dt, self.player)
        
        self.player.resolve_collisions(self.obstacles)
        self.update_camera(dt)

    def update_camera(self, dt):
        target = self.player.position
        dist = rl.vector2_distance(target, self.camera.target)
        direction = rl.vector2_normalize(rl.vector2_subtract(target, self.camera.target))
        self.camera.target = rl.vector2_add(self.camera.target, rl.vector2_scale(direction, 0.1 * dist))

    def draw_ui(self):
        dt = rl.get_frame_time()
        margin, pad = 10.0, 5.0
        
        # Animate health shadow
        if self.player.health < self.health_view:
            self.health_view -= 80.0 * dt
            if self.health_view < self.player.health: self.health_view = self.player.health
        else:
            self.health_view = self.player.health

        bg_rect = rl.Rectangle(margin, margin, 300, 40)
        rl.draw_rectangle_rounded(bg_rect, 0.2, 16, UI_BG_COLOR)

        # Difference Bar (White shadow)
        diff_width = (300 - 2 * pad) * (self.health_view / PLAYER_MAX_HEALTH)
        rl.draw_rectangle_rounded(rl.Rectangle(margin+pad, margin+pad, 
                                               diff_width, 30), 0.2, 16, rl.WHITE)

        # Actual Health Bar
        health_ratio = self.player.health / PLAYER_MAX_HEALTH
        bar_width = (300 - 2 * pad) * health_ratio
        color = Utils.lerp_color(rl.RED, rl.GREEN, health_ratio)
        rl.draw_rectangle_rounded(rl.Rectangle(margin+pad, margin+pad, bar_width, 30), 0.2, 16, color)

    def run(self):
        while not rl.window_should_close():
            self.update()
            
            rl.begin_drawing()
            rl.clear_background(BACKGROUND_COLOR)
            
            rl.begin_mode_2d(self.camera)
            self.player.draw()
            for obs in self.obstacles:
                obs.draw()
            rl.end_mode_2d()

            self.draw_ui()
            rl.end_drawing()
        rl.close_window()

if __name__ == "__main__":
    game = Game()
    game.run()