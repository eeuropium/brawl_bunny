from scripts.constants import *
from scripts.gamestates import *
from scripts.client import Client

class Game():
    def __init__(self):
        pygame.init()

        # window size
        info = pygame.display.Info()

        self.WINDOW_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT) # scaled up window size

        # display flags
        # set display flags - FULLSCREEN to allow toggling between fullscreen and OPENFL and DOUBLEBUF for shaders
        # self.display_flags = pygame.FULLSCREEN | pygame.OPENGL | pygame.DOUBLEBUF # fullscreen at the start
        self.display_flags = pygame.OPENGL | pygame.DOUBLEBUF

        # to enable shader version https://stackoverflow.com/questions/76151435/creating-a-context-utilizing-moderngl-for-pygame
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        # set up display screen (final one)
        self.display_screen = pygame.display.set_mode(self.WINDOW_SIZE, self.display_flags)
        # display screen - mathces user device display size

        self.screen = pygame.Surface((WIDTH, HEIGHT)) # 320, 180

        # clock
        self.clock = pygame.time.Clock()

        # set title
        pygame.display.set_caption("Brawl Bunny")

        # set icon image
        icon_image = load_image("icon/icon.png")
        icon_image = pygame.transform.scale_by(icon_image, 10) # scale icon image to reduce bilinear interpolation effects
        pygame.display.set_icon(icon_image)

        # client
        self.client = Client()
        self.client.run_receive()

        self.player_number = None

    def toggle_screen(self):
        self.display_flags ^= pygame.FULLSCREEN # XOR to change pygame.FULLSCREEN to NOT pygame.FULLSCREEN
        self.display_screen = pygame.display.set_mode(self.WINDOW_SIZE, self.display_flags)

    def run_game(self):

        # order of the gamestates being run
        while True:
            if not TESTING: # only run menu state if testing
                menu = Menu(self)
                menu.run_state()

            matchmaking = MatchMaking(self)
            matchmaking.run_state()

            character_selection = CharacterSelection(self)
            character_selection.run_state()

            gameplay = Gameplay(self)
            gameplay.run_state()

            end_screen = EndScreen(self)
            end_screen.run_state()


def run_game():
    game = Game()
    game.run_game()
