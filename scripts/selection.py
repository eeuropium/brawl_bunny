from scripts.core_funcs import *

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
        # mask_points = self.mask.outline()
        # new_points = [(x + self.card_rect.left, y + self.card_rect.top) for x, y in mask_points]
        #
        # # draw green outline if card is selected
        # if self.card_state == "selected":
        #     pygame.draw.lines(screen, (182, 213, 60), False, new_points, 3) # green outline
        #
        # # draw yellow outline if mouse is on the card
        # elif self.mouse_on_card:
        #     pygame.draw.lines(screen, (244, 179, 27), False, new_points, 3) # yellow outline

        # draw card and bunny
        display_center(screen, self.card_image, self.center_pos)
        display_center(screen, self.bunny_image, self.center_pos)

        # draw gray mask on top if card is picked in another team
        # if self.card_state == "locked":
        #     self.display_mask = self.mask.to_surface()
        #     self.display_mask = palette_swap(self.display_mask, WHITE, (48, 44, 46)) # dark grey
        #     self.display_mask.set_alpha(180)
        #     display_center(screen, self.display_mask, self.center_pos)

class Cards:
    def __init__(self, bunny_names):
        self.cards = [Card(bunny_name) for bunny_name in bunny_names]

        # colours
        self.MY_BLUE = (138, 236, 241)
        self.NORMAL_BLUE = (40, 205, 223)
        self.MY_RED = (230, 71, 46)
        self.NORMAL_RED = (169, 59, 59)

        self.TOTAL_PLAYERS = 4

        # list to store text objects which display which player is selecting each character
        self.player_texts = []

        self.Y_OFFSET = 30 # offset for texts
        self.Y_COOR = MID_Y

        SPACING = 60
        self.X_COOR = [MID_X - 1.5 * SPACING, MID_X - 0.5 * SPACING, MID_X + 0.5 * SPACING, MID_X + 1.5 * SPACING]


        self.next_state_timer = Timer()
        self.next_state = False # indicates if can move on to next state

    def get_message_to_send(self, inputs, player_number):

        # card states:
        # - open: no players have chosen this card yet
        # - selected: this player currently is selecting this card
        # - locked: this card is selected by other players

        select_index = -1

        for index, card in enumerate(self.cards):
            card.update((self.X_COOR[index], self.Y_COOR), inputs["mouse_pos"])

            if card.is_clicked(inputs["events"]):
                select_index = index

        print(select_index)

        return f"{player_number}:{select_index}"


    def update(self, message, my_player_number): # server message

        self.player_texts = []

        # server has non-empty message
        if message:

            # get data of all clients from server
            client_data = message.split(',')

            # starting end state timer if all player has already selected their characters
            if not self.next_state_timer.is_active() and len(client_data) == self.TOTAL_PLAYERS:
                self.next_state_timer.start()

            if self.next_state_timer.time_elapsed >= 2:
                self.next_state = True

            # processing data
            for data in client_data:
                index, player_number = map(int, data.split(":"))

                # this card is not selected, so no text object displayed
                if player_number == 0:
                    continue

                # assigning colour baesd on player number
                if player_number == my_player_number: # my selection, so uses "my" colour
                    if player_number <= self.TOTAL_PLAYERS // 2:
                        colour = self.MY_BLUE
                    else:
                        colour = self.MY_RED
                else:
                    if player_number <= self.TOTAL_PLAYERS // 2:
                        colour = self.NORMAL_BLUE
                    else:
                        colour = self.NORMAL_RED

                # assign text string (what string to display)
                if player_number == my_player_number:
                    text_string = "YOU"
                else:
                    text_string = f"P{player_number}"

                # render text object
                text = FONT_15.render(text_string, False, colour)

                # add it to list of displayed player texts
                self.player_texts.append((text, (self.X_COOR[index], self.Y_COOR - self.Y_OFFSET)))


    def display(self, screen):
        # display cards
        for card in self.cards:
            card.display(screen)

        # display text on top of cards
        for player_text, coor in self.player_texts:
            display_center(screen, player_text, coor)
