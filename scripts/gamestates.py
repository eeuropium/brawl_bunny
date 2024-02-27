from scripts.constants import *
from scripts.core_funcs import *
from scripts.managers import *

# Selection
from scripts.selection import *

# Gameplay
from scripts.entity import *
from scripts.map import Map
from scripts.camera import *
from scripts.shader import Shader
from scripts.client import Client

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

            ''' networking state prefixes '''
            self.state_prefix = STATE_PREFIX_MAP[self.__class__.__name__]

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

class MatchMaking(GameState):
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

        self.player_number_determined = False

        self.players_connected_text = Text("FONT_15", (238, 160, 96), f"{self.players_connected}/{self.total_players}", (MID_X, MID_Y))

        self.end_timer = Timer()

    def process(self):
        # display tables
        # display_center(self.screen, self.vanquish_table, (self.LEFT_MID_X, 110))

        # display buttons
        # self.login_button.display(self.screen, self.inputs["mouse_pos"])
        # self.signup_button.display(self.screen, self.inputs["mouse_pos"])

        # center_draw_rect(self.screen, (57, 71, 120), (MID_X, MID_Y + 20, 100, 120), border_radius = 10)
        # center_draw_rect(self.screen, (57, 120, 168), (MID_X, MID_Y + 20, 80, 100), border_radius = 10)

        if not self.player_number_determined:
            # send mac address to server to establish connection
            self.game.client.send(self.state_prefix, str(self.game.client.mac_address))
        else:
            # send confirmation to server signalling ok to move on to next state (since player number determined)
            self.game.client.send(self.state_prefix, f"OK:{self.game.player_number}")

        # receive message
        message = self.game.client.get_message()

        # server has non-empty message and same state prefix
        if message and message[0] == self.state_prefix:
            # get data of all clients from server
            client_data = message[1:].split(',')

            # check how many players are already connected
            self.players_connected = len(client_data)

            for data in client_data:
                mac_address, player_number = list(map(int, data.split(":")))

                # server has assigned mac_address to a player number, player number obtained (on client)
                if mac_address == self.game.client.get_mac_address():
                    self.game.player_number = player_number
                    self.player_number_determined = True

            # all players joined, move on to next state
            if self.players_connected == self.total_players:
                self.end_timer.start()

        # 2 seconds to move on to next state after all players connected
        if self.end_timer.is_active() and self.end_timer.time_elapsed() >= 2:
            self.run = False

        # display text
        self.players_connected_text.display(self.screen, f"{self.players_connected}/{self.total_players}")


class CharacterSelection(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = (207, 198, 184)

        self.cards = Cards(["orb_bunny", "nature_bunny", "angel_bunny", "shadow_bunny"])

    def process(self):

        # send message to server
        self.game.client.send(self.state_prefix, self.cards.get_message_to_send(self.inputs, self.game.player_number))

        ''' update '''
        message = self.game.client.get_message()

        # update with message from server
        if message and message[0] == self.state_prefix:
            self.cards.update(message[1:], self.game.player_number)

        if self.cards.move_next_state():
            self.run = False

        ''' display '''
        self.cards.display(self.screen)

        # mouse debug
        pygame.draw.circle(self.screen, WHITE, self.inputs["mouse_pos"], 2)

class Gameplay(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = WATER_BLUE

        self.map = Map("map2.json")
        self.camera = Camera(self.map.map_surf)

        self.frame_image_map = self.init_animation_images()

        # camera middle coordinates (to determine offsets)
        self.camera_x, self.camera_y = MID_X, MID_Y # updated in update_display

        # if the shadow bunny is visible on the previous frame
        # this helps us know when to add smoke particles (which are processed locally due to the huge data volume)
        self.prev_shadow_bunny_visible = True

        self.respawn_text = Text("FONT_15", (48, 44, 46), "", (MID_X, MID_Y))
        self.respawn_time_left = -1

    # construct a string representing the client inputs. This is sent to the server
    def get_control_inputs_string(self):
        s = f"{self.game.player_number}:"

        # add mouse coor inputs
        s += str(self.inputs["mouse_pos"])

        mouse_pressed = False
        mouse_up = False

        for event in self.inputs["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_up = True

        # add mouse pressed input
        s += str(int(mouse_pressed)) # 0 or 1 for no click or click
        s += str(int(mouse_up)) # 0 or 1 for no mouse up or mouse up

        # add keyboard pressed down inputs
        for key_character in KEY_ORDERS:
            s += str(int(self.inputs["keys"][eval(f"pygame.K_{key_character.lower()}")]))

        return s

    # construct map of images
    def init_animation_images(self):
        frame_image_map = {}

        ''' General init for all bunnies ''' # idle and run states only

        bunny_names = ["orb_bunny", "nature_bunny", "angel_bunny", "shadow_bunny"]
        character_states = ["idle", "run"]

        for bunny_name in bunny_names:
            frame_image_map[bunny_name] = {}
            for character_state in character_states:
                frames = load_spritesheet(load_image(f"bunny/{bunny_name}/{bunny_name}_{character_state}.png"), 32, 32)
                frame_image_map[bunny_name][character_state] = frames

        ''' Character specific inits '''

        # orb bunny
        frame_image_map["orb_bunny"]["hand"] = load_spritesheet(load_image(f"bunny/orb_bunny/orb_bunny_hands.png"), 32, 32)

        # angel bunny
        frame_image_map["angel_bunny"]["idle_hands"] = load_spritesheet(load_image(f"bunny/angel_bunny/angel_bunny_idle_hands.png"), 32, 32)
        frame_image_map["angel_bunny"]["run_hands"] = load_spritesheet(load_image(f"bunny/angel_bunny/angel_bunny_run_hands.png"), 32, 32)
        frame_image_map["angel_bunny"]["charge_hands"] = load_spritesheet(load_image(f"bunny/angel_bunny/angel_bunny_charge_hands.png"), 32, 32)
        frame_image_map["angel_bunny"]["release_hands"] = load_spritesheet(load_image(f"bunny/angel_bunny/angel_bunny_release_hands.png"), 32, 32)

        # shadow bunny
        frame_image_map["shadow_bunny"]["sword"] = load_spritesheet(load_image(f"bunny/shadow_bunny/shadow_bunny_sword.png"), 64, 32)


        return frame_image_map

    def get_frame_y_offset(self, character_name, character_state, frame_index):
        # idle state has no offset
        if character_state == "idle":
            return 0

        return RUN_Y_OFFSET[character_name][frame_index]

    def process_base_message(self, player_number, character_name, x_coor, y_coor, character_state, frame_index, flip_sprite, health, ability_charge, extra_info):
        # set position of camera to player's coordinate
        if player_number == self.game.player_number:
            self.camera_x, self.camera_y = x_coor, y_coor

        # get the display image from our map
        image = self.frame_image_map[character_name][character_state][frame_index]

        # flip image if needed
        if flip_sprite:
            image = pygame.transform.flip(image, True, False)

        # pass the image into a sprite object so camera can call the object's "display" method
        sprite_object = SimpleSprite(image, (x_coor, y_coor), display_mode = "center")

        # special check as if shadow bunny is in shadow_realm, it should not be added to the camera                         # check if character is alive
        if not(character_name == "shadow_bunny" and player_number != self.game.player_number and bool(int(extra_info[2]))) and health > 0:
            # add object to camera sprites
            self.camera.add_visible_sprite(sprite_object)

        # respawn management
        if player_number == self.game.player_number:
            # in this case health represents negative of the time left till respawn
            if health < 0:
                self.respawn_time_left = -health
            else:
                self.respawn_time_left = -1 # value indicates player is alive and not currently respawning

        ''' Bars '''
        class Bar():
            def __init__(self, percentage_complete, coor, colour, y_offset):
                self.BAR_WIDTH = 20
                self.BAR_HEIGHT = 3

                self.percent = percentage_complete

                self.x, self.y = coor

                self.colour = colour
                self.y_offset = y_offset

            def display(self, screen, offset_x, offset_y):
                top_left_x, top_left_y = int(self.x - self.BAR_WIDTH // 2) + offset_x, int(self.y - self.y_offset - self.BAR_HEIGHT // 2) + offset_y

                # outer border outline
                pygame.draw.rect(screen, (94, 54, 67), (top_left_x - 1, top_left_y - 1, self.BAR_WIDTH + 2, self.BAR_HEIGHT + 2))

                # brown bar indicating full bar
                pygame.draw.rect(screen, (122, 68, 74), (top_left_x, top_left_y, self.BAR_WIDTH, self.BAR_HEIGHT))

                # blue / red bar indicating bar left
                pygame.draw.rect(screen, self.colour, (top_left_x, top_left_y, self.BAR_WIDTH * self.percent, self.BAR_HEIGHT))

            def get_bottom_y(self):
                return self.y

        class HealthBar(Bar):
            def __init__(self, health, total_health, coor, colour):
                percent = health / total_health

                # if there is health, there should be at least one pixel to indicate the health
                if health > 0:
                    percent = max(percent, 1/20) # since bar width is 20, our percent is 1/20

                super().__init__(percent, coor, colour, 20) # y_offset is 20

        class AbilityBar(Bar):
            def __init__(self, ability_charge, total_ability_charge, coor):
                super().__init__(ability_charge / total_ability_charge, coor, (244, 179, 27), 27) # y_offset is 20

        # show health bar for all players
        # special check as health bar should not be shown if shadow bunny is in shadow realm                                # check if alive
        if not(character_name == "shadow_bunny" and player_number != self.game.player_number and bool(int(extra_info[2]))) and health > 0:
            health_bar = HealthBar(health, BUNNY_STATS[character_name]["health"], (x_coor, y_coor), get_player_colour(player_number, self.game.player_number))
            self.camera.add_visible_sprite(health_bar)

        # show abiltiy bar only for YOUR player
        if player_number == self.game.player_number:
            ability_bar = AbilityBar(ability_charge, BUNNY_STATS[character_name]["total_ability_charge"], (x_coor, y_coor))
            self.camera.add_visible_sprite(ability_bar)

    def process_extra_message(self, player_number, character_name, x_coor, y_coor, character_state, frame_index, flip_sprite, health, ability_charge, extra_info):

        if health <= 0: # don't need to display anything since character is dead
            return

        # commonly used variables
        x_direction = (-1 if flip_sprite else 1)
        y_offset = self.get_frame_y_offset(character_name, character_state, frame_index)

        if character_name == "orb_bunny":
            ''' Hand '''
            hand_frame_index = extra_info[0]

            # convert to integer
            hand_frame_index = int(hand_frame_index)

            # get hand image
            hand_image = self.frame_image_map["orb_bunny"]["hand"][hand_frame_index]

            # flip hand image if needed
            if flip_sprite:
                hand_image = pygame.transform.flip(hand_image, True, False)

            # make hand image into a sprite and add to camera
            hand_sprite = SimpleSprite(hand_image, (x_coor + 4 * x_direction, y_coor + 5 - y_offset), display_mode = "center")

            self.camera.add_visible_sprite(hand_sprite)


            ''' Orbs '''
            orbs_info = extra_info[1:]

            # add orbs to camera
            for i in range(0, 5 * 3, 3):
                x, y, radius = int(orbs_info[i]), int(orbs_info[i+1]), float(orbs_info[i+2])

                orb = Circle((138, 236, 241), (x, y), radius)
                self.camera.add_visible_sprite(orb)

                self.shader.shader_data["orbs_data"].append((x + MID_X - self.camera_x, y + MID_Y - self.camera_y, radius + 3)) # glow radius is 10



        elif character_name == "nature_bunny":
            p0, p1, pl, pr = [pygame.math.Vector2() for i in range(4)]

            p0.x, p0.y, p1.x, p1.y, pl.x, pl.y, pr.x, pr.y = list(map(int, extra_info))

            class Vine():
                def __init__(self, p0, p1, p2, bottom_y):
                    DIVISIONS = 100
                    self.points = []

                    for i in range(0, DIVISIONS):
                        t = i / DIVISIONS # t value between 0 and 1
                        self.points.append(p0 * (1 - t) * (1 - t) + 2 * t * (1 - t) * p1 + t * t * p2)

                    self.bottom_y = bottom_y

                def display(self, screen, offset_x, offset_y):
                    render_points = [(p.x + offset_x, p.y + offset_y) for p in self.points]

                    pygame.draw.lines(screen, (57, 120, 168), False, render_points, width = 5)

                def get_bottom_y(self):
                    return self.bottom_y - 1

            # add left vine object
            self.camera.add_visible_sprite(Vine(p0, p1, pl, y_coor))

            # add right vine object
            self.camera.add_visible_sprite(Vine(p0, p1, pr, y_coor))

        elif character_name == "angel_bunny":
            hand_prefix, hand_frame_index, orb_x, orb_y, orb_radius = extra_info

            # convert data types
            hand_frame_index = int(hand_frame_index)
            orb_x = int(orb_x)
            orb_y = int(orb_y)
            orb_radius = float(orb_radius)

            ''' Hand '''
            hand_state = PREFIX_ANGEL_BUNNY_HAND_STATE_MAP[hand_prefix]

            # get hand_image
            hand_image = self.frame_image_map["angel_bunny"][f"{hand_state}_hands"][hand_frame_index]

            # flip hand image if needed
            if flip_sprite:
                hand_image = pygame.transform.flip(hand_image, True, False)

            # running animation already incorporated y-offset in the art
            # if hand_state == "run":
            #     y_offset = 0

            # make hand image into a sprite and add to camera
            hand_sprite = SimpleSprite(hand_image, (x_coor + 0 * x_direction, y_coor - y_offset), y_offset = 3, display_mode = "center")

            self.camera.add_visible_sprite(hand_sprite)

            ''' Orb '''
            # if orb_radius > 0:
                # orb = Circle((244, 179, 27), (orb_x, orb_y), orb_radius, y_offset = orb_radius)

                # self.camera.add_visible_sprite(orb)

            self.shader.shader_data["light_orb"] = (orb_x + MID_X - self.camera_x, orb_y + MID_Y - self.camera_y, orb_radius)


        elif character_name == "shadow_bunny":
            sword_frame_index, visible, in_shadow_realm = extra_info

            # convert data types
            sword_frame_index = int(sword_frame_index)
            visible = bool(int(visible))
            in_shadow_realm = bool(int(in_shadow_realm))


            ''' Sword Animation '''
            # get sword image
            sword_image = self.frame_image_map["shadow_bunny"]["sword"][sword_frame_index]

            # flip sword image if needed
            if flip_sprite:
                sword_image = pygame.transform.flip(sword_image, True, False)

            # make sword image into a sprite and add to camera                                      # y_offset is more than character y so that sword displays in front of the character
            sword_sprite = SimpleSprite(sword_image, (x_coor + 16 * x_direction, y_coor - y_offset), y_offset = y_coor + 1, display_mode = "center")

            # display sword if attacking, even when using ability
            if player_number == self.game.player_number or visible:
                self.camera.add_visible_sprite(sword_sprite)

            ''' Shadow Realm shader ''' # for other players

            if player_number == self.game.player_number:
                self.shader.shader_data["use_shadow_realm_shader"] = in_shadow_realm



    def update_display(self, message):
        client_data = message.split("|")

        for data in client_data:
            player_number, data = data.split(":")

            character_prefix, x_coor, y_coor, character_state_prefix, frame_index, flip_sprite, health, ability_charge, *extra_info = data.split(",")

            # change to appropriate data types
            player_number = int(player_number)
            x_coor = int(x_coor)
            y_coor = int(y_coor)
            frame_index = int(frame_index)
            flip_sprite = bool(int(flip_sprite))
            health = int(health)
            ability_charge = int(ability_charge)

            # get full character name and state from prefixes
            character_name = PREFIX_NAME_MAP[character_prefix]
            character_state = PREFIX_CHARACTER_STATE_MAP[character_state_prefix] # eg: "R" corresponds to the "run" character state

            self.process_base_message(player_number, character_name, x_coor, y_coor, character_state, frame_index, flip_sprite, health, ability_charge, extra_info)

            self.process_extra_message(player_number, character_name, x_coor, y_coor, character_state, frame_index, flip_sprite, health, ability_charge, extra_info)

    def process(self):
        ''' initialise '''
        self.camera.clear_visible_sprites()

        # clear the list
        self.shader.shader_data["orbs_data"] = []

        ''' Sending to Server '''
        # sending input to server
        send_message = self.get_control_inputs_string()
        self.game.client.send(self.state_prefix, send_message)

        ''' Receiving from Server '''
        message = self.game.client.get_message()

        if message[0] != "G":
            return

        ''' Update '''
        # interpret server message and add player sprites to camera
        self.update_display(message[1:])
        objects = self.map.get_neighbouring_chunk_data(self.camera_x, self.camera_y, "objects")

        self.camera.add_visible_sprites(objects)

        self.shader.shader_data["orbs_data"].extend([(0.0, 0.0, 0.0) for i in range(20 - len(self.shader.shader_data["orbs_data"]))])

        ''' display '''
        self.camera.display_sprites(self.screen, self.camera_x, self.camera_y)

        if self.respawn_time_left != -1:
            self.respawn_text.display(self.screen, f"Respawning in: {self.respawn_time_left}")

class TestMap(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.background_colour = WATER_BLUE

        self.map = Map("map2.json")


    def process(self):
        display_center(self.screen, self.map.map_surf, (MID_X, MID_Y))
