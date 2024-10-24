import pygame
import asyncio

# Constants
GRID_WIDTH = 512
GRID_PADDING = 64
CELL_WIDTH = 128
ICON_WIDTH = GRID_WIDTH // 6
SMALL_ICON_WIDTH = ICON_WIDTH // 4

GRAY_COLOR = (128, 128, 128, 100)
RED_COLOR = (255, 0, 0, 128)
FONT_SIZE = 32

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH + GRID_PADDING * 2, GRID_WIDTH + GRID_PADDING * 2))
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)


class AssetLoader:
    """Class responsible for loading and scaling image assets."""

    @staticmethod
    def load_icon(path, resolution):
        icon = pygame.image.load(path)
        return pygame.transform.scale(icon, resolution)


class GameBoard:
    """Class representing the game board and handling its state and logic."""

    def __init__(self):
        self.board = [[None for _ in range(6)] for _ in range(6)]
        self.fixed_cells = [
            (0, 2, 1), (0, 3, 1), (0, 5, 1),
            (1, 1, 1), (2, 0, 1), (3, 0, 1),
            (4, 1, 1), (5, 2, 1), (5, 3, 1), (5, 5, 0)
        ]
        self.fixed_symbols = [
            (1, 3, (1, 2)), (2, 2, (1, 0)),
            (3, 2, (1, 0)), (3, 3, (0, 1)), (4, 3, (1, 0))
        ]
        self.rule_break = False

        # Load assets
        self.grid_image = AssetLoader.load_icon('graphics/grid.png', (GRID_WIDTH, GRID_WIDTH))
        self.icon_orange = AssetLoader.load_icon('graphics/orange_2.png', (ICON_WIDTH, ICON_WIDTH))
        self.icon_banana = AssetLoader.load_icon('graphics/banana.png', (ICON_WIDTH, ICON_WIDTH))
        self.symbol_cross = AssetLoader.load_icon('graphics/cross.png', (SMALL_ICON_WIDTH, SMALL_ICON_WIDTH))
        self.symbol_equal = AssetLoader.load_icon('graphics/equal.png', (SMALL_ICON_WIDTH, SMALL_ICON_WIDTH))

        # Set fixed cell values
        for row, column, value in self.fixed_cells:
            self.board[row][column] = value

    def is_cell_fixed(self, row, column):
        return (row, column) in [(fc[0], fc[1]) for fc in self.fixed_cells]

    def has_symbols(self, row, column):
        return (row, column) in [(fs[0], fs[1]) for fs in self.fixed_symbols]

    def get_board_value(self, row, column):
        return self.board[row][column]

    def set_board_value(self, row, column, value):
        self.board[row][column] = value

    def draw_board(self, screen):
        screen.blit(self.grid_image, (GRID_PADDING, GRID_PADDING))
        for i, row in enumerate(self.board):
            for j, value in enumerate(row):
                if value is not None:
                    self._draw_icon(screen, value, i, j)
                if self.is_cell_fixed(i, j):
                    self._draw_overlay(screen, i, j)

    def draw_symbols(self, screen):
        """Draw fixed symbols (= and X) on the board."""
        for row, column, (right, down) in self.fixed_symbols:
            if right != 0:
                symbol_x = ICON_WIDTH * (column + 1) - SMALL_ICON_WIDTH // 2 + GRID_PADDING
                symbol_y = ICON_WIDTH * row + ICON_WIDTH // 2 - SMALL_ICON_WIDTH // 2 + GRID_PADDING
                symbol = self.symbol_cross if right == 1 else self.symbol_equal
                screen.blit(symbol, (symbol_x, symbol_y))
            if down != 0:
                symbol_x = ICON_WIDTH * (column + 1) - ICON_WIDTH // 2 - SMALL_ICON_WIDTH // 2 + GRID_PADDING
                symbol_y = ICON_WIDTH * row + ICON_WIDTH - SMALL_ICON_WIDTH // 2 + GRID_PADDING
                symbol = self.symbol_cross if down == 1 else self.symbol_equal
                screen.blit(symbol, (symbol_x, symbol_y))

    def _draw_icon(self, screen, value, row, column):
        x = column * ICON_WIDTH + GRID_PADDING
        y = row * ICON_WIDTH + GRID_PADDING
        icon = self.icon_orange if value == 1 else self.icon_banana
        screen.blit(icon, (x, y))

    def _draw_overlay(self, screen, row, column):
        """Draw a gray overlay for fixed cells."""
        x = column * ICON_WIDTH + GRID_PADDING
        y = row * ICON_WIDTH + GRID_PADDING
        overlay = pygame.Surface((ICON_WIDTH, ICON_WIDTH), pygame.SRCALPHA)
        overlay.fill(GRAY_COLOR)
        screen.blit(overlay, (x, y))

    def check_game_status(self):
        """Check if the game is over or if there's any rule break."""
        if self.has_rule_break():
            return "Rule violated!"
        if self.is_grid_full() and not self.rule_break:
            self.level_cleared = True
            return "Level cleared!"
        return None

    def is_grid_full(self):
        return all(self.is_row_full(i) for i in range(6))

    def is_row_full(self, row):
        return all(cell is not None for cell in self.board[row])

    def has_rule_break(self):
        self.rule_break = (
                self.has_three_adjacent_in_rows() or self.has_three_adjacent_in_columns() or
                self.symbols_not_satisfied() or self.has_four_in_line()
        )
        return self.rule_break

    def symbols_not_satisfied(self):
        for row, column, (right, down) in self.fixed_symbols:
            value = self.board[row][column]
            if value is None:
                continue
            if down != 0 and self.board[row + 1][column] is not None:
                if (down == 1 and value == self.board[row + 1][column]) or \
                        (down == 2 and value != self.board[row + 1][column]):
                    return True
            if right != 0 and self.board[row][column + 1] is not None:
                if (right == 1 and value == self.board[row][column + 1]) or \
                        (right == 2 and value != self.board[row][column + 1]):
                    return True
        return False

    def has_three_adjacent_in_rows(self):
        return any(self.has_three_adjacent(self.board[row]) for row in range(6))

    def has_three_adjacent_in_columns(self):
        return any(self.has_three_adjacent([self.board[row][column] for row in range(6)]) for column in range(6))

    def has_three_adjacent(self, cell_list):
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
                count = 1
                last_cell = cell
            if count >= 3:
                return True
        return False

    def has_four_in_line(self):
        return self.has_four_in_rows() or any(self.has_four_in_column(column) for column in range(6))

    def has_four_in_rows(self):
        return any(self.has_four_or_more_in_list(self.board[row]) for row in range(6))

    def has_four_in_column(self, column):
        return self.has_four_or_more_in_list([self.board[row][column] for row in range(6)])

    def has_four_or_more_in_list(self, cell_list):
        count_0 = cell_list.count(0)
        count_1 = cell_list.count(1)
        return count_0 >= 4 or count_1 >= 4


class Game:
    """Class to handle the game loop, event handling, and rendering."""

    def __init__(self):
        self.board = GameBoard()
        self.running = True
        self.game_over = False
        self.status_text = ""

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
            if event.button == 1:
                self.handle_click(event.pos)

    def handle_click(self, mouse_pos):
        adjusted_pos = pygame.math.Vector2(mouse_pos) - pygame.math.Vector2(GRID_PADDING, GRID_PADDING)
        if 0 <= adjusted_pos.x <= GRID_WIDTH and 0 <= adjusted_pos.y <= GRID_WIDTH:
            column, row = map(int, adjusted_pos // ICON_WIDTH)
            if not self.board.is_cell_fixed(row, column):
                current_value = self.board.get_board_value(row, column)
                next_value = 0 if current_value is None else (1 if current_value == 0 else None)
                self.board.set_board_value(row, column, next_value)
        self.update_game_status()

    def update_game_status(self):
        self.status_text = self.board.check_game_status()

    def draw(self):
        screen.fill((255, 255, 255))
        self.board.draw_board(screen)
        self.board.draw_symbols(screen)
        self.draw_status()
        pygame.display.update()

    def draw_status(self):
        if self.status_text:
            text_color = RED_COLOR if "violated" in self.status_text else (0, 255, 0)
            text_surf = font.render(self.status_text, True, text_color)
            screen.blit(text_surf, (GRID_PADDING, GRID_WIDTH + GRID_PADDING // 2))

    async def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            await asyncio.sleep(0)


if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())
