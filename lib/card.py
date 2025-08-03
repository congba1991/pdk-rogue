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
