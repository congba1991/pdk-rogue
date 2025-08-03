import pygame
import random
import itertools
from enum import Enum
from collections import defaultdict

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
CARD_WIDTH = 60
CARD_HEIGHT = 90
FPS = 60

# Colors (pixel art palette)
BG_COLOR = (34, 52, 60)
CARD_COLOR = (241, 242, 246)
CARD_BACK_COLOR = (52, 73, 94)
TEXT_COLOR = (26, 32, 44)
SELECTED_COLOR = (241, 196, 15)
BUTTON_COLOR = (46, 204, 113)
BUTTON_HOVER = (39, 174, 96)
RED_COLOR = (231, 76, 60)
BLACK_COLOR = (26, 32, 44)


class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"


class Card:
    # Card values: 3-10, J=11, Q=12, K=13, A=14, 2=15
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
        return f"{self.rank}{self.suit.value}"

    def __lt__(self, other):
        return self.value < other.value


class ComboType(Enum):
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    STRAIGHT = 4
    TRIPLE_WITH_SINGLE = 5
    TRIPLE_WITH_PAIR = 6
    FOUR_WITH_TWO = 7
    PLANE = 8  # Multiple consecutive triples
    PLANE_WITH_SINGLES = 9  # Like 333444 + 67
    PLANE_WITH_PAIRS = 10  # Like 333444 + 7788
    BOMB = 11


class Combo:
    def __init__(self, cards, combo_type):
        self.cards = sorted(cards)
        self.type = combo_type
        self.lead_value = self._get_lead_value()

    def _get_lead_value(self):
        if self.type == ComboType.SINGLE:
            return self.cards[0].value
        elif self.type in [ComboType.PAIR, ComboType.TRIPLE]:
            return self.cards[0].value
        elif self.type == ComboType.STRAIGHT:
            return self.cards[-1].value  # Highest card in straight
        elif self.type in [ComboType.TRIPLE_WITH_SINGLE, ComboType.TRIPLE_WITH_PAIR]:
            # Find the triple
            value_counts = defaultdict(int)
            for card in self.cards:
                value_counts[card.value] += 1
            for value, count in value_counts.items():
                if count == 3:
                    return value
        elif self.type == ComboType.FOUR_WITH_TWO:
            # Find the four
            value_counts = defaultdict(int)
            for card in self.cards:
                value_counts[card.value] += 1
            for value, count in value_counts.items():
                if count == 4:
                    return value
        elif self.type in [ComboType.PLANE, ComboType.PLANE_WITH_SINGLES, ComboType.PLANE_WITH_PAIRS]:
            # Find the highest triple in the plane
            value_counts = defaultdict(int)
            for card in self.cards:
                value_counts[card.value] += 1
            triple_values = [value for value, count in value_counts.items() if count >= 3]
            return max(triple_values) if triple_values else 0
        elif self.type == ComboType.BOMB:
            return self.cards[0].value
        return 0

    def can_beat(self, other):
        if other is None:
            return True

        # Bombs beat everything except higher bombs
        if self.type == ComboType.BOMB:
            if other.type != ComboType.BOMB:
                return True
            return self.lead_value > other.lead_value

        if other.type == ComboType.BOMB:
            return False

        # Same type comparison
        if self.type == other.type:
            if self.type == ComboType.STRAIGHT:
                # Straights must be same length
                if len(self.cards) != len(other.cards):
                    return False
            elif self.type in [ComboType.PLANE, ComboType.PLANE_WITH_SINGLES, ComboType.PLANE_WITH_PAIRS]:
                # Planes must have same number of consecutive triples
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

        # Count consecutive triples
        count = 1
        for i in range(1, len(triple_values)):
            if triple_values[i] == triple_values[i - 1] + 1:
                count += 1
            else:
                break
        return count


def identify_combo(cards):
    if not cards:
        return None

    cards = sorted(cards)
    n = len(cards)

    # Single
    if n == 1:
        return Combo(cards, ComboType.SINGLE)

    # Check for same values
    value_counts = defaultdict(list)
    for card in cards:
        value_counts[card.value].append(card)

    # Pair
    if n == 2 and len(value_counts) == 1:
        return Combo(cards, ComboType.PAIR)

    # Triple
    if n == 3 and len(value_counts) == 1:
        return Combo(cards, ComboType.TRIPLE)

    # Bomb (4 of same)
    if n == 4 and len(value_counts) == 1:
        return Combo(cards, ComboType.BOMB)

    # Check for planes (consecutive triples) with attachments
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
        # Check if triples are consecutive
        triple_values.sort()
        consecutive_count = 1
        for i in range(1, len(triple_values)):
            if triple_values[i] == triple_values[i - 1] + 1 and triple_values[i] <= 14:  # No 2s
                consecutive_count += 1
            else:
                break

        if consecutive_count >= 2:
            # We have a plane base
            plane_cards = []
            for i in range(consecutive_count):
                val = triple_values[i]
                for card in cards:
                    if card.value == val and len([c for c in plane_cards if c.value == val]) < 3:
                        plane_cards.append(card)

            remaining = [c for c in cards if c not in plane_cards]

            # Pure plane (no attachments)
            if len(remaining) == 0 and len(plane_cards) == n:
                return Combo(cards, ComboType.PLANE)

            # Plane with singles (like 333444 + 56)
            if len(remaining) == consecutive_count:
                return Combo(cards, ComboType.PLANE_WITH_SINGLES)

            # Plane with pairs (like 333444 + 5566)
            if len(remaining) == consecutive_count * 2:
                # Check if attachments form valid pairs
                attach_counts = defaultdict(int)
                for card in remaining:
                    attach_counts[card.value] += 1

                pair_count = sum(1 for count in attach_counts.values() if count >= 2)
                if pair_count == consecutive_count:
                    return Combo(cards, ComboType.PLANE_WITH_PAIRS)

    # Straight (5+ consecutive cards, no 2s)
    if n >= 5:
        is_straight = True
        for i in range(1, n):
            if cards[i].value != cards[i - 1].value + 1:
                is_straight = False
                break
            if cards[i].value > 14:  # No 2s in straights
                is_straight = False
                break
        if is_straight and cards[0].value <= 14:
            return Combo(cards, ComboType.STRAIGHT)

    # Triple with single
    if n == 4:
        for value, same_cards in value_counts.items():
            if len(same_cards) == 3:
                return Combo(cards, ComboType.TRIPLE_WITH_SINGLE)

    # Triple with pair
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

    # Four with two
    if n == 6:
        has_four = False
        for value, same_cards in value_counts.items():
            if len(same_cards) == 4:
                has_four = True
                break
        if has_four:
            return Combo(cards, ComboType.FOUR_WITH_TWO)

    return None


class Player:
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


class AIPlayer(Player):
    def __init__(self, name):
        super().__init__(name, is_ai=True)

    def find_valid_plays(self, last_combo):
        valid_combos = []

        # Group cards by value
        value_groups = defaultdict(list)
        for card in self.hand:
            value_groups[card.value].append(card)

        # If no last combo, we can play anything
        if last_combo is None:
            # Try singles
            for card in self.hand:
                combo = identify_combo([card])
                if combo:
                    valid_combos.append(combo)

            # Try pairs
            for cards in value_groups.values():
                if len(cards) >= 2:
                    combo = identify_combo(cards[:2])
                    if combo:
                        valid_combos.append(combo)

            # Try triples
            for cards in value_groups.values():
                if len(cards) >= 3:
                    combo = identify_combo(cards[:3])
                    if combo:
                        valid_combos.append(combo)

            # Try straights
            valid_combos.extend(self._find_straights())

            # Try planes
            valid_combos.extend(self._find_planes())

        else:
            # Find combos that can beat last_combo
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

            # Always check for bombs
            for cards in value_groups.values():
                if len(cards) == 4:
                    bomb = identify_combo(cards)
                    if bomb and bomb.can_beat(last_combo):
                        valid_combos.append(bomb)

        return valid_combos

    def _find_straights(self, target_length=None):
        straights = []
        values = sorted(set(card.value for card in self.hand if card.value <= 14))  # No 2s

        min_length = target_length if target_length else 5

        for start_idx in range(len(values)):
            for end_idx in range(start_idx + min_length - 1, len(values)):
                # Check if consecutive
                is_consecutive = True
                for i in range(start_idx + 1, end_idx + 1):
                    if values[i] != values[i - 1] + 1:
                        is_consecutive = False
                        break

                if is_consecutive:
                    length = end_idx - start_idx + 1
                    if target_length is None or length == target_length:
                        # Get cards for this straight
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

        # Find all triples
        triple_values = []
        for value, cards in value_groups.items():
            if len(cards) >= 3 and value <= 14:  # No 2s in planes
                triple_values.append(value)

        if len(triple_values) < 2:
            return planes

        triple_values.sort()

        # Find consecutive triples
        for start_idx in range(len(triple_values)):
            consecutive = [triple_values[start_idx]]

            for i in range(start_idx + 1, len(triple_values)):
                if triple_values[i] == consecutive[-1] + 1:
                    consecutive.append(triple_values[i])
                else:
                    break

            if len(consecutive) >= 2:
                # We have consecutive triples, try different combinations
                for length in range(2, len(consecutive) + 1):
                    plane_base = []
                    for val in consecutive[:length]:
                        for card in value_groups[val][:3]:
                            plane_base.append(card)

                    # Try pure plane
                    combo = identify_combo(plane_base)
                    if combo:
                        planes.append(combo)

                    # Try with singles
                    available_singles = []
                    for card in self.hand:
                        if card not in plane_base:
                            available_singles.append(card)

                    if len(available_singles) >= length:
                        # Try different combinations of singles
                        for singles in itertools.combinations(available_singles, length):
                            test_cards = plane_base + list(singles)
                            combo = identify_combo(test_cards)
                            if combo and combo.type == ComboType.PLANE_WITH_SINGLES:
                                planes.append(combo)

                    # Try with pairs
                    available_for_pairs = defaultdict(list)
                    for card in self.hand:
                        if card not in plane_base:
                            available_for_pairs[card.value].append(card)

                    pairs = []
                    for value, cards in available_for_pairs.items():
                        if len(cards) >= 2:
                            pairs.append(cards[:2])

                    if len(pairs) >= length:
                        # Try different combinations of pairs
                        for pair_combo in itertools.combinations(pairs, length):
                            test_cards = plane_base[:]
                            for pair in pair_combo:
                                test_cards.extend(pair)
                            combo = identify_combo(test_cards)
                            if combo and combo.type == ComboType.PLANE_WITH_PAIRS:
                                planes.append(combo)

        return planes

    def choose_play(self, last_combo, game_state):
        valid_plays = self.find_valid_plays(last_combo)

        if not valid_plays:
            return None  # Pass

        # Simple AI strategy
        # If starting a new round, play smaller combos first
        if last_combo is None:
            # Prefer singles and pairs to get rid of small cards
            singles = [c for c in valid_plays if c.type == ComboType.SINGLE]
            pairs = [c for c in valid_plays if c.type == ComboType.PAIR]

            if len(self.hand) > 10 and singles:
                # Play smallest single
                return min(singles, key=lambda c: c.lead_value)
            elif pairs:
                # Play smallest pair
                return min(pairs, key=lambda c: c.lead_value)

        # If we have few cards left, try to finish
        if len(self.hand) <= 3:
            # Play anything we can
            return valid_plays[0]

        # Otherwise, play the weakest combo that beats the last one
        valid_plays.sort(key=lambda c: (c.type.value, c.lead_value))

        # Don't waste bombs early
        non_bombs = [c for c in valid_plays if c.type != ComboType.BOMB]
        if non_bombs:
            return non_bombs[0]

        # If only bombs available and we have many cards, consider passing
        if len(self.hand) > 10:
            return None

        return valid_plays[0]

class SmartAIPlayer(AIPlayer):
    def __init__(self, name):
        super().__init__(name)
        self.played_cards = []  # Track all cards played in the game
        self.cards_per_player = {}  # Track approximate cards remaining per player
        
    def choose_play(self, last_combo, game_state):
        """Enhanced choose_play with heuristic evaluation and lookahead search"""
        valid_plays = self.find_valid_plays(last_combo)
        
        if not valid_plays:
            return None  # Pass
        
        # Add passing as an option if we're not starting
        if last_combo is not None:
            valid_plays.append(None)  # None represents passing
        
        # Special case: if we can win immediately, do it
        for play in valid_plays:
            if play and len(play.cards) == len(self.hand):
                return play
        
        # Use minimax search with heuristic evaluation
        best_play, best_score = self._minimax_search(
            valid_plays, 
            last_combo, 
            game_state, 
            depth=3,
            is_maximizing=True
        )
        
        return best_play
    
    def _minimax_search(self, valid_plays, last_combo, game_state, depth, is_maximizing, alpha=-float('inf'), beta=float('inf'), simulated_hand=None):
        """Minimax search with alpha-beta pruning"""
        # Use simulated hand if provided, otherwise use actual hand
        current_hand = simulated_hand if simulated_hand is not None else self.hand
        
        # Base case: depth 0 or game over
        if depth == 0 or len(current_hand) == 0:
            return None, self._evaluate_position_with_hand(game_state, current_hand)
        
        best_play = None
        
        if is_maximizing:
            max_eval = -float('inf')
            
            for play in valid_plays:
                # Skip if this is a pass
                if play is None:
                    # For passing, hand remains the same
                    new_hand = current_hand
                else:
                    # Check if we can actually make this play with simulated hand
                    can_play = all(
                        sum(1 for c in current_hand if c.value == card.value and c.suit == card.suit) >= 
                        sum(1 for pc in play.cards if pc.value == card.value and pc.suit == card.suit)
                        for card in play.cards
                    )
                    if not can_play:
                        continue
                    
                    # Simulate making this play
                    new_hand = [c for c in current_hand if c not in play.cards]
                    
                    if len(new_hand) == 0:
                        # Winning move
                        return play, 10000
                
                # Generate opponent's possible responses
                opponent_plays = self._estimate_opponent_responses(
                    play if play else last_combo, 
                    game_state
                )
                
                # Recursively evaluate with the new hand state
                _, eval_score = self._minimax_search(
                    opponent_plays,
                    play if play else last_combo,
                    game_state,
                    depth - 1,
                    False,
                    alpha,
                    beta,
                    new_hand  # Pass the simulated hand
                )
                
                # Add immediate move evaluation
                if play:
                    eval_score += self._evaluate_move_with_hand(play, last_combo, game_state, current_hand) * 0.3
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_play = play
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            return best_play, max_eval
        
        else:
            min_eval = float('inf')
            
            for play in valid_plays:
                # Simulate opponent's play (doesn't affect our hand)
                new_hand = current_hand
                
                # Our possible responses based on simulated hand
                our_responses = self._find_valid_plays_for_hand(
                    play if play else last_combo,
                    new_hand
                )
                if play is None or not our_responses:
                    our_responses = [None]
                
                # Recursively evaluate
                _, eval_score = self._minimax_search(
                    our_responses,
                    play if play else last_combo,
                    game_state,
                    depth - 1,
                    True,
                    alpha,
                    beta,
                    new_hand  # Pass the simulated hand
                )
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_play = play
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return best_play, min_eval
    
    def _evaluate_position_with_hand(self, game_state, hand):
        """Evaluate the current game position with a specific hand"""
        score = 0
        
        # Hand strength evaluation
        hand_strength = self._evaluate_hand_strength(hand)
        score += hand_strength * 10
        
        # Cards remaining penalty (fewer cards is better)
        score -= len(hand) * 50
        
        # Control evaluation
        controls = self._count_controls(hand)
        score += controls * 100
        
        # Hand shape quality
        shape_score = self._analyze_hand_shape(hand)
        score += shape_score * 20
        
        # Estimate turns to win
        turns = self._estimate_turns_to_win(hand)
        score -= turns * 200
        
        return score
    
    def _evaluate_move_with_hand(self, combo, last_combo, game_state, hand):
        """Evaluate a specific move with a specific hand"""
        if combo is None:
            return -50  # Passing has a small penalty
        
        score = 0
        
        # Prefer to get rid of low singles early
        if combo.type == ComboType.SINGLE and combo.lead_value < 10:
            score += 30
        
        # Prefer to keep high cards and bombs
        avg_value = sum(card.value for card in combo.cards) / len(combo.cards)
        score -= avg_value * 2
        
        # Bonus for using many cards at once
        score += len(combo.cards) * 10
        
        # Penalty for breaking up potential combinations
        remaining_hand = [c for c in hand if c not in combo.cards]
        shape_before = self._analyze_hand_shape(hand)
        shape_after = self._analyze_hand_shape(remaining_hand)
        score -= (shape_before - shape_after) * 15
        
        # Penalty for using bombs too early
        if combo.type == ComboType.BOMB and len(hand) > 10:
            score -= 200
        
        return score
    
    def _find_valid_plays_for_hand(self, last_combo, hand):
        """Find valid plays for a specific hand (used in simulation)"""
        # Temporarily swap hands
        original_hand = self.hand
        self.hand = hand
        
        # Find valid plays
        valid_plays = self.find_valid_plays(last_combo)
        
        # Restore original hand
        self.hand = original_hand
        
        return valid_plays
    
    def _evaluate_hand_strength(self, hand=None):
        """Evaluate overall hand strength"""
        if hand is None:
            hand = self.hand
        
        if not hand:
            return 0
        
        strength = 0
        
        # High cards value
        for card in hand:
            if card.value >= 13:  # K, A, 2
                strength += (card.value - 10) * 3
        
        # Bombs are very valuable
        value_counts = defaultdict(int)
        for card in hand:
            value_counts[card.value] += 1
        
        for value, count in value_counts.items():
            if count == 4:
                strength += 50
        
        return strength
    
    def _count_controls(self, hand=None):
        """Count control cards (high cards and bombs)"""
        if hand is None:
            hand = self.hand
        
        controls = 0
        value_counts = defaultdict(int)
        
        for card in hand:
            value_counts[card.value] += 1
        
        # Count 2s (highest cards)
        controls += value_counts.get(15, 0)
        
        # Count Aces
        controls += value_counts.get(14, 0) * 0.7
        
        # Count bombs
        for value, count in value_counts.items():
            if count == 4:
                controls += 2
        
        return controls
    
    def _analyze_hand_shape(self, hand=None):
        """Analyze hand shape quality"""
        if hand is None:
            hand = self.hand
        
        if not hand:
            return 0
        
        shape_score = 0
        value_counts = defaultdict(int)
        
        for card in hand:
            value_counts[card.value] += 1
        
        # Penalty for isolated cards
        singles = sum(1 for count in value_counts.values() if count == 1)
        shape_score -= singles * 5
        
        # Bonus for pairs and triples
        pairs = sum(1 for count in value_counts.values() if count == 2)
        triples = sum(1 for count in value_counts.values() if count == 3)
        shape_score += pairs * 3 + triples * 5
        
        # Check for potential straights
        values = sorted(value_counts.keys())
        consecutive = 0
        for i in range(1, len(values)):
            if values[i] == values[i-1] + 1 and values[i] <= 14:
                consecutive += 1
            else:
                if consecutive >= 4:
                    shape_score += consecutive * 2
                consecutive = 0
        
        return shape_score
    
    def _estimate_turns_to_win(self, hand=None):
        """Estimate minimum turns needed to empty hand"""
        if hand is None:
            hand = list(self.hand)
        
        if not hand:
            return 0
        
        # Group by value
        value_groups = defaultdict(list)
        for card in hand:
            value_groups[card.value].append(card)
        
        turns = 0
        remaining_cards = list(hand)
        
        # First, count bombs (they can be played anytime)
        for value, cards in value_groups.items():
            if len(cards) == 4:
                turns += 1
                remaining_cards = [c for c in remaining_cards if c.value != value]
        
        # Then count triples
        value_groups = defaultdict(list)
        for card in remaining_cards:
            value_groups[card.value].append(card)
        
        for value, cards in list(value_groups.items()):
            if len(cards) >= 3:
                turns += 1
                for _ in range(3):
                    remaining_cards.remove(cards[0])
                    cards.pop(0)
        
        # Count pairs
        value_groups = defaultdict(list)
        for card in remaining_cards:
            value_groups[card.value].append(card)
        
        for value, cards in list(value_groups.items()):
            if len(cards) >= 2:
                turns += 1
                remaining_cards = [c for c in remaining_cards if c != cards[0] and c != cards[1]]
        
        # Remaining singles
        turns += len(remaining_cards)
        
        # This is optimistic; real turns might be more
        return max(turns, len(hand) // 5)
    
    def _simulate_play(self, play, game_state, is_own_play):
        """Simulate making a play and return new game state"""
        new_state = game_state.copy() if hasattr(game_state, 'copy') else game_state
        
        # Don't actually modify self.hand during simulation
        # Just track what would be removed
        if is_own_play and play:
            # Store the original hand and create a simulated version
            # This is handled in the search by tracking remaining cards
            pass
        
        return new_state
    
    def _estimate_opponent_responses(self, last_combo, game_state):
        """Estimate possible opponent responses"""
        # For simplicity, generate a few likely responses
        # In a real implementation, this would use card counting
        
        responses = []
        
        if last_combo is None:
            # Opponent can play anything; assume they play conservatively
            responses.extend([
                self._create_mock_combo(ComboType.SINGLE, 8),
                self._create_mock_combo(ComboType.SINGLE, 10),
                self._create_mock_combo(ComboType.PAIR, 9),
                None  # Pass
            ])
        else:
            # Opponent needs to beat our combo
            if last_combo.type == ComboType.SINGLE:
                for value in range(last_combo.lead_value + 1, 16):
                    responses.append(self._create_mock_combo(ComboType.SINGLE, value))
            elif last_combo.type == ComboType.PAIR:
                for value in range(last_combo.lead_value + 1, 16):
                    responses.append(self._create_mock_combo(ComboType.PAIR, value))
            
            responses.append(None)  # Can always pass
            
            # Consider bombs
            if last_combo.type != ComboType.BOMB:
                responses.append(self._create_mock_combo(ComboType.BOMB, 10))
        
        return responses[:5]  # Limit responses for performance
    
    def _create_mock_combo(self, combo_type, lead_value):
        """Create a mock combo for simulation"""
        # This is a simplified version; real implementation would be more sophisticated
        mock_cards = []
        
        if combo_type == ComboType.SINGLE:
            mock_cards = [type('Card', (), {'value': lead_value, 'suit': 0})]
        elif combo_type == ComboType.PAIR:
            mock_cards = [
                type('Card', (), {'value': lead_value, 'suit': 0}),
                type('Card', (), {'value': lead_value, 'suit': 1})
            ]
        elif combo_type == ComboType.BOMB:
            mock_cards = [
                type('Card', (), {'value': lead_value, 'suit': i}) 
                for i in range(4)
            ]
        
        # Create a mock combo object
        combo = type('Combo', (), {
            'type': combo_type,
            'cards': mock_cards,
            'lead_value': lead_value,
            'can_beat': lambda other: other is None or combo_type == ComboType.BOMB or lead_value > other.lead_value
        })()
        
        return combo

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)

        self.player = Player("Player")
        self.ai = SmartAIPlayer("AI")
        self.current_player = None
        self.last_combo = None
        self.last_player = None
        self.selected_cards = []

        self.play_button = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 80, 100, 40)
        self.pass_button = pygame.Rect(WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT - 80, 100, 40)

        self.game_over = False
        self.winner = None
        self.player_card_rects = []  # Store card positions for better click detection

        self.init_game()

    def init_game(self):
        # Create deck
        deck = []
        for suit in Suit:
            for rank in Card.VALUE_MAP.keys():
                deck.append(Card(rank, suit))

        # Shuffle and deal
        random.shuffle(deck)

        # Discard first 8 cards
        deck = deck[8:]

        # Deal remaining 44 cards
        self.player.hand = deck[:22]
        self.ai.hand = deck[22:]

        self.player.sort_hand()
        self.ai.sort_hand()

        # Player with 3♦ starts
        self.current_player = self.player
        for card in self.player.hand:
            if card.rank == "3" and card.suit == Suit.DIAMONDS:
                self.current_player = self.player
                break
        else:
            for card in self.ai.hand:
                if card.rank == "3" and card.suit == Suit.DIAMONDS:
                    self.current_player = self.ai
                    break

    def draw_card(self, card, x, y, show_face=True):
        # Draw card background
        if show_face:
            pygame.draw.rect(self.screen, CARD_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(self.screen, TEXT_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

            # Draw rank
            color = RED_COLOR if card.suit in [Suit.HEARTS, Suit.DIAMONDS] else BLACK_COLOR
            rank_text = self.font.render(card.rank, True, color)
            self.screen.blit(rank_text, (x + 5, y + 5))

            # Draw suit
            suit_text = self.font.render(card.suit.value, True, color)
            self.screen.blit(suit_text, (x + 5, y + 25))

            # Highlight if selected
            if card.selected:
                pygame.draw.rect(self.screen, SELECTED_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT), 4)
        else:
            pygame.draw.rect(self.screen, CARD_BACK_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(self.screen, TEXT_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

    def draw_hand(self, player, y_pos, show_cards=True):
        if not player.hand:
            return

        # Calculate card spacing - overlap cards if needed
        total_width = WINDOW_WIDTH - 100  # Leave margins
        max_card_spacing = 50  # Maximum spacing between cards

        if len(player.hand) * CARD_WIDTH <= total_width:
            # Cards fit without overlap
            card_spacing = CARD_WIDTH + 5
        else:
            # Need to overlap cards
            card_spacing = min(max_card_spacing, (total_width - CARD_WIDTH) // (len(player.hand) - 1))

        total_hand_width = CARD_WIDTH + (len(player.hand) - 1) * card_spacing
        start_x = (WINDOW_WIDTH - total_hand_width) // 2

        # Store card positions for click detection
        if player == self.player:
            self.player_card_rects = []

        for i, card in enumerate(player.hand):
            x = start_x + i * card_spacing
            y = y_pos - 30 if show_cards and card.selected else y_pos
            self.draw_card(card, x, y, show_cards)

            # Store rect for click detection (for player only)
            if player == self.player:
                self.player_card_rects.append((card, pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)))

    def draw_button(self, rect, text, hover=False):
        color = BUTTON_HOVER if hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, 2)

        text_surf = self.font.render(text, True, CARD_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_game_info(self):
        # Draw HP
        player_hp_text = self.font.render(f"Player HP: {self.player.hp}", True, CARD_COLOR)
        ai_hp_text = self.font.render(f"AI HP: {self.ai.hp}", True, CARD_COLOR)
        self.screen.blit(player_hp_text, (20, WINDOW_HEIGHT - 30))
        self.screen.blit(ai_hp_text, (20, 20))

        # Draw turn indicator
        turn_text = self.font.render(f"Current Turn: {self.current_player.name}", True, CARD_COLOR)
        self.screen.blit(turn_text, (WINDOW_WIDTH // 2 - 80, 20))

        # Draw last played combo
        if self.last_combo and self.last_player:
            combo_text = self.font.render(
                f"Last Play: {self.last_player.name} - {self.last_combo.type.name}", True, CARD_COLOR
            )
            self.screen.blit(combo_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2))

            # Draw last played cards
            start_x = (WINDOW_WIDTH - 40 * len(self.last_combo.cards)) // 2
            for i, card in enumerate(self.last_combo.cards):
                self.draw_card(card, start_x + i * 40, WINDOW_HEIGHT // 2 + 30, True)

    def handle_card_click(self, mouse_pos):
        if self.current_player != self.player or self.game_over:
            return

        # Check clicks from right to left (top cards first due to overlap)
        for card, rect in reversed(self.player_card_rects):
            if rect.collidepoint(mouse_pos):
                card.selected = not card.selected
                break

    def get_selected_cards(self):
        return [card for card in self.player.hand if card.selected]

    def play_cards(self, player, cards):
        if not cards:
            return False

        combo = identify_combo(cards)
        if not combo:
            return False

        if self.last_combo and self.last_player != player:
            if not combo.can_beat(self.last_combo):
                return False

        # Valid play
        player.remove_cards(cards)
        self.last_combo = combo
        self.last_player = player

        # Clear selections
        for card in self.player.hand:
            card.selected = False

        return True

    def pass_turn(self):
        if self.last_player != self.current_player:
            self.current_player.hp -= 1

        # Switch turns
        self.current_player = self.ai if self.current_player == self.player else self.player

        # If the last player gets the turn back, clear the table
        if self.last_player == self.current_player:
            self.last_combo = None

    def check_game_over(self):
        if len(self.player.hand) == 0:
            self.game_over = True
            self.winner = self.player
        elif len(self.ai.hand) == 0:
            self.game_over = True
            self.winner = self.ai
        elif self.player.hp <= 0:
            self.game_over = True
            self.winner = self.ai
        elif self.ai.hp <= 0:
            self.game_over = True
            self.winner = self.player

    def ai_turn(self):
        if self.current_player != self.ai or self.game_over:
            return

        # AI thinking delay
        pygame.time.wait(1000)

        # AI chooses play
        combo = self.ai.choose_play(
            self.last_combo,
            {
                "player_cards": len(self.player.hand),
                "ai_cards": len(self.ai.hand),
                "player_hp": self.player.hp,
                "ai_hp": self.ai.hp,
            },
        )

        if combo:
            self.play_cards(self.ai, combo.cards)
            self.current_player = self.player
        else:
            self.pass_turn()

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Draw hands
        self.draw_hand(self.ai, 100, show_cards=False)  # Hide AI cards
        self.draw_hand(self.player, WINDOW_HEIGHT - 250, show_cards=True)  # Moved up to avoid button overlap

        # Draw game info
        self.draw_game_info()

        # Draw buttons (only for player turn)
        if self.current_player == self.player and not self.game_over:
            mouse_pos = pygame.mouse.get_pos()
            self.draw_button(self.play_button, "Play", self.play_button.collidepoint(mouse_pos))
            self.draw_button(self.pass_button, "Pass", self.pass_button.collidepoint(mouse_pos))

        # Draw game over
        if self.game_over:
            winner_text = self.big_font.render(f"{self.winner.name} Wins!", True, CARD_COLOR)
            text_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
            self.screen.blit(winner_text, text_rect)

        # Card count
        player_count = self.font.render(f"Cards: {len(self.player.hand)}", True, CARD_COLOR)
        ai_count = self.font.render(f"Cards: {len(self.ai.hand)}", True, CARD_COLOR)
        self.screen.blit(player_count, (20, WINDOW_HEIGHT - 50))
        self.screen.blit(ai_count, (20, 50))

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()

                        # Check card clicks
                        self.handle_card_click(mouse_pos)

                        # Check button clicks
                        if self.current_player == self.player and not self.game_over:
                            if self.play_button.collidepoint(mouse_pos):
                                selected = self.get_selected_cards()
                                if self.play_cards(self.player, selected):
                                    self.current_player = self.ai

                            elif self.pass_button.collidepoint(mouse_pos):
                                self.pass_turn()

            # AI turn
            self.ai_turn()

            # Check game over
            self.check_game_over()

            # Draw everything
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


# Main
if __name__ == "__main__":
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("跑得快 (Run Fast)")

    game = Game(screen)
    game.run()
