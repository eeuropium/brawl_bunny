from scripts.constants import *

# physics
def angle_move_x(angle, speed):
    return speed * math.sin(math.radians(angle))

def angle_move_y(angle, speed):
    return -speed * math.cos(math.radians(angle)) # negative needed because up is negative in pygame coordinate system

class Particle():
    def __init__(self, x, y, angle, speed, radius, decay_rate, colour):
        self.x = x
        self.y = y

        self.dx = angle_move_x(angle, speed)
        self.dy = angle_move_y(angle, speed)

        self.radius = radius
        self.diameter = 2 * radius

        self.decay_rate = decay_rate

        self.colour = colour

    def update(self):
        self.x += self.dx
        self.y += self.dy

        self.radius -= self.decay_rate

    # only for out of screen
    def should_remove(self):
        return (self.radius < 0 or
                self.x < -self.diameter or # checking for out of bounds
                self.x > WIDTH + self.diameter or
                self.y < -self.diameter or
                self.y > HEIGHT + self.diameter)

    def display(self, screen, offset_x, offset_y):
        display_coor = (int(self.x) + offset_x, int(self.y) + offset_y)
        pygame.draw.circle(screen, self.colour, display_coor, self.radius)

    def get_bottom_y(self):
        return self.y + self.radius

# particle group
class Particles():
    def __init__(self):
        self.particles = []

    def add_particles(self, spawn_x, spawn_y, number):
        for i in range(number):
            self.particles.append(Particle(
            spawn_x,
            spawn_y,
            random.randint(-30, 30), # angle
            random.randint(1, 10) / 10, # speed
            random.randint(7, 12), # radius
            random.randint(3, 9) / 10, # decay rate between 0.3 and 0.9
            random.choice([(125, 112, 113), (160, 147, 142), (90, 83, 83), (48, 44, 46)])
            ))

    def update(self):
        new_particles = []

        for particle in self.particles:
            particle.update()

            if not particle.should_remove():
                new_particles.append(particle)

        self.particles = new_particles


    def display(self):
        for particle in self.particles:
            particle.display()
