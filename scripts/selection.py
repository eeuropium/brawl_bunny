from scripts.core_funcs import *
from scripts.managers import EndStateTimer

class Card:
    def __init__(self, bunny_name):
        self.card_image = load_image("gamestates/character_selection/card.png")
        self.bunny_image = load_image(f"bunny/{bunny_name}/{bunny_name}_concept.png")

        self.center_pos = (0, 0)
        self.mouse_on_card = False

        self.mask = pygame.mask.from_surface(self.card_image)

    def update(self, display_pos, mouse_pos):
        self.center_pos = display_pos
        self.card_rect = self.card_image.get_rect(center = (display_pos))

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
        # draw card and bunny
        display_center(screen, self.card_image, self.center_pos)
        display_center(screen, self.bunny_image, self.center_pos)

class Cards:
    def __init__(self, bunny_names):
        self.cards = [Card(bunny_name) for bunny_name in bunny_names]

        self.TOTAL_PLAYERS = 4

        # list to store text objects which display which player is selecting each character
        self.player_texts = []

        self.Y_OFFSET = 30 # offset for texts
        self.Y_COOR = MID_Y

        SPACING = 60
        self.X_COOR = [MID_X - 1.5 * SPACING, MID_X - 0.5 * SPACING, MID_X + 0.5 * SPACING, MID_X + 1.5 * SPACING]


        self.next_state_timer = EndStateTimer(2)
        self.next_state = False # indicates if can move on to next state

    def get_message_to_send(self, inputs, player_number):
        select_index = -1

        for index, card in enumerate(self.cards):
            card.update((self.X_COOR[index], self.Y_COOR), inputs["mouse_pos"])

            if card.is_clicked(inputs["events"]):
                select_index = index

        # testing (auto-selection)
        if TESTING:
            return f"{player_number}:{player_number - 1}"

        # actual
        return f"{player_number}:{select_index}"

    def update(self, message, my_player_number): # server message

        self.player_texts = []

        # server has non-empty message
        if message:
            # get data of all clients from server
            client_data = message.split(',')

            all_players_selected = True

            # processing data
            for data in client_data:
                index, player_number = map(int, data.split(":"))

                # this card is not selected, so no text object displayed
                if player_number == 0:
                    all_players_selected = False
                    continue

                # assigning colour baesd on player number
                colour = get_player_colour(player_number, my_player_number)

                # assign text string (what string to display)
                if player_number == my_player_number:
                    text_string = "YOU"
                else:
                    text_string = f"P{player_number}"

                # render text object
                text = FONT_15.render(text_string, False, colour)

                # add it to list of displayed player texts
                self.player_texts.append((text, (self.X_COOR[index], self.Y_COOR - self.Y_OFFSET)))

            # move on to next state if all player has already selected their characters
            self.next_state = self.next_state_timer.next_state(all_players_selected)

    def display(self, screen):
        # display cards
        for card in self.cards:
            card.display(screen)

        # display text on top of cards
        for player_text, coor in self.player_texts:
            display_center(screen, player_text, coor)

    def move_next_state(self):
        return self.next_state
