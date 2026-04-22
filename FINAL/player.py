from pyray import *

GRAVITY = 0.5
JUMP_FORCE = -10
MOVE_SPEED = 3

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 32

        self.vel_x = 0
        self.vel_y = 0

        self.on_ground = False

    def get_rect(self):
        return Rectangle(self.x, self.y, self.width, self.height)

    def update(self, level):
        # Horizontal movement
        self.vel_x = 0
        if is_key_down(KEY_RIGHT):
            self.vel_x = MOVE_SPEED
        if is_key_down(KEY_LEFT):
            self.vel_x = -MOVE_SPEED

        # Jump
        if is_key_pressed(KEY_SPACE) and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Apply gravity
        self.vel_y += GRAVITY

        # Horizontal collision
        self.x += self.vel_x
        self.handle_collisions(level, horizontal=True)

        # Vertical collision
        self.y += self.vel_y
        self.handle_collisions(level, horizontal=False)

    def handle_collisions(self, level, horizontal):
        player_rect = self.get_rect()

        for tile_rect in level.get_solid_tiles():
            if check_collision_recs(player_rect, tile_rect):
                if horizontal:
                    if self.vel_x > 0:
                        self.x = tile_rect.x - self.width
                    elif self.vel_x < 0:
                        self.x = tile_rect.x + tile_rect.width
                else:
                    if self.vel_y > 0:
                        self.y = tile_rect.y - self.height
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.y = tile_rect.y + tile_rect.height
                        self.vel_y = 0

                player_rect = self.get_rect()

    def draw(self):
        draw_rectangle(int(self.x), int(self.y), self.width, self.height, BLUE)