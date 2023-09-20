from scripts.constants import *

''' import / loading data '''

def load_image(path):
    image = pygame.image.load("data/images/" + path).convert_alpha()
    return image

def load_spritesheet(spritesheet_image, frame_width, frame_height):
    columns = spritesheet_image.get_width() // frame_width
    rows = spritesheet_image.get_height() // frame_height

    frames = []

    # cut each frame out and put into the list
    for y in range(0, spritesheet_image.get_height(), frame_height):
        for x in range(0, spritesheet_image.get_width(), frame_width):
            frames.append(spritesheet_image.subsurface(x, y, frame_width, frame_height))

    # pattern:
    # ---->----
    # ---->----
    # ---->----

    return frames

''' displays '''

def display_center(screen, surf, coordinates): # surf is usually an image
    surf_rect = surf.get_rect(center = coordinates)
    screen.blit(surf, surf_rect)

''' calculations '''

def calc_chunk_xy(x, y):
    chunk_x = int(x // (CHUNK_SIZE * TILE_SIZE))
    chunk_y = int(x // (CHUNK_SIZE * TILE_SIZE))

    return chunk_x, chunk_y

def get_box(path):
    hitbox_image = load_image(f"{path}")

    image_width = hitbox_image.get_width()
    image_height = hitbox_image.get_height()

    found = False

    # pixel will be non-transparent if it is part of the hitbox
    # pixel will be transparent if it is not part of the hitbox
    # we use image.get_at((x, y)) and check the alpha channel of the pixel to determine the transparency

    # find top left point
    for y in range(image_height):
        for x in range(image_width):
            if hitbox_image.get_at((x, y)).a != 0:
                top = y
                left = x

                # end program when found
                found = True
                break
        if found:
            break

    # find width of hitbox
    for x in range(left, image_width):
        if hitbox_image.get_at((x, top)).a == 0:
            width = x - left
            break

    # find height of hitbox
    for y in range(top, image_height):
        if hitbox_image.get_at((left, y)).a == 0:
            height = y - top
            break

    return left, top, width, height

''' colours '''

def palette_swap(org_image, old_colour, new_colour):
    black_surf = pygame.Surface(org_image.get_size())
    black_surf.blit(org_image, (0, 0))
    black_surf.set_colorkey(old_colour)

    final_surf = pygame.Surface(org_image.get_size())
    final_surf.fill(new_colour)
    final_surf.blit(black_surf, (0 ,0))
    final_surf.set_colorkey((0, 0, 0))

    return final_surf
