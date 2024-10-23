#main script for tango puzzle game

import pygame
import asyncio

#pygame setup
pygame.init()
window_width = 512
icon_width = window_width // 6
small_icon_width = icon_width // 4

screen = pygame.display.set_mode((window_width, window_width))
clock = pygame.time.Clock()

font = pygame.font.Font('freesansbold.ttf', 32)
status_text = font.render('', True, 'green')
text_rect = status_text.get_rect()
text_rect.center = (icon_width, window_width - icon_width)

running = True
game_over = False
rule_break = False

def load_icon(path, resolution):
    icon = pygame.image.load(path)
    return pygame.transform.scale(icon, resolution)

GRID = load_icon('graphics/grid.png', (window_width, window_width))
ICON_BANANA = load_icon('graphics/banana.png', (icon_width, icon_width))
ICON_ORANGE = load_icon('graphics/orange_2.png', (icon_width, icon_width))
SYMBOL_CROSS = load_icon('graphics/cross.png', (small_icon_width, small_icon_width))
SYMBOL_EQUAL = load_icon('graphics/equal.png', (small_icon_width, small_icon_width))

board = [
    [None, None, None, None, None, None],
    [None, None, None, None, None, None],
    [None, None, None, None, None, None],
    [None, None, None, None, None, None],
    [None, None, None, None, None, None],
    [None, None, None, None, None, None]
]

# Set some fixed cells with initial values
fixed_cells = [
    (0, 2, 1), (0, 3, 1), (0, 5, 1),
    (1, 1, 1),
    (2, 0, 1),
    (3, 0, 1),
    (4, 1, 1),
    (5, 2, 1), (5, 3, 1), (5, 5, 0)

]  # (row, column, value)

# Set fixed = and x symbols
fixed_symbols = [
    (1, 3, (1, 2)),
    (2, 2, (1, 0)),
    (3, 2, (1, 0)), (3, 3, (0, 1)),
    (4, 3, (1, 0))
] # (row, column, (right, down)) 0 = empty, 1 = cross, 2 = equal

for row, column, value in fixed_cells:
    board[row][column] = value

# Example function to protect fixed cells (assuming you are applying this in-game logic)
def is_cell_fixed(row, column):
    return (row, column) in [(fc[0], fc[1]) for fc in fixed_cells]

def has_symbols(row, column):
    return (row, column) in [(fs[0], fs[1]) for fs in fixed_symbols]

def show_symbols():
    for row, column, (right, down) in fixed_symbols:
        if right != 0:
            screen.blit(SYMBOL_CROSS if right == 1 else SYMBOL_EQUAL, (icon_width * (column + 1) - small_icon_width // 2,
                                       icon_width * row + icon_width // 2 - small_icon_width // 2))
        if down != 0:
            screen.blit(SYMBOL_CROSS if down == 1 else SYMBOL_EQUAL, (icon_width * (column + 1) - icon_width // 2 - small_icon_width // 2,
                                       icon_width * row + icon_width - small_icon_width // 2))

def show_icons():
    for i, row in enumerate(board):
        for j, column in enumerate(board[i]):
            if board[i][j] == 1:
                screen.blit(ICON_ORANGE, (j * icon_width, i * icon_width))
            elif board[i][j] == 0:
                screen.blit(ICON_BANANA, (j * icon_width, i * icon_width))

def play_turn(mouse_pos):
    if mouse_pos:
        current_coordinates = pygame.math.Vector2(pygame.mouse.get_pos()) // icon_width
        # print(current_coordinates)
        column, row = map(int, current_coordinates)
        if is_cell_fixed(row, column): return
        if board[row][column] is None: # Check if the cell is empty
            board[row][column] = 0
        elif board[row][column] == 0:
            board[row][column] = 1
        else: board[row][column] = None

def check_game_status():
    global status_text, game_over
    if has_rule_break():
        status_text = font.render('Rules are not satisfied!', True, 'red')

    if grid_full() and not rule_break:
        status_text = font.render('Game over', True, 'green')
        game_over = True

def has_rule_break():
    global rule_break
    if has_three_adjacent_in_rows() or has_four_in_line() or has_three_adjacent_in_columns() \
            or symbols_not_satisfied():
        rule_break = True
    else: rule_break = False
    return rule_break

def symbols_not_satisfied():
    for row, column, (right, down) in fixed_symbols:
        if board[row][column] is None: continue

        if down != 0:
            if board[row + 1][column] is not None:
                if down == 1:
                    if board[row][column] == board[row + 1][column]:
                        return True
                elif down == 2:
                    if board[row][column] != board[row + 1][column]:
                        return True

        if right != 0:
            if board[row][column + 1] is not None:
                if right == 1:
                    if board[row][column] == board[row][column + 1]:
                        return True
                elif right == 2:
                    if board[row][column] != board[row][column  + 1]:
                        return True
        return False

def grid_full():
    for i in range(0, 6):
        if not row_full(i): return False
    return True

def row_full(row):
    for cell in board[row]:
        if cell is None: return False
    return True

def has_three_adjacent_in_rows():
    if has_three_adjacent(board[0]) or has_three_adjacent(board[1]) or has_three_adjacent(board[2]):
        return True
    return False

def has_three_adjacent_in_columns():
    return has_three_adjacent_in_column(0) or has_three_adjacent_in_column(1) \
            or has_three_adjacent_in_column(2) or has_three_adjacent_in_column(3) \
            or has_three_adjacent_in_column(4) or has_three_adjacent_in_column(5)

def has_three_adjacent_in_column(column):
    cell_list = [
        board[0][column], board[1][column],
        board[2][column], board[3][column],
        board[4][column], board[5][column]
    ]
    if has_three_adjacent(cell_list):
        return True
    return False

def has_three_adjacent(cell_list):
    if len(cell_list) < 3:
        return False  # Not enough cells to have three adjacent

    last_cell = cell_list[0]
    count = 1

    for i in range(1, len(cell_list)):
        cell = cell_list[i]

        if cell is None:
            count = 0  # Reset count when encountering None
            continue

        if cell == last_cell:
            count += 1
        else:
            count = 1  # Reset count for a new sequence
            last_cell = cell

        if count >= 3:
            return True

    return False

def has_four_in_line():
    if has_four_in_rows() or has_four_in_column(0) or has_four_in_column(1) \
        or has_four_in_column(2) or has_four_in_column(3) \
        or has_four_in_column(4) or has_four_in_column(5):
        return True
    return False

def has_four_in_rows():
    if has_four_or_more_in_list(board[0]) or has_four_or_more_in_list(board[1]) or has_four_or_more_in_list(board[2]) \
        or has_four_or_more_in_list(board[3]) or has_four_or_more_in_list(board[4]) or has_four_or_more_in_list(board[5]):
        return True
    return False

def has_four_in_column(column):
    cell_list = [
        board[0][column], board[1][column],
        board[2][column], board[3][column],
        board[4][column], board[5][column]
    ]
    if has_four_or_more_in_list(cell_list):
        return True
    return False

def has_four_or_more_in_list(cell_list):
    count_0 = 0
    count_1 = 0

    for item in cell_list:
        if item == 0: count_0 += 1
        elif item == 1: count_1 += 1

    if count_0 >= 4 or count_1 >= 4:
        return True
    return False

def check_elements_are_equal(cell_list):
    if len(list) < 2:
        return True  # If the list has 0 or 1 element, all elements are "equal" by default

    first_element = list[0]
    for i in range(1, len(list)):
        if list[i] != first_element:
            return False
    return True

def has_different_adjacent_cell():
    pass

def has_same_adjacent_cell():
    pass

async def main():
    global running
    
    while running:
        mouse_click_position = None # To store mouse click position

        #poll for events
        #pygame.QUIT means the user clicked X to close the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:
                    mouse_click_position = event.pos

        #flip() the display to put changes on screen
        pygame.display.flip()

        #fill the screen with a color to wipe away anything from last frame
        screen.fill('white')

        #RENDER THE GAME
        screen.blit(GRID, (0, 0))

        if not game_over:
            play_turn(mouse_click_position)

        show_icons()

        show_symbols()

        # Check for any rule break
        check_game_status()

        if rule_break: screen.blit(status_text, text_rect)

        if game_over: screen.blit(status_text, text_rect)

        clock.tick(60) # limit FPS to 60

        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())

