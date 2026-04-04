from pyray import *


class SpriteAnimator:
    """Animates a single-row spritesheet by stepping through frames each tick."""

    def __init__(self, texture, num_frames, fps=8):
        self._texture = texture
        self._num_frames = num_frames
        self._fps = fps
        self._frame = 0
        self._counter = 0
        frame_w = float(texture.width) / num_frames
        self._frame_rec = Rectangle(0.0, 0.0, frame_w, float(texture.height))

    def update(self):
        self._counter += 1
        if self._counter >= 60 / self._fps:
            self._counter = 0
            self._frame = (self._frame + 1) % self._num_frames
            self._frame_rec.x = self._frame * (float(self._texture.width) / self._num_frames)

    def draw(self, position, size):
        """Draw the current frame scaled to fit size x size pixels."""
        dest = Rectangle(float(position.x), float(position.y), float(size), float(size))
        draw_texture_pro(self._texture, self._frame_rec, dest, Vector2(0.0, 0.0), 0.0, WHITE)
