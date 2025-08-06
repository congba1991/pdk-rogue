from dataclasses import dataclass
from typing import List, Optional, Any
from lib.card import EquipmentTier


@dataclass
class Equipment:
    """Base equipment class"""
    name: str
    tier: EquipmentTier
    description: str
    slot: int = 1  # How many equipment slots this takes
    
    def on_equip(self, game_state: Any) -> bool:
        """Called when equipment is equipped"""
        return True
    
    def on_unequip(self, game_state: Any) -> bool:
        """Called when equipment is unequipped"""
        return True
    
    def on_fight_start(self, game_state: Any) -> bool:
        """Called at the start of each fight"""
        return True
    
    def on_fight_end(self, game_state: Any) -> bool:
        """Called at the end of each fight"""
        return True
    
    def on_turn_start(self, game_state: Any) -> bool:
        """Called at the start of each turn"""
        return True
    
    def on_damage_taken(self, game_state: Any, damage: int) -> int:
        """Called when damage is taken. Returns modified damage."""
        return damage
    
    def on_damage_dealt(self, game_state: Any, damage: int) -> int:
        """Called when damage is dealt. Returns modified damage."""
        return damage


class SturdyBoots(Equipment):
    """+1 Max HP in fights"""
    
    def __init__(self):
        super().__init__(
            name="Sturdy Boots",
            tier=EquipmentTier.STARTER,
            description="+1 Max HP in fights",
            slot=1
        )
    
    def on_equip(self, game_state: Any) -> bool:
        # Add 1 to current HP (since there's no max_hp concept in FightPlayer)
        game_state.player.hp += 1
        return True
    
    def on_unequip(self, game_state: Any) -> bool:
        # Reduce HP by 1, but don't go below 1
        game_state.player.hp = max(1, game_state.player.hp - 1)
        return True


class QuickFingers(Equipment):
    """Once per fight: Steal 1 random card from opponent"""
    
    def __init__(self):
        super().__init__(
            name="Quick Fingers",
            tier=EquipmentTier.STARTER,
            description="Once per fight: Steal 1 random card from opponent",
            slot=1
        )
        self.used_this_fight = False
    
    def on_fight_start(self, game_state: Any) -> bool:
        self.used_this_fight = False
        return True
    
    def can_steal_card(self, game_state: Any) -> bool:
        """Check if we can steal a card this fight"""
        return (not self.used_this_fight and 
                len(game_state.ai.hand) > 0)
    
    def steal_card(self, game_state: Any) -> bool:
        """Steal a random card from opponent"""
        if not self.can_steal_card(game_state):
            return False
        
        import random
        stolen_card = random.choice(game_state.ai.hand)
        
        # Add to player hand
        game_state.player.hand.append(stolen_card)
        
        # Remove from opponent hand
        game_state.ai.hand.remove(stolen_card)
        
        # Resort the player's hand
        game_state.resort_hand(game_state.player)
        
        self.used_this_fight = True
        return True


class LuckyCoin(Equipment):
    """25% chance to block first damage each fight"""
    
    def __init__(self):
        super().__init__(
            name="Lucky Coin",
            tier=EquipmentTier.STARTER,
            description="25% chance to block first damage each fight",
            slot=1
        )
        self.first_damage_blocked = False
    
    def on_fight_start(self, game_state: Any) -> bool:
        self.first_damage_blocked = False
        return True
    
    def on_damage_taken(self, game_state: Any, damage: int) -> int:
        if not self.first_damage_blocked:
            import random
            if random.random() < 0.25:  # 25% chance
                self.first_damage_blocked = True
                return 0  # Block the damage
        return damage


class SharpMind(Equipment):
    """Start each fight seeing 4 discarded cards"""
    
    def __init__(self):
        super().__init__(
            name="Sharp Mind",
            tier=EquipmentTier.STARTER,
            description="Start each fight seeing 4 discarded cards",
            slot=1
        )
    
    def on_fight_start(self, game_state: Any) -> bool:
        # Show 4 cards from discard pile (or all if less than 4)
        cards_to_show = min(4, len(game_state.discard_pile))
        if cards_to_show > 0:
            shown_cards = game_state.discard_pile[:cards_to_show]
            # In a real implementation, this would show a UI
            print(f"Sharp Mind reveals: {[str(card) for card in shown_cards]}")
        return True


class GamblersDice(Equipment):
    """Once per fight: Return hand to discard, get same number of random cards"""
    
    def __init__(self):
        super().__init__(
            name="Gambler's Dice",
            tier=EquipmentTier.ADVANCED,
            description="Once per fight: Return hand to discard, get same number of random cards",
            slot=1
        )
        self.used_this_fight = False
    
    def on_fight_start(self, game_state: Any) -> bool:
        self.used_this_fight = False
        return True
    
    def can_use(self, game_state: Any) -> bool:
        """Check if we can use the dice this fight"""
        return not self.used_this_fight
    
    def use(self, game_state: Any) -> bool:
        """Use the gambler's dice"""
        if not self.can_use(game_state):
            return False
        
        # Return current hand to discard pile
        hand_size = len(game_state.player.hand)
        game_state.discard_pile.extend(game_state.player.hand)
        game_state.player.hand.clear()
        
        # Draw same number of random cards
        import random
        if len(game_state.discard_pile) > 0:
            drawn_cards = random.sample(
                game_state.discard_pile, 
                min(hand_size, len(game_state.discard_pile))
            )
            game_state.player.hand.extend(drawn_cards)
            
            # Remove drawn cards from discard pile
            for card in drawn_cards:
                game_state.discard_pile.remove(card)
        
        # Resort the player's hand
        game_state.resort_hand(game_state.player)
        
        self.used_this_fight = True
        return True


# Registry of all equipment
EQUIPMENT = {
    "Sturdy Boots": SturdyBoots,
    "Quick Fingers": QuickFingers,
    "Lucky Coin": LuckyCoin,
    "Sharp Mind": SharpMind,
    "Gambler's Dice": GamblersDice,
}


def get_equipment(name: str) -> Optional[Equipment]:
    """Get an equipment instance by name"""
    if name in EQUIPMENT:
        return EQUIPMENT[name]()
    return None


def get_all_equipment() -> List[Equipment]:
    """Get all available equipment"""
    return [equipment_class() for equipment_class in EQUIPMENT.values()]


def get_equipment_by_tier(tier: EquipmentTier) -> List[Equipment]:
    """Get equipment filtered by tier"""
    return [equipment_class() for equipment_class in EQUIPMENT.values() 
            if equipment_class().tier == tier] 