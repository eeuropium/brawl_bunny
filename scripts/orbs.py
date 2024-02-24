from scripts.constants import *
import numpy as np

SCALE = 20

class Orbs():
    def __init__(self, n): # n is the number of orbs
        # assigning initial empty array
        self.points_3d = np.zeros(shape = (n, 3))
        # n rows to store x, y, z coordinates of the n ords

        theta = 15 # initial anti-clockwise angle

        for i in range(n):
            # assigning points
            self.points_3d[i] = [math.cos(math.radians(theta)), math.sin(math.radians(theta)), 0]

            # increase the angle by a fixed amount
            theta += 360 / n

        self.points_2d = []

        # rotation angles - the angle to rotate our cube in each axis
        self.rot_x_angle = 0
        self.rot_y_angle = 0
        self.rot_z_angle = 0

        # rotation speeds - the speed at which the rotation angles increases
        self.rot_x_speed = 0
        self.rot_y_speed = 0
        self.rot_z_speed = 3

        self.start_time = time.time()

    # increase the rotation angles
    def rotate(self):
        self.rot_x_angle += self.rot_x_speed
        self.rot_y_angle += self.rot_y_speed
        self.rot_z_angle += self.rot_z_speed

    # apply the rotation transformations and get our projected 2D coordinates
    def apply_transformations(self, player_x, player_y):
        # initialise our projected_points to be initially same as points_3d
        projected_points = self.points_3d

        # apply the transformations
        projected_points = np.dot(projected_points, rot_x_matrix(math.radians(self.rot_x_angle + 30 * math.sin(time.time() - self.start_time)))) # perform x rotation
        projected_points = np.dot(projected_points, rot_y_matrix(math.radians(self.rot_y_angle))) # perform y rotation
        projected_points = np.dot(projected_points, rot_z_matrix(math.radians(self.rot_z_angle))) # perform z rotation

        # get points in terms of screen coordinates by scaling and offsetting
        self.points_2d = [(x * SCALE + player_x, z * SCALE + player_y, 5 + 2 * y) for x, y, z in projected_points]
        # x, y, and radius

        # x axis - left, right
        # y axis - into and out of the page
        # z axis - up and down

    def get_info(self):
        return self.points_2d

    def get_send_message(self):
        s = ""

        if len(self.points_2d) == 0:
            s += "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"

        for x, y, radius in self.points_2d:
            s += f"{int(x)},{int(y)},{int(radius)},"

        return s[:-1]

    def draw_points(self, screen):
        # draw the points (vertices) onto the screen
        for x, y, radius in self.points_2d:
            pygame.draw.circle(screen, BLACK, (x, y), radius)

    # shows the index of each point
    def display_points_index(self, screen):
        for index in range(len(self.points_2d)):
            number_text = FONT.render(str(index), True, BLACK)

            x, y, radius = self.points_2d[index]
            y += 10 # offset the text

            # display the text
            screen.blit(number_text, (x, y))

# linear transformation matrix for rotation in x, y, z axis
def rot_x_matrix(angle):
    return np.array([
    [1, 0, 0],
    [0, math.cos(angle), -math.sin(angle)],
    [0, math.sin(angle), math.cos(angle)]
    ])

def rot_y_matrix(angle):
    return np.array([
    [math.cos(angle), 0, math.sin(angle)],
    [0, 1, 0],
    [-math.sin(angle), 0, math.cos(angle)]
    ])

def rot_z_matrix(angle):
    return np.array([
    [math.cos(angle), -math.sin(angle), 0],
    [math.sin(angle), math.cos(angle), 0],
    [0, 0, 1]
    ])


    # # only increase the rotation angles if the A key is pressed
    # if (keys[pygame.K_a]):
    #     orb1.rotate()
    #
    # orb1.apply_transformations()
    #
    # orb1.draw_points(screen)
    #
    # # orb1.display_points_index(screen)
