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
    SkillCard("Card Steal", Rarity.COMMON, "Take 1 random card from opponent's hand"),
    SkillCard("Damage Boost", Rarity.COMMON, "Your next combo deals +1 damage if passed"),
    SkillCard("Peek", Rarity.COMMON, "Can see 3 random cards from opponent's hand"),
    SkillCard("Recovery", Rarity.COMMON, "Heal 1 HP in this fight"),
    SkillCard("Quick Swap", Rarity.COMMON, "Swap one card from your hand with one random card from opponent's hand"),   
    SkillCard("Offload", Rarity.COMMON, "Discard 1 card and draw 1 random card"),   
    SkillCard("Upgrade", Rarity.COMMON, "Upgrade 1 card in your hand to next rank (max 2)"),
    SkillCard("Downgrade", Rarity.COMMON, "Downgrade 1 card in your hand to next rank (min 3)"), 
    SkillCard("Break", Rarity.COMMON, "Change 1 random card from opponent's hand into another random card"),
    SkillCard("Drop", Rarity.COMMON, "Discard 1 card from opponent's hand"),
    SkillCard("Double", Rarity.COMMON, "Add an extra card to your selected card for this fight"),
    SkillCard("Spade Master", Rarity.COMMON, "Change 2 cards into spades for this fight"),
    SkillCard("Heart Champion", Rarity.COMMON, "Change 2 cards into hearts for this fight"),
    SkillCard("Club Knight", Rarity.COMMON, "Change 2 cards into clubs for this fight"),
    SkillCard("Diamond King", Rarity.COMMON, "Change 2 cards into diamonds for this fight"),
    SkillCard("Pair Master", Rarity.COMMON, "Play any single as if it were a pair"),


    # Rare
    SkillCard("Discard Grab 2", Rarity.RARE, "Take 4 random cards from the discard pile into your hand"),
    SkillCard("Card Steal 2", Rarity.RARE, "Take 2 random cards from opponent's hand"), 
    SkillCard("Damage Boost 2", Rarity.RARE, "Your next combo deals +2 damage if passed"),
    SkillCard("Peek 2", Rarity.RARE, "Can see 6 random cards from opponent's hand"),
    SkillCard("Recovery 2", Rarity.RARE, "Heal 2 HP in this fight"),
    SkillCard("Quick Swap 2", Rarity.RARE, "Swap 2 cards from your hand with 2 random cards from opponent's hand"),  
    SkillCard("Offload 2", Rarity.RARE, "Discard 2 cards and draw 2 random cards"),
    
    SkillCard("Triple Master", Rarity.RARE, "Play any single as if it were a triple"),
    SkillCard("Mirror", Rarity.RARE, "Take one random card from opponent's last played combo into your hand"),
    SkillCard("Wild Card", Rarity.RARE, "Change a card to wild card (can be used as any rank) for this fight"),


    # Epic
    SkillCard("Discard Grab 3", Rarity.EPIC, "Choose 4 cards from the discard pile to add to your hand"),
    SkillCard("Card Steal 3", Rarity.EPIC, "Take the top 2 cards from opponent's hand"),
    SkillCard("Damage Boost 3", Rarity.EPIC, "Your next combo deals +3 damage if passed"),
    SkillCard("Peek 3", Rarity.EPIC, "Can see all cards from opponent's hand"),
    SkillCard("Recovery 3", Rarity.EPIC, "Heal 1 LP in this run"),
    SkillCard("Quick Swap 3", Rarity.EPIC, "Swap your hand with your opponent's hand"),   
    SkillCard("Offload 3", Rarity.EPIC, "Discard entire hand and draw same number of random cards"),
    
    SkillCard("Bomb Master", Rarity.EPIC, "Play any single as if it were a bomb"),   
    SkillCard("Mirror 2", Rarity.EPIC, "Take all cards from opponent's last played combo into your hand"),
    SkillCard("Wild Card 2", Rarity.EPIC, "Change 2 cards to wild cards (can be used as any rank) for this fight"),

]