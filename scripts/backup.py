# old rotation method
'''
class OrbBunny(Bunny):
    def __init__(self):
        super().__init__()


        self.org_hand_image = load_image("orb_bunny_hand.png")


    def update(self, keys, mouse_pos, dt):
        super().update(keys, mouse_pos, dt)

        # calculate angle in radians
        rotate_angle = math.atan2(self.y - mouse_pos.y, mouse_pos.x - self.x)
        # self.y - mouse_pos.y as the y-axis of pygame's coordinate system is different from cartesian system

        # convert to degree
        rotate_angle = math.degrees(rotate_angle)

        # get rotated image
        self.rotated_hand_image = pygame.transform.rotate(self.org_hand_image, rotate_angle)

    def display(self, screen):
        super().display(screen)
        display_center(screen, self.rotated_hand_image, (int(self.x + 3 * self.x_direction), int(self.y + 3)))
'''

# old self map without using Tiled
'''
from scripts.constants import *
from scripts.core_funcs import *

class Map:
    def __init__(self, map_path, tile_path):
        self.tile_dict = self.build_tiles(tile_path)
        self.map_surf = self.build_map_surf(map_path)

    def build_tiles(self, tile_path):
        tile_images = load_spritesheet(load_image(tile_path), TILE_SIZE, TILE_SIZE)
        tile_values = [64, 8,  224, 32,
                       16, 56, 170, 131,
                       4,  2,  14,  128,
                       0,  16, 68,  1]

        tile_dict = {}

        for i in range(16):
            tile_dict[tile_values[i]] = tile_images[i]

        # sort by number of 1 bits
        tile_dict = dict(sorted(tile_dict.items(), key = lambda x : -bin(x[0]).count('1') - 0.5 * (math.log2(max(x[0], 1)) % 2 == 1)))
        # old python version 3.7.9 does not have int.bit_count()
        # negative for reverse sort
        # log to prioritise side tiles instead of corner tiles

        print(tile_dict)

        return tile_dict

    def get_tile_value(self, tile_x, tile_y, map_data, rows, columns):
        if map_data[tile_y][tile_x] == '1':
            return 170

        value_dict = {
                     (-1, -1): 1,
                     (0,  -1): 2,
                     (1,  -1): 4,
                     (1,  0) : 8,
                     (1,  1) : 16,
                     (0,  1) : 32,
                     (-1, 1) : 64,
                     (-1, 0) : 128
        }

        tile_value = 0

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                current_x = tile_x + dx
                current_y = tile_y + dy

                # exception handling of center tile
                if dx == 0 and dy == 0:
                    continue

                # exception handling of out of bound tiles
                if (current_x < 0) or (current_x >= columns) or (current_y < 0) or (current_y >= rows):
                    continue

                if map_data[current_y][current_x] == '1':
                    tile_value += value_dict[(dx, dy)]

        return tile_value

    def get_tile_surface(self, tile_value):
        for bitmask, tile_surf in self.tile_dict.items():
            print(tile_value, bitmask, tile_value & bitmask)

            if tile_value & bitmask == bitmask:
                return tile_surf

    def build_map_surf(self, map_path):
        file = open(f"data/maps/{map_path}")
        map_data = file.read().splitlines()
        file.close()

        # 1 is path, 0 is grass

        rows = len(map_data)
        columns = len(map_data[0])

        map_surf = pygame.Surface((columns * TILE_SIZE, rows * TILE_SIZE))

        for row in range(rows):
            for col in range(columns):
                tile_value = self.get_tile_value(col, row, map_data, rows, columns)
                tile_surf = self.get_tile_surface(tile_value)

                print(tile_value)

                # x, y coordinates on map surface
                x, y = col * TILE_SIZE, row * TILE_SIZE
                map_surf.blit(tile_surf, (x, y))

        # map_surf = pygame.Surface((16 * 16, 16))
        #
        # x = 0
        # for k, v in self.tile_dict.items():
        #     print(k)
        #     map_surf.blit(v, (x, 0))
        #     x += TILE_SIZE

        return map_surf

'''

# CSV map
'''
    # open first file to get rows and columns info
    layer_file = open(f"data/maps/map1/map1_{layers[0]}.csv")
    layer_data = layer_file.read().splitlines()
    layer_data = [list(map(int, line.split(','))) for line in layer_data]
    layer_file.close()

    # create empty map surface
    map_surf = pygame.Surface((columns * TILE_SIZE, rows * TILE_SIZE))
    map_surf.set_colorkey(BLACK)

    for layer in layers:
        # load csv file into 2D array
        layer_file = open(f"data/maps/map1/map1_{layer}.csv")
        layer_data = layer_file.read().splitlines()
        layer_data = [list(map(int, line.split(','))) for line in layer_data]
        layer_file.close()

        # iterate through 2D array to create map surface
        for row in range(rows):
            for col in range(columns):
                tile_value = layer_data[row][col]

                # no tiles at current position
                if tile_value == -1:
                    continue

                tile_surf = self.tile_dict[tile_value]

                # calculate x, y coordinates on map surface
                x, y = col * TILE_SIZE, row * TILE_SIZE
                map_surf.blit(tile_surf, (x, y))

    return map_surf

'''


# old selection classes
'''
from scripts.core_funcs import *

class Card:
    def __init__(self, bunny_name):
        self.card_image = load_image("gamestates/character_selection/card.png")
        self.bunny_image = load_image(f"bunny/{bunny_name}/{bunny_name}_concept.png")

        self.center_pos = (0, 0)
        self.mouse_on_card = False

        self.mask = pygame.mask.from_surface(self.card_image)

    def update(self, display_pos, mouse_pos, card_state):
        self.center_pos = display_pos
        self.card_rect = self.card_image.get_rect(center = (display_pos))

        self.card_state = card_state

        # check if mouse is on card
        if self.card_rect.collidepoint(mouse_pos):
            self.mouse_on_card = True
        else:
            self.mouse_on_card = False

    def is_clicked(self, events):
        if self.mouse_on_card:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return True
        return False


    def display(self, screen):
        mask_points = self.mask.outline()
        new_points = [(x + self.card_rect.left, y + self.card_rect.top) for x, y in mask_points]

        # draw green outline if card is selected
        if self.card_state == "selected":
            pygame.draw.lines(screen, (182, 213, 60), False, new_points, 3) # green outline

        # draw yellow outline if mouse is on the card
        elif self.mouse_on_card:
            pygame.draw.lines(screen, (244, 179, 27), False, new_points, 3) # yellow outline

        # draw card and bunny
        display_center(screen, self.card_image, self.center_pos)
        display_center(screen, self.bunny_image, self.center_pos)

        # draw gray mask on top if card is picked in another team
        if self.card_state == "locked":
            self.display_mask = self.mask.to_surface()
            self.display_mask = palette_swap(self.display_mask, WHITE, (48, 44, 46)) # dark grey
            self.display_mask.set_alpha(180)
            display_center(screen, self.display_mask, self.center_pos)

class Cards:
    def __init__(self, bunny_names):
        # blue cards and red cards separate to represent choosing characters from opposite teams
        # self.blue_cards = [Card(bunny_name) for bunny_name in bunny_names]
        # self.red_cards = [Card(bunny_name) for bunny_name in bunny_names]

        self.cards = {"BLUE": [Card(bunny_name) for bunny_name in bunny_names],
                      "RED": [Card(bunny_name) for bunny_name in bunny_names]}

        # constants to define the coordinates of placing the cards
        self.START_X = 70
        self.SPACING = 60
        self.Y_COOR = {"BLUE" : 50, "RED" : 120}

        self.selected_index = -1

        self.teams = ["BLUE", "RED"]

    def update(self, inputs):
        for team in self.teams:
            for index, card in enumerate(self.cards[team]):
                # set card state - selected, locked or open
                if self.selected_index == index:
                    if self.selected_team == team:
                        card_state = "selected"
                    else:
                        card_state = "locked"
                else:
                    card_state = "open"

                # update must come before is_clicked as update checks the position of the mouse
                card.update((self.START_X + index * self.SPACING, self.Y_COOR[team]), inputs["mouse_pos"], card_state)

                # select card is mosue is clicked
                if card.is_clicked(inputs["events"]):
                    self.selected_index = index
                    self.selected_team = team

    def display(self, screen):
        for team in self.teams:
            for card in self.cards[team]:
                card.display(screen)

'''
