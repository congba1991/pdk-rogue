
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

# --- Custom StrEnum implementation for Python 3.9 compatibility ---
class StrEnum(str, Enum):
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

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


# --- All Skill Card Instances ---
SKILL_CARDS = [
    # Common
    SkillCard("Discard Grab", Rarity.COMMON, "Take 2 random cards from the discard pile into your hand"),
    SkillCard("Time Warp", Rarity.COMMON, "Take an extra turn after this one"),
    SkillCard("Card Steal", Rarity.COMMON, "Take 1 random card from opponent's hand"),
    SkillCard("Damage Boost", Rarity.COMMON, "Your next combo deals +2 damage if passed"),
    SkillCard("Peek", Rarity.COMMON, "Can see 3 random cards from opponent's hand"),
    SkillCard("Add One", Rarity.COMMON, "Play any single as if it were a pair"),
    SkillCard("Straight Helper", Rarity.COMMON, "For this turn, gaps in straights are allowed (3-5-6-7 is valid)"),
    SkillCard("Recovery", Rarity.COMMON, "Heal 1 HP in this fight"),
    SkillCard("Steal", Rarity.COMMON, "Take one card from opponent's last played combo into your hand"),

    # Rare
    SkillCard("Discard Grab 2", Rarity.RARE, "Take 4 random cards from the discard pile into your hand"),
    SkillCard("Card Steal 2", Rarity.RARE, "Take 2 random cards from opponent's hand"),
    SkillCard("Peek 2", Rarity.RARE, "Can see 6 random cards from opponent's hand"),
    SkillCard("Recovery 2", Rarity.RARE, "Heal 1 LP in this run"),
    SkillCard("Double Strike", Rarity.RARE, "Play two combos of the same type this turn (opponent has to beat the bigger combo)"),
    SkillCard("Reversal", Rarity.RARE, "Next combo your opponent plays treated as what you plays"),
    SkillCard("Wild Card", Rarity.RARE, "Change the value of a card to any value you want"),
    SkillCard("Steal 2", Rarity.RARE, "Take the cards from opponent's last played combo into your hand"),
    SkillCard("Power Surge", Rarity.RARE, "All your combos (including your opponent's) deal +1 damage when passed for the rest of this fight"),
    SkillCard("Forced Pass", Rarity.RARE, "Force opponent to pass their next turn (and take damage)"),

    # Epic
    SkillCard("Perfect Information", Rarity.EPIC, "See opponent's entire hand for this fight"),
    SkillCard("Mirror Match", Rarity.EPIC, "Copy the last combo your opponent played"),
    SkillCard("Hand Swap", Rarity.EPIC, "Exchange your entire hand with your opponent's (can only use at the beginning of a fight)"),
    SkillCard("Wild Card 2", Rarity.EPIC, "Turn all cards of one rank in your hand into another rank"),
    SkillCard("Ultimate Defense", Rarity.EPIC, "Take no damage for the next 3 turns"),
    SkillCard("Recovery 3", Rarity.EPIC, "Heal 2 LP in this run"),
]


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


# --- All Item Instances ---
ITEMS = [
    # Passive Items
    Item("Lucky Charm", Rarity.COMMON, "First damage each fight has 50% chance to be blocked", item_type="Passive"),
    Item("Momentum Token", Rarity.COMMON, "After winning a fight with <5 cards, heal 1 LP", item_type="Passive"),
    Item("Combo Counter", Rarity.RARE, "Every 5th combo you play deals +2 damage when passed", item_type="Passive"),
    Item("Defensive Barrier", Rarity.RARE, "Block first damage in next 3 fights (then destroyed)", item_type="Passive"),
    Item("Pair Master's Ring", Rarity.EPIC, "All pairs count as having +1 rank value", item_type="Passive"),

    # Active Items
    Item("Scrying Orb", Rarity.COMMON, "Look at 5 cards from the discard pile", item_type="Active", uses=3),
    Item("Discard Retriever", Rarity.COMMON, "Take 2 random cards from discard pile", item_type="Active", uses=3),
    Item("Hand Mixer", Rarity.RARE, "Return up to 5 cards to discard, take that many random cards back", item_type="Active", uses=2),
    Item("Damage Amplifier", Rarity.RARE, "Next combo deals twice damage (on top of any other damage amplification) when passed", item_type="Active", uses=3),
    Item("Emergency Block", Rarity.EPIC, "Block all damage from next enemy hand", item_type="Active", uses=2),

    # Triggered Items
    Item("Straight Bonus", Rarity.COMMON, "Next 10 straights you play deal +1 damage when passed", item_type="Triggered", triggered_condition="Next 10 straights"),
    Item("Plane Reward", Rarity.RARE, "When playing a plane combo, draw 1 skill card (once per fight)", item_type="Triggered", triggered_condition="Play plane combo"),
    Item("Bomb Echo", Rarity.EPIC, "After playing a bomb, opponent takes 2 damage (once per fight)", item_type="Triggered", triggered_condition="Play bomb"),
    Item("Pass Punishment", Rarity.EPIC, "When opponent passes, they take 1 extra damage (3 fights, then destroyed)", item_type="Triggered", triggered_condition="Opponent passes"),
]


# --- Equipment ---
@dataclass
class Equipment:
    name: str
    tier: EquipmentTier
    description: str
    slot: int = 1


# --- All Equipment Instances ---
EQUIPMENTS = [
    # Starter Equipment
    Equipment("Sturdy Boots", EquipmentTier.STARTER, "+1 Max HP in fights"),
    Equipment("Quick Fingers", EquipmentTier.STARTER, "Once per fight: Steal 1 random card from opponent"),
    Equipment("Lucky Coin", EquipmentTier.STARTER, "25% chance to block first damage each fight"),
    Equipment("Sharp Mind", EquipmentTier.STARTER, "Start each fight seeing 4 discarded cards"),

    # Advanced Equipment
    Equipment("Gambler's Dice", EquipmentTier.ADVANCED, "Once per fight: Return hand to discard, get same number of random cards"),
    Equipment("Combo Manual", EquipmentTier.ADVANCED, "Triples can be played to beat any pairs"),
    Equipment("Defensive Stance", EquipmentTier.ADVANCED, "After passing, next pass has 50% chance to take no damage."),
    Equipment("Aggressive Style", EquipmentTier.ADVANCED, "After causing damage, next damaging hand has 50% chance to cause +1 damage."),
    Equipment("Survivor's Will", EquipmentTier.ADVANCED, "Once per run: Survive a lethal hit with 1 HP"),
    Equipment("Straight Flush", EquipmentTier.ADVANCED, "Straights of same suit deal +2 damage"),

    # Master Equipment
    Equipment("Phoenix Feather", EquipmentTier.MASTER, "Once per run: Revive with 2 LP when defeated"),
    Equipment("Plane Master", EquipmentTier.MASTER, "Planes takes 1 more attachment (minimum 0, max 3)"),
    Equipment("Grand Master's Token", EquipmentTier.MASTER, "+1 Equipment slot, +1 Card Inventory, +1 Item Inventory"),
]

from enum import Enum


class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    RED_JOKER = "🃏"
    BLACK_JOKER = "🂿"


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
        "Black Joker": 16,
        "Red Joker": 17,
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
