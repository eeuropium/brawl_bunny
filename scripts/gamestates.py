from scripts.constants import *
from scripts.core_funcs import *
from scripts.entity import *
from scripts.map import Map
from scripts.camera import Camera

class GameState():
    def __init__(self, game):
        self.game = game

        self.screen = pygame.Surface((WIDTH, HEIGHT)) # render screen (smaller scaled)

        self.last_time = time.time()

        self.background_colour = BLACK #default background colour

        self.run = True

    def process():
        pass

    def run_state(self):

        while self.run:
            ''' fill screen with background colour '''
            self.screen.fill(self.background_colour)

            ''' dt calculations '''
            self.dt = time.time() - self.last_time
            self.dt *= FPS # scale up dt to make more sense - now values are in terms of 1 FPS
            # if you want to test lower FPS, keep this at 60 (intended FPS)

            self.last_time = time.time()

            ''' get inputs '''
            self.events = pygame.event.get()
            self.keys = pygame.key.get_pressed()

            # convert mouse_pos from tuple to vector2
            self.mouse_pos = pygame.mouse.get_pos()
            self.mouse_pos = pygame.math.Vector2(self.mouse_pos)

            # scale to match coordinates to render size
            self.mouse_pos.x = round(self.mouse_pos.x * WIDTH / DISPLAY_WIDTH)
            self.mouse_pos.y = round(self.mouse_pos.y * HEIGHT / DISPLAY_HEIGHT)

            ''' handle quitting '''

            if self.keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            for event in self.events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_EQUALS:
                        self.game.toggle_screen()

            # changed for each unique state
            self.process()

            ''' display and updates '''

            # display scaled up screen on user screen
            self.game.display_screen.blit(pygame.transform.scale(self.screen, self.game.display_screen.get_size()), (0, 0))

            pygame.display.update()
            self.game.clock.tick(FPS)


class Gameplay(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = WATER_BLUE

        self.map = Map("map2.json")
        self.camera = Camera(self.map.map_surf)

        self.player = OrbBunny()

    def process(self):
        ''' initialise '''
        self.camera.clear_visible_sprites()
        collision_boxes =  self.map.get_neighbouring_chunk_data(self.player.x, self.player.y, "collision_boxes")
        objects = self.map.get_neighbouring_chunk_data(self.player.x, self.player.y, "objects")

        ''' updates '''
        self.player.update(self.keys, self.mouse_pos, collision_boxes, self.dt)

        self.camera.add_visible_sprite(self.player)

        self.camera.add_visible_sprites(objects)

        ''' display '''
        self.camera.display_sprites(self.screen, int(self.player.x), int(self.player.y))

class TestMap(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = WATER_BLUE

        self.map = Map("map2.json")


    def process(self):
        display_center(self.screen, self.map.map_surf, (MID_X, MID_Y))
