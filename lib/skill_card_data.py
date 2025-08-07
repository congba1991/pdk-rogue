"""
Skill card definitions and data.
Contains all skill card instances used in the game.
"""

from dataclasses import dataclass
from lib.core_types import Rarity


@dataclass
class SkillCard:
    name: str
    rarity: Rarity
    description: str
    max_inventory: int = 5
    one_time_use: bool = True


# All Skill Card Instances
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