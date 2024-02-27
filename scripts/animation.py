from scripts.constants import *
from scripts.core_funcs import *

class Animation():
    def __init__(self, spritesheet_path, frame_width, frame_height, frame_interval = FRAME_INTERVAL):

        spritesheet_image = load_image(spritesheet_path)

        self.frame_interval = frame_interval

        self.frames = load_spritesheet(spritesheet_image, frame_width, frame_height)

        self.start_time = time.time()

    def get_cycles(self): # returns the number of times the animation has been looped through
        return (time.time() - self.start_time) // (self.frame_interval * len(self.frames))

    def get_frame_index(self):
        # calculate the current frame index - must round to integer
        return int(((time.time() - self.start_time) // self.frame_interval) % len(self.frames))

    def get_frame(self):
        return self.frames[self.get_frame_index()]

    def reset(self):
        self.start_time = time.time()

class SingleAnimation(Animation):
    def __init__(self, spritesheet_path, frame_width, frame_height, frame_interval = FRAME_INTERVAL):
        super().__init__(spritesheet_path, frame_width, frame_height, frame_interval = FRAME_INTERVAL)

    def get_first_frame(self):
        return self.frames[0]

    def start(self):
        self.reset()

    def ended(self):
        return self.get_cycles() >= 1
