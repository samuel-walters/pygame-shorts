import pygame
import numpy as np
import pygame.midi
import time
import threading

# Initialize Pygame and Pygame MIDI
pygame.init()
pygame.midi.init()

# MIDI setup
midi_output = pygame.midi.Output(0)
midi_output.set_instrument(0)

# Function to play a MIDI note asynchronously
def play_midi_note_async(note, duration=100):
    def play_note():
        midi_output.note_on(note, velocity=127)
        time.sleep(duration / 1000)
        midi_output.note_off(note, velocity=127)
    threading.Thread(target=play_note).start()

# Constants
WIDTH, HEIGHT = 600, 600
LARGE_CIRCLE_RADIUS = 250
SMALL_CIRCLE_RADIUS = 30
GRAVITY = 9.81 / 60.0  # Assuming 60 frames per second
FRICTION = 0.1  # Kinetic friction
STATIC_FRICTION_THRESHOLD = 2.0
BOUNCE_FACTOR = 0.7
SOUND_COOLDOWN = 0.2

# Initial velocity for the small ball
INITIAL_SPEED = 15.0
INITIAL_ANGLE = np.radians(45)

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
        self.last_sound_time = time.time()

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self, note_to_play, play_sound=False):
        current_time = time.time()

        # Apply gravity
        gravity_force = GRAVITY
        self.vel_y += gravity_force

        # Calculate next position
        next_x = self.x + self.vel_x
        next_y = self.y + self.vel_y

        # Check for collision with large circle
        dist = np.hypot(WIDTH / 2 - next_x, HEIGHT / 2 - next_y)
        if dist + self.radius >= LARGE_CIRCLE_RADIUS:
            # Collision detected, resolve it
            nx, ny = (next_x - WIDTH / 2) / dist, (next_y - HEIGHT / 2) / dist
            overlap = (dist + self.radius) - LARGE_CIRCLE_RADIUS

            # Position correction
            self.x -= overlap * nx
            self.y -= overlap * ny

            # Reflect velocity
            vel_dot_norm = self.vel_x * nx + self.vel_y * ny
            self.vel_x -= 2 * vel_dot_norm * nx * BOUNCE_FACTOR
            self.vel_y -= 2 * vel_dot_norm * ny * BOUNCE_FACTOR

            # Play sound on collision
            if play_sound and current_time - self.last_sound_time > SOUND_COOLDOWN:
                play_midi_note_async(note_to_play)
                self.last_sound_time = current_time
                note_to_play = (note_to_play + 1) % 128

        # Friction and rolling
        if dist + self.radius > LARGE_CIRCLE_RADIUS:
            # Static friction
            if np.hypot(self.vel_x, self.vel_y) < STATIC_FRICTION_THRESHOLD:
                self.vel_x, self.vel_y = 0, 0
            else:
                # Kinetic friction
                friction_force = FRICTION * gravity_force
                self.vel_x -= np.sign(self.vel_x) * friction_force
                self.vel_y -= np.sign(self.vel_y) * friction_force

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        return note_to_play

# Initialize circles
large_circle = Circle(WIDTH // 2, HEIGHT // 2, LARGE_CIRCLE_RADIUS, WHITE)
small_circle = Circle(WIDTH // 2, HEIGHT // 2 - LARGE_CIRCLE_RADIUS + SMALL_CIRCLE_RADIUS, SMALL_CIRCLE_RADIUS, RED, INITIAL_SPEED * np.cos(INITIAL_ANGLE), INITIAL_SPEED * np.sin(INITIAL_ANGLE))

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
