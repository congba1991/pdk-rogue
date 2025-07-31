import pygame
from lib.constants import *
from lib.game import Game

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("跑得快 (Run Fast)")
    game = Game(screen)
    game.run()
