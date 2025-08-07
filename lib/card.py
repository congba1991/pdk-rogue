"""
Card-related types and legacy imports.
This file now mainly provides backward compatibility imports.
"""

# Import from the new centralized location
from lib.core_types import Card, Suit
from lib.skill_card_data import SkillCard, SKILL_CARDS
from lib.item_data import Item, ITEMS
from lib.equipment_data import Equipment, EQUIPMENTS

# Re-export for backward compatibility
__all__ = ['Card', 'Suit', 'SkillCard', 'SKILL_CARDS', 'Item', 'ITEMS', 'Equipment', 'EQUIPMENTS']
