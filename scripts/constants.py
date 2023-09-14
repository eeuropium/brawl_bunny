import pygame
import time
import random
import math
import sys

pygame.init()

''' FPS '''
FPS = 60 # this is the maximum FPS

''' Display Info '''
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

SCALE_RATIO = 20
WIDTH = 16 * SCALE_RATIO # 16 : 9 scaled by SCALE_RATIO
HEIGHT = 9 * SCALE_RATIO

MID_X = WIDTH // 2
MID_Y = HEIGHT // 2

''' Colours '''
BLACK = (0  , 0  , 0  )
WHITE = (255, 255, 255)

WATER_BLUE = (48, 162, 196)

''' Map '''
TILE_SIZE = 16
CHUNK_SIZE = 10



# TBD names
# good bunnies:
# orb_bunny - Eunova
# nature_bunny - Quillia
# angel_bunny - Areisa
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
