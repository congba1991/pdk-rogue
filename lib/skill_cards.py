from dataclasses import dataclass
from typing import List, Optional, Any
from lib.core_types import Rarity
import pygame


@dataclass
class SkillCard:
    """Base skill card class"""
    name: str
    rarity: Rarity
    description: str
    energy_cost: int = 0
    max_inventory: int = 5
    one_time_use: bool = True
    
    def can_use(self, game_state: Any) -> bool:
        """Check if the skill card can be used"""
        return True
    
    def use(self, game_state: Any) -> bool:
        """Use the skill card. Returns True if successful."""
        return True
    
    def draw_hover_description(self, surface, font, card_rect, window_width, bg_color, text_color):
        """Draw a floating description box above the card when hovered"""
        desc_text = self.description
        box_width = 260
        # Wrap description text to fit box width
        wrapped = []
        words = desc_text.split()
        line = ""
        for word in words:
            test_line = line + (" " if line else "") + word
            test_surface = font.render(test_line, True, text_color)
            if test_surface.get_width() > box_width - 20:
                wrapped.append(line)
                line = word
            else:
                line = test_line
        if line:
            wrapped.append(line)
        # Calculate box height based on number of lines
        line_height = 18
        padding = 20
        box_height = len(wrapped) * line_height + padding
        box_x = card_rect.centerx - box_width // 2
        box_y = card_rect.top - box_height - 10
        # Ensure box stays within screen
        box_x = max(10, min(box_x, window_width - box_width - 10))
        box_y = max(10, box_y)
        desc_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, bg_color, desc_rect)
        pygame.draw.rect(surface, text_color, desc_rect, 2)
        # Render wrapped description lines
        for j, wrap_line in enumerate(wrapped):
            wrap_surface = font.render(wrap_line, True, text_color)
            surface.blit(wrap_surface, (desc_rect.x + 10, desc_rect.y + 10 + j * line_height))


class DiscardGrab(SkillCard):
    """Take 2 random cards from the discard pile into your hand"""
    
    def __init__(self):
        super().__init__(
            name="Discard Grab",
            rarity=Rarity.COMMON,
            description="Take 2 random cards from the discard pile into your hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        # Check if discard pile has at least 2 cards
        return hasattr(game_state, 'discard_pile') and len(game_state.discard_pile) >= 2
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        # Take 2 random cards from discard pile
        import random
        cards_to_take = min(2, len(game_state.discard_pile))
        taken_cards = random.sample(game_state.discard_pile, cards_to_take)
        
        # Add to player hand
        game_state.player.hand.extend(taken_cards)
        
        # Remove from discard pile
        for card in taken_cards:
            game_state.discard_pile.remove(card)
        
        return True


class TimeWarp(SkillCard):
    """Take an extra turn after this one"""
    
    def __init__(self):
        super().__init__(
            name="Time Warp",
            rarity=Rarity.COMMON,
            description="Take an extra turn after this one",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        # Grant extra turn
        game_state.extra_turns += 1
        return True


class CardSteal(SkillCard):
    """Take 1 random card from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Card Steal",
            rarity=Rarity.COMMON,
            description="Take 1 random card from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) > 0
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        # Take 1 random card from opponent
        import random
        stolen_card = random.choice(game_state.ai.hand)
        
        # Add to player hand
        game_state.player.hand.append(stolen_card)
        
        # Remove from opponent hand
        game_state.ai.hand.remove(stolen_card)
        
        return True


class DamageBoost(SkillCard):
    """Next damage you deal is increased by 1"""
    
    def __init__(self):
        super().__init__(
            name="Damage Boost",
            rarity=Rarity.COMMON,
            description="Next damage you deal is increased by 1",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        # Add damage bonus for next combo that beats opponent
        game_state.last_combo_damage_bonus += 1
        return True


class HandRefresh(SkillCard):
    """Draw 3 cards from the deck if available"""
    
    def __init__(self):
        super().__init__(
            name="Hand Refresh",
            rarity=Rarity.COMMON,
            description="Draw 3 cards from the deck if available",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        # Can use if we're in a proper game state (has discard pile)
        return hasattr(game_state, 'discard_pile')
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        # Draw up to 3 cards from discard pile (simulating deck)
        import random
        cards_to_draw = min(3, len(game_state.discard_pile))
        if cards_to_draw > 0:
            drawn_cards = random.sample(game_state.discard_pile, cards_to_draw)
            game_state.player.hand.extend(drawn_cards)
            for card in drawn_cards:
                game_state.discard_pile.remove(card)
        return True


class ShieldBreaker(SkillCard):
    """Next time opponent would take damage, they take 1 extra damage"""
    
    def __init__(self):
        super().__init__(
            name="Shield Breaker",
            rarity=Rarity.RARE,
            description="Next time opponent would take damage, they take 1 extra damage",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        # Add damage bonus for next successful attack
        game_state.last_combo_damage_bonus += 1
        return True


class CardSort(SkillCard):
    """Reorganize your hand optimally"""
    
    def __init__(self):
        super().__init__(
            name="Card Sort",
            rarity=Rarity.COMMON,
            description="Reorganize your hand optimally",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'sort_hand')):
            return False
        
        # Resort the hand
        game_state.player.sort_hand()
        return True


class LifeSteal(SkillCard):
    """Next damage you deal also heals you for 1 HP"""
    
    def __init__(self):
        super().__init__(
            name="Life Steal",
            rarity=Rarity.RARE,
            description="Next damage you deal also heals you for 1 HP",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        # This would need special handling in combat system
        game_state.last_combo_damage_bonus += 0  # No damage bonus
        # TODO: Add life steal effect tracking
        return True


# Registry of all skill cards
SKILL_CARDS = {
    "Discard Grab": DiscardGrab,
    "Time Warp": TimeWarp,
    "Card Steal": CardSteal,
    "Damage Boost": DamageBoost,
    "Hand Refresh": HandRefresh,
    "Shield Breaker": ShieldBreaker,
    "Card Sort": CardSort,
    "Life Steal": LifeSteal,
}


def get_skill_card(name: str) -> Optional[SkillCard]:
    """Get a skill card instance by name"""
    if name in SKILL_CARDS:
        return SKILL_CARDS[name]()
    return None


def get_all_skill_cards() -> List[SkillCard]:
    """Get all available skill cards"""
    return [card_class() for card_class in SKILL_CARDS.values()]


def get_random_skill_cards(count: int = 3, exclude: List[str] = None) -> List[SkillCard]:
    """Get random skill cards for rewards"""
    import random
    exclude = exclude or []
    available_cards = [name for name in SKILL_CARDS.keys() if name not in exclude]
    
    if len(available_cards) < count:
        count = len(available_cards)
    
    selected_names = random.sample(available_cards, count)
    return [get_skill_card(name) for name in selected_names]


def get_skill_card_image_path(card_name: str) -> str:
    """Get the file path for a skill card image"""
    import os
    filename = card_name.lower().replace(" ", "_").replace("'", "") + ".png"
    return os.path.join("images/skill_cards", filename)


def load_skill_card_image(card_name: str):
    """Load a skill card image, return None if not found"""
    try:
        import pygame
        import os
        image_path = get_skill_card_image_path(card_name)
        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        else:
            # Return a placeholder if image doesn't exist
            return None
    except:
        return None 