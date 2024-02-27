from scripts.constants import *
from scripts.core_funcs import *

''' Text and Buttons '''

class Text():
    def __init__(self, font_name, colour, text, coordinates):
        self.colour = colour
        self.coordinates = coordinates

        # get the font and font_size from the font string given
        self.font = eval(font_name)
        self.font_size = int(font_name.split('_')[1])

        # render the text surface
        self.text_surf = self.font.render(text, False, self.colour)

    def display(self, screen, *optional_text):
        # re-render the text_surface is an optional text is given
        if optional_text:
            self.text_surf = self.font.render(optional_text[0], False, self.colour)

        # display the font surface
        display_center(screen, self.text_surf, self.coordinates)

class Button():
    def __init__(self, font_name, text, coordinates):
        # create text object
        self.font = font_name

        self.mouse_off_text = Text(self.font, (238, 160, 96), text, coordinates)
        self.mouse_on_text = Text(self.font, (244, 204, 161), text, coordinates)

        self.coordinates = coordinates

        # determine button width and height
        text_surf = self.mouse_on_text.font.render(text, False, (238, 160, 96))
        self.width, self.height = text_surf.get_width(), text_surf.get_height()

        self.background_added_x, self.background_added_y = 10, 4
        self.border_added_x, self.border_added_y = 14, 8

        total_w, total_h = self.width + self.border_added_x, self.height + self.border_added_y
        self.collision_rect = pygame.Rect(coordinates[0] - total_w // 2, coordinates[1] - total_h // 2, total_w, total_h)


    def display(self, screen, mouse_pos):
        # display different things depending on if the mouse is on the button
        if self.collision_rect.collidepoint(mouse_pos):
            center_draw_rect(screen, (122, 68, 74), (self.coordinates[0], self.coordinates[1], self.width + self.border_added_x, self.height + self.border_added_y), border_radius = 10)
            center_draw_rect(screen, (191, 121, 88), (self.coordinates[0], self.coordinates[1], self.width + self.background_added_x, self.height + self.background_added_y), border_radius = 10)
            self.mouse_on_text.display(screen)
        else:
            center_draw_rect(screen, (122, 68, 74), (self.coordinates[0], self.coordinates[1], self.width + self.border_added_x, self.height + self.border_added_y), border_radius = 10)
            center_draw_rect(screen, (160, 91, 83), (self.coordinates[0], self.coordinates[1], self.width + self.background_added_x, self.height + self.background_added_y), border_radius = 10)
            self.mouse_off_text.display(screen)

    def is_clicked(self, events, mouse_pos):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.collision_rect.collidepoint(mouse_pos):
                    return True
                return False

class Timer():
    def __init__(self):
        self.active = False

    def is_active(self):
        return self.active

    def start(self):
        self.start_time = time.time()
        self.active = True

    def end(self):
        self.active = False

    def time_elapsed(self):
        return time.time() - self.start_time

    def restart(self):
        self.start_time = time.time()

class LimitTimer(Timer):
    def __init__(self, time_limit):
        super().__init__()
        self.time_limit = time_limit
        self.time_offset = 0

    def end(self):
        super().end()
        self.time_offset = 0
        
    def is_over(self):
        return (self.time_elapsed() + self.time_offset) >= self.time_limit

    def get_t_value(self):
        return (self.time_elapsed() + self.time_offset) / self.time_limit

    def set_t_value(self, t):
        self.time_offset = (t - self.get_t_value()) * self.time_limit

class EndStateTimer(Timer):
    def __init__(self, wait_time):
        super().__init__()
        self.wait_time = wait_time

    def next_state(self, condition): # condition to move onto next state
        if not self.active and condition:
            self.start()

        if self.active and self.time_elapsed() >= self.wait_time:
            return True

        return False
