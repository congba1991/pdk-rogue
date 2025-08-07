"""
UI utility functions for drawing common interface elements.
Centralized location for all shared UI drawing functions.
"""

import pygame
from lib.constants import *


class UIUtils:
    """Utility class for common UI drawing functions"""
    
    @staticmethod
    def draw_button(screen, font, rect, text, hover=False, disabled=False):
        """Draw a styled button with hover and disabled states"""
        color = BUTTON_HOVER if hover else BUTTON_COLOR
        if disabled:
            color = (100, 100, 100)
            
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, TEXT_COLOR, rect, 2)
        
        text_color = TEXT_COLOR if not disabled else (150, 150, 150)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
    
    @staticmethod
    def draw_selection_box(screen, font, rect, text, selected=False, hover=False):
        """Draw a selection box for items with selection states"""
        color = SELECTED_COLOR if selected else CARD_COLOR
        if hover:
            color = BUTTON_HOVER
            
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, TEXT_COLOR, rect, 2)
        
        text_surface = font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(midleft=(rect.x + 10, rect.centery))
        screen.blit(text_surface, text_rect)
    
    @staticmethod
    def draw_input_box(screen, font, rect, text, active=False):
        """Draw an input text box"""
        color = SELECTED_COLOR if active else CARD_COLOR
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, TEXT_COLOR, rect, 2)
        
        text_surface = font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(midleft=(rect.x + 10, rect.centery))
        screen.blit(text_surface, text_rect)
    
    @staticmethod
    def center_button(window_width, button_width, y_pos, button_height=40):
        """Calculate centered button rectangle"""
        center_x = window_width // 2 - button_width // 2
        return pygame.Rect(center_x, y_pos, button_width, button_height)
    
    @staticmethod
    def draw_title(screen, font, text, y_pos, window_width):
        """Draw centered title text"""
        title_surface = font.render(text, True, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(window_width // 2, y_pos))
        screen.blit(title_surface, title_rect)
        return title_rect