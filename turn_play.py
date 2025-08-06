import pygame
import sys
from lib.constants import *
from main_menu import MainMenu

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PDK Rogue")
    menu = MainMenu(screen)
    menu.run()
