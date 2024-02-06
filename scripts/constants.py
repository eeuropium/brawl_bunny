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

WATER_BLUE = (48, 162, 196)

''' Map '''
TILE_SIZE = 16
CHUNK_SIZE = 10

''' Fonts '''
FONT_15 = pygame.font.Font("data/cooper_black.ttf", 15)
FONT_10 = pygame.font.Font("data/cooper_black.ttf", 10)

''' Networking '''
PORT = 5555
# SERVER_IP = "192.168.0.5"
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)

SERVER_IP = server_ip

# networking prefixes

def reverse_map(map):
    return {v: k for k, v in map.items()}

STATE_PREFIX_MAP = {"Menu":               "Z",
                    "MatchMaking" :       "M",
                    "CharacterSelection": "C",
                    "Gameplay":           "G"}

NAME_PREFIX_MAP = {"orb_bunny":    "E",
                   "nature_bunny": "Q",
                   "shadow_bunny": "T",
                   "angel_bunny":  "R"}
PREFIX_NAME_MAP = reverse_map(NAME_PREFIX_MAP)

CHARACTER_STATE_PREFIX_MAP = {"idle": "I",
                              "run":  "R"}
PREFIX_CHARACTER_STATE_MAP = reverse_map(CHARACTER_STATE_PREFIX_MAP)


INDEX_BUNNY_MAP = ["OrbBunny", "NatureBunny", "ShadowBunny", "AngelBunny"] # the order of the bunny cards


KEY_ORDERS = "WASDE"
KEY_FUNCTIONS = ["click", "up", "left", "down", "right", "ability"]

RUN_Y_OFFSET = {"orb_bunny":    [0, 1, 3, 1, 0, 1, 3, 1],
                "nature_bunny": [0, 1, 2, 1, 0, 1, 2, 1]}
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
