import pygame
import asyncio
from game_board import GameBoard
from constants import GRID_WIDTH, GRID_PADDING, ICON_WIDTH, RED_COLOR

class Game:
    """Class to handle the game loop, event handling, and rendering."""

    def __init__(self, screen, font):
        self.board = GameBoard()
        self.screen = screen
        self.font = font
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
        """Update the status of the game after a move."""
        self.status_text = self.board.check_game_status()

    def draw(self):
        """Render the game board and current status."""
        self.screen.fill((255, 255, 255))
        self.board.draw_board(self.screen)
        self.board.draw_symbols(self.screen)
        self.draw_status()
        pygame.display.update()

    def draw_status(self):
        """Draw the current status of the game on the screen."""
        if self.status_text:
            text_color = RED_COLOR if "violated" in self.status_text else (0, 255, 0)
            text_surf = self.font.render(self.status_text, True, text_color)
            self.screen.blit(text_surf, (GRID_PADDING, GRID_PADDING // 2))

    async def run(self):
        """Main game loop running asynchronously."""
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            await asyncio.sleep(0)

