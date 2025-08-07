"""
Equipment definitions and data.
Contains all equipment instances used in the game.
"""

from dataclasses import dataclass
from lib.core_types import EquipmentTier


@dataclass
class Equipment:
    name: str
    tier: EquipmentTier
    description: str
    slot: int = 1


# All Equipment Instances
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