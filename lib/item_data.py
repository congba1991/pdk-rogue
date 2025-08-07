"""
Item definitions and data.
Contains all item instances used in the game.
"""

from dataclasses import dataclass
from typing import Optional
from lib.core_types import Rarity


@dataclass
class Item:
    name: str
    rarity: Rarity
    description: str
    max_inventory: int = 5
    item_type: str = "Passive"  # 'Passive', 'Active', 'Triggered'
    uses: Optional[int] = None  # For active items
    triggered_condition: Optional[str] = None  # For triggered items


# All Item Instances
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