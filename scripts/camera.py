from scripts.entity import *
from scripts.map import Map

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
