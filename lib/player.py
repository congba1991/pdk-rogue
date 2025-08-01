from lib.card import Card
from lib.combo import identify_combo, ComboType
from collections import defaultdict
import itertools
import copy
import random
import json
try:
    import mcts_rust
except ImportError:
    mcts_rust = None

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
                    if values[i] != values[i - 1] + 1:
                        is_consecutive = False
                        break
                if is_consecutive:
                    length = end_idx - start_idx + 1
                    if target_length is None or length == target_length:
                        straight_cards = []
                        for val in values[start_idx : end_idx + 1]:
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

    def choose_play(self, last_combo, game_state, num_simulations=10):
        def card_to_dict(card):
            return {'rank': card.rank, 'suit': card.suit.value if hasattr(card.suit, 'value') else card.suit}

        valid_plays = self.find_valid_plays(last_combo)
        if not valid_plays:
            return None
        if len(valid_plays) == 1:
            return valid_plays[0]

        best_play = None
        best_score = -1
        for play in valid_plays:
            wins = 0
            for _ in range(num_simulations):
                ai_hand = copy.deepcopy(self.hand)
                opp_hand = [Card(c.rank, c.suit) for c in game_state.get('opponent_hand', [])] if 'opponent_hand' in game_state else [Card('3', '♦')]*len(self.hand)
                if not opp_hand:
                    all_ranks = list(Card.VALUE_MAP.keys())
                    all_suits = list(set(c.suit for c in ai_hand))
                    opp_hand = [Card(random.choice(all_ranks), random.choice(all_suits)) for _ in range(len(self.hand))]
                if mcts_rust:
                    result = mcts_rust.simulate_playout_py(
                        json.dumps([card_to_dict(c) for c in ai_hand]),
                        json.dumps([card_to_dict(c) for c in opp_hand]),
                        json.dumps([card_to_dict(c) for c in play.cards]),
                        json.dumps([]),  # last_combo, can be improved
                        True
                    )
                    if result:
                        wins += 1
                else:
                    # fallback: always lose
                    pass
            if wins > best_score:
                best_score = wins
                best_play = play
        return best_play if best_play else random.choice(valid_plays)
