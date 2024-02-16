import pygame
import numpy as np
import pygame.midi

# Initialize Pygame and Pygame MIDI
pygame.init()
pygame.midi.init()

# MIDI setup
midi_output = pygame.midi.Output(0)
midi_output.set_instrument(0)

# Function to play a MIDI note
def play_midi_note(note, duration=100):
    midi_output.note_on(note, velocity=127)
    pygame.time.delay(duration)
    midi_output.note_off(note, velocity=127)

# Constants
WIDTH, HEIGHT = 600, 600
LARGE_CIRCLE_RADIUS = 250
SMALL_CIRCLE_RADIUS = 30
GRAVITY = 0.5
FRICTION = 0.99
BOUNCE_FACTOR = 0.8
MIN_VELOCITY_FOR_SOUND = 1.0
VELOCITY_CHANGE_FOR_SOUND = 1.0

# Initial velocity for the small circle
INITIAL_VELOCITY = 5
INITIAL_ANGLE = np.pi / 4  # 45 degrees

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle Physics Simulation")
clock = pygame.time.Clock()

# Circle class
class Circle:
    def __init__(self, x, y, radius, color, vel_x=0, vel_y=0):
        self.x, self.y = x, y
        self.radius = radius
        self.color = color
        self.vel_x, self.vel_y = vel_x, vel_y

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self, note_to_play, play_sound=False):
        initial_velocity = np.hypot(self.vel_x, self.vel_y)
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= FRICTION
        self.vel_y *= FRICTION

        dist = np.hypot(WIDTH/2 - self.x, HEIGHT/2 - self.y)
        if dist + self.radius >= LARGE_CIRCLE_RADIUS:
            overlap = dist + self.radius - LARGE_CIRCLE_RADIUS
            nx, ny = (self.x - WIDTH/2) / dist, (self.y - HEIGHT/2) / dist
            vel_dot_norm = self.vel_x * nx + self.vel_y * ny
            self.vel_x -= 2 * vel_dot_norm * nx * BOUNCE_FACTOR
            self.vel_y -= 2 * vel_dot_norm * ny * BOUNCE_FACTOR
            self.x -= overlap * nx
            self.y -= overlap * ny
            
            final_velocity = np.hypot(self.vel_x, self.vel_y)
            velocity_change = abs(final_velocity - initial_velocity)

            if play_sound and (initial_velocity > MIN_VELOCITY_FOR_SOUND or velocity_change > VELOCITY_CHANGE_FOR_SOUND):
                play_midi_note(note_to_play)
                return (note_to_play + 1) % 128
        return note_to_play

# Initialize circles
large_circle = Circle(WIDTH // 2, HEIGHT // 2, LARGE_CIRCLE_RADIUS, WHITE)
small_circle = Circle(WIDTH // 2, HEIGHT // 2 - LARGE_CIRCLE_RADIUS + SMALL_CIRCLE_RADIUS, SMALL_CIRCLE_RADIUS, RED, INITIAL_VELOCITY * np.cos(INITIAL_ANGLE), INITIAL_VELOCITY * np.sin(INITIAL_ANGLE))

note_to_play = 60  # Middle C

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    large_circle.draw()
    note_to_play = small_circle.update(note_to_play, play_sound=True)
    small_circle.draw()

    pygame.display.flip()
    clock.tick(60)

# Clean up
midi_output.close()
pygame.midi.quit()
pygame.quit()
