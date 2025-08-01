from lib.card import Card
from lib.combo import identify_combo, ComboType
from collections import defaultdict
import itertools

class RoguePlayer:
    def __init__(self, name):
        self.name = name
        self.life = 10
        self.skill_cards = []
        self.items = []

class FightPlayer:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.hand = []
        self.hp = 10
    def sort_hand(self):
        self.hand.sort()
    def remove_cards(self, cards):
        for card in cards:
            self.hand.remove(card)

class AIFightPlayer(FightPlayer):
    def __init__(self, name):
        super().__init__(name, is_ai=True)
    def find_valid_plays(self, last_combo):
        # ...existing code...
        valid_combos = []
        value_groups = defaultdict(list)
        for card in self.hand:
            value_groups[card.value].append(card)
        if last_combo is None:
            for card in self.hand:
                combo = identify_combo([card])
                if combo:
                    valid_combos.append(combo)
            for cards in value_groups.values():
                if len(cards) >= 2:
                    combo = identify_combo(cards[:2])
                    if combo:
                        valid_combos.append(combo)
            for cards in value_groups.values():
                if len(cards) >= 3:
                    combo = identify_combo(cards[:3])
                    if combo:
                        valid_combos.append(combo)
            valid_combos.extend(self._find_straights())
            valid_combos.extend(self._find_planes())
        else:
            if last_combo.type == ComboType.SINGLE:
                for card in self.hand:
                    if card.value > last_combo.lead_value:
                        combo = identify_combo([card])
                        if combo:
                            valid_combos.append(combo)
            elif last_combo.type == ComboType.PAIR:
                for cards in value_groups.values():
                    if len(cards) >= 2 and cards[0].value > last_combo.lead_value:
                        combo = identify_combo(cards[:2])
                        if combo:
                            valid_combos.append(combo)
            elif last_combo.type == ComboType.TRIPLE:
                for cards in value_groups.values():
                    if len(cards) >= 3 and cards[0].value > last_combo.lead_value:
                        combo = identify_combo(cards[:3])
                        if combo:
                            valid_combos.append(combo)
            elif last_combo.type == ComboType.STRAIGHT:
                straights = self._find_straights(len(last_combo.cards))
                for combo in straights:
                    if combo.can_beat(last_combo):
                        valid_combos.append(combo)
            elif last_combo.type in [ComboType.PLANE, ComboType.PLANE_WITH_SINGLES, ComboType.PLANE_WITH_PAIRS]:
                planes = self._find_planes()
                for combo in planes:
                    if combo.can_beat(last_combo):
                        valid_combos.append(combo)
            for cards in value_groups.values():
                if len(cards) == 4:
                    bomb = identify_combo(cards)
                    if bomb and bomb.can_beat(last_combo):
                        valid_combos.append(bomb)
        return valid_combos
    def _find_straights(self, target_length=None):
        # ...existing code...
        straights = []
        values = sorted(set(card.value for card in self.hand if card.value <= 14))
        min_length = target_length if target_length else 5
        for start_idx in range(len(values)):
            for end_idx in range(start_idx + min_length - 1, len(values)):
                is_consecutive = True
                for i in range(start_idx + 1, end_idx + 1):
                    if values[i] != values[i-1] + 1:
                        is_consecutive = False
                        break
                if is_consecutive:
                    length = end_idx - start_idx + 1
                    if target_length is None or length == target_length:
                        straight_cards = []
                        for val in values[start_idx:end_idx+1]:
                            for card in self.hand:
                                if card.value == val and card not in straight_cards:
                                    straight_cards.append(card)
                                    break
                        if len(straight_cards) == length:
                            combo = identify_combo(straight_cards)
                            if combo:
                                straights.append(combo)
        return straights
    def _find_planes(self):
        # ...existing code...
        planes = []
        value_groups = defaultdict(list)
        for card in self.hand:
            value_groups[card.value].append(card)
        triple_values = []
        for value, cards in value_groups.items():
            if len(cards) >= 3 and value <= 14:
                triple_values.append(value)
        if len(triple_values) < 2:
            return planes
        triple_values.sort()
        for start_idx in range(len(triple_values)):
            consecutive = [triple_values[start_idx]]
            for i in range(start_idx + 1, len(triple_values)):
                if triple_values[i] == consecutive[-1] + 1:
                    consecutive.append(triple_values[i])
                else:
                    break
            if len(consecutive) >= 2:
                for length in range(2, len(consecutive) + 1):
                    plane_base = []
                    for val in consecutive[:length]:
                        for card in value_groups[val][:3]:
                            plane_base.append(card)
                    combo = identify_combo(plane_base)
                    if combo:
                        planes.append(combo)
                    available_singles = []
                    for card in self.hand:
                        if card not in plane_base:
                            available_singles.append(card)
                    if len(available_singles) >= length:
                        for singles in itertools.combinations(available_singles, length):
                            test_cards = plane_base + list(singles)
                            combo = identify_combo(test_cards)
                            if combo and combo.type == ComboType.PLANE_WITH_SINGLES:
                                planes.append(combo)
                    available_for_pairs = defaultdict(list)
                    for card in self.hand:
                        if card not in plane_base:
                            available_for_pairs[card.value].append(card)
                    pairs = []
                    for value, cards in available_for_pairs.items():
                        if len(cards) >= 2:
                            pairs.append(cards[:2])
                    if len(pairs) >= length:
                        for pair_combo in itertools.combinations(pairs, length):
                            test_cards = plane_base[:]
                            for pair in pair_combo:
                                test_cards.extend(pair)
                            combo = identify_combo(test_cards)
                            if combo and combo.type == ComboType.PLANE_WITH_PAIRS:
                                planes.append(combo)
        return planes
    def choose_play(self, last_combo, game_state):
        # ...existing code...
        valid_plays = self.find_valid_plays(last_combo)
        if not valid_plays:
            return None
        if last_combo is None:
            singles = [c for c in valid_plays if c.type == ComboType.SINGLE]
            pairs = [c for c in valid_plays if c.type == ComboType.PAIR]
            if len(self.hand) > 10 and singles:
                return min(singles, key=lambda c: c.lead_value)
            elif pairs:
                return min(pairs, key=lambda c: c.lead_value)
        if len(self.hand) <= 3:
            return valid_plays[0]
        valid_plays.sort(key=lambda c: (c.type.value, c.lead_value))
        non_bombs = [c for c in valid_plays if c.type != ComboType.BOMB]
        if non_bombs:
            return non_bombs[0]
        if len(self.hand) > 10:
            return None
        return valid_plays[0]
