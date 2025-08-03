
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum, StrEnum

# --- Enums for Rarity and Equipment Tier ---
class Rarity(StrEnum):
    COMMON = "Common"
    RARE = "Rare"
    EPIC = "Epic"

class EquipmentTier(StrEnum):
    STARTER = "Starter"
    ADVANCED = "Advanced"
    MASTER = "Master"


# --- Skill Cards ---
@dataclass
class SkillCard:
    name: str
    rarity: Rarity
    description: str
    max_inventory: int = 5
    one_time_use: bool = True


# --- Items ---
@dataclass
class Item:
    name: str
    rarity: Rarity
    description: str
    max_inventory: int = 5
    item_type: str = "Passive"  # 'Passive', 'Active', 'Triggered'
    uses: Optional[int] = None  # For active items
    triggered_condition: Optional[str] = None  # For triggered items


# --- Equipment ---
@dataclass
class Equipment:
    name: str
    tier: EquipmentTier
    description: str
    slot: int = 1

from enum import Enum


class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"


class Card:
    VALUE_MAP = {
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14,
        "2": 15,
    }

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = self.VALUE_MAP[rank]
        self.selected = False

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __lt__(self, other):
        return self.value < other.value
