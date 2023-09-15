from scripts.core_funcs import *

class Card:
    def __init__(self, bunny_name):
        self.card_image = load_image("selection/card.png")
        self.bunny_image = load_image(f"bunny/{bunny_name}/{bunny_name}_concept.png")

        self.center_pos = (0, 0)
        self.mouse_on_card = False

        self.card_outline = pygame.Surface((self.card_image.get_width(), self.card_image.get_height()))
        # self.card_outline.set_colorkey((0,0,0))

        self.mask = pygame.mask.from_surface(self.card_image)

    def update(self, display_pos, mouse_pos):
        self.center_pos = display_pos

        center_x, center_y = display_pos
        width, height = self.card_image.get_width(), self.card_image.get_height()

        self.card_rect = pygame.Rect(center_x - width // 2 , center_y - height // 2, width, height)

        if self.card_rect.collidepoint(mouse_pos):
            self.mouse_on_card = True
        else:
            self.mouse_on_card = False

    def display(self, screen):

        mask_points = self.mask.outline()
        new_points = [(x + self.card_rect.left, y + self.card_rect.top) for x, y in mask_points]

        if self.mouse_on_card:
            pygame.draw.lines(screen, (244, 179, 27), False, new_points, 3)

        display_center(screen, self.card_image, self.center_pos)
        display_center(screen, self.bunny_image, self.center_pos)


class Cards:
    def __init__(self, bunny_names):
        self.cards = [Card(bunny_name) for bunny_name in bunny_names]

        self.START_X = 70
        self.SPACING = 50

    def update(self, mouse_pos):
        for index, card in enumerate(self.cards):
            card.update((self.START_X + index * self.SPACING, 100), mouse_pos)


    def display(self, screen):
        for card in self.cards:
            card.display(screen)
