from scripts.core_funcs import *

class Card:
    def __init__(self, bunny_name):
        self.card_image = load_image("selection/card.png")
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
