import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions and circle parameters
WIDTH, HEIGHT = 600, 600
LARGE_CIRCLE_RADIUS = 250
SMALL_CIRCLE_RADIUS = 30
GRAVITY = 0.5
FRICTION = 0.99
BOUNCE_FACTOR = 0.8  # Factor to control the 'bounciness'

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle Physics Simulation")
clock = pygame.time.Clock()

# Circle class
class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= FRICTION
        self.vel_y *= FRICTION

        # Collision detection with the larger circle
        dist = np.hypot(WIDTH/2 - self.x, HEIGHT/2 - self.y)
        if dist + self.radius > LARGE_CIRCLE_RADIUS:
            # Calculate bounce
            overlap = dist + self.radius - LARGE_CIRCLE_RADIUS
            nx, ny = (self.x - WIDTH/2) / dist, (self.y - HEIGHT/2) / dist
            self.x -= overlap * nx
            self.y -= overlap * ny

            # Reflect velocity
            vel_dot_norm = self.vel_x * nx + self.vel_y * ny
            self.vel_x -= 2 * vel_dot_norm * nx * BOUNCE_FACTOR
            self.vel_y -= 2 * vel_dot_norm * ny * BOUNCE_FACTOR

# Initialize circles
large_circle = Circle(WIDTH // 2, HEIGHT // 2, LARGE_CIRCLE_RADIUS, WHITE)
small_circle = Circle(WIDTH // 2, HEIGHT // 2 - LARGE_CIRCLE_RADIUS + SMALL_CIRCLE_RADIUS, SMALL_CIRCLE_RADIUS, RED)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    large_circle.draw()
    small_circle.update()
    small_circle.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
