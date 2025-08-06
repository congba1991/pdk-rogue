#!/usr/bin/env python3
"""
Create placeholder skill card images in pixelated style
"""
import pygame
import os
from lib.skill_cards import SKILL_CARDS

# Initialize pygame for image creation
pygame.init()

# Card dimensions (pixelated style - smaller resolution)
CARD_WIDTH = 80
CARD_HEIGHT = 100
PIXEL_SIZE = 2  # Each "pixel" is 2x2 actual pixels for pixelated look

# Colors (pixelated game palette)
COLORS = {
    'bg': (40, 44, 52),           # Dark background
    'border': (255, 255, 255),    # White border
    'common': (108, 117, 125),    # Gray for common
    'rare': (52, 144, 220),       # Blue for rare  
    'epic': (155, 89, 182),       # Purple for epic
    'text': (255, 255, 255),      # White text
    'accent': (241, 196, 15),     # Gold accent
}

def create_skill_card_image(name, rarity, filename):
    """Create a pixelated skill card image"""
    # Create surface
    surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    surface.fill(COLORS['bg'])
    
    # Draw border (thick pixelated border)
    border_thickness = 3
    pygame.draw.rect(surface, COLORS['border'], 
                    (0, 0, CARD_WIDTH, CARD_HEIGHT), border_thickness)
    
    # Draw rarity color strip at top
    rarity_color = COLORS['common']  # default
    if hasattr(rarity, 'name'):
        rarity_name = rarity.name.lower()
        if rarity_name in COLORS:
            rarity_color = COLORS[rarity_name]
    
    pygame.draw.rect(surface, rarity_color,
                    (border_thickness, border_thickness, 
                     CARD_WIDTH - 2*border_thickness, 12))
    
    # Draw main content area
    content_rect = pygame.Rect(border_thickness + 2, 18, 
                              CARD_WIDTH - 2*border_thickness - 4, 
                              CARD_HEIGHT - 25)
    pygame.draw.rect(surface, (60, 64, 72), content_rect)
    
    # Create fonts (small pixelated style)
    font_small = pygame.font.Font(None, 12)
    font_tiny = pygame.font.Font(None, 10)
    
    # Draw card name (abbreviated to fit)
    name_parts = name.split()
    short_name = ""
    if len(name_parts) == 1:
        short_name = name[:8]  # First 8 chars
    else:
        # Take first letter of each word
        short_name = "".join([word[0] for word in name_parts])
        if len(short_name) < 4:  # If too short, add more
            short_name = name_parts[0][:4]
    
    name_surface = font_small.render(short_name, True, COLORS['text'])
    name_rect = name_surface.get_rect()
    name_rect.centerx = CARD_WIDTH // 2
    name_rect.y = 22
    surface.blit(name_surface, name_rect)
    
    # Draw simple icon/symbol based on card type
    icon_y = 40
    icon_size = 8
    
    # Simple pixelated icons based on card name
    if "discard" in name.lower():
        # Draw recycling arrows (simple squares)
        pygame.draw.rect(surface, COLORS['accent'], 
                        (CARD_WIDTH//2 - 6, icon_y, 4, 4))
        pygame.draw.rect(surface, COLORS['accent'], 
                        (CARD_WIDTH//2 + 2, icon_y + 4, 4, 4))
    elif "time" in name.lower():
        # Draw clock (circle with line)
        pygame.draw.circle(surface, COLORS['accent'], 
                          (CARD_WIDTH//2, icon_y + 4), 6, 2)
        pygame.draw.line(surface, COLORS['accent'],
                        (CARD_WIDTH//2, icon_y + 4), 
                        (CARD_WIDTH//2 + 3, icon_y + 1), 2)
    elif "steal" in name.lower() or "card" in name.lower():
        # Draw hand/grab icon (rectangles)
        for i in range(3):
            pygame.draw.rect(surface, COLORS['accent'], 
                            (CARD_WIDTH//2 - 4 + i*2, icon_y + i, 2, 6))
    elif "damage" in name.lower() or "boost" in name.lower():
        # Draw sword/attack (diagonal line with guard)
        pygame.draw.line(surface, COLORS['accent'],
                        (CARD_WIDTH//2 - 4, icon_y + 8), 
                        (CARD_WIDTH//2 + 4, icon_y), 3)
        pygame.draw.rect(surface, COLORS['accent'], 
                        (CARD_WIDTH//2 - 2, icon_y + 2, 4, 2))
    else:
        # Default icon (diamond/gem)
        points = [
            (CARD_WIDTH//2, icon_y),
            (CARD_WIDTH//2 + 4, icon_y + 4),
            (CARD_WIDTH//2, icon_y + 8),
            (CARD_WIDTH//2 - 4, icon_y + 4)
        ]
        pygame.draw.polygon(surface, COLORS['accent'], points)
    
    # Draw rarity indicator at bottom
    rarity_text = rarity.name[0] if hasattr(rarity, 'name') else 'C'  # C/R/E
    rarity_surface = font_tiny.render(rarity_text, True, rarity_color)
    rarity_rect = rarity_surface.get_rect()
    rarity_rect.centerx = CARD_WIDTH // 2
    rarity_rect.y = CARD_HEIGHT - 15
    surface.blit(rarity_surface, rarity_rect)
    
    # Add some pixelated texture/noise for authenticity
    import random
    random.seed(hash(name))  # Consistent noise per card
    for _ in range(5):
        x = random.randint(10, CARD_WIDTH - 10)
        y = random.randint(55, CARD_HEIGHT - 20)
        noise_color = (
            COLORS['bg'][0] + random.randint(-10, 10),
            COLORS['bg'][1] + random.randint(-10, 10),
            COLORS['bg'][2] + random.randint(-10, 10)
        )
        pygame.draw.rect(surface, noise_color, (x, y, 2, 2))
    
    return surface

def main():
    """Create all skill card images"""
    # Create images directory
    images_dir = "images/skill_cards"
    os.makedirs(images_dir, exist_ok=True)
    
    print("Creating skill card images...")
    
    # Create images for all skill cards
    for name, card_class in SKILL_CARDS.items():
        card_instance = card_class()
        rarity = card_instance.rarity
        
        # Create filename (replace spaces with underscores, lowercase)
        filename = name.lower().replace(" ", "_").replace("'", "") + ".png"
        filepath = os.path.join(images_dir, filename)
        
        # Create and save image
        card_surface = create_skill_card_image(name, rarity, filename)
        pygame.image.save(card_surface, filepath)
        
        print(f"Created: {filepath}")
    
    print(f"Created {len(SKILL_CARDS)} skill card images in {images_dir}/")
    pygame.quit()

if __name__ == "__main__":
    main()