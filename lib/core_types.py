"""
Core type definitions and enums for the game.
This module contains fundamental types used throughout the codebase.
"""

from dataclasses import dataclass
import pygame
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


# --- Suit Enum ---
class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    RED_JOKER = "🃏"
    BLACK_JOKER = "🂿"


# --- Card Class ---
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