from scripts.constants import *
from scripts.core_funcs import *
from scripts.animation import *

''' Character States '''

class CharacterState():
    def __init__(self, character):
        self.character = character

    def update(self):
        self.character.image = self.animation.get_frame()

        if self.character.x_direction == -1:
            self.character.image = pygame.transform.flip(self.character.image, True, False)

class Idle(CharacterState):
    def __init__(self, character, animation_path):
        super().__init__(character)
        self.animation = Animation(animation_path, 32, 32, 0.1)

    def determine_state(self):
        if self.character.direction.magnitude() != 0:
            self.character.change_state(self.character.run_state)

class Run(CharacterState):
    def __init__(self, character, animation_path):
        super().__init__(character)
        self.animation = Animation(animation_path, 32, 32, 0.1)

    def determine_state(self):
        if self.character.direction.magnitude() == 0:
            self.character.change_state(self.character.idle_state)

    def update(self):
        super().update()

''' Entities '''

class Bunny():
    def __init__(self, name):
        ''' States '''
        self.idle_state = Idle(self, f"bunny/{name}/{name}_idle.png")
        self.run_state = Run(self, f"bunny/{name}/{name}_run.png")

        self.state = self.idle_state

        ''' Movement '''
        self.SPEED = 1.5
        self.x = MID_X
        self.y = MID_Y
        self.direction = pygame.math.Vector2()
        self.x_direction = 1 # 1 for facing right, -1 for facing left

        ''' Hitbox '''
        self.collision_box_x_offset, self.collision_box_y_offset, hitbox_width, hitbox_height = get_box(f"box/collision_box/entities/{name}_collision_box.png")
        self.collision_box = pygame.FRect(MID_X, MID_Y, hitbox_width, hitbox_height) # placeholder for start_x, start_y

        ''' Keyboard Controls '''

        # # arrow keys
        # self.controls = {"left":  pygame.K_LEFT,
        #                  "right": pygame.K_RIGHT,
        #                  "up":    pygame.K_UP,
        #                  "down":  pygame.K_DOWN}

        # WASD
        self.controls = {"left":  pygame.K_a,
                         "right": pygame.K_d,
                         "up":    pygame.K_w,
                         "down":  pygame.K_s}

    def change_state(self, state):
        self.state = state
        self.state.animation.reset()

    # def check_collision(self, )
    def update(self, keys, mouse_pos, collision_boxes, dt):
        ''' Movement '''

        # similar to legend of zelda youtube tutorial

        # update direction vector based on inputs
        if keys[self.controls["left"]]:
            self.direction.x = -1
        elif keys[self.controls["right"]]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if keys[self.controls["up"]]:
            self.direction.y = -1
        elif keys[self.controls["down"]]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # normalize so that speed is constant even when travelling diagonally
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize() * self.SPEED * dt

        # update x coordinate
        self.collision_box.centerx += self.direction.x

        # handle collisions in the x axis
        for collision_box in collision_boxes:
            if self.collision_box.colliderect(collision_box):
                if self.direction.x > 0: # moving right
                    self.collision_box.right = collision_box.left
                elif self.direction.x < 0: # moving left
                    self.collision_box.left = collision_box.right

        # update y coordinate
        self.collision_box.centery += self.direction.y

        # handle collisions in the y axis
        for collision_box in collision_boxes:
            if self.collision_box.colliderect(collision_box):
                if self.direction.y > 0: # moving down
                    self.collision_box.bottom = collision_box.top
                elif self.direction.y < 0: # moving up
                    self.collision_box.top = collision_box.bottom

        # update positions for displaying character
        self.x = self.collision_box.left - self.collision_box_x_offset
        self.y = self.collision_box.top - self.collision_box_y_offset

        # determine animation direction with mouse position
        if mouse_pos.x < MID_X:
            self.x_direction = -1
        else:
            self.x_direction = 1

        ''' Animation '''

        self.state.determine_state()
        self.state.update()

        # self.debug = collision_boxes


    def display(self, screen, offset_x, offset_y):
        screen.blit(self.image, (int(self.x) + offset_x, int(self.y) + offset_y))

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

        self.hand_sprites = load_spritesheet(load_image("bunny/orb_bunny/angled_hands.png"), 32, 32)
        self.hand_angles = [90, 60, 30, 0, -15, -45, -75, -90]

        self.hand_images = {}
        self.walk_y_offsets = [0, 1, 3, 1, 0, 1, 3, 1]

        for index, angle in enumerate(self.hand_angles):
            self.hand_images[angle] = self.hand_sprites[index]


    def find_closest_angle(self, angle, available_angles):
        min_diff = 180 # initialise to greatest possible

        for curr_angle in available_angles:
            diff = abs(angle - curr_angle)

            if diff < min_diff:
                min_diff = diff
                closest_angle = curr_angle

        return closest_angle


    def update(self, keys, mouse_pos, objects, dt):
        super().update(keys, mouse_pos, objects, dt)

        # calculate angle in radians
        rotate_angle = math.atan2(self.y - mouse_pos.y, abs(mouse_pos.x - self.x))
        # self.y - mouse_pos.y as the y-axis of pygame's coordinate system is different from cartesian system
        # abs makes sure that even when image is flipped we still get the correct angles

        # convert to degree
        rotate_angle = math.degrees(rotate_angle)

        # get angled_hand image
        best_angle = self.find_closest_angle(rotate_angle, self.hand_angles)
        self.hand_image = self.hand_images[best_angle]

        # flip hand if facing left

        if self.x_direction == -1:
            self.hand_image = pygame.transform.flip(self.hand_image, True, False)

        # set y offset for hand
        self.hand_y_offset = 5

        if self.state == self.run_state:
            frame_index = self.state.animation.get_frame_index()
            self.hand_y_offset -= self.walk_y_offsets[frame_index]


    def display(self, screen, offset_x, offset_y):
        super().display(screen, offset_x, offset_y)

        screen.blit(self.hand_image, (int(self.x + 4 * self.x_direction) + offset_x, int(self.y + self.hand_y_offset) + offset_y))

class NatureBunny(Bunny):
    def __init__(self):
        super().__init__("nature_bunny")

class ShadowBunny(Bunny):
    def __init__(self):
        super().__init__("shadow_bunny")
