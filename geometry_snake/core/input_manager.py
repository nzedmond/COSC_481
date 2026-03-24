from pyray import *

class InputManager:
    def is_holding(self):
        return is_key_down(KEY_SPACE) or is_mouse_button_down(MOUSE_LEFT_BUTTON)