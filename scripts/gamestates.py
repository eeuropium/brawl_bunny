from scripts.constants import *
from scripts.core_funcs import *
from scripts.managers import *

# Selection
from scripts.selection import *

# Gameplay
from scripts.entity import *
from scripts.map import Map
from scripts.camera import Camera
from scripts.shader import Shader
from scripts.client import Client

class GameState():
    def __init__(self, game):
        self.game = game

        self.screen = pygame.Surface((WIDTH, HEIGHT)) # render screen (smaller scaled)

        self.last_time = time.time()

        self.background_colour = BLACK #default background colour

        self.run = True

        self.client = Client()
        self.client.run_receive()

    def process():
        pass

    def run_state(self):
        self.shader = Shader()

        while self.run:
            ''' fill screen with background colour '''
            self.screen.fill(self.background_colour)

            ''' dt calculations '''
            self.dt = time.time() - self.last_time
            self.dt *= FPS # scale up dt to make more sense - now values are in terms of 1 FPS
            # if you want to test lower FPS, keep this at 60 (intended FPS)

            self.last_time = time.time()

            ''' get inputs '''
            # convert mouse_pos from tuple to vector2
            self.mouse_pos = pygame.mouse.get_pos()
            self.mouse_pos = pygame.math.Vector2(self.mouse_pos)

            # scale to match coordinates to render size
            self.mouse_pos.x = round(self.mouse_pos.x * WIDTH / DISPLAY_WIDTH)
            self.mouse_pos.y = round(self.mouse_pos.y * HEIGHT / DISPLAY_HEIGHT)

            # self.mouse_pos.x = round(self.mouse_pos.x * WIDTH / pygame.display.Info().current_h)
            # self.mouse_pos.y = round(self.mouse_pos.y * HEIGHT / pygame.display.Info().current_w)

            # place all inputs into a dictionary for better scalability (if new inputs need to be added itf)
            self.inputs = {}
            self.inputs["dt"] = self.dt
            self.inputs["keys"] = pygame.key.get_pressed()
            self.inputs["events"] = pygame.event.get()
            self.inputs["mouse_pos"] = self.mouse_pos

            ''' handle quitting '''

            if self.inputs["keys"][pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            for event in self.inputs["events"]:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_EQUALS:
                        self.game.toggle_screen()

            # changed for each unique state
            self.process()

            ''' display and updates '''
            self.shader.apply_shader(self.screen)

            # shader now scales and displays the surface so this is not needed
            # self.game.display_screen.blit(pygame.transform.scale(self.screen, self.game.display_screen.get_size()), (0, 0))

            pygame.display.flip()

            self.shader.release_memory()

            self.game.clock.tick(FPS)

class Menu(GameState):
    def __init__(self, game):
        super().__init__(game)

        # set background colour
        self.background_colour = (48, 44, 46)

        # define coordinate constants
        self.FLAG_X_OFFSET = 100
        self.FLAG_Y = 125

        # load flag images
        self.blue_flag = Animation("gamestates/menu/blue_flag.png", 71, 72, 0.7)
        self.red_flag = Animation("gamestates/menu/red_flag.png", 71, 72, 0.7)

        # load title image
        self.title_image = load_image("gamestates/menu/title.png")

        # buttons
        self.play_button = Button("FONT_15", "Start", (MID_X, 120))

    def process(self):
        # display flags
        display_center(self.screen, self.blue_flag.get_frame(), (MID_X - self.FLAG_X_OFFSET, self.FLAG_Y))
        display_center(self.screen, self.red_flag.get_frame(), (MID_X + self.FLAG_X_OFFSET, self.FLAG_Y))

        # display title "Brawl Bunny"
        display_center(self.screen, self.title_image, (MID_X, 50))

        # display menu text
        self.play_button.display(self.screen, self.inputs["mouse_pos"])

        # check for mouse click to move to next state
        if self.play_button.is_clicked(self.inputs["events"], self.inputs["mouse_pos"]):
            self.run = False

class WaitingScreen(GameState):
    def __init__(self, game):
        super().__init__(game)

        # set background colour
        self.background_colour = (48, 44, 46)

        # define coordinate constants
        self.BUTTON_Y = 15
        self.LEFT_MID_X = MID_X // 2
        self.RIGHT_MID_X = MID_X + MID_X // 2

        # # load table images
        # self.vanquish_table = load_image("gamestates/mode_selection/vanquish_table.png")

        # buttons
        # self.login_button = Button("FONT_10", "Log In", (220, self.BUTTON_Y))
        # self.signup_button = Button("FONT_10", "Sign Up", (280, self.BUTTON_Y))

        self.total_players = 4
        self.players_connected = 0

        self.connected = False
        self.player_number_determined = False

        self.players_connected_text = Text("FONT_15", (238, 160, 96), f"{self.players_connected}/{self.total_players}", (MID_X, MID_Y))

        # print(self.client)

    def process(self):
        # display tables
        # display_center(self.screen, self.vanquish_table, (self.LEFT_MID_X, 110))

        # display buttons
        # self.login_button.display(self.screen, self.inputs["mouse_pos"])
        # self.signup_button.display(self.screen, self.inputs["mouse_pos"])

        # center_draw_rect(self.screen, (57, 71, 120), (MID_X, MID_Y + 20, 100, 120), border_radius = 10)
        # center_draw_rect(self.screen, (57, 120, 168), (MID_X, MID_Y + 20, 80, 100), border_radius = 10)

        if not self.connected:
            self.client.send("1") # request to connect to server

        # if not self.player_number_determined:
        #     print(self.client.get_message())


        self.players_connected_text.display(self.screen, f"{self.players_connected}/{self.total_players}")


class CharacterSelection(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = (207, 198, 184)

        self.cards = Cards(["orb_bunny", "nature_bunny", "angel_bunny", "shadow_bunny"])

    def process(self):
        ''' update '''
        self.cards.update(self.inputs)

        ''' display '''
        self.cards.display(self.screen)
        pygame.draw.circle(self.screen, WHITE, self.inputs["mouse_pos"], 2)


class Gameplay(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = WATER_BLUE

        self.map = Map("map2.json")
        self.camera = Camera(self.map.map_surf)

        self.player = ShadowBunny()

    def process(self):
        ''' initialise '''
        self.camera.clear_visible_sprites()
        map_obj_collision_boxes =  self.map.get_neighbouring_chunk_data(self.player.x, self.player.y, "map_obj_collision_boxes")
        objects = self.map.get_neighbouring_chunk_data(self.player.x, self.player.y, "objects")

        ''' updates '''
        self.player.update(self.inputs, map_obj_collision_boxes)

        self.camera.add_visible_sprite(self.player)

        self.camera.add_visible_sprites(objects)

        ''' display '''
        self.camera.display_sprites(self.screen, int(self.player.x + 16), int(self.player.y + 16))

class TestMap(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = WATER_BLUE

        self.map = Map("map2.json")


    def process(self):
        display_center(self.screen, self.map.map_surf, (MID_X, MID_Y))
