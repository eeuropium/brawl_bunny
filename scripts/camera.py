from scripts.entity import *
from scripts.map import Map

class SimpleSprite():
    def __init__(self, image, coor, y_offset = 0, display_mode = "blit"):
        self.image = image
        self.x, self.y = coor

        # optional arguments
        self.display_mode = display_mode
        self.y_offset = y_offset

    def display(self, screen, offset_x, offset_y):
        display_coor = (int(self.x) + offset_x, int(self.y) + offset_y)

        if self.display_mode == "blit":
            screen.blit(self.image, display_coor)
        elif self.display_mode == "center":
            display_center(screen, self.image, display_coor)

    def get_bottom_y(self):
        return self.y + 16 # WARNING


class Camera():
    def __init__(self, map_surf):
        self.visible_sprites = []
        self.map_surf = map_surf

    def clear_visible_sprites(self):
        self.visible_sprites = []

    def add_visible_sprite(self, sprite):
        self.visible_sprites.append(sprite)

    def add_visible_sprites(self, sprites):
        self.visible_sprites.extend(sprites)

    def display_sprites(self, screen, player_x, player_y):
        offset_x = MID_X - player_x
        offset_y = MID_Y - player_y

        screen.blit(self.map_surf, (offset_x, offset_y))

        for sprite in sorted(self.visible_sprites, key = lambda sprite : sprite.get_bottom_y()):
            sprite.display(screen, offset_x, offset_y)
