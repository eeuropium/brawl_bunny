from scripts.constants import *
from scripts.core_funcs import *
from scripts.animation import *
from scripts.managers import *
from scripts.orbs import Orbs # for Orb Bunny
import cmath # for Orb Bunny complex numbers

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

        ''' Movement '''
        self.SPEED = BUNNY_STATS[self.name]["speed"]

        self.x = MID_X
        self.y = MID_Y

        self.x, self.y = random.choice(RESPAWN_POINTS[USE_MAP])

        self.direction = pygame.math.Vector2()
        self.x_direction = 1 # 1 for facing right, -1 for facing left

        ''' Boxes '''
        self.collision_box_x_offset, self.collision_box_y_offset, self.org_collision_box_width, self.org_collision_box_height = get_box(f"box/collision_box/entities/{self.name}_collision_box.png")
        self.collision_box = pygame.FRect(self.x, self.y, self.org_collision_box_width, self.org_collision_box_height) # placeholder for start_x, start_y

        self.hitbox_x_offset, self.hitbox_y_offset, self.org_hitbox_width, self.org_hitbox_height = get_box(f"box/hitbox/entities/{self.name}_hitbox.png")
        self.hitbox = pygame.FRect(self.x, self.y, self.org_hitbox_width, self.org_hitbox_height) # placeholder for start_x, start_y

        ''' Attacking '''
        self.last_hit_timers = [Timer() for i in range(TOTAL_PLAYERS // 2)] # this is the number of enemies

        for timer in self.last_hit_timers:
            timer.start() # start all the timers.
            # This assumes that the first latest hit is the time when the game starts which is long enough before the first hit to cause any impact on the gameplay

        ''' Networking '''
        self.frame_index = 0

        ''' Health '''
        self.TOTAL_HEALTH = BUNNY_STATS[self.name]["health"]
        self.health = self.TOTAL_HEALTH # start with full health
        self.respawn_timer = LimitTimer(RESPAWN_WAIT_TIME)

        ''' Ability '''
        self.ability_charge = 0 # starts with 0 ability charged
        self.TOTAL_ABILITY_CHARGE = BUNNY_STATS[self.name]["total_ability_charge"]

    def init_ability_timer(self):
        self.ability_timer = LimitTimer(BUNNY_STATS[self.name]["ability_time"])

    def update_timed_ability(self):
        if self.ability_timer.is_active():
            # calculate ability charge from time elapsed since activating the ability
            if self.ability_timer.is_over():
                self.ability_charge = 0
            else:
                self.ability_charge = int((BUNNY_STATS[self.name]["ability_time"] - self.ability_timer.time_elapsed()) / BUNNY_STATS[self.name]["ability_time"] * self.TOTAL_ABILITY_CHARGE)


    def change_state(self, state):
        self.state = state
        self.state.animation.reset()

    def change_hand_state(self, hand_state):
        self.hand_state = hand_state
        self.hand_state.animation.reset()

    def get_aim_vec(self):
        return self.controls["mouse_pos"] - pygame.math.Vector2(MID_X, MID_Y)
                                                                                       # so that nature bunny can't move during grappling
    def update(self, input_message, map_obj_collision_boxes, map_obj_hitboxes, enemies, moving = True):
        ''' Respawn '''
        if self.respawn_timer.is_active() and self.respawn_timer.is_over():
            self.respawn_timer.end()
            self.health = self.TOTAL_HEALTH

            respawn_x, respawn_y = random.choice(RESPAWN_POINTS[USE_MAP])
            # collision box coordinates determines self.x, self.y and hitbox coordinates so we reset this to reset all of them
            self.collision_box = pygame.FRect(respawn_x, respawn_y, self.org_collision_box_width, self.org_collision_box_height)

            # turn on back the hitbox
            self.hitbox.width = self.org_hitbox_width
            self.hitbox.height = self.org_hitbox_height

        # no updating needed if player is dead so we return
        if self.respawn_timer.is_active():
            return

        ''' Inputs / Controls '''
        # give meaningful names to user message string
        self.controls = {}

        # "mouse_coor" - list containing two elements, x and y coordinates of mouse
        # "click" - 0 or 1 indiciating if mouse is clicked
        # "mouse_up" - 0 or 1 indicating if mouse is lifted
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
        if moving:
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
        else:
            self.direction = pygame.math.Vector2(0, 0)

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

        # update positions for displaying character (this is the center position)
        self.x = self.collision_box.left - self.collision_box_x_offset + 16
        self.y = self.collision_box.top - self.collision_box_y_offset + 16

        # update positions for hitbox
        self.hitbox.left = self.collision_box.left - self.collision_box_x_offset + self.hitbox_x_offset
        self.hitbox.top = self.collision_box.top - self.collision_box_y_offset + self.hitbox_y_offset

        # determine animation direction with mouse position
        if self.controls["mouse_pos"].x < MID_X:
            self.x_direction = -1
        else:
            self.x_direction = 1

        ''' Animation '''
        # responsible for updating the frame index of idle or running animation

        # # check if have to change from current state to new state
        self.state.determine_state()

        # # updates image (frame index sent to client) and direction
        self.state.update()

    # called by inherrited classes to deal damage to enemies
    def damage_update(self, index, enemy, attack_hit_enemy: bool, damage_value):
        # no collision detected, so no damage will be dealt. We return the function.
        if not attack_hit_enemy:
            return

        # check if time since last hit is long enough for another different attack to hit
        if self.last_hit_timers[index].time_elapsed() >= MIN_ATTACK_INTERVAL:
            enemy.take_damage(damage_value)

            # update ability charge
            self.ability_charge += damage_value
            self.ability_charge = min(self.ability_charge, self.TOTAL_ABILITY_CHARGE) # cap the ability charge at max

            # update last hit timers
            self.last_hit_timers[index].restart()

    def take_damage(self, damage):
        self.health -= damage
        self.health = max(0, self.health) # make sure health does not go below 0 (negative)

        if self.health == 0:
            # start respawning
            self.respawn_timer.start()

            # turn off hitbox
            self.hitbox.width = 0
            self.hitbox.height = 0


    def get_server_send_message(self):
        # get prefixes
        character_prefix = NAME_PREFIX_MAP[self.name]

        character_state_prefix = CHARACTER_STATE_PREFIX_MAP[self.state.__class__.__name__.lower()]

        # change x_direction to a 0 or 1 boolean
        if self.x_direction == 1:
            flip_sprite = 0
        else:
            flip_sprite = 1

        # character is dead and currently waiting to respawn
        if self.respawn_timer.is_active():
             # we send negative of the number of seconds left to wait. Cap it at 0 (can't go more than 0)
            health_data = min(0, -int(RESPAWN_WAIT_TIME - self.respawn_timer.time_elapsed()))
            # negative allows us to distinguish if it is the health (positive) or a timer time (negative)
        else:
            health_data = self.health

        #         (character type)        (coordinates)                  (state)           (frame number)  (horizontal flip) (health / respawn time)  (ability charge)
        return f"{character_prefix},{int(self.x)},{int(self.y)},{character_state_prefix},{self.frame_index},{flip_sprite},{health_data},{self.ability_charge}"


class OrbBunny(Bunny):
    def __init__(self):
        super().__init__("orb_bunny")

        ''' Hand '''
        self.hand_angles = [90, 60, 30, 0, -15, -45, -75, -90]

        # initialise starting hand frame index at 0 degrees
        self.hand_frame_index = 3

        ''' Orbs '''

        self.NUMBER_OF_ORBS = 5
        self.ATTACK_RANGE = 100

        self.orbs = Orbs(self.NUMBER_OF_ORBS)
        self.orbs_list = [] # list storing position of orbs (includes attacking orb position)
        self.attack_orb_index = -1 # -1 if no orb is used in attack currently

        self.TOTAL_ATTACK_TIME = 1.5

        self.orb_targets = [None for i in range(self.NUMBER_OF_ORBS)]
        self.orb_timers = [LimitTimer(self.TOTAL_ATTACK_TIME) for i in range(self.NUMBER_OF_ORBS)]


    def orb_ease(self, x):
        return -4 * (x - 0.5) * (x - 0.5) + 1 # upside down quadratic, peak at x = 0.5

    def find_closest_angle(self, angle, available_angles):
        min_diff = 180 # initialise to greatest possible

        for curr_angle in available_angles:
            diff = abs(angle - curr_angle)

            if diff < min_diff:
                min_diff = diff
                closest_angle = curr_angle

        return closest_angle

    def update(self, inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies):
        super().update(inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies)

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

        ''' Normal Attack '''

        # checks if any orb (ammo) is available
        if any([target_pos == None for target_pos in self.orb_targets]) and self.controls["click"]:
            best_dist = 1e9

            # mouse pos is only relative to the screen. To make it relative to the world map, we minus MID position and add the player's position vectords
            shoot_vec = self.get_aim_vec()

            if shoot_vec.magnitude() != 0: # check if can normalize

                # times by range allows constant range for the attacks
                self.target_pos = shoot_vec.normalize() * self.ATTACK_RANGE + pygame.math.Vector2(self.x, self.y)

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

        ''' Ability Attack '''

           # checks that ability is charged and can be used         # check that all orbs are not used in an attack                # checks that ability control is pressed
        if self.ability_charge == self.TOTAL_ABILITY_CHARGE and all([target_pos == None for target_pos in self.orb_targets]) and self.controls["ability"]:
            # reset ability charge
            self.ability_charge = 0

            # the direction of the orbs is determined by the mouse position
            z_vec = self.get_aim_vec()

            if z_vec.magnitude() != 0:  # check if can normalize
                z_vec = z_vec.normalize() * 1e10 # scale up the z_vec so effect is noticeable

                z = complex(z_vec.x, z_vec.y)
                n = self.NUMBER_OF_ORBS

                # calculate the nth roots of unity
                roots_of_unity = [cmath.exp(2j * cmath.pi * k / n) for k in range(n)]

                # calculate the complex roots of z
                complex_roots = [z ** (1/n) * root for root in roots_of_unity]

                # use the complex roots to determine target position of the orbs
                self.orb_targets = [pygame.math.Vector2(root.real + self.x, root.imag + self.y) for root in complex_roots]

                for orb_timer in self.orb_timers:
                    orb_timer.start()

        ''' Update Orbs '''

        # calculate position of all orbs
        for orb_index in range(self.NUMBER_OF_ORBS):
            orb_timer = self.orb_timers[orb_index]

            # check if attacking of orb is over. If it is, reset to idle state.
            if orb_timer.is_active():
                if orb_timer.is_over():
                    self.orb_targets[orb_index] = None
                    self.orb_timers[orb_index].end()

            x, y, radius = self.orbs_list[orb_index]

            idle_pos = pygame.math.Vector2(x, y)

            if orb_timer.is_active():
                # t = self.orb_ease(orb_timer.time_elapsed() / self.TOTAL_ATTACK_TIME)
                t = orb_timer.get_t_value()
                lerp = self.orb_ease(orb_timer.get_t_value())

                # caluclate new position
                new_x, new_y = lerp * (self.orb_targets[orb_index]) + (1 - lerp) * idle_pos

                # check for collision. If collided, the orb bounces back
                SIDE_LENGTH = 6
                orb_collision_box = pygame.FRect(new_x - SIDE_LENGTH // 2, new_y - SIDE_LENGTH // 2, SIDE_LENGTH, SIDE_LENGTH)

                rebound = False # make the orb travel back to the player if something is hit

                # rebound if hit map obstacles
                for hitbox in map_obj_hitboxes:
                    if orb_collision_box.colliderect(hitbox):
                        rebound = True

                # deal damage to enemies
                for index, enemy in enumerate(enemies):
                    self.damage_update(index, enemy, orb_collision_box.colliderect(enemy.hitbox), BUNNY_STATS[self.name]["normal_attack_damage"])

                # rebound if hit enemies
                for enemy in enemies:
                    if orb_collision_box.colliderect(enemy.hitbox):
                        rebound = True

                if rebound and t < 0.5:
                    orb_timer.set_t_value(1 - t) # symetrically reflect t-value over t = 0.5, the peak so the orb bounces back

                # update orbs list with new calculated orb position for the attacking orb
                self.orbs_list[orb_index] = (new_x, new_y, 5) # attacking orb has constant radius

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

        self.attack_timer = LimitTimer(BUNNY_STATS[self.name]["attack_cooldown"])

        ''' Ability '''
        self.init_ability_timer()

        self.HOOK_SPEED = BUNNY_STATS[self.name]["hook_speed"]
        self.HOOK_RANGE = BUNNY_STATS[self.name]["hook_range"]

        self.hook_pos = pygame.math.Vector2(0, 0) # the position of the hook point
        self.hook_move_vec = pygame.math.Vector2(0, 0) # the vector which the hook is moving in
        self.hooking = False # if the hook is being fired currently
        self.grappling = False # if the player becomes airboen and move towards the hook


    def vine_ease(self, x):
        return -(x-1)**3

    def reset_ability(self):
        # self.ability_charge = 0
        self.grappling = False

    def update(self, inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies):
        super().update(inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies, moving = not self.grappling)

        ''' Attack '''
        # vector from middle of the screen to the mouse
        vec = self.get_aim_vec()

        # reduce the magnitude of the radius so that its capped at MAX_MAGNITUDE

        current_magnitude = min(vec.magnitude(), self.MAX_MAGNITUDE)

        if vec.magnitude() != 0: # normalize function cannot work if magnitude is 0
            # start the attack timer if mouse is clicked
            if self.controls["click"] and not self.attack_timer.is_active():
                self.attack_timer.start()

            # calculate new magnitude based on time since last click
            if self.attack_timer.is_active():
                if self.attack_timer.is_over(): # end attack timer if attack time has passed
                    self.attack_timer.end()
                else:
                    current_magnitude += self.VINE_EXTENSION * self.vine_ease(self.attack_timer.get_t_value())

            vec = vec.normalize() * current_magnitude

        ''' Ability '''

        # start ability timer
        if self.ability_charge == self.TOTAL_ABILITY_CHARGE and self.controls["ability"]:
            self.ability_timer.start()

        # end ability timer
        if self.ability_timer.is_active() and self.ability_timer.is_over():
            self.ability_timer.end()

        # calculate ability charge
        self.update_timed_ability()

        # get aim vec
        if self.ability_timer.is_active() and self.controls["ability"]:
            aim_vec = self.get_aim_vec()

            if aim_vec.magnitude != 0:
                self.hook_move_vec = aim_vec.normalize() * self.HOOK_SPEED # hook speed
                self.hook_pos = pygame.math.Vector2(self.collision_box.centerx, self.collision_box.centery) # hook starts at player position

                self.hooking = True

        if self.hooking:
            DIVISIONS = 10

            collided = False # boolean for if the hook position collided with collision boxes

            if self.hook_pos.distance_to(pygame.math.Vector2(self.x, self.y)) >= self.HOOK_RANGE:
                self.hooking = False

            for i in range(DIVISIONS):
                # intermediate points to detect collision. Without this, we might skip pass entire obstacles
                self.hook_pos += self.hook_move_vec / DIVISIONS

                for collision_box in map_obj_collision_boxes + [enemy.hitbox for enemy in enemies]:
                    if collision_box.collidepoint(self.hook_pos):
                        collided = True
                        break

                if collided:
                    break

            if collided:
                self.hooking = False
                self.grappling = True

        elif self.grappling:

            # determine move vec
            # check if distance travelled by the vector is not more than the distance to the hook pos to prevent overshooting

            hook_to_center_dist_before_moving = pygame.math.Vector2(self.collision_box.centerx, self.collision_box.centery).distance_to(self.hook_pos)
            hook_to_center_dist_after_moving = (pygame.math.Vector2(self.collision_box.centerx, self.collision_box.centery) + self.hook_move_vec).distance_to(self.hook_pos)

                # within range to end hooking                                           # moving away from hook. This should not be the case so we end the hook.
            if (hook_to_center_dist_before_moving < self.hook_move_vec.magnitude() or hook_to_center_dist_after_moving > hook_to_center_dist_before_moving):
                move_vec = pygame.math.Vector2(self.hook_pos.x - self.collision_box.centerx, self.hook_pos.y - self.collision_box.centery)
                self.grappling = False
            else:
                move_vec = self.hook_move_vec


            # update x coordinate
            self.collision_box.centerx += move_vec.x

            # handle collisions in the x axis
            for collision_box in map_obj_collision_boxes + [enemy.hitbox for enemy in enemies]:
                if self.collision_box.colliderect(collision_box):
                    self.reset_ability()

                    if move_vec.x > 0: # moving right
                        self.collision_box.right = collision_box.left
                    elif move_vec.x < 0: # moving left
                        self.collision_box.left = collision_box.right

            # update y coordinate
            self.collision_box.centery += move_vec.y

            # handle collisions in the y axis
            for collision_box in map_obj_collision_boxes + [enemy.hitbox for enemy in enemies]:
                if self.collision_box.colliderect(collision_box):
                    self.reset_ability()

                    if move_vec.y > 0: # moving down
                        self.collision_box.bottom = collision_box.top
                    elif move_vec.y < 0: # moving up
                        self.collision_box.top = collision_box.bottom

            # update positions for displaying character (this is the center position)
            self.x = self.collision_box.left - self.collision_box_x_offset + 16
            self.y = self.collision_box.top - self.collision_box_y_offset + 16

            # update positions for hitbox
            self.hitbox.left = self.collision_box.left - self.collision_box_x_offset + self.hitbox_x_offset
            self.hitbox.top = self.collision_box.top - self.collision_box_y_offset + self.hitbox_y_offset

        # idle offset for Bezier endpoint
        x_offset = 20
        y_offset = 5 + 3 * math.sin(time.time() * 0.9)

        lx, ly = int(self.x - x_offset), int(self.y + y_offset)
        rx, ry = int(self.x + x_offset), int(self.y + y_offset)

        if self.hooking or self.grappling: # using ability
            if self.controls["mouse_pos"].x < MID_X:
                lx, ly = self.hook_pos
                lx, ly = int(lx), int(ly)
            else:
                rx, ry = self.hook_pos
                rx, ry = int(rx), int(ry)

        else:
            # new "fake" mouse position
            mouse_x, mouse_y = (pygame.math.Vector2(MID_X, MID_Y) + vec).x, (pygame.math.Vector2(MID_X, MID_Y) + vec).y


            # left vine moves
            if mouse_x < MID_X:
                lx = int(mouse_x - MID_X + self.x)
                ly = int(mouse_y - MID_Y + self.y)

                hit_x, hit_y = lx, ly
            else:
                rx = int(mouse_x - MID_X + self.x)
                ry = int(mouse_y - MID_Y + self.y)

                hit_x, hit_y = rx, ry

            # deal damage to enemies
            if self.attack_timer.is_active(): # if currently in attack
                for index, enemy in enumerate(enemies):
                    self.damage_update(index, enemy, enemy.hitbox.clipline(self.x, self.y, hit_x, hit_y), BUNNY_STATS[self.name]["normal_attack_damage"])
                                                 # check if the line (connecting the start and endpoint of the Bezier curves) intersect / collide with enemy hitbox

        self.vine_lx, self.vine_ly, self.vine_rx, self.vine_ry = lx, ly, rx, ry

    def get_server_send_message(self):
        s = super().get_server_send_message()

        s += f",{int(self.x)},{int(self.y)},{int(self.x)},{int(self.y - 30)},{self.vine_lx},{self.vine_ly},{self.vine_rx},{self.vine_ry}"

        return s

class AngelBunny(Bunny):
    def __init__(self):
        super().__init__("angel_bunny")

        ''' Hand '''
        self.hand_state = "idle"
        # possible hand states are
        # idle - when the character's hand is not attacking. Either the idle or run hand animation can be playing
        # charge - when the character is charging up the attack
        # release - when the character shoots the attack

        self.hand_prefix = ANGEL_BUNNY_HAND_STATE_PREFIX_MAP["idle"]
        self.hand_frame_index = 0

        self.hand_timer = Timer()
        self.hand_timer.start()

        ''' Attack '''

        self.ORB_CHARGE_RATE = BUNNY_STATS[self.name]["radius_charge_rate"] # per second
        self.MAX_RADIUS = BUNNY_STATS[self.name]["max_radius"]

        self.orb_timer = Timer()
        self.orb_vec = pygame.math.Vector2(0, 0)

        self.orb_radius = 0
        self.orb_pos = pygame.math.Vector2(self.x, self.y)

        self.orb_alive = False # checks if the orb projectile still exists


        ''' Ability '''
        self.ability_target_x = -1
        self.ability_target_y = -1

        self.init_ability_timer()

    def hand_idle_to_run(self):
        return self.state == self.run_state

    def hand_run_to_idle(self):
        return self.state == self.idle_state

    def update(self, inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies):
        super().update(inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies)

        self.hand_frame_index = int(self.hand_timer.time_elapsed() // FRAME_INTERVAL)

        ''' (Hand) and Attack State Transitions '''

        # changing from idle / run to charging         # don't allow attack if orb is still present in the game (there can only be one orb existing at any time)
        if self.hand_state == "idle" and self.controls["click"] and not self.orb_alive:
            self.hand_state = "charge"
            self.hand_timer.restart()
            self.hand_frame_index = 0

            # start orb timer
            self.orb_timer.start()

            # reset orb position
            self.orb_pos = pygame.math.Vector2(self.x, self.y + ANGEL_BUNNY_ATTACK_Y_OFFSET)

        # changing from charge to release
        elif self.hand_state == "charge" and  self.controls["mouse_up"]:
            self.hand_state = "release"
            self.hand_timer.restart()
            self.hand_frame_index = 0

            # orbs
            self.orb_vec = self.get_aim_vec()

            if self.orb_vec.magnitude() != 0:
                self.orb_vec = self.orb_vec.normalize() * BUNNY_STATS["angel_bunny"]["projectile_speed"]

            self.orb_timer.end()
            self.orb_alive = True

        # changing from release to idle / run
        elif self.hand_state == "release" and self.hand_frame_index >= 5:
            self.hand_state = "idle"
            self.hand_timer.restart()
            self.hand_frame_index = 0

        ''' Hand State Frames '''

        if self.hand_state == "idle": # can either be idle or run hands

            if self.state == self.idle_state:
                self.hand_frame_index = 0 # idle has only 1 frame
                self.hand_prefix = ANGEL_BUNNY_HAND_STATE_PREFIX_MAP["idle"]

            elif self.state == self.run_state:
                self.hand_frame_index %= 8 # running animation has 8 frames in total
                self.hand_prefix = ANGEL_BUNNY_HAND_STATE_PREFIX_MAP["run"]

        elif self.hand_state == "charge":
            self.hand_frame_index = min(self.hand_frame_index, 3) # charge animation has 4 frames in total. Since 0-indexing is used, maximum is index 3.
            self.hand_prefix = ANGEL_BUNNY_HAND_STATE_PREFIX_MAP["charge"]

        elif self.hand_state == "release":
            self.hand_frame_index = min(self.hand_frame_index, 4) # release animation has 5 frames in total.
            self.hand_prefix = ANGEL_BUNNY_HAND_STATE_PREFIX_MAP["release"]

        ''' Attack '''

        if self.orb_timer.is_active(): # still charging the orb
            # calcualte orb radius
            self.orb_radius = min(self.MAX_RADIUS, self.orb_timer.time_elapsed() * self.ORB_CHARGE_RATE)

            # calculate orb position to stay with the player
            self.orb_pos = (self.x, self.y + ANGEL_BUNNY_ATTACK_Y_OFFSET)

        # update orb position by moving it in the firing direction
        self.orb_pos += self.orb_vec

        # create orb collision box
        SIDE_LENGTH = max(2, int(self.orb_radius))
        orb_collision_box = pygame.FRect(self.orb_pos.x - SIDE_LENGTH // 2, self.orb_pos.y - SIDE_LENGTH // 2, SIDE_LENGTH, SIDE_LENGTH)

        # deal damage to enemies
        for index, enemy in enumerate(enemies):
            self.damage_update(index, enemy, orb_collision_box.colliderect(enemy.hitbox), int(self.orb_radius * BUNNY_STATS[self.name]["normal_attack_scaling"]))

        # orb collision
        orb_hit_object = False

        # destroy orb if hit map obstacles
        for hitbox in map_obj_hitboxes:
            if orb_collision_box.colliderect(hitbox):
                orb_hit_object = True

        # destroy orb if hit enemies
        for enemy in enemies:
            if orb_collision_box.colliderect(enemy.hitbox):
                orb_hit_object = True

        # reset orb
        if orb_hit_object or pygame.math.Vector2(self.x, self.y + ANGEL_BUNNY_ATTACK_Y_OFFSET).distance_to(self.orb_pos) >= BUNNY_STATS[self.name]["max_range"]:
            self.orb_alive = False
            self.orb_radius = 0

        ''' Ability '''

        if self.ability_charge == self.TOTAL_ABILITY_CHARGE and self.controls["ability"]:
            self.ability_timer.start()

        if self.ability_timer.is_active():
            # shooting beam direction
            vec = self.get_aim_vec()

            if vec.magnitude() != 0:
                vec = vec.normalize() * 100

                # don't update ability target position if mouse is at middle of screen (no aiming direction)
                self.ability_target_x = self.x + vec.x
                self.ability_target_y = self.y + vec.y

                # deal damage to enemies
                for index, enemy in enumerate(enemies):
                    self.damage_update(index, enemy, enemy.hitbox.clipline(self.x, self.y + ANGEL_BUNNY_ATTACK_Y_OFFSET, self.ability_target_x, self.ability_target_y), BUNNY_STATS[self.name]["ability_damage"])

            # end ability
            if self.ability_timer.is_over():
                self.ability_timer.end()
                self.ability_charge = 0 # reset to no ability charge
                self.ability_target_x, self.ability_target_y = -1, -1 # reset target values

        # calculate ability charge
        self.update_timed_ability()

    def get_server_send_message(self):
        # print(self.ability_target_x, self.ability_target_y)

        s = super().get_server_send_message()
        #      (type of hand animation)   (frame)                      (orb position)                    (orb radius)              (beam position)
        s += f",{self.hand_prefix},{self.hand_frame_index},{int(self.orb_pos.x)},{int(self.orb_pos.y)},{self.orb_radius},{int(self.ability_target_x)},{int(self.ability_target_y)}"

        return s

    # def display(self, screen, offset_x, offset_y):
    #     display_x, display_y = self.get_display_coords(offset_x, offset_y)
    #
    #     # display body
    #     super().display(screen, offset_x, offset_y)
    #
    #     # display hand
    #     self.hand_layer.display(screen, display_x, display_y)

class ShadowBunny(Bunny):
    def __init__(self):
        super().__init__("shadow_bunny")

        ''' Sword '''
        self.sword_animation = SingleAnimation(f"bunny/{self.name}/{self.name}_sword.png", 64, 32)

        self.playing_sword_animation = False
        self.sword_index = 0

        ''' Ability '''
        self.visible = True # bunny is not visible if in shadow realm AND not attacking
        # self.shadow_realm_timer = LimitTimer(BUNNY_STATS[self.name]["ability_time"])

        self.init_ability_timer()


    def update(self, inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies):
        super().update(inputs, map_obj_collision_boxes, map_obj_hitboxes, enemies)

        ''' Updating Sword Animation '''

        # only check if not currently playing animation
        if not self.playing_sword_animation:
            self.sword_index = 0

            # check for input to start animation
            if self.controls["click"]:
                self.playing_sword_animation = True
                self.sword_animation.start()

        else:
            self.sword_index = self.sword_animation.get_frame_index()

            if self.sword_animation.ended():
                self.playing_sword_animation = False


        ''' Dealing Damage '''

        if self.sword_index == 4: # damaging frame (frame number 4) Only can deal damage on this frame
            # determine the hurtbox of the attack based on x direction
            if self.x_direction == 1:
                sword_hurtbox = pygame.Rect(self.x - 6, self.y - 6, 29, 15)
            elif self.x_direction == -1:
                sword_hurtbox = pygame.Rect(self.x + 6 - 29, self.y - 6, 29, 15)

            # deal damage to enemies
            for index, enemy in enumerate(enemies):
                self.damage_update(index, enemy, sword_hurtbox.colliderect(enemy.hitbox), BUNNY_STATS[self.name]["normal_attack_damage"])

        ''' Ability '''

        # activating ability
        if self.ability_charge == self.TOTAL_ABILITY_CHARGE and self.controls["ability"]:
            self.ability_timer.start()

        # calculate ability charge
        self.update_timed_ability()

        # if ability is currently in use
        if self.ability_timer.is_active():
            # ending ability if time is over
            if self.ability_timer.is_over():
                self.ability_timer.end()
                self.visible = True

            # updating visibility
            self.visible = self.playing_sword_animation


    def get_server_send_message(self):
        s = super().get_server_send_message()

        s += f",{self.sword_index},{int(self.visible)},{int(self.ability_timer.is_active())}"
        # self.visible - visibility (for other players to determine if shadow bunny should be displayed)
        # self.shadow_realm_timer.is_active() - checks if ability is used currently: for the shadow bunny player to use shadow realm

        return s
