# Export SmartAIPlayer for use in other modules
__all__ = [
    'RoguePlayer',
    'FightPlayer',
    'SmartAIPlayer',
]

from lib.card import Card
from lib.combo import identify_combo, ComboType
from collections import defaultdict
import itertools
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
    def find_valid_plays(self, last_combo):
        value_groups = defaultdict(list)
        for card in self.hand:
            value_groups[card.value].append(card)
        valid_combos = []
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
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.hand = []
        self.hp = 5

    def sort_hand(self):
        self.hand.sort()

    def remove_cards(self, cards):
        for card in cards:
            self.hand.remove(card)


class SmartAIPlayer(FightPlayer):
    def __init__(self, name):
        super().__init__(name, is_ai=True)

    def choose_play(self, last_combo, game_state, depth=20):
        def card_to_dict(card):
            return {'rank': card.rank, 'suit': card.suit.value if hasattr(card.suit, 'value') else card.suit}

        valid_plays = self.find_valid_plays(last_combo)
        if not valid_plays:
            return None
        if len(valid_plays) == 1:
            return valid_plays[0]

        # Always use Rust minimax if available
        if mcts_rust and hasattr(mcts_rust, 'minimax_search_py'):
            ai_hand_json = json.dumps([card_to_dict(c) for c in self.hand])
            # Estimate opponent hand (fallback: same size, random cards)
            opp_hand = [Card(c.rank, c.suit) for c in game_state.get('opponent_hand', [])] if 'opponent_hand' in game_state else [Card('3', '♦')]*len(self.hand)
            if not opp_hand:
                all_ranks = list(Card.VALUE_MAP.keys())
                all_suits = list(set(c.suit for c in self.hand))
                opp_hand = [Card(random.choice(all_ranks), random.choice(all_suits)) for _ in range(len(self.hand))]
            opp_hand_json = json.dumps([card_to_dict(c) for c in opp_hand])
            # Always convert Combo to dict of cards for JSON serialization
            if last_combo:
                combo_type = getattr(last_combo, 'type', 'SINGLE')
                if hasattr(combo_type, 'name'):
                    combo_type = combo_type.name
                last_combo_json = json.dumps({
                    'cards': [card_to_dict(c) for c in last_combo.cards],
                    'combo_type': combo_type,
                    'lead_value': getattr(last_combo, 'lead_value', 0)
                })
            else:
                last_combo_json = json.dumps(None)
            try:
                result = mcts_rust.minimax_search_py(
                    ai_hand_json,
                    last_combo_json,
                    opp_hand_json,
                    getattr(self, 'hp', 10),
                    game_state.get('opponent_hp', 10),
                    depth
                )
                if hasattr(result, 'unwrap'):
                    result = result.unwrap()
                if result and result != 'null':
                    # Parse Combo from JSON
                    combo_dict = json.loads(result)
                    # Reconstruct Combo as in ComboType
                    combo_cards = [Card(c['rank'], c['suit']) for c in combo_dict['cards']]
                    combo_type = combo_dict.get('combo_type', 'SINGLE')
                    lead_value = combo_dict.get('lead_value', 0)
                    # Try to match to a valid play
                    for play in valid_plays:
                        if set((c.rank, str(c.suit)) for c in play.cards) == set((c['rank'], str(c['suit'])) for c in combo_dict['cards']):
                            return play
            except Exception:
                pass
        # Fallback: random play
        return random.choice(valid_plays)
