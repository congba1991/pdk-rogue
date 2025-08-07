from typing import List, Optional, Tuple
import random
from lib.skill_cards import SkillCard, get_skill_card, get_all_skill_cards
from lib.items import Item, get_item, get_all_items
from lib.core_types import Rarity


class ExchangeNode:
    """Handles exchange functionality: 2 cards/items for 1 rare card/item"""
    
    def __init__(self):
        self.name = "Exchange Node"
        self.description = "Trade 2 cards for 1 rare card, or 2 items for 1 rare item"
    
    def get_rare_skill_cards(self) -> List[SkillCard]:
        """Get all rare skill cards available for exchange"""
        all_cards = get_all_skill_cards()
        rare_cards = [card for card in all_cards if card.rarity == Rarity.RARE]
        return rare_cards
    
    def get_rare_items(self) -> List[Item]:
        """Get all rare items available for exchange"""
        # Since all current items are common, let's create some rare items
        # For now, return empty list - we'll need to add rare items
        all_items = get_all_items()
        rare_items = [item for item in all_items if item.rarity == Rarity.RARE]
        return rare_items
    
    def can_exchange_skill_cards(self, player_skill_cards: List[str]) -> bool:
        """Check if player has at least 2 skill cards to exchange"""
        return len(player_skill_cards) >= 2
    
    def can_exchange_items(self, player_items: List[str]) -> bool:
        """Check if player has at least 2 items to exchange"""
        return len(player_items) >= 2
    
    def exchange_skill_cards(self, player_skill_cards: List[str], 
                           selected_cards: List[str]) -> Optional[SkillCard]:
        """Exchange 2 selected skill cards for 1 rare skill card"""
        if len(selected_cards) != 2:
            return None
        
        # Check that player actually has these cards
        for card_name in selected_cards:
            if card_name not in player_skill_cards:
                return None
        
        # Get available rare cards
        rare_cards = self.get_rare_skill_cards()
        if not rare_cards:
            return None
        
        # Remove the selected cards from player's inventory
        for card_name in selected_cards:
            player_skill_cards.remove(card_name)
        
        # Give a random rare card
        rare_card = random.choice(rare_cards)
        return rare_card
    
    def exchange_items(self, player_items: List[str], 
                      selected_items: List[str]) -> Optional[Item]:
        """Exchange 2 selected items for 1 rare item"""
        if len(selected_items) != 2:
            return None
        
        # Check that player actually has these items
        for item_name in selected_items:
            if item_name not in player_items:
                return None
        
        # Get available rare items
        rare_items = self.get_rare_items()
        if not rare_items:
            return None
        
        # Remove the selected items from player's inventory
        for item_name in selected_items:
            player_items.remove(item_name)
        
        # Give a random rare item
        rare_item = random.choice(rare_items)
        return rare_item
    
    def get_exchange_options(self, player_skill_cards: List[str], 
                           player_items: List[str]) -> Tuple[bool, bool]:
        """Get what exchange options are available to the player"""
        can_exchange_cards = self.can_exchange_skill_cards(player_skill_cards) and len(self.get_rare_skill_cards()) > 0
        can_exchange_items = self.can_exchange_items(player_items) and len(self.get_rare_items()) > 0
        return can_exchange_cards, can_exchange_items


def create_exchange_node() -> ExchangeNode:
    """Factory function to create an exchange node"""
    return ExchangeNode()