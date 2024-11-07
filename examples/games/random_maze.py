from qwstpad import QwSTPad
import time
import random
import pygame
from collections import namedtuple
import gc

WIDTH, HEIGHT = 500, 500

PLAYER = pygame.Color(227, 231, 110)
WALL = pygame.Color(127, 125, 244)
BACKGROUND = pygame.Color(60, 57, 169)
PATH = pygame.Color((227 + 60) // 2, (231 + 57) // 2, (110 + 169) // 2)

# Gameplay Constants
Position = namedtuple("Position", ("x", "y"))
MIN_MAZE_WIDTH = 2
MAX_MAZE_WIDTH = 5
MIN_MAZE_HEIGHT = 2
MAX_MAZE_HEIGHT = 5
WALL_SHADOW = 4
WALL_GAP = 1
TEXT_SHADOW = 4
MOVEMENT_SLEEP = 0.1
DIFFICULT_SCALE = 0.5

# Variables
complete = False  # Has the game been completed?
level = 0


# Classes
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bottom = True
        self.right = True
        self.visited = False

    @staticmethod
    def remove_walls(current, next):
        dx, dy = current.x - next.x, current.y - next.y
        if dx == 1:
            next.right = False
        if dx == -1:
            current.right = False
        if dy == 1:
            next.bottom = False
        if dy == -1:
            current.bottom = False


class MazeBuilder:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.cell_grid = []
        self.maze = []

    def build(self, width, height):
        if width <= 0:
            raise ValueError("width out of range. Expected greater than 0")

        if height <= 0:
            raise ValueError("height out of range. Expected greater than 0")

        self.width = width
        self.height = height

        # Set the starting cell to the centre
        cx = (self.width - 1) // 2
        cy = (self.height - 1) // 2

        gc.collect()

        # Create a grid of cells for building a maze
        self.cell_grid = [[Cell(x, y) for y in range(self.height)] for x in range(self.width)]
        cell_stack = []

        # Retrieve the starting cell and mark it as visited
        current = self.cell_grid[cx][cy]
        current.visited = True

        # Loop until every cell has been visited
        while True:
            next = self.choose_neighbour(current)
            # Was a valid neighbour found?
            if next is not None:
                # Move to the next cell, removing walls in the process
                next.visited = True
                cell_stack.append(current)
                Cell.remove_walls(current, next)
                current = next

            # No valid neighbour. Backtrack to a previous cell
            elif len(cell_stack) > 0:
                current = cell_stack.pop()

            # No previous cells, so exit
            else:
                break

        gc.collect()

        # Use the cell grid to create a maze grid of 0's and 1s
        self.maze = []

        row = [1]
        for x in range(0, self.width):
            row.append(1)
            row.append(1)
        self.maze.append(row)

        for y in range(0, self.height):
            row = [1]
            for x in range(0, self.width):
                row.append(0)
                row.append(1 if self.cell_grid[x][y].right else 0)
            self.maze.append(row)

            row = [1]
            for x in range(0, self.width):
                row.append(1 if self.cell_grid[x][y].bottom else 0)
                row.append(1)
            self.maze.append(row)

        self.cell_grid.clear()
        gc.collect()

        self.grid_columns = (self.width * 2 + 1)
        self.grid_rows = (self.height * 2 + 1)

    def choose_neighbour(self, current):
        unvisited = []
        for dx in range(-1, 2, 2):
            x = current.x + dx
            if x >= 0 and x < self.width and not self.cell_grid[x][current.y].visited:
                unvisited.append((x, current.y))

        for dy in range(-1, 2, 2):
            y = current.y + dy
            if y >= 0 and y < self.height and not self.cell_grid[current.x][y].visited:
                unvisited.append((current.x, y))

        if len(unvisited) > 0:
            x, y = random.choice(unvisited)
            return self.cell_grid[x][y]

        return None

    def maze_width(self):
        return (self.width * 2) + 1

    def maze_height(self):
        return (self.height * 2) + 1

    def draw(self):
        # Draw the maze we have built. Each '1' in the array represents a wall
        for row in range(self.grid_rows):
            for col in range(self.grid_columns):
                # Calculate the screen coordinates
                x = (col * wall_separation) + offset_x
                y = (row * wall_separation) + offset_y

                if self.maze[row][col] == 1:
                    # Draw a wall shadow
                    pygame.draw.rect(screen, "black", pygame.Rect(x + WALL_SHADOW, y + WALL_SHADOW, wall_size, wall_size))

                    # Draw a wall top
                    pygame.draw.rect(screen, WALL, pygame.Rect(x, y, wall_size, wall_size))

                if self.maze[row][col] == 2:
                    # Draw the player path
                    pygame.draw.rect(screen, PATH, pygame.Rect(x, y, wall_size, wall_size))


class Player(object):
    def __init__(self, x, y, colour, pad):
        self.x = x
        self.y = y
        self.colour = colour
        self.pad = pad

    def position(self, x, y):
        self.x = x
        self.y = y

    def update(self, maze):
        # Read the player's gamepad
        button = self.pad.read_buttons()

        if button['L'] and maze[self.y][self.x - 1] != 1:
            self.x -= 1
            time.sleep(MOVEMENT_SLEEP)

        elif button['R'] and maze[self.y][self.x + 1] != 1:
            self.x += 1
            time.sleep(MOVEMENT_SLEEP)

        elif button['U'] and maze[self.y - 1][self.x] != 1:
            self.y -= 1
            time.sleep(MOVEMENT_SLEEP)

        elif button['D'] and maze[self.y + 1][self.x] != 1:
            self.y += 1
            time.sleep(MOVEMENT_SLEEP)

        maze[self.y][self.x] = 2

    def draw(self):

        pygame.draw.rect(screen, self.colour, pygame.Rect(self.x * wall_separation + offset_x,
                         self.y * wall_separation + offset_y,
                         wall_size, wall_size))


def build_maze():
    global wall_separation
    global wall_size
    global offset_x
    global offset_y
    global start
    global goal

    difficulty = int(level * DIFFICULT_SCALE)
    width = random.randrange(MIN_MAZE_WIDTH, MAX_MAZE_WIDTH)
    height = random.randrange(MIN_MAZE_HEIGHT, MAX_MAZE_HEIGHT)
    builder.build(width + difficulty, height + difficulty)

    wall_separation = min(HEIGHT // builder.grid_rows,
                          WIDTH // builder.grid_columns)
    wall_size = wall_separation - WALL_GAP

    offset_x = (WIDTH - (builder.grid_columns * wall_separation) + WALL_GAP) // 2
    offset_y = (HEIGHT - (builder.grid_rows * wall_separation) + WALL_GAP) // 2

    start = Position(1, builder.grid_rows - 2)
    goal = Position(builder.grid_columns - 2, 1)


pygame.init()
pygame.display.set_caption('Random Maze')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)
running = True

# Create the maze builder and build the first maze and put
builder = MazeBuilder()
build_maze()

# Create the player object if a QwSTPad is connected
try:
    player = Player(*start, PLAYER, QwSTPad())
except OSError:
    print("QwSTPad: Not Connected ... Exiting")
    raise SystemExit

print("QwSTPad: Connected ... Starting")

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not complete:
            # Update the player's position in the maze
            player.update(builder.maze)

            # Check if any player has reached the goal position
            if player.x == goal.x and player.y == goal.y:
                complete = True
        else:
            # Check for the player wanting to continue
            if player.pad.read_buttons()['+']:
                complete = False
                level += 1
                build_maze()
                player.position(*start)

        # Clear the screen to the background colour
        screen.fill(BACKGROUND)

        # Draw the maze walls
        builder.draw()

        # Draw the start location square

        pygame.draw.rect(screen, "red", pygame.Rect(start.x * wall_separation + offset_x,
                         start.y * wall_separation + offset_y,
                         wall_size, wall_size))

        # Draw the goal location square
        pygame.draw.rect(screen, "green", pygame.Rect(goal.x * wall_separation + offset_x,
                         goal.y * wall_separation + offset_y,
                         wall_size, wall_size))

        # Draw the player
        player.draw()

        level_text_shadow = font.render(f"Lvl: {level}", True, "black", None)
        screen.blit(level_text_shadow, (2 + TEXT_SHADOW, 2 + TEXT_SHADOW))

        level_text = font.render(f"Lvl: {level}", True, "white", None)
        screen.blit(level_text, (2, 2))

        if complete:

            pygame.draw.rect(screen, "black", pygame.Rect(4, HEIGHT // 2 - 96, WIDTH, 150))
            pygame.draw.rect(screen, PLAYER, pygame.Rect(0, HEIGHT // 2 - 100, WIDTH, 150))

            banner_text_size_1 = font.size("Maze Complete!")
            banner_text_size_2 = font.size("Press + to continue")

            banner_text_shadow_1 = font.render("Maze Complete!", True, "black", None)
            banner_text_shadow_2 = font.render("Press + to continue", True, "black", None)
            banner_text_1 = font.render("Maze Complete!", True, "white", None)
            banner_text_2 = font.render("Press + to continue", True, "white", None)

            screen.blit(banner_text_shadow_1, ((WIDTH // 2) - (banner_text_size_1[0] // 2 + TEXT_SHADOW), (HEIGHT // 2 - 50) - (banner_text_size_1[1] // 2) + TEXT_SHADOW))
            screen.blit(banner_text_shadow_2, ((WIDTH // 2) - (banner_text_size_2[0] // 2 + TEXT_SHADOW), (HEIGHT // 2) - (banner_text_size_2[1] // 2) + TEXT_SHADOW))

            screen.blit(banner_text_1, ((WIDTH // 2) - (banner_text_size_1[0] // 2), (HEIGHT // 2 - 50) - (banner_text_size_1[1] // 2)))
            screen.blit(banner_text_2, ((WIDTH // 2) - (banner_text_size_2[0] // 2), (HEIGHT // 2) - (banner_text_size_2[1] // 2)))

        # Update the screen
        pygame.display.flip()
        clock.tick(60)

# Handle the QwSTPad being disconnected unexpectedly
except OSError:
    print("QwSTPad: Disconnected .. Exiting")

# Turn off the LEDs of the connected QwSTPad
finally:
    try:
        player.pad.clear_leds()
    except OSError:
        pass

    pygame.quit()
