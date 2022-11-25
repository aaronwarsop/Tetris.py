import pygame
import random
import time

# Global vars
screen_width = 800
screen_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30
score_file = 'score.txt'
win = pygame.display.set_mode((screen_width, screen_height))

# initializes python fonts
pygame.font.init()
# start x pos
top_left_x = (screen_width - play_width) // 2
# start y pos
top_left_y = screen_height - play_height


# Shape variations

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# Creates a list of shapes and shape colours, used for indexing to their retrospected colour
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


class Piece(object):
    rows = 20
    columns = 10

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        # matches shape with colour at same index position
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_positions={}):
    # creates a grid list and 20 sublists for each row to store the colour value
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]
    # i = row value, j = col value, goes through the grid and stores colour values in each position
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                colour = locked_positions[(j, i)]
                grid[i][j] = colour
    return grid


def draw_grid(play_area, row, col):
    # i = horizontal lines, j = vertical lines, creates grey lines representing the grid
    for i in range(row):
        pygame.draw.line(play_area, (128,128,128), (top_left_x, top_left_y+ i* block_size), (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(col):
            pygame.draw.line(play_area, (128,128,128), (top_left_x + j * block_size, top_left_y), (top_left_x + j * block_size, top_left_y + play_height))


def random_shape():
    # chooses a random shape from shapes list and spawns it at (5,0) (middle-ish)
    return Piece(5, 0, random.choice(shapes))


def convert_shape_format(piece):
    pos = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    # goes through the list of shape
    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pos.append((piece.x + j, piece.y + i))

    for i, position in enumerate(pos):
        pos[i] = (position[0] - 2, position[1] - 4)

    return pos


def valid_pos(piece, grid):
    # adds every position into j and i, if statement is to check if the pos is black in the grid, meaning no shape is there
    valid_position = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    valid_position = [j for sub in valid_position for j in sub]
    formatted = convert_shape_format(piece)

    # stops us from moving out the grid
    for position in formatted:
        if position not in valid_position:
            if position[1] > -1:
                return False
    return True


def game_over(positions):
    # loop to check if y pos is less than 1, if less than 1 game_over will return true
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def draw_text(text, size, color, play_area):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    play_area.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))


def clear_rows(grid, locked):
    # need to see if row is clear the shift every other row above down one

    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)


def draw_next_shape(piece, play_area):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(play_area, piece.color, (sx + j*30, sy + i*30, 30, 30), 0)

    play_area.blit(label, (sx + 10, sy- 30))


def draw_to_screen(play_area):
    play_area.fill((0,0,0))
    font = pygame.font.SysFont('comicsans', 60)
    title = font.render('TETRIS', True, (255, 255, 255))
    play_area.blit(title, (top_left_x + play_width / 2 - (title.get_width() / 2), 30))

    # i = row, j = col
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            # draws shapes to the screen, grid[i][j] represents colour, calcs after are for x and y values
            pygame.draw.rect(play_area, grid[i][j], (top_left_x + j* block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draws grid
    draw_grid(play_area, 20, 10)
    # draws border
    pygame.draw.rect(play_area, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)


def main():
    global grid
    locked_positions = {}
    change_piece = False
    gamestate = True
    current_piece = random_shape()
    next_piece = random_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    # time.time() function gets current time
    start_time = time.time()

    while gamestate:
        fall_speed = 0.3
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        time_running = time.time() - start_time


        # PIECE FALLING CODE
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_pos(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gamestate = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    current_piece.rotation += 1
                    if not (valid_pos(current_piece, grid)):
                        current_piece.rotation -= 1
                if event.key == pygame.K_a:
                    current_piece.x -= 1
                    if not (valid_pos(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_s:
                    current_piece.y += 1
                    if not (valid_pos(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_d:
                    current_piece.x += 1
                    if not (valid_pos(current_piece, grid)):
                        current_piece.x -= 1

        shape_pos = convert_shape_format(current_piece)

        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        #
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = random_shape()
            change_piece = False
            clear_rows(grid, locked_positions)

        draw_to_screen(win)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check if user lost
        if game_over(locked_positions):
            gamestate = False

    draw_text("You Lost", 40, (255,255,255), win)
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu():
    gamestate = True
    while gamestate:
        win.fill((0,0,0))
        draw_text('Press any key to begin.', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gamestate = False

            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()


main_menu()