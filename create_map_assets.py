#!/usr/bin/env python3
"""
Create map assets (player icon, node graphics) for the roguelike map system
"""
import pygame
import os

# Initialize pygame for image creation
pygame.init()

# Colors for map assets
COLORS = {
    'player': (100, 150, 255),      # Blue for player
    'player_outline': (255, 255, 255),  # White outline
    'combat': (200, 100, 100),      # Red for combat nodes
    'elite': (150, 50, 150),        # Purple for elite nodes  
    'exchange': (100, 200, 100),    # Green for exchange nodes
    'mystery': (200, 200, 100),     # Yellow for mystery nodes
    'boss': (150, 0, 0),            # Dark red for boss nodes
    'outline': (255, 255, 255),     # White outline for nodes
    'path': (150, 150, 150),        # Gray for paths
    'bg': (40, 44, 52),             # Dark background
}

NODE_SIZE = 30
PLAYER_SIZE = 20

def create_player_icon():
    """Create a simple pixelated player icon"""
    surface = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
    
    # Simple person shape in pixel art style
    # Head (circle)
    pygame.draw.circle(surface, COLORS['player'], (PLAYER_SIZE//2, 6), 4)
    pygame.draw.circle(surface, COLORS['player_outline'], (PLAYER_SIZE//2, 6), 4, 1)
    
    # Body (rectangle)
    body_rect = pygame.Rect(PLAYER_SIZE//2 - 3, 10, 6, 8)
    pygame.draw.rect(surface, COLORS['player'], body_rect)
    pygame.draw.rect(surface, COLORS['player_outline'], body_rect, 1)
    
    # Arms (small rectangles)
    pygame.draw.rect(surface, COLORS['player'], (PLAYER_SIZE//2 - 6, 12, 3, 2))
    pygame.draw.rect(surface, COLORS['player'], (PLAYER_SIZE//2 + 3, 12, 3, 2))
    
    # Legs (small rectangles)
    pygame.draw.rect(surface, COLORS['player'], (PLAYER_SIZE//2 - 3, 18, 2, 3))
    pygame.draw.rect(surface, COLORS['player'], (PLAYER_SIZE//2 + 1, 18, 2, 3))
    
    return surface

def create_node_icon(node_type):
    """Create a node icon for different node types"""
    surface = pygame.Surface((NODE_SIZE, NODE_SIZE), pygame.SRCALPHA)
    
    # Base circle
    color = COLORS.get(node_type, COLORS['combat'])
    pygame.draw.circle(surface, color, (NODE_SIZE//2, NODE_SIZE//2), NODE_SIZE//2 - 2)
    pygame.draw.circle(surface, COLORS['outline'], (NODE_SIZE//2, NODE_SIZE//2), NODE_SIZE//2 - 2, 2)
    
    # Add symbols for different node types
    center = NODE_SIZE // 2
    
    if node_type == 'combat':
        # Sword symbol (crossed lines)
        pygame.draw.line(surface, COLORS['outline'], 
                        (center - 6, center - 6), (center + 6, center + 6), 2)
        pygame.draw.line(surface, COLORS['outline'],
                        (center - 6, center + 6), (center + 6, center - 6), 2)
        # Guard
        pygame.draw.rect(surface, COLORS['outline'], (center - 2, center - 1, 4, 2))
        
    elif node_type == 'elite':
        # Crown symbol (triangle with decorations)
        points = [(center, center - 6), (center - 6, center + 3), (center + 6, center + 3)]
        pygame.draw.polygon(surface, COLORS['outline'], points, 2)
        # Crown decorations
        pygame.draw.line(surface, COLORS['outline'], (center - 3, center - 2), (center - 3, center - 6), 2)
        pygame.draw.line(surface, COLORS['outline'], (center, center - 2), (center, center - 8), 2)
        pygame.draw.line(surface, COLORS['outline'], (center + 3, center - 2), (center + 3, center - 6), 2)
        
    elif node_type == 'exchange':
        # Two arrows in circle
        pygame.draw.line(surface, COLORS['outline'], 
                        (center - 4, center - 2), (center + 4, center - 2), 2)
        pygame.draw.line(surface, COLORS['outline'],
                        (center - 4, center + 2), (center + 4, center + 2), 2)
        # Arrowheads
        pygame.draw.polygon(surface, COLORS['outline'], 
                           [(center + 4, center - 2), (center + 2, center - 4), (center + 2, center)], 0)
        pygame.draw.polygon(surface, COLORS['outline'],
                           [(center - 4, center + 2), (center - 2, center), (center - 2, center + 4)], 0)
        
    elif node_type == 'mystery':
        # Question mark
        font = pygame.font.Font(None, 20)
        text_surface = font.render("?", True, COLORS['outline'])
        text_rect = text_surface.get_rect(center=(center, center))
        surface.blit(text_surface, text_rect)
        
    elif node_type == 'boss':
        # Skull symbol (simplified)
        pygame.draw.circle(surface, COLORS['outline'], (center, center - 2), 6, 2)
        # Eyes
        pygame.draw.circle(surface, COLORS['outline'], (center - 3, center - 4), 2)
        pygame.draw.circle(surface, COLORS['outline'], (center + 3, center - 4), 2)
        # Jaw
        pygame.draw.rect(surface, COLORS['outline'], (center - 4, center + 2, 8, 4), 2)
    
    return surface

def create_path_texture():
    """Create a simple path texture"""
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    
    # Dotted line pattern
    for i in range(0, 20, 4):
        pygame.draw.circle(surface, COLORS['path'], (i, 10), 1)
    
    return surface

def main():
    """Create all map assets"""
    # Create images directory
    os.makedirs("images/map", exist_ok=True)
    
    print("Creating map assets...")
    
    # Create player icon
    player_icon = create_player_icon()
    pygame.image.save(player_icon, "images/map/player.png")
    print("Created: images/map/player.png")
    
    # Create node icons
    node_types = ['combat', 'elite', 'exchange', 'mystery', 'boss']
    for node_type in node_types:
        node_icon = create_node_icon(node_type)
        pygame.image.save(node_icon, f"images/map/node_{node_type}.png")
        print(f"Created: images/map/node_{node_type}.png")
    
    # Create path texture
    path_texture = create_path_texture()
    pygame.image.save(path_texture, "images/map/path.png")
    print("Created: images/map/path.png")
    
    print(f"Created {len(node_types) + 2} map assets in images/map/")
    pygame.quit()

if __name__ == "__main__":
    main()