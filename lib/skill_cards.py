from dataclasses import dataclass
from typing import List, Optional, Any
from lib.card import Rarity


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
        return len(game_state.discard_pile) >= 2
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
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
        return len(game_state.opponent.hand) > 0
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        # Take 1 random card from opponent
        import random
        stolen_card = random.choice(game_state.opponent.hand)
        
        # Add to player hand
        game_state.player.hand.append(stolen_card)
        
        # Remove from opponent hand
        game_state.opponent.hand.remove(stolen_card)
        
        return True


# Registry of all skill cards
SKILL_CARDS = {
    "Discard Grab": DiscardGrab,
    "Time Warp": TimeWarp,
    "Card Steal": CardSteal,
}


def get_skill_card(name: str) -> Optional[SkillCard]:
    """Get a skill card instance by name"""
    if name in SKILL_CARDS:
        return SKILL_CARDS[name]()
    return None


def get_all_skill_cards() -> List[SkillCard]:
    """Get all available skill cards"""
    return [card_class() for card_class in SKILL_CARDS.values()] 