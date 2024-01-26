from scripts.constants import *
from scripts.gamestates import *

class Game():
    def __init__(self):
        pygame.init()

        info = pygame.display.Info()

        self.WINDOW_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT) # scaled up window size

        # set display flags - FULLSCREEN to allow toggling between fullscreen and OPENFL and DOUBLEBUF for shaders
        self.display_flags = pygame.FULLSCREEN | pygame.OPENGL | pygame.DOUBLEBUF

        # to enable shader version https://stackoverflow.com/questions/76151435/creating-a-context-utilizing-moderngl-for-pygame
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        # set up display screen (final one)
        self.display_screen = pygame.display.set_mode(self.WINDOW_SIZE, self.display_flags)
        # display screen - mathces user device display size

        # SCALE_RATIO = 20
        self.screen = pygame.Surface((WIDTH, HEIGHT)) # 320, 180

        self.clock = pygame.time.Clock()

        pygame.display.set_caption("NEA prototype")

    def toggle_screen(self):
        self.display_flags ^= pygame.FULLSCREEN # XOR to change pygame.FULLSCREEN to NOT pygame.FULLSCREEN
        self.display_screen = pygame.display.set_mode(self.WINDOW_SIZE, self.display_flags)

    def run_game(self):
        state1 = Menu(self)
        state1.run_state()

        state2 = WaitingScreen(self)
        state2.run_state()

def run_game():
    game = Game()
    game.run_game()
