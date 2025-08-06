from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum
import random
import pygame
import os

class NodeType(Enum):
    COMBAT = "combat"
    ELITE = "elite"
    EXCHANGE = "exchange"
    MYSTERY = "mystery"
    BOSS = "boss"
    START = "start"

@dataclass
class MapNode:
    """A single node on the roguelike map"""
    x: int
    y: int
    node_type: NodeType
    connections: List['MapNode'] = field(default_factory=list)
    visited: bool = False
    completed: bool = False
    
    def can_reach(self, other: 'MapNode') -> bool:
        """Check if this node can reach another node"""
        return other in self.connections
    
    def add_connection(self, other: 'MapNode'):
        """Add a connection to another node"""
        if other not in self.connections:
            self.connections.append(other)

@dataclass 
class RegionMap:
    """Complete map for a region"""
    nodes: List[MapNode] = field(default_factory=list)
    start_node: Optional[MapNode] = None
    boss_node: Optional[MapNode] = None
    current_node: Optional[MapNode] = None
    width: int = 800
    height: int = 600
    layers: int = 8  # Number of vertical layers
    
    def get_available_next_nodes(self) -> List[MapNode]:
        """Get nodes the player can move to from current position"""
        if not self.current_node:
            return [self.start_node] if self.start_node else []
        
        available = []
        for node in self.current_node.connections:
            if not node.completed:
                available.append(node)
        return available
    
    def move_to_node(self, node: MapNode) -> bool:
        """Move player to a specific node"""
        if node in self.get_available_next_nodes():
            if self.current_node:
                self.current_node.visited = True
            self.current_node = node
            return True
        return False
    
    def complete_current_node(self):
        """Mark current node as completed"""
        if self.current_node:
            self.current_node.completed = True
            self.current_node.visited = True

class MapGenerator:
    """Generates procedural maps for regions"""
    
    @staticmethod
    def generate_region_map(region_name: str = "Tutorial") -> RegionMap:
        """Generate a map for the given region"""
        map_obj = RegionMap()
        
        # Define map layout parameters (more like Slay the Spire)
        layers = 8
        nodes_per_layer = [1, 3, 4, 5, 4, 3, 2, 1]  # Start, progression layers, boss
        layer_spacing = map_obj.height // (layers + 1)
        
        # Node type distribution per layer (more Slay the Spire-like)
        node_type_weights = {
            0: [NodeType.START],  # Layer 0: Start only
            1: [NodeType.COMBAT, NodeType.COMBAT, NodeType.COMBAT],  # Layer 1: All combat
            2: [NodeType.COMBAT, NodeType.COMBAT, NodeType.EXCHANGE, NodeType.MYSTERY],  # Layer 2: Mostly combat
            3: [NodeType.COMBAT, NodeType.COMBAT, NodeType.ELITE, NodeType.MYSTERY, NodeType.EXCHANGE],  # Layer 3: Mixed
            4: [NodeType.COMBAT, NodeType.ELITE, NodeType.MYSTERY, NodeType.EXCHANGE],  # Layer 4: Balanced
            5: [NodeType.ELITE, NodeType.MYSTERY, NodeType.EXCHANGE],  # Layer 5: Pre-boss prep
            6: [NodeType.ELITE, NodeType.MYSTERY],  # Layer 6: Elite encounters
            7: [NodeType.BOSS],  # Layer 7: Boss only
        }
        
        # Generate nodes layer by layer
        layers_nodes = []
        for layer_idx in range(layers):
            layer_nodes = []
            num_nodes = nodes_per_layer[layer_idx]
            
            # Calculate node positions in this layer
            if num_nodes == 1:
                x_positions = [map_obj.width // 2]
            else:
                spacing = map_obj.width // (num_nodes + 1)
                x_positions = [spacing * (i + 1) for i in range(num_nodes)]
            
            y_position = layer_spacing * (layer_idx + 1)
            
            # Create nodes for this layer
            available_types = node_type_weights[layer_idx]
            for i in range(num_nodes):
                if len(available_types) == 1:
                    node_type = available_types[0]
                else:
                    node_type = random.choice(available_types)
                
                node = MapNode(
                    x=x_positions[i],
                    y=y_position,
                    node_type=node_type
                )
                
                layer_nodes.append(node)
                map_obj.nodes.append(node)
                
                # Set special nodes
                if node_type == NodeType.START:
                    map_obj.start_node = node
                elif node_type == NodeType.BOSS:
                    map_obj.boss_node = node
            
            layers_nodes.append(layer_nodes)
        
        # Connect nodes between layers (forward-only, no loops like Slay the Spire)
        for layer_idx in range(len(layers_nodes) - 1):
            current_layer = layers_nodes[layer_idx]
            next_layer = layers_nodes[layer_idx + 1]
            
            # Ensure every node in next layer has at least one incoming connection
            for next_node in next_layer:
                next_node._incoming_connections = 0
            
            # First pass: Connect each current node to 1-3 next layer nodes
            for current_node in current_layer:
                # Each node connects to 1-3 nodes in the next layer (based on layer size)
                max_connections = min(3, len(next_layer))
                connections_to_make = random.randint(1, max_connections)
                
                # Prefer connections to nearby nodes (spatially close)
                next_layer_sorted = sorted(next_layer, 
                                         key=lambda n: abs(n.x - current_node.x))
                
                # Connect to closest available nodes
                connected = 0
                for next_node in next_layer_sorted:
                    if connected >= connections_to_make:
                        break
                    
                    current_node.add_connection(next_node)
                    next_node._incoming_connections += 1
                    connected += 1
            
            # Second pass: Ensure no node in next layer is unreachable
            for next_node in next_layer:
                if next_node._incoming_connections == 0:
                    # Find closest node in current layer to connect to this orphaned node
                    closest_current = min(current_layer, 
                                        key=lambda n: abs(n.x - next_node.x))
                    closest_current.add_connection(next_node)
        
        return map_obj

class MapRenderer:
    """Handles rendering of the roguelike map"""
    
    def __init__(self):
        self.node_images = {}
        self.player_image = None
        self.load_assets()
    
    def load_assets(self):
        """Load map visual assets"""
        try:
            # Load node images
            for node_type in NodeType:
                if node_type != NodeType.START:  # Start node uses same as combat
                    image_path = f"images/map/node_{node_type.value}.png"
                    if os.path.exists(image_path):
                        self.node_images[node_type] = pygame.image.load(image_path)
            
            # Use combat node for start node
            if NodeType.COMBAT in self.node_images:
                self.node_images[NodeType.START] = self.node_images[NodeType.COMBAT]
            
            # Load player image
            player_path = "images/map/player.png"
            if os.path.exists(player_path):
                self.player_image = pygame.image.load(player_path)
                
        except Exception as e:
            print(f"Warning: Could not load map assets: {e}")
    
    def draw_path(self, surface, start_pos: Tuple[int, int], end_pos: Tuple[int, int], color=(150, 150, 150)):
        """Draw a path between two nodes"""
        pygame.draw.line(surface, color, start_pos, end_pos, 3)
    
    def draw_node(self, surface, node: MapNode, is_current: bool = False, is_available: bool = False):
        """Draw a single node"""
        pos = (node.x, node.y)
        
        # Use loaded image if available, otherwise fallback to colored circles
        if node.node_type in self.node_images:
            image = self.node_images[node.node_type]
            image_rect = image.get_rect(center=pos)
            surface.blit(image, image_rect)
        else:
            # Fallback to colored circles
            color_map = {
                NodeType.COMBAT: (200, 100, 100),
                NodeType.ELITE: (150, 50, 150), 
                NodeType.EXCHANGE: (100, 200, 100),
                NodeType.MYSTERY: (200, 200, 100),
                NodeType.BOSS: (150, 0, 0),
                NodeType.START: (100, 100, 100),
            }
            color = color_map.get(node.node_type, (100, 100, 100))
            pygame.draw.circle(surface, color, pos, 15)
            pygame.draw.circle(surface, (255, 255, 255), pos, 15, 2)
        
        # Draw status indicators
        if node.completed:
            # Green checkmark overlay
            pygame.draw.circle(surface, (0, 200, 0), pos, 18, 3)
        elif is_available and not is_current:
            # Pulsing yellow border for available nodes
            pygame.draw.circle(surface, (255, 255, 0), pos, 20, 2)
        
        if is_current:
            # Bright border for current node
            pygame.draw.circle(surface, (255, 255, 255), pos, 22, 3)
    
    def draw_player(self, surface, node: MapNode):
        """Draw the player at a node position"""
        if self.player_image:
            player_rect = self.player_image.get_rect(center=(node.x, node.y - 25))
            surface.blit(self.player_image, player_rect)
        else:
            # Fallback to simple blue circle
            pygame.draw.circle(surface, (100, 150, 255), (node.x, node.y - 25), 8)
            pygame.draw.circle(surface, (255, 255, 255), (node.x, node.y - 25), 8, 1)
    
    def draw_map(self, surface, region_map: RegionMap):
        """Draw the complete map"""
        # Clear background
        surface.fill((40, 44, 52))  # Dark background
        
        # Draw all paths first (so they appear behind nodes)
        for node in region_map.nodes:
            for connected_node in node.connections:
                self.draw_path(surface, (node.x, node.y), (connected_node.x, connected_node.y))
        
        # Get available next nodes
        available_nodes = region_map.get_available_next_nodes()
        
        # Draw all nodes
        for node in region_map.nodes:
            is_current = (node == region_map.current_node)
            is_available = (node in available_nodes)
            self.draw_node(surface, node, is_current, is_available)
        
        # Draw player
        if region_map.current_node:
            self.draw_player(surface, region_map.current_node)
        
        # Draw map title
        font = pygame.font.Font(None, 36)
        title_surface = font.render("Region Map", True, (255, 255, 255))
        surface.blit(title_surface, (20, 20))
        
        # Draw legend
        legend_y = 60
        legend_font = pygame.font.Font(None, 24)
        legend_items = [
            ("Combat", (200, 100, 100)),
            ("Elite", (150, 50, 150)),
            ("Exchange", (100, 200, 100)),
            ("Mystery", (200, 200, 100)),
            ("Boss", (150, 0, 0))
        ]
        
        for i, (name, color) in enumerate(legend_items):
            y_pos = legend_y + i * 25
            pygame.draw.circle(surface, color, (30, y_pos), 8)
            pygame.draw.circle(surface, (255, 255, 255), (30, y_pos), 8, 1)
            text_surface = legend_font.render(name, True, (255, 255, 255))
            surface.blit(text_surface, (50, y_pos - 10))
    
    def get_clicked_node(self, region_map: RegionMap, mouse_pos: Tuple[int, int]) -> Optional[MapNode]:
        """Get the node that was clicked, if any"""
        mouse_x, mouse_y = mouse_pos
        
        for node in region_map.nodes:
            # Check if click is within node radius
            distance = ((node.x - mouse_x) ** 2 + (node.y - mouse_y) ** 2) ** 0.5
            if distance <= 20:  # Node click radius
                return node
        
        return None