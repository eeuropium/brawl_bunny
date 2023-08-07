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
