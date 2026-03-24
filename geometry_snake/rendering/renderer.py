from pyray import *


class Renderer:
    def __init__(self, player, trail, obstacles, camera, parallax):
        self.player = player
        self.trail = trail
        self.obstacles = obstacles
        self.camera = camera
        self.parallax = parallax

    def draw(self):
        # 1. Parallax fills the background in screen space (no camera transform)
        self.parallax.draw(self.camera.scroll_x)

        # 2. World objects drawn under the camera transform
        self.camera.begin()
        self._draw_trail()
        self._draw_player()
        self._draw_obstacles()
        self.camera.end()

    def _draw_player(self):
        draw_circle(int(self.player.pos.x), int(self.player.pos.y), 6, WHITE)

    def _draw_trail(self):
        for point in self.trail.points:
            draw_circle(int(point.x), int(point.y), 3, GRAY)

    def _draw_obstacles(self):
        for obs in self.obstacles:
            draw_rectangle(obs.x, obs.y, obs.w, obs.h, RED)
