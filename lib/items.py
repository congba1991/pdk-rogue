from dataclasses import dataclass
from typing import List, Optional, Any
from lib.card import Rarity


@dataclass
class Item:
    """Base item class"""
    name: str
    rarity: Rarity
    description: str
    item_type: str = "Passive"  # 'Passive', 'Active', 'Triggered'
    max_inventory: int = 5
    uses: Optional[int] = None  # For active items
    triggered_condition: Optional[str] = None  # For triggered items
    
    def can_use(self, game_state: Any) -> bool:
        """Check if the item can be used"""
        if self.item_type == "Active" and self.uses is not None:
            return self.uses > 0
        return True
    
    def use(self, game_state: Any) -> bool:
        """Use the item. Returns True if successful."""
        if self.item_type == "Active" and self.uses is not None:
            self.uses -= 1
        return True
    
    def on_trigger(self, game_state: Any, trigger_type: str) -> bool:
        """Handle triggered effects"""
        return True


class LuckyCharm(Item):
    """First damage each fight has 50% chance to be blocked"""
    
    def __init__(self):
        super().__init__(
            name="Lucky Charm",
            rarity=Rarity.COMMON,
            description="First damage each fight has 50% chance to be blocked",
            item_type="Passive"
        )
    
    def on_trigger(self, game_state: Any, trigger_type: str) -> bool:
        if trigger_type == "first_damage":
            import random
            return random.random() < 0.5  # 50% chance to block
        return False


class MomentumToken(Item):
    """After winning a fight with <5 cards, heal 1 LP"""
    
    def __init__(self):
        super().__init__(
            name="Momentum Token",
            rarity=Rarity.COMMON,
            description="After winning a fight with <5 cards, heal 1 LP",
            item_type="Passive"
        )
    
    def on_trigger(self, game_state: Any, trigger_type: str) -> bool:
        if trigger_type == "fight_won" and len(game_state.player.hand) < 5:
            game_state.player.life_points = min(
                game_state.player.life_points + 1,
                game_state.player.max_life_points
            )
            return True
        return False


class ScryingOrb(Item):
    """Look at 5 cards from the discard pile"""
    
    def __init__(self):
        super().__init__(
            name="Scrying Orb",
            rarity=Rarity.COMMON,
            description="Look at 5 cards from the discard pile",
            item_type="Active",
            uses=3
        )
    
    def can_use(self, game_state: Any) -> bool:
        return super().can_use(game_state) and len(game_state.discard_pile) > 0
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        # Show 5 cards from discard pile (or all if less than 5)
        cards_to_show = min(5, len(game_state.discard_pile))
        shown_cards = game_state.discard_pile[:cards_to_show]
        
        # In a real implementation, this would show a UI
        print(f"Scrying Orb shows: {[str(card) for card in shown_cards]}")
        
        return super().use(game_state)


class StraightBonus(Item):
    """Next 10 straights you play deal +1 damage when passed"""
    
    def __init__(self):
        super().__init__(
            name="Straight Bonus",
            rarity=Rarity.COMMON,
            description="Next 10 straights you play deal +1 damage when passed",
            item_type="Triggered",
            triggered_condition="Next 10 straights"
        )
        self.straights_remaining = 10
    
    def on_trigger(self, game_state: Any, trigger_type: str) -> bool:
        if trigger_type == "straight_played" and self.straights_remaining > 0:
            self.straights_remaining -= 1
            # Add damage bonus to the straight
            game_state.last_combo_damage_bonus += 1
            return True
        return False


# Registry of all items
ITEMS = {
    "Lucky Charm": LuckyCharm,
    "Momentum Token": MomentumToken,
    "Scrying Orb": ScryingOrb,
    "Straight Bonus": StraightBonus,
}


def get_item(name: str) -> Optional[Item]:
    """Get an item instance by name"""
    if name in ITEMS:
        return ITEMS[name]()
    return None


def get_all_items() -> List[Item]:
    """Get all available items"""
    return [item_class() for item_class in ITEMS.values()]


def get_items_by_type(item_type: str) -> List[Item]:
    """Get items filtered by type"""
    return [item_class() for item_class in ITEMS.values() 
            if item_class().item_type == item_type] 