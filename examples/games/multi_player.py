import math
from collections import namedtuple

import pygame

from qwstpad import ADDRESSES, QwSTPad

WIDTH, HEIGHT = 500, 500

# Gameplay Constants
PlayerDef = namedtuple("PlayerDef", ("x", "y", "colour"))
PLAYERS = (PlayerDef(x=30, y=50, colour="GREEN"),
           PlayerDef(x=280, y=50, colour="MAGENTA"),
           PlayerDef(x=30, y=200, colour="CYAN"),
           PlayerDef(x=280, y=200, colour="BLUE"))
PLAYER_RADIUS = 10
PLAYER_SPEED = 4
LINE_LENGTH = 25
START_ANGLE = 20
PROJECTILE_LIMIT = 15
PROJECTILE_SPEED = 5
GRID_SPACING = 20
SCORE_TARGET = 1000
TEXT_SHADOW = 2

# Colour Constants
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
CYAN = pygame.Color(0, 255, 255)
MAGENTA = pygame.Color(255, 0, 255)
YELLOW = pygame.Color(255, 255, 0)
GREEN = pygame.Color(0, 255, 0)
RED = pygame.Color(255, 0, 0)
BLUE = pygame.Color(0, 0, 255)
GREY = pygame.Color(115, 115, 115)

players = []                                    # The list that will store the player objects
complete = False                                # Has the game been completed?

pygame.init()
pygame.display.set_caption('Multi-Player')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 28)
running = True


# Classes
class Projectile:
    def __init__(self, x, y, direction, colour):
        self.x = x
        self.y = y
        self.direction = direction
        self.colour = colour

    def update(self):
        self.x += PROJECTILE_SPEED * math.cos(self.direction)
        self.y += PROJECTILE_SPEED * math.sin(self.direction)

    def draw(self):
        pygame.draw.rect(screen, self.colour, pygame.Rect(int(self.x), int(self.y), 1, 1))

    def is_on_screen(self):
        return self.x >= 0 and self.x < WIDTH and self.y >= 0 and self.y < HEIGHT

    def has_hit(self, player):
        xdiff = self.x - player.x
        ydiff = self.y - player.y

        sqdist = xdiff ** 2 + ydiff ** 2
        return sqdist < player.size ** 2


class Player:
    def __init__(self, index, x, y, size, colour, pad):
        self.index = index
        self.x = x
        self.y = y
        self.direction = math.radians(START_ANGLE)
        self.size = size
        self.colour = colour
        self.pad = pad

        self.projectiles = []
        self.was_hit = False
        self.score = 0

    def fire(self):
        if len(self.projectiles) < PROJECTILE_LIMIT:
            self.projectiles.append(Projectile(self.x, self.y, self.direction, self.colour))

    def update(self):
        # Read the player's gamepad
        button = self.pad.read_buttons()

        if button['L']:
            self.direction -= 0.1

        if button['R']:
            self.direction += 0.1

        if button['U']:
            self.x += PLAYER_SPEED * math.cos(self.direction)
            self.y += PLAYER_SPEED * math.sin(self.direction)

        if button['D']:
            self.x -= PLAYER_SPEED * math.cos(self.direction)
            self.y -= PLAYER_SPEED * math.sin(self.direction)

        # Clamp the player to the screen area
        self.x = min(max(self.x, self.size), WIDTH - self.size)
        self.y = min(max(self.y, self.size), HEIGHT - self.size)

        if button['A']:
            self.fire()

        new_proj = []
        for projectile in self.projectiles:
            projectile.update()
            if projectile.is_on_screen():
                new_proj.append(projectile)

        self.projectiles = new_proj

    def hit(self):
        self.was_hit = True
        self.pad.set_leds(0b1111)

    def draw(self):
        x, y = int(self.x), int(self.y)
        pygame.draw.circle(screen, self.colour, (x, y), self.size)
        pygame.draw.circle(screen, "black" if not self.was_hit else "red", (x, y), self.size - 1)

        self.was_hit = False
        self.pad.set_leds(self.pad.address_code())

        # Draw the direction line in our colour
        pygame.draw.line(screen, self.colour, (x, y), (int(self.x + (LINE_LENGTH * math.cos(self.direction))), int(self.y + (LINE_LENGTH * math.sin(self.direction)))))

        # Draw the projectiles in our colour
        for p in self.projectiles:
            p.draw()

        # Draw our score at the bottom of the screen
        score_text = font.render(f"P{self.index + 1}: {self.score}", True, self.colour, None)
        screen.blit(score_text, (5 + self.index * 120, HEIGHT - 30))

    def check_hits(self, players):
        for other in players:
            if other is not self:
                for projectile in self.projectiles:
                    if projectile.has_hit(other):
                        other.hit()
                        self.score += 1


# Create a player for each connected QwSTPad
for i in range(len(ADDRESSES)):
    try:
        p = PLAYERS[i]
        pad = QwSTPad(address=ADDRESSES[i])
        players.append(Player(i, p.x, p.y, PLAYER_RADIUS, p.colour, pad))
        print(f"P{i + 1}: Connected")
    except OSError:
        print(f"P{i + 1}: Not Connected")

if len(players) == 0:
    print("No QwSTPads connected ... Exiting")
    raise SystemExit

print("QwSTPads connected ... Starting")

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen to the background colour
        screen.fill("black")

        if not complete:
            # Update all players (and their projectiles)
            for p in players:
                try:
                    p.update()
                # Handle QwSTPads being disconnected unexpectedly
                except OSError:
                    print(f"P{p.index + 1}: Disconnected ... Exiting")
                    raise SystemExit

                # Check if any projectiles have hit players
                for p in players:
                    p.check_hits(players)

                    # Check if any player has reached the score target
                    if p.score >= SCORE_TARGET:
                        complete = True

            # Draw a grid for the background
            for x in range(0, WIDTH, GRID_SPACING):
                for y in range(0, HEIGHT, GRID_SPACING):
                    pygame.draw.rect(screen, GREY, pygame.Rect(x, y, 1, 1))

            # Draw players
            for p in players:
                p.draw()

        if complete:

            pygame.draw.rect(screen, "black", pygame.Rect(4, HEIGHT // 2 - 96, WIDTH, 100))
            pygame.draw.rect(screen, GREEN, pygame.Rect(0, HEIGHT // 2 - 100, WIDTH, 100))

            banner_text_size_1 = font.size("Game Complete!!")
            banner_text_shadow_1 = font.render("Game Complete!!", True, "black", None)
            banner_text_1 = font.render("Game Complete!!", True, "white", None)

            screen.blit(banner_text_shadow_1, ((WIDTH // 2) - (banner_text_size_1[0] // 2 + TEXT_SHADOW), (HEIGHT // 2 - 50) - (banner_text_size_1[1] // 2) + TEXT_SHADOW))
            screen.blit(banner_text_1, ((WIDTH // 2) - (banner_text_size_1[0] // 2), (HEIGHT // 2 - 50) - (banner_text_size_1[1] // 2)))

        # Update the screen
        pygame.display.flip()
        clock.tick(60)

finally:
    for p in players:
        try:
            p.pad.clear_leds()
        except OSError:
            pass
