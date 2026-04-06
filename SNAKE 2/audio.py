import os

from pyray import *
from settings import *

BASE = os.path.join(os.path.dirname(__file__), "Game_Assets")
MUSIC_DIR = os.path.join(BASE, "bg_music")
SFX_DIR = os.path.join(BASE, "sfx")

GAMEPLAY_TRACK = {
    Mode.CLASSIC: "classic",
    Mode.TIME_ATTACK: "attack",
    Mode.SURVIVAL: "survival",
}

SFX_FILE = {
    FoodType.NORMAL: "hit-01.wav",
    FoodType.GOLDEN: "hit-02.wav",
    FoodType.POISON: "hit-03.wav",
    FoodType.MOVING: "hit-04.wav",
}


class AudioManager:
    def __init__(self):
        self._music = {}
        self._sfx = {}
        self._current = None
        self._loaded = False

    def load(self):
        init_audio_device()
        self._music = {
            "menu": load_music_stream(os.path.join(MUSIC_DIR, "menu.mp3")),
            "classic": load_music_stream(os.path.join(MUSIC_DIR, "classic.mp3")),
            "attack": load_music_stream(os.path.join(MUSIC_DIR, "attack.mp3")),
            "survival": load_music_stream(os.path.join(MUSIC_DIR, "survival.mp3")),
        }
        self._sfx = {
            ft: load_sound(os.path.join(SFX_DIR, fname))
            for ft, fname in SFX_FILE.items()
        }
        self._loaded = True

    def unload(self):
        if not self._loaded:
            return
        for music in self._music.values():
            unload_music_stream(music)
        for sound in self._sfx.values():
            unload_sound(sound)
        close_audio_device()
        self._loaded = False

    def update(self, screen, mode):
        track = "menu" if screen != Screen.GAMEPLAY else GAMEPLAY_TRACK[mode]
        if track != self._current:
            if self._current is not None:
                stop_music_stream(self._music[self._current])
            self._current = track
            play_music_stream(self._music[track])
        update_music_stream(self._music[track])

    def play_hit(self, food_type):
        play_sound(self._sfx[food_type])
