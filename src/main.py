import pygame
import asyncio
from game import Game
from constants import GRID_WIDTH, GRID_PADDING, FONT_SIZE

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH + GRID_PADDING * 2, GRID_WIDTH + GRID_PADDING * 2))

font_path = 'assets/fonts/RobotoSlab-Regular.ttf'
font = pygame.font.Font(font_path, FONT_SIZE)

if __name__ == "__main__":
    game = Game(screen, font)
    asyncio.run(game.run())
