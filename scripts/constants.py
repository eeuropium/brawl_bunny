import pygame
import time
import random
import math
import sys
import socket

pygame.init()

''' FPS '''
FPS = 60 # this is the maximum FPS

''' Display Info '''
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

SCALE_RATIO = 20
WIDTH = 16 * SCALE_RATIO # 16 : 9 scaled by SCALE_RATIO
HEIGHT = 9 * SCALE_RATIO

# 320 x 180 screen

MID_X = WIDTH // 2
MID_Y = HEIGHT // 2

''' Colours '''
BLACK = (0  , 0  , 0  )
WHITE = (255, 255, 255)

OWN_BLUE = (138, 236, 241)
TEAMMATE_BLUE = (40, 205, 223)

OWN_RED = (230, 71, 46)
TEAMMATE_RED = (169, 59, 59)

''' Map '''
TILE_SIZE = 16
CHUNK_SIZE = 10

USE_MAP = 3
# USE_MAP 2 is a test map
# USE_MAP 3 is the actual map

# the location blue team starts at
BLUE_START_POINT = {2: (MID_X, MID_Y), # starting position for map 2
                    3: (350, 545)} # starting position for map 3

# the location red team players start at
RED_START_POINT = {2: (MID_X, MID_Y),
                   3: (742, 571)}

# the location blue team players start at
RESPAWN_POINTS = {2: [(MID_X, MID_Y)],
                  3: [(521, 427), (742, 571), (744, 434), (350, 545)]}

''' Camera '''

MID_TO_FEET = 14 # number of pixels from the center display y-coordinate to the feet (bottom_y) of the bunny

''' Animation '''
FRAME_INTERVAL = 0.1

''' Fonts '''
FONT_15 = pygame.font.Font("data/cooper_black.ttf", 15)
FONT_10 = pygame.font.Font("data/cooper_black.ttf", 10)

''' Networking '''
PORT = 9991

hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)

SERVER_IP = server_ip

# for actual testing on multipler computers
SERVER_IP = "10.80.5.134"


# networking prefixes

def reverse_map(map):
    return {v: k for k, v in map.items()}

STATE_PREFIX_MAP = {"Menu":               "Z", # doesn't matter since does not require server
                    "MatchMaking" :       "M",
                    "CharacterSelection": "C",
                    "Gameplay":           "G",
                    "EndScreen":          "E"}

# character name to a character prefix
NAME_PREFIX_MAP = {"orb_bunny":    "E",
                   "nature_bunny": "Q",
                   "shadow_bunny": "T",
                   "angel_bunny":  "R"}
PREFIX_NAME_MAP = reverse_map(NAME_PREFIX_MAP)

# character state to a  character prefix
CHARACTER_STATE_PREFIX_MAP = {"idle": "I",
                              "run":  "R"}
PREFIX_CHARACTER_STATE_MAP = reverse_map(CHARACTER_STATE_PREFIX_MAP)


ANGEL_BUNNY_HAND_STATE_PREFIX_MAP = {"idle":    "I",
                                     "run":     "R",
                                     "charge":  "C",
                                     "release": "L"}
PREFIX_ANGEL_BUNNY_HAND_STATE_MAP = reverse_map(ANGEL_BUNNY_HAND_STATE_PREFIX_MAP)


INDEX_BUNNY_MAP = ["OrbBunny", "NatureBunny", "ShadowBunny", "AngelBunny"] # the order of the bunny cards


KEY_ORDERS = "WASDE"
KEY_FUNCTIONS = ["click", "mouse_up", "up", "left", "down", "right", "ability"]


''' Match '''

MATCH_TEXT_Y = 10

# total players for each match. Must be an even number
TOTAL_PLAYERS = 4

MATCH_DURATION = 120 # in seconds

# number of kills needed to end the match and win
KILLS_TO_WIN = 7

''' End Screen '''

WIN_TEXT_Y = 20

''' Gameplay '''

RUN_Y_OFFSET = {"orb_bunny":    [0, 1, 3, 1, 0, 1, 3, 1],
                "nature_bunny": [0, 1, 2, 1, 0, 1, 2, 1],
                "angel_bunny":  [0, 1, 2, 1, 0, 1, 2, 1],
                "shadow_bunny": [0, 1, 3, 1, 0, 1, 3, 1]}

ANGEL_BUNNY_ATTACK_Y_OFFSET = 4 # y offset for where the attacks are released from

# BALANCING STATS
# health - health
# normal_attack_damage - damage dealt per each normal attack hit
# total_ability_charge - total damage needed to deal to charge up super ability

BUNNY_STATS = {"orb_bunny":    {"health": 5200,
                                "speed": 1.5,
                                "normal_attack_damage": 500,
                                "total_ability_charge": 3000},
               "nature_bunny": {"health": 6800,
                                "speed": 1.6,
                                "normal_attack_damage": 1000,
                                "attack_cooldown": 0.5,
                                "total_ability_charge": 6000,
                                "ability_time": 5,
                                "hook_speed": 5,
                                "hook_range": 130},
               "angel_bunny":  {"health": 4200,
                                "speed": 1.5,
                                "normal_attack_scaling": 500, # the damage is calculated by orb_radius * normal_attack_scaling
                                "radius_charge_rate": 1, # increase in radius per second
                                "max_radius": 6, # maximum radius of the projectile
                                "total_ability_charge": 3000,
                                "projectile_speed": 3,
                                "max_range": 120,
                                "ability_time": 5,
                                "ability_damage": 800}, # damage is dealt every MIN_ATTACK_INTERVAL
               "shadow_bunny": {"health": 6200,
                                "speed": 1.6,
                                "normal_attack_damage": 1400,
                                "total_ability_charge": 7000,
                                "ability_time": 6}
}


# the least amount of time interval that the same attack can deal damage to the same enemy
MIN_ATTACK_INTERVAL = 0.5

# number of seconds to wait before respawning
RESPAWN_WAIT_TIME = 4

# number of seconds to wait after match ended before moving to the end screen state
MATCH_END_WAIT_TIME = 3

# number of seconds to wait before exit button appears
EXIT_BUTTON_WAIT_TIME = 2

# network inputs for gameplay gamestate

# TBD names
# good bunnies:
# orb_bunny - Eunova
# nature_bunny - Quillia
# angel_bunny - Areisa / Risa
# shadow_bunny - Shadowstrike

# bad bunnies:
# hex_bunny - ?
# snow_bunny - ?
# fist_bunny - Bangtan
# tech_bunny- Technovrak

'''
Time Bunny - Chrona:

Abilities:
Temporal Rift: Chrona creates rifts in time that slow down players and their projectiles, making them easier targets.
Time Warp Dash: She can dash through time to quickly reposition herself or dodge attacks, leaving behind afterimages.
Temporal Paradox: Chrona can reverse time for herself, healing back to a previous state and nullifying any damage taken in the last few seconds.

Gravity Bunny - Gravita:

Abilities:
Gravitational Pull: Gravita can manipulate gravity to pull players towards her, disrupting their movement and positioning.
Singularity Burst: She creates miniature black holes that suck players and objects into their center, causing damage and chaos.
Anti-Gravity Field: Gravita generates a field that reduces the weight of players within, allowing them to jump higher but making them more vulnerable to attacks.

Sound Bunny - Echoa:

Abilities:
Sonic Wave: Echoa emits powerful sound waves that knock back players and break objects in their path.
Disorienting Echoes: She creates echoes that confuse and disorient players, reversing their controls temporarily.
Harmonic Resonance: Echoa can heal herself and her allies by harmonizing with sound waves, making her a supportive but tricky adversary.
'''
