import pygame
WIDTH, HEIGHT = 800, 800
STATUS_BAR_HEIGHT = 20
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH//COLS


BRIGHT = (226, 192, 129)
DARK = (85, 37, 0)
LIGHT_YELLOW = (255, 194, 38)
STATUS_BAR_COLOR = (169, 169, 169)
STATUS_COLOR = (0, 0, 0)

WHITE = pygame.image.load("assets/white_checkers.png")
WHITE_KING = pygame.image.load("assets/white_checkers_super.png")
BLACK = pygame.image.load("assets/black_checkers.png")
BLACK_KING = pygame.image.load("assets/black_checkers_super.png")