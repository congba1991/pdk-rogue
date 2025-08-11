from dataclasses import dataclass
from typing import List, Optional, Any
from lib.core_types import Rarity
import pygame


@dataclass
class SkillCard:
    """Base skill card class"""
    name: str
    rarity: Rarity
    description: str
    energy_cost: int = 0
    max_inventory: int = 5
    one_time_use: bool = True
    
    def can_use(self, game_state: Any) -> bool:
        """Check if the skill card can be used"""
        return True
    
    def use(self, game_state: Any) -> bool:
        """Use the skill card. Returns True if successful."""
        return True
    
    def draw_hover_description(self, surface, font, card_rect, window_width, bg_color, text_color):
        """Draw a floating description box above the card when hovered"""
        desc_text = self.description
        box_width = 260
        # Wrap description text to fit box width
        wrapped = []
        words = desc_text.split()
        line = ""
        for word in words:
            test_line = line + (" " if line else "") + word
            test_surface = font.render(test_line, True, text_color)
            if test_surface.get_width() > box_width - 20:
                wrapped.append(line)
                line = word
            else:
                line = test_line
        if line:
            wrapped.append(line)
        # Calculate box height based on number of lines
        line_height = 18
        padding = 20
        box_height = len(wrapped) * line_height + padding
        box_x = card_rect.centerx - box_width // 2
        box_y = card_rect.top - box_height - 10
        # Ensure box stays within screen
        box_x = max(10, min(box_x, window_width - box_width - 10))
        box_y = max(10, box_y)
        desc_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, bg_color, desc_rect)
        pygame.draw.rect(surface, text_color, desc_rect, 2)
        # Render wrapped description lines
        for j, wrap_line in enumerate(wrapped):
            wrap_surface = font.render(wrap_line, True, text_color)
            surface.blit(wrap_surface, (desc_rect.x + 10, desc_rect.y + 10 + j * line_height))


# COMMON SKILL CARDS (in order from skill_card_data.py)

class DiscardGrab(SkillCard):
    """Take 2 random cards from the discard pile into your hand"""
    
    def __init__(self):
        super().__init__(
            name="Discard Grab",
            rarity=Rarity.COMMON,
            description="Take 2 random cards from the discard pile into your hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'discard_pile') and len(game_state.discard_pile) >= 2
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        import random
        cards_to_take = min(2, len(game_state.discard_pile))
        taken_cards = random.sample(game_state.discard_pile, cards_to_take)
        
        game_state.player.hand.extend(taken_cards)
        for card in taken_cards:
            game_state.discard_pile.remove(card)
        
        return True


class CardSteal(SkillCard):
    """Take 1 random card from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Card Steal",
            rarity=Rarity.COMMON,
            description="Take 1 random card from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) > 0
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        import random
        stolen_card = random.choice(game_state.ai.hand)
        game_state.player.hand.append(stolen_card)
        game_state.ai.hand.remove(stolen_card)
        
        return True


class DamageBoost(SkillCard):
    """Your next combo deals +1 damage if passed"""
    
    def __init__(self):
        super().__init__(
            name="Damage Boost",
            rarity=Rarity.COMMON,
            description="Your next combo deals +1 damage if passed",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        game_state.last_combo_damage_bonus += 1
        return True


class Peek(SkillCard):
    """Can see 3 random cards from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Peek",
            rarity=Rarity.COMMON,
            description="Can see 3 random cards from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) >= 3
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        import random
        cards_to_peek = min(3, len(game_state.ai.hand))
        peeked_cards = random.sample(game_state.ai.hand, cards_to_peek)
        print(f"Peek reveals: {[str(card) for card in peeked_cards]}")
        return True


class Recovery(SkillCard):
    """Heal 1 HP in this fight"""
    
    def __init__(self):
        super().__init__(
            name="Recovery",
            rarity=Rarity.COMMON,
            description="Heal 1 HP in this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if hasattr(game_state, 'player') and hasattr(game_state.player, 'hp'):
            max_hp = getattr(game_state.player, 'max_hp', 10)
            game_state.player.hp = min(max_hp, game_state.player.hp + 1)
            return True
        return False


class QuickSwap(SkillCard):
    """Swap one card from your hand with one random card from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Quick Swap",
            rarity=Rarity.COMMON,
            description="Swap one card from your hand with one random card from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and 
                len(game_state.player.hand) > 0 and hasattr(game_state, 'ai') and 
                hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) > 0)
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        import random
        player_card = random.choice(game_state.player.hand)
        ai_card = random.choice(game_state.ai.hand)
        
        game_state.player.hand.remove(player_card)
        game_state.ai.hand.remove(ai_card)
        game_state.player.hand.append(ai_card)
        game_state.ai.hand.append(player_card)
        
        return True


class Offload(SkillCard):
    """Discard 1 card and draw 1 random card"""
    
    def __init__(self):
        super().__init__(
            name="Offload",
            rarity=Rarity.COMMON,
            description="Discard 1 card and draw 1 random card",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and 
                len(game_state.player.hand) > 0 and hasattr(game_state, 'discard_pile') and 
                len(game_state.discard_pile) > 0)
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        import random
        discarded_card = random.choice(game_state.player.hand)
        game_state.player.hand.remove(discarded_card)
        game_state.discard_pile.append(discarded_card)
        
        drawn_card = random.choice(game_state.discard_pile)
        game_state.discard_pile.remove(drawn_card)
        game_state.player.hand.append(drawn_card)
        
        return True


class Upgrade(SkillCard):
    """Upgrade 1 card in your hand to next rank (max 2)"""
    
    def __init__(self):
        super().__init__(
            name="Upgrade",
            rarity=Rarity.COMMON,
            description="Upgrade 1 card in your hand to next rank (max 2)",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and len(game_state.player.hand) > 0):
            return False
        
        import random
        card_to_upgrade = random.choice(game_state.player.hand)
        # TODO: Implement rank upgrade logic
        print(f"Upgraded {card_to_upgrade}")
        return True


class Downgrade(SkillCard):
    """Downgrade 1 card in your hand to next rank (min 3)"""
    
    def __init__(self):
        super().__init__(
            name="Downgrade",
            rarity=Rarity.COMMON,
            description="Downgrade 1 card in your hand to next rank (min 3)",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) > 0):
            return False
        
        import random
        card_to_downgrade = random.choice(game_state.ai.hand)
        # TODO: Implement rank downgrade logic
        print(f"Downgraded opponent's {card_to_downgrade}")
        return True


class Break(SkillCard):
    """Change 1 random card from opponent's hand into another random card"""
    
    def __init__(self):
        super().__init__(
            name="Break",
            rarity=Rarity.COMMON,
            description="Change 1 random card from opponent's hand into another random card",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) > 0):
            return False
        
        import random
        from lib.core_types import Card, Suit
        
        old_card = random.choice(game_state.ai.hand)
        game_state.ai.hand.remove(old_card)
        
        suits = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]
        ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
        new_card = Card(random.choice(ranks), random.choice(suits))
        game_state.ai.hand.append(new_card)
        
        print(f"Broke opponent's {old_card} into {new_card}")
        return True


class Drop(SkillCard):
    """Discard 1 card from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Drop",
            rarity=Rarity.COMMON,
            description="Discard 1 card from opponent's hand",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) > 0):
            return False
        
        import random
        dropped_card = random.choice(game_state.ai.hand)
        game_state.ai.hand.remove(dropped_card)
        
        if hasattr(game_state, 'discard_pile'):
            game_state.discard_pile.append(dropped_card)
        
        print(f"Dropped opponent's {dropped_card}")
        return True


class Double(SkillCard):
    """Add an extra card to your selected card for this fight"""
    
    def __init__(self):
        super().__init__(
            name="Double",
            rarity=Rarity.COMMON,
            description="Add an extra card to your selected card for this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not hasattr(game_state, 'double_active'):
            game_state.double_active = 0
        game_state.double_active += 1
        return True


class SpadeMaster(SkillCard):
    """Change 2 cards into spades for this fight"""
    
    def __init__(self):
        super().__init__(
            name="Spade Master",
            rarity=Rarity.COMMON,
            description="Change 2 cards into spades for this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and len(game_state.player.hand) >= 2):
            return False
        
        import random
        from lib.core_types import Suit
        
        cards_to_change = random.sample(game_state.player.hand, min(2, len(game_state.player.hand)))
        for card in cards_to_change:
            card.suit = Suit.SPADES
        
        print(f"Changed {len(cards_to_change)} cards to spades")
        return True


class HeartChampion(SkillCard):
    """Change 2 cards into hearts for this fight"""
    
    def __init__(self):
        super().__init__(
            name="Heart Champion",
            rarity=Rarity.COMMON,
            description="Change 2 cards into hearts for this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and len(game_state.player.hand) >= 2):
            return False
        
        import random
        from lib.core_types import Suit
        
        cards_to_change = random.sample(game_state.player.hand, min(2, len(game_state.player.hand)))
        for card in cards_to_change:
            card.suit = Suit.HEARTS
        
        print(f"Changed {len(cards_to_change)} cards to hearts")
        return True


class ClubKnight(SkillCard):
    """Change 2 cards into clubs for this fight"""
    
    def __init__(self):
        super().__init__(
            name="Club Knight",
            rarity=Rarity.COMMON,
            description="Change 2 cards into clubs for this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and len(game_state.player.hand) >= 2):
            return False
        
        import random
        from lib.core_types import Suit
        
        cards_to_change = random.sample(game_state.player.hand, min(2, len(game_state.player.hand)))
        for card in cards_to_change:
            card.suit = Suit.CLUBS
        
        print(f"Changed {len(cards_to_change)} cards to clubs")
        return True


class DiamondKing(SkillCard):
    """Change 2 cards into diamonds for this fight"""
    
    def __init__(self):
        super().__init__(
            name="Diamond King",
            rarity=Rarity.COMMON,
            description="Change 2 cards into diamonds for this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and len(game_state.player.hand) >= 2):
            return False
        
        import random
        from lib.core_types import Suit
        
        cards_to_change = random.sample(game_state.player.hand, min(2, len(game_state.player.hand)))
        for card in cards_to_change:
            card.suit = Suit.DIAMONDS
        
        print(f"Changed {len(cards_to_change)} cards to diamonds")
        return True


class PairMaster(SkillCard):
    """Play any single as if it were a pair"""
    
    def __init__(self):
        super().__init__(
            name="Pair Master",
            rarity=Rarity.COMMON,
            description="Play any single as if it were a pair",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not hasattr(game_state, 'pair_master_active'):
            game_state.pair_master_active = 0
        game_state.pair_master_active += 1
        return True


# RARE SKILL CARDS

class DiscardGrab2(SkillCard):
    """Take 4 random cards from the discard pile into your hand"""
    
    def __init__(self):
        super().__init__(
            name="Discard Grab 2",
            rarity=Rarity.RARE,
            description="Take 4 random cards from the discard pile into your hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'discard_pile') and len(game_state.discard_pile) >= 4
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        import random
        cards_to_take = min(4, len(game_state.discard_pile))
        taken_cards = random.sample(game_state.discard_pile, cards_to_take)
        
        game_state.player.hand.extend(taken_cards)
        for card in taken_cards:
            game_state.discard_pile.remove(card)
        
        return True


class CardSteal2(SkillCard):
    """Take 2 random cards from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Card Steal 2",
            rarity=Rarity.RARE,
            description="Take 2 random cards from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) >= 2
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        import random
        stolen_cards = random.sample(game_state.ai.hand, min(2, len(game_state.ai.hand)))
        
        for card in stolen_cards:
            game_state.player.hand.append(card)
            game_state.ai.hand.remove(card)
        
        return True


class DamageBoost2(SkillCard):
    """Your next combo deals +2 damage if passed"""
    
    def __init__(self):
        super().__init__(
            name="Damage Boost 2",
            rarity=Rarity.RARE,
            description="Your next combo deals +2 damage if passed",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        game_state.last_combo_damage_bonus += 2
        return True


class Peek2(SkillCard):
    """Can see 6 random cards from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Peek 2",
            rarity=Rarity.RARE,
            description="Can see 6 random cards from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) > 0
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        import random
        cards_to_peek = min(6, len(game_state.ai.hand))
        peeked_cards = random.sample(game_state.ai.hand, cards_to_peek)
        print(f"Peek 2 reveals: {[str(card) for card in peeked_cards]}")
        return True


class Recovery2(SkillCard):
    """Heal 2 HP in this fight"""
    
    def __init__(self):
        super().__init__(
            name="Recovery 2",
            rarity=Rarity.RARE,
            description="Heal 2 HP in this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if hasattr(game_state, 'player') and hasattr(game_state.player, 'hp'):
            max_hp = getattr(game_state.player, 'max_hp', 10)
            game_state.player.hp = min(max_hp, game_state.player.hp + 2)
            return True
        return False


class QuickSwap2(SkillCard):
    """Swap 2 cards from your hand with 2 random cards from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Quick Swap 2",
            rarity=Rarity.RARE,
            description="Swap 2 cards from your hand with 2 random cards from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and 
                len(game_state.player.hand) >= 2 and hasattr(game_state, 'ai') and 
                hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) >= 2)
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        import random
        player_cards = random.sample(game_state.player.hand, 2)
        ai_cards = random.sample(game_state.ai.hand, 2)
        
        for card in player_cards:
            game_state.player.hand.remove(card)
        for card in ai_cards:
            game_state.ai.hand.remove(card)
        
        game_state.player.hand.extend(ai_cards)
        game_state.ai.hand.extend(player_cards)
        
        return True


class Offload2(SkillCard):
    """Discard 2 cards and draw 2 random cards"""
    
    def __init__(self):
        super().__init__(
            name="Offload 2",
            rarity=Rarity.RARE,
            description="Discard 2 cards and draw 2 random cards",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and 
                len(game_state.player.hand) >= 2 and hasattr(game_state, 'discard_pile') and 
                len(game_state.discard_pile) >= 2)
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        import random
        discarded_cards = random.sample(game_state.player.hand, 2)
        for card in discarded_cards:
            game_state.player.hand.remove(card)
            game_state.discard_pile.append(card)
        
        drawn_cards = random.sample(game_state.discard_pile, 2)
        for card in drawn_cards:
            game_state.discard_pile.remove(card)
            game_state.player.hand.append(card)
        
        return True


class TripleMaster(SkillCard):
    """Play any single as if it were a triple"""
    
    def __init__(self):
        super().__init__(
            name="Triple Master",
            rarity=Rarity.RARE,
            description="Play any single as if it were a triple",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not hasattr(game_state, 'triple_master_active'):
            game_state.triple_master_active = 0
        game_state.triple_master_active += 1
        return True


class Mirror(SkillCard):
    """Take one random card from opponent's last played combo into your hand"""
    
    def __init__(self):
        super().__init__(
            name="Mirror",
            rarity=Rarity.RARE,
            description="Take one random card from opponent's last played combo into your hand",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        # TODO: Implement last combo tracking
        print("Mirror activated - would copy from last combo")
        return True


class WildCard(SkillCard):
    """Change a card to wild card (can be used as any rank) for this fight"""
    
    def __init__(self):
        super().__init__(
            name="Wild Card",
            rarity=Rarity.RARE,
            description="Change a card to wild card (can be used as any rank) for this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and len(game_state.player.hand) > 0):
            return False
        
        import random
        card_to_wild = random.choice(game_state.player.hand)
        # TODO: Implement wild card marking
        print(f"Made {card_to_wild} into a wild card")
        return True


# EPIC SKILL CARDS

class DiscardGrab3(SkillCard):
    """Choose 4 cards from the discard pile to add to your hand"""
    
    def __init__(self):
        super().__init__(
            name="Discard Grab 3",
            rarity=Rarity.EPIC,
            description="Choose 4 cards from the discard pile to add to your hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'discard_pile') and len(game_state.discard_pile) >= 4
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        import random
        cards_to_take = min(4, len(game_state.discard_pile))
        taken_cards = random.sample(game_state.discard_pile, cards_to_take)
        
        game_state.player.hand.extend(taken_cards)
        for card in taken_cards:
            game_state.discard_pile.remove(card)
        
        print(f"Chose cards: {[str(card) for card in taken_cards]}")
        return True


class CardSteal3(SkillCard):
    """Take the top 2 cards from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Card Steal 3",
            rarity=Rarity.EPIC,
            description="Take the top 2 cards from opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand') and len(game_state.ai.hand) >= 2
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand')):
            return False
        
        stolen_cards = game_state.ai.hand[:2]
        
        for card in stolen_cards:
            game_state.player.hand.append(card)
            game_state.ai.hand.remove(card)
        
        return True


class DamageBoost3(SkillCard):
    """Your next combo deals +3 damage if passed"""
    
    def __init__(self):
        super().__init__(
            name="Damage Boost 3",
            rarity=Rarity.EPIC,
            description="Your next combo deals +3 damage if passed",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        game_state.last_combo_damage_bonus += 3
        return True


class Peek3(SkillCard):
    """Can see all cards from opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Peek 3",
            rarity=Rarity.EPIC,
            description="Can see all cards from opponent's hand",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand'):
            print(f"Peek 3 reveals all cards: {[str(card) for card in game_state.ai.hand]}")
            return True
        return False


class Recovery3(SkillCard):
    """Heal 1 LP in this run"""
    
    def __init__(self):
        super().__init__(
            name="Recovery 3",
            rarity=Rarity.EPIC,
            description="Heal 1 LP in this run",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        # TODO: This would need to affect run manager life points
        print("Recovery 3 healed 1 Life Point for the run")
        return True


class QuickSwap3(SkillCard):
    """Swap your hand with your opponent's hand"""
    
    def __init__(self):
        super().__init__(
            name="Quick Swap 3",
            rarity=Rarity.EPIC,
            description="Swap your hand with your opponent's hand",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and 
                hasattr(game_state, 'ai') and hasattr(game_state.ai, 'hand'))
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        player_hand = game_state.player.hand[:]
        ai_hand = game_state.ai.hand[:]
        
        game_state.player.hand.clear()
        game_state.ai.hand.clear()
        
        game_state.player.hand.extend(ai_hand)
        game_state.ai.hand.extend(player_hand)
        
        return True


class Offload3(SkillCard):
    """Discard entire hand and draw same number of random cards"""
    
    def __init__(self):
        super().__init__(
            name="Offload 3",
            rarity=Rarity.EPIC,
            description="Discard entire hand and draw same number of random cards",
            energy_cost=0
        )
    
    def can_use(self, game_state: Any) -> bool:
        return (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and 
                len(game_state.player.hand) > 0 and hasattr(game_state, 'discard_pile') and 
                len(game_state.discard_pile) >= len(game_state.player.hand))
    
    def use(self, game_state: Any) -> bool:
        if not self.can_use(game_state):
            return False
        
        import random
        hand_size = len(game_state.player.hand)
        
        game_state.discard_pile.extend(game_state.player.hand)
        game_state.player.hand.clear()
        
        drawn_cards = random.sample(game_state.discard_pile, hand_size)
        for card in drawn_cards:
            game_state.discard_pile.remove(card)
            game_state.player.hand.append(card)
        
        return True


class BombMaster(SkillCard):
    """Play any single as if it were a bomb"""
    
    def __init__(self):
        super().__init__(
            name="Bomb Master",
            rarity=Rarity.EPIC,
            description="Play any single as if it were a bomb",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not hasattr(game_state, 'bomb_master_active'):
            game_state.bomb_master_active = 0
        game_state.bomb_master_active += 1
        return True


class Mirror2(SkillCard):
    """Take all cards from opponent's last played combo into your hand"""
    
    def __init__(self):
        super().__init__(
            name="Mirror 2",
            rarity=Rarity.EPIC,
            description="Take all cards from opponent's last played combo into your hand",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        # TODO: Implement last combo tracking
        print("Mirror 2 activated - would copy all cards from last combo")
        return True


class WildCard2(SkillCard):
    """Change 2 cards to wild cards (can be used as any rank) for this fight"""
    
    def __init__(self):
        super().__init__(
            name="Wild Card 2",
            rarity=Rarity.EPIC,
            description="Change 2 cards to wild cards (can be used as any rank) for this fight",
            energy_cost=0
        )
    
    def use(self, game_state: Any) -> bool:
        if not (hasattr(game_state, 'player') and hasattr(game_state.player, 'hand') and len(game_state.player.hand) >= 2):
            return False
        
        import random
        cards_to_wild = random.sample(game_state.player.hand, 2)
        # TODO: Implement wild card marking
        print(f"Made {len(cards_to_wild)} cards into wild cards")
        return True


# Registry of all skill cards
SKILL_CARDS = {
    # Common cards (in exact order from skill_card_data.py)
    "Discard Grab": DiscardGrab,
    "Card Steal": CardSteal,
    "Damage Boost": DamageBoost,
    "Peek": Peek,
    "Recovery": Recovery,
    "Quick Swap": QuickSwap,
    "Offload": Offload,
    "Upgrade": Upgrade,
    "Downgrade": Downgrade,
    "Break": Break,
    "Drop": Drop,
    "Double": Double,
    "Spade Master": SpadeMaster,
    "Heart Champion": HeartChampion,
    "Club Knight": ClubKnight,
    "Diamond King": DiamondKing,
    "Pair Master": PairMaster,
    
    # Rare cards (in exact order from skill_card_data.py)
    "Discard Grab 2": DiscardGrab2,
    "Card Steal 2": CardSteal2,
    "Damage Boost 2": DamageBoost2,
    "Peek 2": Peek2,
    "Recovery 2": Recovery2,
    "Quick Swap 2": QuickSwap2,
    "Offload 2": Offload2,
    "Triple Master": TripleMaster,
    "Mirror": Mirror,
    "Wild Card": WildCard,
    
    # Epic cards (in exact order from skill_card_data.py)
    "Discard Grab 3": DiscardGrab3,
    "Card Steal 3": CardSteal3,
    "Damage Boost 3": DamageBoost3,
    "Peek 3": Peek3,
    "Recovery 3": Recovery3,
    "Quick Swap 3": QuickSwap3,
    "Offload 3": Offload3,
    "Bomb Master": BombMaster,
    "Mirror 2": Mirror2,
    "Wild Card 2": WildCard2,
}


def get_skill_card(name: str) -> Optional[SkillCard]:
    """Get a skill card instance by name"""
    if name in SKILL_CARDS:
        return SKILL_CARDS[name]()
    return None


def get_all_skill_cards() -> List[SkillCard]:
    """Get all available skill cards"""
    return [card_class() for card_class in SKILL_CARDS.values()]


def get_random_skill_cards(count: int = 3, exclude: List[str] = None) -> List[SkillCard]:
    """Get random skill cards for rewards"""
    import random
    exclude = exclude or []
    available_cards = [name for name in SKILL_CARDS.keys() if name not in exclude]
    
    if count > len(available_cards):
        count = len(available_cards)
    
    selected_names = random.sample(available_cards, count)
    return [get_skill_card(name) for name in selected_names]


def load_skill_card_image(card_name: str):
    """Load skill card image from file"""
    import pygame
    import os
    try:
        image_path = f"assets/skill_cards/{card_name.lower().replace(' ', '_')}.png"
        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        else:
            # Return placeholder image
            placeholder = pygame.Surface((100, 140))
            placeholder.fill((128, 128, 128))
            return placeholder
    except:
        # Return placeholder on error
        placeholder = pygame.Surface((100, 140))
        placeholder.fill((128, 128, 128))
        return placeholder


def get_skill_card_image_path(card_name: str) -> str:
    """Get the file path for a skill card image"""
    filename = card_name.lower().replace(' ', '_').replace("'", '')
    return f"images/skill_cards/{filename}.png"
