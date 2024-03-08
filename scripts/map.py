import json
import os
from scripts.constants import *
from scripts.core_funcs import *

class Object:
    def __init__(self, x, y, image, collision_box_rect, hitbox_rect):
        ''' Coordinates '''
        self.x = x
        self.bottom_y = y

        self.y = y - image.get_height()

        ''' Image '''
        self.image = image

        ''' Collision Box '''
        left, top, width, height = collision_box_rect
        left += self.x
        top += self.y

        self.collision_box = pygame.Rect((left, top, width, height))

        ''' Hitbox '''
        left, top, width, height = hitbox_rect
        left += self.x
        top += self.y

        self.hit_box = pygame.Rect((left, top, width, height))


    def get_bottom_y(self):
        return self.bottom_y

    def display(self, screen, offset_x, offset_y):
        screen.blit(self.image, (self.x + offset_x, self.y + offset_y))

        # # drawing collision_box
        # left, top, width, height = self.collision_box
        # left += offset_x
        # top += offset_y
        # pygame.draw.rect(screen, (255, 0, 0), (left, top, width, height))

class Map:
    def __init__(self, map_path):

        # initialise dicts
        self.tile_dict = {} # tile id to tile surface
        self.id_to_name = {} # coresponding number id of objects eg: {"big_tree" : 257, "bush" : 258 ...}
        self.object_surf = {} # corresponding surface / image of objects
        self.object_collision_box = {} # corresponding collision rect tuple
        self.object_hitbox = {} # corresponding hit rect tuple

        self.build_dicts()

        # map surf
        self.map_surf, self.chunks = self.build_map_surf(map_path)

    def build_dicts(self):
        ''' Tile Dict '''

        tile_images = load_spritesheet(load_image("map_assets/tiles.png"), TILE_SIZE, TILE_SIZE)
        num_tiles = len(tile_images)

        if USE_MAP == 3:
            self.tile_dict = {i + 157: tile_images[i] for i in range(num_tiles)}
        elif USE_MAP == 2:
            self.tile_dict = {i + 1: tile_images[i] for i in range(num_tiles)}
        else:
            assert False

        ''' Object Dicts '''

        # go through all the files in the specified folder, listed in alphabetical order (indicated by sorted)
        for index, file_name in enumerate(sorted(os.listdir(f"data/images/map_assets/objects/map{USE_MAP}"))):

            object_name = file_name[:-4] # -4 to take away ".png"

            if USE_MAP == 3:
                self.id_to_name[index + 118] = object_name # assign ID
            elif USE_MAP == 2:
                self.id_to_name[num_tiles + index + 1] = object_name # assign ID
            else:
                assert False

            self.object_surf[object_name] = load_image(f"map_assets/objects/map{USE_MAP}/{file_name}")


            try:
                self.object_collision_box[object_name] = get_box(f"box/collision_box/objects/map{USE_MAP}/{object_name}_collision_box.png")
                collision_box_exist = True
            except FileNotFoundError:
                self.object_collision_box[object_name] = (0, 0, 0, 0)
                collision_box_exist = False

            if collision_box_exist:
                # try to find for hitbox object
                try:
                    self.object_hitbox[object_name] = get_box(f"box/hitbox/objects/map{USE_MAP}/{object_name}_hitbox.png")
                # if not hitbox file found, set the hitbox to the collision box
                except FileNotFoundError:
                    self.object_hitbox[object_name] = self.object_collision_box[object_name]
            else:
                self.object_hitbox[object_name] = (0, 0, 0, 0)

            # This works because of how I created the map. I first created the collision box for all objects
            # If the object has a different hitbox, I draw it and add it to the hitbox folder.
            # If the hitbox is the same as the collision box, there will be no hitbox file, only the collision box file.


    def build_map_surf(self, map_path):
        # load json file containing map data
        with open(f"data/maps/{map_path}", 'r') as f:
            map_data = json.load(f)

        # get rows and columns
        rows = map_data["height"]
        columns = map_data["width"]

        layers = map_data["layers"]

        # create empty map surface
        map_surf = pygame.Surface((columns * TILE_SIZE, rows * TILE_SIZE))
        map_surf.set_colorkey(BLACK)

        # initialise chunk dictionary
        chunks = {}

        for x in range(-5, (columns // CHUNK_SIZE) + 5): # -5 to account for objects which may be partly offscreen
            for y in range(-5, (rows // CHUNK_SIZE) + 5): # +5 to account for rounding down division and objects which are partly offscreen
                chunks[(x, y)] = {"objects": [],
                                  "map_obj_collision_boxes": [],
                                  "map_obj_hitboxes": []}

        for layer in layers:
            if layer["type"] == "tilelayer":
                layer_data = layer["data"]

                # iterate through 2D array to create map surface
                for cur_row in range(rows):
                    for cur_col in range(columns):
                        # formula to calculate index since layer_data is a 1D array
                        tile_id = layer_data[cur_row * columns + cur_col]

                        # converting layer_data to 2D array would be more inefficient

                        # no tiles at current position
                        if tile_id == 0:
                            continue

                        tile_surf = self.tile_dict[tile_id]

                        # calculate x, y coordinates on map surface
                        x, y = cur_col * TILE_SIZE, cur_row * TILE_SIZE

                        OBSTACLE_TILE_IDS = [1, 2, 3, 4, 5, 17, 19, 33, 34, 35]

                        if USE_MAP == 3: # the ID is offset for map3 because of the way the Tiled application is structure which I used to create the maps
                            OBSTACLE_TILE_IDS = [e + 156 for e in OBSTACLE_TILE_IDS]

                        if tile_id in OBSTACLE_TILE_IDS: # hard coded
                            chunk_x, chunk_y = calc_chunk_xy(x, y)
                            chunks[(chunk_x, chunk_y)]["map_obj_collision_boxes"].append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                            chunks[(chunk_x, chunk_y)]["map_obj_hitboxes"].append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

                        map_surf.blit(tile_surf, (x, y))

            elif layer["type"] == "objectgroup":
                objects = layer["objects"]

                for object in objects:
                    # get x, y and id of object
                    x = round(object["x"])
                    y = round(object["y"])

                    object_id = object["gid"]
                    object_name = self.id_to_name[object_id]

                    # get surface and collision box of object
                    surf = self.object_surf[object_name]

                    # get collision box rectangle
                    collision_box_rect = self.object_collision_box[object_name]
                    # get hitbox rectangle
                    hitbox_rect = self.object_hitbox[object_name]

                    # create obstacle object
                    object = Object(x, y, surf, collision_box_rect, hitbox_rect)

                    # add object to corresponding chunk
                    chunk_x, chunk_y = calc_chunk_xy(x, y)
                    chunks[(chunk_x, chunk_y)]["objects"].append(object)
                    chunks[(chunk_x, chunk_y)]["map_obj_collision_boxes"].append(object.collision_box)
                    chunks[(chunk_x, chunk_y)]["map_obj_hitboxes"].append(object.hit_box)


        return map_surf, chunks

    def get_neighbouring_chunk_data(self, x, y, data_name):
        chunk_x, chunk_y = calc_chunk_xy(x, y)

        data = []

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                try:
                    data.extend(self.chunks[(chunk_x + dx, chunk_y + dy)][data_name])
                except KeyError: # chunks out of bound
                    pass

        return data
