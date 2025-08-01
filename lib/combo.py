from enum import Enum
from collections import defaultdict


class ComboType(Enum):
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    STRAIGHT = 4
    PAIR_STRAIGHT = 5
    TRIPLE_WITH_SINGLE = 6
    TRIPLE_WITH_PAIR = 7
    FOUR_WITH_TWO = 8
    PLANE = 9
    PLANE_WITH_SINGLES = 10
    PLANE_WITH_PAIRS = 11
    BOMB = 12


class Combo:
    def __init__(self, cards, combo_type):
        self.cards = sorted(cards)
        self.type = combo_type
        self.lead_value = self._get_lead_value()

    def _get_lead_value(self):
        # ...existing code...
        if self.type == ComboType.SINGLE:
            return self.cards[0].value
        elif self.type in [ComboType.PAIR, ComboType.TRIPLE]:
            return self.cards[0].value
        elif self.type == ComboType.STRAIGHT:
            return self.cards[-1].value
        elif self.type in [ComboType.TRIPLE_WITH_SINGLE, ComboType.TRIPLE_WITH_PAIR]:
            value_counts = defaultdict(int)
            for card in self.cards:
                value_counts[card.value] += 1
            for value, count in value_counts.items():
                if count == 3:
                    return value
        elif self.type == ComboType.FOUR_WITH_TWO:
            value_counts = defaultdict(int)
            for card in self.cards:
                value_counts[card.value] += 1
            for value, count in value_counts.items():
                if count == 4:
                    return value
        elif self.type in [ComboType.PLANE, ComboType.PLANE_WITH_SINGLES, ComboType.PLANE_WITH_PAIRS]:
            value_counts = defaultdict(int)
            for card in self.cards:
                value_counts[card.value] += 1
            triple_values = [value for value, count in value_counts.items() if count >= 3]
            return max(triple_values) if triple_values else 0
        elif self.type == ComboType.BOMB:
            return self.cards[0].value
        return 0

    def can_beat(self, other):
        # ...existing code...
        if other is None:
            return True
        if self.type == ComboType.BOMB:
            if other.type != ComboType.BOMB:
                return True
            return self.lead_value > other.lead_value
        if other.type == ComboType.BOMB:
            return False
        if self.type == other.type:
            if self.type == ComboType.STRAIGHT:
                if len(self.cards) != len(other.cards):
                    return False
            elif self.type in [ComboType.PLANE, ComboType.PLANE_WITH_SINGLES, ComboType.PLANE_WITH_PAIRS]:
                my_triples = self._count_consecutive_triples()
                other_triples = other._count_consecutive_triples()
                if my_triples != other_triples:
                    return False
            return self.lead_value > other.lead_value
        return False

    def _count_consecutive_triples(self):
        value_counts = defaultdict(int)
        for card in self.cards:
            value_counts[card.value] += 1
        triple_values = sorted([value for value, count in value_counts.items() if count >= 3])
        if not triple_values:
            return 0
        count = 1
        for i in range(1, len(triple_values)):
            if triple_values[i] == triple_values[i - 1] + 1:
                count += 1
            else:
                break
        return count


def identify_combo(cards):
    # ...existing code...
    if not cards:
        return None
    cards = sorted(cards)
    n = len(cards)
    if n == 1:
        return Combo(cards, ComboType.SINGLE)
    value_counts = defaultdict(list)
    for card in cards:
        value_counts[card.value].append(card)
    if n == 2 and len(value_counts) == 1:
        return Combo(cards, ComboType.PAIR)
    if n == 3 and len(value_counts) == 1:
        return Combo(cards, ComboType.TRIPLE)
    if n == 4 and len(value_counts) == 1:
        return Combo(cards, ComboType.BOMB)

    # Pair straight (consecutive pairs, at least 3 pairs, no 2s)
    if n >= 6 and n % 2 == 0:
        pairs = [value for value, same_cards in value_counts.items() if len(same_cards) >= 2 and value <= 14]
        if len(pairs) == n // 2:
            pairs.sort()
            is_consecutive = True
            for i in range(1, len(pairs)):
                if pairs[i] != pairs[i-1] + 1:
                    is_consecutive = False
                    break
            if is_consecutive and len(pairs) >= 3:
                # Build the pair straight cards in order
                pair_straight_cards = []
                for val in pairs:
                    count = 0
                    for card in cards:
                        if card.value == val and count < 2:
                            pair_straight_cards.append(card)
                            count += 1
                if len(pair_straight_cards) == n:
                    return Combo(pair_straight_cards, ComboType.PAIR_STRAIGHT)
    triple_values = []
    triple_cards = []
    other_cards = []
    for value, same_cards in value_counts.items():
        if len(same_cards) >= 3:
            triple_values.append(value)
            triple_cards.extend(same_cards[:3])
            if len(same_cards) > 3:
                other_cards.extend(same_cards[3:])
        else:
            other_cards.extend(same_cards)
    if len(triple_values) >= 2:
        triple_values.sort()
        consecutive_count = 1
        for i in range(1, len(triple_values)):
            if triple_values[i] == triple_values[i - 1] + 1 and triple_values[i] <= 14:
                consecutive_count += 1
            else:
                break
        if consecutive_count >= 2:
            plane_cards = []
            for i in range(consecutive_count):
                val = triple_values[i]
                for card in cards:
                    if card.value == val and len([c for c in plane_cards if c.value == val]) < 3:
                        plane_cards.append(card)
            remaining = [c for c in cards if c not in plane_cards]
            if len(remaining) == 0 and len(plane_cards) == n:
                return Combo(cards, ComboType.PLANE)
            if len(remaining) == consecutive_count:
                return Combo(cards, ComboType.PLANE_WITH_SINGLES)
            if len(remaining) == consecutive_count * 2:
                attach_counts = defaultdict(int)
                for card in remaining:
                    attach_counts[card.value] += 1
                pair_count = sum(1 for count in attach_counts.values() if count >= 2)
                if pair_count == consecutive_count:
                    return Combo(cards, ComboType.PLANE_WITH_PAIRS)
    if n >= 5:
        is_straight = True
        for i in range(1, n):
            if cards[i].value != cards[i - 1].value + 1:
                is_straight = False
                break
            if cards[i].value > 14:
                is_straight = False
                break
        if is_straight and cards[0].value <= 14:
            return Combo(cards, ComboType.STRAIGHT)
    if n == 4:
        for value, same_cards in value_counts.items():
            if len(same_cards) == 3:
                return Combo(cards, ComboType.TRIPLE_WITH_SINGLE)
    if n == 5:
        has_triple = False
        has_pair = False
        for value, same_cards in value_counts.items():
            if len(same_cards) == 3:
                has_triple = True
            elif len(same_cards) == 2:
                has_pair = True
        if has_triple and has_pair:
            return Combo(cards, ComboType.TRIPLE_WITH_PAIR)
    if n == 6:
        has_four = False
        for value, same_cards in value_counts.items():
            if len(same_cards) == 4:
                has_four = True
                break
        if has_four:
            return Combo(cards, ComboType.FOUR_WITH_TWO)
    return None
