from scripts.constants import *
from scripts.gamestates import *

class Game():
    def __init__(self):
        pygame.init()

        info = pygame.display.Info()

        self.WINDOW_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT) # scaled up window size

        self.display_flags = pygame.FULLSCREEN

        self.display_screen = pygame.display.set_mode(self.WINDOW_SIZE, self.display_flags)
        # display screen - mathces user device display size

        SCALE_RATIO = 40
        self.screen = pygame.Surface((16 * SCALE_RATIO, 9 * SCALE_RATIO)) # (640, 360)

        self.clock = pygame.time.Clock()

        pygame.display.set_caption("NEA prototype")

    def toggle_screen(self):
        self.display_flags ^= pygame.FULLSCREEN
        self.display_screen = pygame.display.set_mode(self.WINDOW_SIZE, self.display_flags)

    def run_game(self):
        state1 = Gameplay(self)
        state1.run_state()
#
# git init
# git remote add origin https://github.com/eeuropium/bunny_game.git
# git add .
# git commit -m "commit 1"
# git push --set-upstream origin master



def run_game():
    game = Game()
    game.run_game()
