import pygame

class AssetLoader:
    """Class responsible for loading and scaling image assets."""

    @staticmethod
    def load_icon(path, resolution):
        icon = pygame.image.load(path)
        return pygame.transform.scale(icon, resolution)
