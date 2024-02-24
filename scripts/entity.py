from scripts.constants import *
from scripts.core_funcs import *
from scripts.animation import *
from scripts.managers import *
from scripts.orbs import Orbs # for Orb Bunny

''' Character States '''

class CharacterState():
    def __init__(self, character):
        self.character = character

    def update(self):
        self.character.frame_index = self.animation.get_frame_index()

        # if self.character.x_direction == -1:
        #     self.character.image = pygame.transform.flip(self.character.image, True, False)

    def get_y_offsets(self):
        return None

class Idle(CharacterState):
    def __init__(self, character, animation_path):
        super().__init__(character)
        self.animation = Animation(animation_path, 32, 32)

    def determine_state(self):
        if self.character.direction.magnitude() != 0:
            self.character.change_state(self.character.run_state)

class Run(CharacterState):
    def __init__(self, character, animation_path):
        super().__init__(character)
        self.animation = Animation(animation_path, 32, 32)

    def determine_state(self):
        if self.character.direction.magnitude() == 0:
            self.character.change_state(self.character.idle_state)

    def set_y_offsets(self, y_offsets):
        self.y_offsets = y_offsets

    def get_y_offsets(self):
        if self.y_offsets:
            return self.y_offsets
        else:
            return None

    def update(self):
        super().update()

''' Hand State '''



''' Layer '''

class Layer():
    def __init__(self):
        pass

    def update(self, image, x_direction):
        self.image = image

        if x_direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def display(self, screen, display_x, display_y):
        screen.blit(self.image, (display_x, display_y))


class ChangingLayer(Layer):                                     # for when facing left and right
    def __init__(self, base_offset_x = 0, base_offset_y = 0, left_offset_x = 0, right_offset_x = 0):
        # constant values
        self.base_offset_x = base_offset_x
        self.base_offset_y = base_offset_y
        self.left_offset_x = left_offset_x
        self.right_offset_x = right_offset_x

        # depends on state
        self.y_offset = 0
        self.x_offset = 0

    def update(self, image, x_direction, state):
        super().update(image, x_direction)

        # calculate x offset
        self.x_offset = self.base_offset_x * x_direction + (x_direction == -1) * self.left_offset_x + (x_direction == 1) * self.right_offset_x

        # calculate y offset
        self.y_offset = self.base_offset_y

        y_offsets = state.get_y_offsets()

        if y_offsets:
            self.y_offset -= y_offsets[state.animation.get_frame_index()]

    def display(self, screen, display_x, display_y):
        screen.blit(self.image, (display_x + self.x_offset, display_y + self.y_offset))

''' Entities '''

class Bunny():
    def __init__(self, name):
        self.name = name

        ''' States '''
        # character (body)
        self.idle_state = Idle(self, f"bunny/{self.name}/{self.name}_idle.png")
        self.run_state = Run(self, f"bunny/{self.name}/{self.name}_run.png")

        self.state = self.idle_state

        # ''' Image '''
        # self.character_layer = Layer()


        ''' Movement '''
        self.SPEED = 1.5
        self.x = MID_X
        self.y = MID_Y
        self.direction = pygame.math.Vector2()
        self.x_direction = 1 # 1 for facing right, -1 for facing left

        ''' Hitbox '''
        self.collision_box_x_offset, self.collision_box_y_offset, hitbox_width, hitbox_height = get_box(f"box/collision_box/entities/{name}_collision_box.png")
        self.collision_box = pygame.FRect(MID_X, MID_Y, hitbox_width, hitbox_height) # placeholder for start_x, start_y

        ''' Networking '''
        self.frame_index = 0

    def change_state(self, state):
        self.state = state
        self.state.animation.reset()

    def change_hand_state(self, hand_state):
        self.hand_state = hand_state
        self.hand_state.animation.reset()

    # def update(self, client_message, map_obj_collision_boxes):
    def update(self, input_message, map_obj_collision_boxes):
        # give meaningful names to user message string
        self.controls = {}

        # "mouse_coor" - list containing two elements, x and y coordinates of mouse
        # "click" - 0 or 1 indiciating if mouse is clicked
        # "up" - W key pressed
        # "left" - A key pressed
        # "down" - S key pressed
        # "right" - D key pressed
        # "ability" - E key pressed

        mouse_coor, key_inputs = input_message.split("]")

        mouse_coor = list(map(int, mouse_coor[1:].split(", ")))
        mouse_coor = pygame.math.Vector2(mouse_coor)

        self.controls["mouse_pos"] = mouse_coor

        for index, key_function in enumerate(KEY_FUNCTIONS):
            self.controls[key_function] = bool(int(key_inputs[index]))

        ''' Movement '''
        # similar to legend of zelda youtube tutorial

        # update direction vector based on inputs
        if self.controls["left"]:
            self.direction.x = -1
        elif self.controls["right"]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if self.controls["up"]:
            self.direction.y = -1
        elif self.controls["down"]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # normalize so that speed is constant even when travelling diagonally
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize() * self.SPEED

        # update x coordinate
        self.collision_box.centerx += self.direction.x

        # handle collisions in the x axis
        for collision_box in map_obj_collision_boxes:
            if self.collision_box.colliderect(collision_box):
                if self.direction.x > 0: # moving right
                    self.collision_box.right = collision_box.left
                elif self.direction.x < 0: # moving left
                    self.collision_box.left = collision_box.right

        # update y coordinate
        self.collision_box.centery += self.direction.y

        # handle collisions in the y axis
        for collision_box in map_obj_collision_boxes:
            if self.collision_box.colliderect(collision_box):
                if self.direction.y > 0: # moving down
                    self.collision_box.bottom = collision_box.top
                elif self.direction.y < 0: # moving up
                    self.collision_box.top = collision_box.bottom

        # update positions for displaying character
        self.x = self.collision_box.left - self.collision_box_x_offset + 16
        self.y = self.collision_box.top - self.collision_box_y_offset + 16


        # determine animation direction with mouse position
        if self.controls["mouse_pos"].x < MID_X:
            self.x_direction = -1
        else:
            self.x_direction = 1

        ''' Animation '''

        # # check if have to change from current state to new state
        self.state.determine_state()

        # # updates image (frame index sent to client) and direction
        self.state.update()

    def get_server_send_message(self):
        character_prefix = NAME_PREFIX_MAP[self.name]

        character_state_prefix = CHARACTER_STATE_PREFIX_MAP[self.state.__class__.__name__.lower()]

        if self.x_direction == 1:
            flip_sprite = 0
        else:
            flip_sprite = 1

        #         (character type)        (coordinates)                  (state)           (frame number)  (horizontal flip)
        return f"{character_prefix},{int(self.x)},{int(self.y)},{character_state_prefix},{self.frame_index},{flip_sprite}"

    def get_display_coords(self, offset_x, offset_y):
        return (int(self.x) + offset_x, int(self.y) + offset_y)

    def display(self, screen, offset_x, offset_y):
        # calculate the display coordinates
        display_x, display_y = self.get_display_coords(offset_x, offset_y)

        # display character
        screen.blit(self.image, (display_x, display_y))

        # for box in self.debug:
        #     pygame.draw.rect(screen, (255, 0, 0), (box.left + offset_x, box.top + offset_y, box.width, box.height))

        # left, top, width, height = self.collision_box
        # left += offset_x
        # top += offset_y
        # pygame.draw.rect(screen, (0, 255, 0), (left, top, width, height))

    def get_bottom_y(self):
        return self.collision_box.bottom

class OrbBunny(Bunny):
    def __init__(self):
        super().__init__("orb_bunny")

        ''' Hand '''
        self.hand_sprites = load_spritesheet(load_image(f"bunny/{self.name}/{self.name}_hands.png"), 32, 32)
        self.hand_angles = [90, 60, 30, 0, -15, -45, -75, -90]

        self.hand_images = {}

        for index, angle in enumerate(self.hand_angles):
            self.hand_images[angle] = self.hand_sprites[index]

        # initialise starting hand frame index
        self.hand_frame_index = 3

        self.run_state.set_y_offsets([0, 1, 3, 1, 0, 1, 3, 1])

        ''' Orbs '''

        self.NUMBER_OF_ORBS = 5

        self.orbs = Orbs(self.NUMBER_OF_ORBS)
        self.orbs_list = [] # list storing position of orbs (includes attacking orb position)
        self.attack_orb_index = -1 # -1 if no orb is used in attack currently

        self.orb_targets = [None for i in range(self.NUMBER_OF_ORBS)]
        self.orb_timers = [Timer() for i in range(self.NUMBER_OF_ORBS)]

        self.attack_timer = Timer()
        self.TOTAL_ATTACK_TIME = 1.5

    def orb_ease(self, x):
        return -4 * (x - 0.5) * (x - 0.5) + 1

    def find_closest_angle(self, angle, available_angles):
        min_diff = 180 # initialise to greatest possible

        for curr_angle in available_angles:
            diff = abs(angle - curr_angle)

            if diff < min_diff:
                min_diff = diff
                closest_angle = curr_angle

        return closest_angle

    def update(self, inputs, map_obj_collision_boxes):
        super().update(inputs, map_obj_collision_boxes)

        ''' Hand '''
        # calculate angle in radians
        rotate_angle = math.atan2(MID_Y - self.controls["mouse_pos"].y, abs(self.controls["mouse_pos"].x - MID_X))
        # self.y - mouse_pos.y as the y-axis of pygame's coordinate system is different from cartesian system
        # abs makes sure that even when image is flipped we still get the correct angles

        # convert to degree
        rotate_angle = math.degrees(rotate_angle)

        # best angle calculations
        best_angle = self.find_closest_angle(rotate_angle, self.hand_angles)
        self.hand_frame_index = self.hand_angles.index(best_angle)

        # self.hand_layer.update(self.hand_images[best_angle], self.x_direction, self.state)

        ''' Orbs '''
        self.orbs.rotate()
        self.orbs.apply_transformations(self.x, self.y)

        self.orbs_list = self.orbs.get_info()

        # normal attack

        # if not self.attack_timer.is_active() and self.controls["click"]:
        #     best_dist = 1e9
        #
        #     # mouse pos is only relative to the screen. To make it relative to the world map, we minus MID position and add the player's position vectords
        #     self.target_pos = self.controls["mouse_pos"] - pygame.math.Vector2(MID_X, MID_Y) + pygame.math.Vector2(self.x, self.y)
        #
        #     for index, (x, y, radius) in enumerate(self.orbs_list):
        #         idle_pos = pygame.math.Vector2(x, y)
        #         cur_dist = self.target_pos.distance_to(idle_pos)
        #
        #         if cur_dist < best_dist:
        #             self.attack_orb_index = index
        #             best_dist = cur_dist
        #
        #     self.attack_timer.start()

        # checks if any orb (ammo) is available
        if any([target_pos == None for target_pos in self.orb_targets]) and self.controls["click"]:
            best_dist = 1e9

            # mouse pos is only relative to the screen. To make it relative to the world map, we minus MID position and add the player's position vectords
            self.target_pos = self.controls["mouse_pos"] - pygame.math.Vector2(MID_X, MID_Y) + pygame.math.Vector2(self.x, self.y)

            # selecting the orb closest to the clicked position
            for index, (x, y, radius) in enumerate(self.orbs_list):

                # don't allow orbs that are currently used in attack to be selected
                if self.orb_targets[index] != None:
                    continue

                idle_pos = pygame.math.Vector2(x, y)
                cur_dist = self.target_pos.distance_to(idle_pos)

                if cur_dist < best_dist:
                    attack_orb_index = index
                    best_dist = cur_dist

            # choose the closest orb as the attacking orb
            self.orb_timers[attack_orb_index].start()
            self.orb_targets[attack_orb_index] = self.target_pos


        # calculate position of all orbs
        for orb_index in range(self.NUMBER_OF_ORBS):
            orb_timer = self.orb_timers[orb_index]

            if orb_timer.is_active():
                if orb_timer.time_elapsed() >= self.TOTAL_ATTACK_TIME:
                    self.orb_targets[orb_index] = None
                    self.orb_timers[orb_index].end()

            x, y, radius = self.orbs_list[orb_index]

            idle_pos = pygame.math.Vector2(x, y)

            if orb_timer.is_active():
                t = self.orb_ease(orb_timer.time_elapsed() / self.TOTAL_ATTACK_TIME)

                # caluclate new position
                new_x, new_y = t * (self.orb_targets[orb_index]) + (1 - t) * idle_pos

                # update orbs list with new calculated orb position for the attacking orb
                self.orbs_list[orb_index] = (new_x, new_y, 5)



    def get_server_send_message(self):
        s = super().get_server_send_message()

        # add hand info
        s += f",{self.hand_frame_index},"

        # add orbs info
        if len(self.orbs_list) == 0:
            s += "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"
        else:
            for x, y, radius in self.orbs_list:
                s += f"{int(x)},{int(y)},{radius},"

        # s += "," + self.orbs.get_send_message()

        return s[:-1]

    def display(self, screen, offset_x, offset_y):
        display_x, display_y = self.get_display_coords(offset_x, offset_y)

        # display body
        super().display(screen, offset_x, offset_y)

        # display hand
        self.hand_layer.display(screen, display_x, display_y)

class NatureBunny(Bunny):
    def __init__(self):
        super().__init__("nature_bunny")

        self.controls = {}
        self.controls["mouse_pos"] = (MID_X, MID_Y)


        ''' Attack '''

        # initialise vine (Bezier curves) start point, control point and end point variables
        self.vine_lx, self.vine_ly, self.vine_rx, self.vine_ry = MID_X, MID_Y, MID_X, MID_Y

        self.MAX_MAGNITUDE = 20 # max magnitude of end point for idle vine, limit the radius to a certain cap so vine does not extend indefinitely
        self.VINE_EXTENSION = 20 # extension when clicking attack

        self.attack_timer = Timer()
        self.TOTAL_ATTACK_TIME = 0.5

    def vine_ease(self, x):
        return -(x-1)**3

    def update(self, inputs, map_obj_collision_boxes):
        super().update(inputs, map_obj_collision_boxes)

        ''' update vines '''

        mouse_x, mouse_y = self.controls["mouse_pos"]

        # vector from middle of the screen to the mouse
        vec = (pygame.math.Vector2(mouse_x, mouse_y) - pygame.math.Vector2(MID_X, MID_Y))

        # reduce the magnitude of the radius so that its capped at MAX_MAGNITUDE

        current_magnitude = min(vec.magnitude(), self.MAX_MAGNITUDE)

        if vec.magnitude() != 0: # normalize function cannot work if magnitude is 0
            # start the attack timer if mouse is clicked
            if self.controls["click"] and not self.attack_timer.is_active():
                self.attack_timer.start()

            # calculate new magnitude based on time since last click
            if self.attack_timer.is_active():
                if self.attack_timer.time_elapsed() >= self.TOTAL_ATTACK_TIME: # end attack timer if attack time has passed
                    self.attack_timer.end()
                else:
                    current_magnitude += self.VINE_EXTENSION * self.vine_ease(self.attack_timer.time_elapsed() / self.TOTAL_ATTACK_TIME)

            vec = vec.normalize() * current_magnitude

        # new "fake" mouse position
        mouse_x, mouse_y = (pygame.math.Vector2(MID_X, MID_Y) + vec).x, (pygame.math.Vector2(MID_X, MID_Y) + vec).y

        # idle offset for Bezier endpoint
        x_offset = 20
        y_offset = 5 + 3 * math.sin(time.time() * 0.9)

        lx, ly = int(self.x - x_offset), int(self.y + y_offset)
        rx, ry = int(self.x + x_offset), int(self.y + y_offset)

        # left vine moves
        if mouse_x < MID_X:
            lx = int(mouse_x - MID_X + self.x)
            ly = int(mouse_y - MID_Y + self.y)
        else:
            rx = int(mouse_x - MID_X + self.x)
            ry = int(mouse_y - MID_Y + self.y)

        self.vine_lx, self.vine_ly, self.vine_rx, self.vine_ry = lx, ly, rx, ry

    def get_server_send_message(self):
        s = super().get_server_send_message()

        s += f",{int(self.x)},{int(self.y)},{int(self.x)},{int(self.y - 30)},{self.vine_lx},{self.vine_ly},{self.vine_rx},{self.vine_ry}"

        return s

class AngelBunny(Bunny):
    def __init__(self):
        super().__init__("angel_bunny")

        ''' Hand '''
        self.hand_layer = ChangingLayer()

        self.hand_state = "idle"

        self.hand_animations = {
        "idle" : Animation(f"bunny/{self.name}/{self.name}_idle_hands.png", 32, 32),
        "run": Animation(f"bunny/{self.name}/{self.name}_run_hands.png", 32, 32)
        }

        self.idle_hand_animation = Animation(f"bunny/{self.name}/{self.name}_idle_hands.png", 32, 32)
        self.run_hand_animation = Animation(f"bunny/{self.name}/{self.name}_run_hands.png", 32, 32)
        self.charge_hand_animation = Animation(f"bunny/{self.name}/{self.name}_charge_hands.png", 32, 32)
        self.release_hand_animation = Animation(f"bunny/{self.name}/{self.name}_release_hands.png", 32, 32)

        self.transitions = {"idle" : {"run" : "self.hand_idle_to_run()"},
                            "run": {"idle" : "self.hand_run_to_idle()"}
                            }

        self.run_state.set_y_offsets([0, 1, 2, 1, 0, 1, 2, 1])

    def hand_idle_to_run(self):
        return self.state == self.run_state

    def hand_run_to_idle(self):
        return self.state == self.idle_state

    def update(self, inputs, map_obj_collision_boxes):
        # super().update(inputs, map_obj_collision_boxes)

        for new_state, condition_function in self.transitions[self.hand_state].items():
            if eval(condition_function):
                self.hand_state = new_state

        self.hand_layer.update(self.hand_animations[self.hand_state].get_frame(), self.x_direction, self.state)

        super().update(inputs, map_obj_collision_boxes)

    def display(self, screen, offset_x, offset_y):
        display_x, display_y = self.get_display_coords(offset_x, offset_y)

        # display body
        super().display(screen, offset_x, offset_y)

        # display hand
        self.hand_layer.display(screen, display_x, display_y)

class ShadowBunny(Bunny):
    def __init__(self):
        super().__init__("shadow_bunny")

        ''' Sword '''
        self.sword_layer = ChangingLayer(0, 0, -32, 0)
        self.sword_animation = SingleAnimation(f"bunny/{self.name}/{self.name}_sword.png", 64, 32)
        self.playing_sword_animation = False

        self.run_state.set_y_offsets([0, 1, 3, 1, 0, 1, 3, 1])

    def update(self, inputs, map_obj_collision_boxes):
        super().update(inputs, map_obj_collision_boxes)

        ''' Updating Sword Animation '''

        # only check if not currently playing animation
        if not self.playing_sword_animation:
            self.sword_layer.update(self.sword_animation.get_first_frame(), self.x_direction, self.state)

            # check for input to start animation
            for event in inputs["events"]:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.playing_sword_animation = True
                    self.sword_animation.start()
        else:
            self.sword_layer.update(self.sword_animation.get_frame(), self.x_direction, self.state)

            if self.sword_animation.ended():
                self.playing_sword_animation = False

        self.sword_image = self.sword_animation.get_frame()


    def display(self, screen, offset_x, offset_y):
        display_x, display_y = self.get_display_coords(offset_x, offset_y)

        # display body
        super().display(screen, offset_x, offset_y)

        # display sword (and attached hand)
        self.sword_layer.display(screen, display_x, display_y)
