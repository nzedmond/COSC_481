from pyray import *
from config.settings import *
from core.input_manager import InputManager
from core.state import GameState
from entities.player import Player
from entities.trail import Trail
from entities.obstacle import Obstacle
from systems.collision_manager import CollisionManager
from rendering.renderer import Renderer

class Game:
    def __init__(self):
        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Geometry Snake")
        set_target_fps(FPS)
        
        self.state = GameState.PLAYING
        self.input = InputManager()
        self.reset()
        
    def reset(self):
        self.state = GameState.PLAYING
        self.player = Player()
        self.trail = Trail()
        
        self.obstacles = [
            Obstacle(400, 200, 40, 200),
            Obstacle(650, 0, 40, 300),
            Obstacle(900, 300, 40, 300),
        ]
        self.collision = CollisionManager(self.player, self.trail, self.obstacles)
        self.renderer = Renderer(self.player, self.trail, self.obstacles)
        
    def run(self):
        while not window_should_close():
            dt = get_frame_time()
            self.update(dt)
            self.render()
        close_window()
        
    def update(self, dt):
        if self.state == GameState.GAME_OVER:
            if is_key_pressed(KEY_R):
                self.reset()
            return
        
        holding = self.input.is_holding()
        self.player.apply_control(holding)
        self.player.update(dt)
        self.trail.update(self.player.pos)
        
        if self.collision.check_all():
            self.state = GameState.GAME_OVER
            
    def render(self):
        begin_drawing()
        clear_background(BLACK)
        
        self.renderer.draw()
        
        if self.state == GameState.GAME_OVER:
            draw_text("GAME_OVER - Press R to Restart", 180, 280, 20, RED)
        
        end_drawing()