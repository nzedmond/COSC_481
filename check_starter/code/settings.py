from pyray import *
from random import randint, uniform
from pathlib import Path

from os.path import join

## Assets provided by
# https://o-lobster.itch.io/platformmetroidvania-pixel-art-asset-pack
# other dataset site

THIS_DIR = Path(__file__).resolve().parent

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60

SHEET = str(THIS_DIR/"hero-sheet.png")

SPRITE_SHEET_TILE_SIZE = 16
PLAYER_SIZE = 100
GROUND_Y = Rectangle(0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 50)

