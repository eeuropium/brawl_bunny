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
        # blue cards and red cards separate to represent choosing characters from opposite teams
        # self.blue_cards = [Card(bunny_name) for bunny_name in bunny_names]
        # self.red_cards = [Card(bunny_name) for bunny_name in bunny_names]

        # self.cards = {"BLUE": [Card(bunny_name) for bunny_name in bunny_names],
        #               "RED": [Card(bunny_name) for bunny_name in bunny_names]}
        #
        # # constants to define the coordinates of placing the cards
        # self.START_X = 70
        # self.SPACING = 60
        # self.Y_COOR = {"BLUE" : 50, "RED" : 120}
        #
        # self.selected_index = -1
        #
        # self.teams = ["BLUE", "RED"]

        self.START_X = 70
        self.SPACING = 60
        self.Y_COOR = 50

        self.cards = [Card(bunny_name) for bunny_name in bunny_names]

        # colours
        self.MY_BLUE = (138, 236, 241)
        self.NORMAL_BLUE = (40, 205, 223)
        self.MY_RED = (230, 71, 46)
        self.NORMAL_RED = (169, 59, 59)

        self.TOTAL_PLAYERS = 4
        #
        # # initiating player_texts map (text objects)
        # for player_number in range(1, 5):
        #     # assigning colour baesd on player number
        #     if player_number == my_player_number: # my selection, so uses "my" colour
        #         if i <= TOTAL_PLAYERS // 2:
        #             colour = MY_BLUE
        #         else:
        #             colour = MY_RED
        #     else:
        #         if i <= TOTAL_PLAYERS // 2:
        #             colour = NORMAL_BLUE
        #         else:
        #             colour = NORMAL_RED
        #
        #     self.player_texts[player_number] = Text("FONT_15", colour, f"P{player_number}", self.START_X + (player_number - 1) * self.SPACING, self.Y_COOR - 50)

        self.player_texts = []

    def get_message_to_send(self, inputs, player_number):

        # card states:
        # - open: no players have chosen this card yet
        # - selected: this player currently is selecting this card
        # - locked: this card is selected by other players

        select_index = -1

        for index, card in enumerate(self.cards):
            card.update((self.START_X + index * self.SPACING, self.Y_COOR), inputs["mouse_pos"])

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
                self.player_texts.append((text, (self.START_X + index * self.SPACING - 20, self.Y_COOR - 50)))


        # for team in self.teams:
        #     for index, card in enumerate(self.cards[team]):
        #         # set card state - selected, locked or open
        #         if self.selected_index == index:
        #             if self.selected_team == team:
        #                 card_state = "selected"
        #             else:
        #                 card_state = "locked"
        #         else:
        #             card_state = "open"
        #
        #         # update must come before is_clicked as update checks the position of the mouse
        #         card.update((self.START_X + index * self.SPACING, self.Y_COOR[team]), inputs["mouse_pos"], card_state)
        #
        #         # select card is mosue is clicked
        #         if card.is_clicked(inputs["events"]):
        #             self.selected_index = index
        #             self.selected_team = team

    def display(self, screen):
        for card in self.cards:
            card.display(screen)

        for player_text, coor in self.player_texts:
            screen.blit(player_text, coor)
