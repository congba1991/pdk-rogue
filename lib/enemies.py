from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum
import random
import json

from lib.player import FightPlayer, SmartAIPlayer
from lib.skill_cards import SkillCard, get_skill_card
from lib.items import Item, get_item
from lib.combo import ComboType
from lib.card import Card


class EnemyType(Enum):
    REGULAR = "regular"
    ELITE = "elite"
    BOSS = "boss"


class PlayStyle(Enum):
    DEFENSIVE = "defensive"  # Focuses on blocking player combos
    AGGRESSIVE = "aggressive"  # Prioritizes own combos over blocking
    BALANCED = "balanced"  # Mix of both strategies
    COMBO_FOCUSED = "combo_focused"  # Seeks to play complex combos


@dataclass
class EnemyAbility:
    """Special ability that an enemy can have"""
    name: str
    description: str
    ability_type: str  # "passive", "active", "trigger"
    
    def can_use(self, enemy: Any, game_state: Any) -> bool:
        """Check if ability can be used"""
        return True
    
    def use(self, enemy: Any, game_state: Any) -> bool:
        """Use the ability"""
        return True
    
    def on_fight_start(self, enemy: Any, game_state: Any):
        """Called when fight starts"""
        pass
    
    def on_turn_start(self, enemy: Any, game_state: Any):
        """Called at start of enemy's turn"""
        pass
    
    def on_damage_taken(self, enemy: Any, damage: int) -> int:
        """Called when enemy takes damage, returns modified damage"""
        return damage


class BanComboAbility(EnemyAbility):
    """Boss ability: Ban certain combo types"""
    
    def __init__(self, banned_types: List[ComboType]):
        super().__init__(
            name="Combo Ban",
            description=f"Player cannot use {', '.join(t.name for t in banned_types)} combos",
            ability_type="passive"
        )
        self.banned_types = banned_types
    
    def on_fight_start(self, enemy: Any, game_state: Any):
        # Store banned types in game state
        if not hasattr(game_state, 'banned_combo_types'):
            game_state.banned_combo_types = []
        game_state.banned_combo_types.extend(self.banned_types)


class DoubleDamageAbility(EnemyAbility):
    """Boss ability: Deal double damage"""
    
    def __init__(self):
        super().__init__(
            name="Double Damage",
            description="All damage dealt by this enemy is doubled",
            ability_type="passive"
        )
    
    def on_fight_start(self, enemy: Any, game_state: Any):
        enemy.damage_multiplier = 2.0


class PhaseTransitionAbility(EnemyAbility):
    """Boss ability: Phase transition at half health"""
    
    def __init__(self, phase_2_abilities: List[EnemyAbility]):
        super().__init__(
            name="Phase Transition",
            description="Gains new abilities when health drops below half",
            ability_type="trigger"
        )
        self.phase_2_abilities = phase_2_abilities
        self.phase_2_triggered = False
    
    def on_damage_taken(self, enemy: Any, damage: int) -> int:
        # Check if we should trigger phase 2 after taking damage
        if not self.phase_2_triggered and (enemy.hp - damage) <= enemy.max_hp // 2:
            self.phase_2_triggered = True
            # Add phase 2 abilities
            enemy.abilities.extend(self.phase_2_abilities)
            # Trigger their fight start effects
            if hasattr(enemy, 'current_game_state'):
                for ability in self.phase_2_abilities:
                    ability.on_fight_start(enemy, enemy.current_game_state)
        
        return damage


class RegenerateAbility(EnemyAbility):
    """Ability: Regenerate health each turn"""
    
    def __init__(self, heal_amount: int = 1):
        super().__init__(
            name="Regenerate",
            description=f"Heals {heal_amount} HP at start of each turn",
            ability_type="passive"
        )
        self.heal_amount = heal_amount
    
    def on_turn_start(self, enemy: Any, game_state: Any):
        enemy.hp = min(enemy.max_hp, enemy.hp + self.heal_amount)


class Enemy(SmartAIPlayer):
    """Base enemy class with abilities and enhanced AI"""
    
    def __init__(self, 
                 name: str, 
                 enemy_type: EnemyType,
                 max_hp: int = 5,
                 play_style: PlayStyle = PlayStyle.BALANCED,
                 skill_cards: List[str] = None,
                 items: List[str] = None,
                 abilities: List[EnemyAbility] = None):
        super().__init__(name)
        self.enemy_type = enemy_type
        self.max_hp = max_hp
        self.hp = max_hp
        self.play_style = play_style
        self.damage_multiplier = 1.0
        
        # Load skill cards and items
        self.skill_cards = []
        if skill_cards:
            for card_name in skill_cards:
                card = get_skill_card(card_name)
                if card:
                    self.skill_cards.append(card)
        
        self.items = []
        if items:
            for item_name in items:
                item = get_item(item_name)
                if item:
                    self.items.append(item)
        
        self.abilities = abilities or []
        self.current_game_state = None
    
    def on_fight_start(self, game_state: Any):
        """Called when fight begins"""
        self.current_game_state = game_state
        
        # Trigger all abilities
        for ability in self.abilities:
            ability.on_fight_start(self, game_state)
    
    def on_turn_start(self, game_state: Any):
        """Called at start of enemy's turn"""
        self.current_game_state = game_state
        
        # Trigger all abilities
        for ability in self.abilities:
            ability.on_turn_start(self, game_state)
    
    def take_damage(self, damage: int) -> int:
        """Take damage, applying ability modifiers"""
        # Apply ability damage modifications
        for ability in self.abilities:
            damage = ability.on_damage_taken(self, damage)
        
        actual_damage = min(damage, self.hp)
        self.hp -= actual_damage
        return actual_damage
    
    def choose_play(self, last_combo, game_state, depth=20):
        """Enhanced AI that considers play style and abilities"""
        # Use skill cards if available and beneficial
        if self.can_use_skill_cards(game_state):
            skill_result = self.try_use_skill_card(last_combo, game_state)
            if skill_result:
                return skill_result
        
        valid_plays = self.find_valid_plays(last_combo)
        if not valid_plays:
            return None
        
        if len(valid_plays) == 1:
            return valid_plays[0]
        
        # Apply play style to AI decision making
        if self.play_style == PlayStyle.DEFENSIVE:
            return self._choose_defensive_play(valid_plays, last_combo, game_state)
        elif self.play_style == PlayStyle.AGGRESSIVE:
            return self._choose_aggressive_play(valid_plays, last_combo, game_state)
        elif self.play_style == PlayStyle.COMBO_FOCUSED:
            return self._choose_combo_focused_play(valid_plays, last_combo, game_state)
        else:  # BALANCED
            return self._choose_balanced_play(valid_plays, last_combo, game_state)
    
    def _choose_defensive_play(self, valid_plays, last_combo, game_state):
        """Prioritize blocking player's combos with minimal waste"""
        if last_combo:
            # Find the cheapest play that beats the last combo
            blocking_plays = [play for play in valid_plays if play.can_beat(last_combo)]
            if blocking_plays:
                return min(blocking_plays, key=lambda p: len(p.cards))
        
        # If no combo to block, play smallest combo
        return min(valid_plays, key=lambda p: len(p.cards))
    
    def _choose_aggressive_play(self, valid_plays, last_combo, game_state):
        """Prioritize playing own strong combos"""
        # Prefer larger, more powerful combos
        return max(valid_plays, key=lambda p: (len(p.cards), p.lead_value))
    
    def _choose_combo_focused_play(self, valid_plays, last_combo, game_state):
        """Prioritize complex combo types"""
        # Score combos by complexity
        complexity_scores = {
            ComboType.SINGLE: 1,
            ComboType.PAIR: 2,
            ComboType.TRIPLE: 3,
            ComboType.STRAIGHT: 4,
            ComboType.BOMB: 5,
            ComboType.PLANE: 6,
            ComboType.PLANE_WITH_SINGLES: 7,
            ComboType.PLANE_WITH_PAIRS: 8,
            ComboType.JOKER_BOMB: 10
        }
        
        return max(valid_plays, key=lambda p: complexity_scores.get(p.type, 0))
    
    def _choose_balanced_play(self, valid_plays, last_combo, game_state):
        """Balanced approach using original AI logic"""
        return super().choose_play(last_combo, game_state)
    
    def can_use_skill_cards(self, game_state: Any) -> bool:
        """Check if enemy can use skill cards"""
        return len(self.skill_cards) > 0
    
    def try_use_skill_card(self, last_combo, game_state):
        """Try to use a beneficial skill card"""
        for skill_card in self.skill_cards[:]:  # Copy list since we might modify it
            if skill_card.can_use(game_state):
                # Simple heuristic: use skill cards when they would be beneficial
                if self._should_use_skill_card(skill_card, last_combo, game_state):
                    skill_card.use(game_state)
                    self.skill_cards.remove(skill_card)
                    return None  # Skill card use is the action this turn
        
        return None
    
    def _should_use_skill_card(self, skill_card: SkillCard, last_combo, game_state) -> bool:
        """Simple heuristic for when to use skill cards"""
        # Use defensive cards when in danger
        if self.hp <= 3:
            if "heal" in skill_card.description.lower() or "shield" in skill_card.description.lower():
                return True
        
        # Use aggressive cards when opponent is in danger
        if hasattr(game_state, 'player') and game_state.player.hp <= 3:
            if "damage" in skill_card.description.lower() or "steal" in skill_card.description.lower():
                return True
        
        # Use utility cards randomly with low probability
        return random.random() < 0.1


# Predefined Enemy Templates

def create_goblin_scout() -> Enemy:
    """Basic regular enemy"""
    return Enemy(
        name="Goblin Scout",
        enemy_type=EnemyType.REGULAR,
        max_hp=5,
        play_style=PlayStyle.AGGRESSIVE
    )


def create_orc_warrior() -> Enemy:
    """Regular enemy with higher health"""
    return Enemy(
        name="Orc Warrior",
        enemy_type=EnemyType.REGULAR,
        max_hp=5,
        play_style=PlayStyle.DEFENSIVE
    )


def create_bandit_leader() -> Enemy:
    """Elite enemy with skill cards"""
    return Enemy(
        name="Bandit Leader",
        enemy_type=EnemyType.ELITE,
        max_hp=7,
        play_style=PlayStyle.BALANCED,
        skill_cards=["Card Steal", "Discard Grab"],
        abilities=[RegenerateAbility(1)]
    )


def create_shadow_assassin() -> Enemy:
    """Elite enemy focused on combos"""
    return Enemy(
        name="Shadow Assassin",
        enemy_type=EnemyType.ELITE,
        max_hp=7,
        play_style=PlayStyle.COMBO_FOCUSED,
        skill_cards=["Time Warp", "Damage Boost"],
        items=["Lucky Charm"]
    )


def create_flame_elemental() -> Enemy:
    """Elite enemy with damage focus"""
    return Enemy(
        name="Flame Elemental",
        enemy_type=EnemyType.ELITE,
        max_hp=7,
        play_style=PlayStyle.AGGRESSIVE,
        abilities=[DoubleDamageAbility()]
    )


def create_combo_bane_boss() -> Enemy:
    """Boss that bans certain combo types"""
    banned_combos = random.sample([ComboType.STRAIGHT, ComboType.PLANE, ComboType.TRIPLE], 2)
    
    return Enemy(
        name="Combo Bane",
        enemy_type=EnemyType.BOSS,
        max_hp=9,
        play_style=PlayStyle.DEFENSIVE,
        skill_cards=["Time Warp", "Card Steal", "Damage Boost"],
        abilities=[BanComboAbility(banned_combos)]
    )


def create_arcane_overlord() -> Enemy:
    """Boss with phase transition"""
    phase_2_abilities = [
        DoubleDamageAbility(),
        RegenerateAbility(2)
    ]
    
    return Enemy(
        name="Arcane Overlord",
        enemy_type=EnemyType.BOSS,
        max_hp=9,
        play_style=PlayStyle.BALANCED,
        skill_cards=["Time Warp", "Discard Grab"],
        items=["Scrying Orb", "Lucky Charm"],
        abilities=[PhaseTransitionAbility(phase_2_abilities)]
    )


def create_shadow_lord() -> Enemy:
    """Ultimate boss with multiple abilities"""
    return Enemy(
        name="Shadow Lord",
        enemy_type=EnemyType.BOSS,
        max_hp=9,
        play_style=PlayStyle.COMBO_FOCUSED,
        skill_cards=["Time Warp", "Card Steal", "Damage Boost", "Discard Grab"],
        items=["Scrying Orb"],
        abilities=[
            BanComboAbility([ComboType.PAIR]),
            DoubleDamageAbility(),
            RegenerateAbility(1)
        ]
    )


# Enemy registry for easy access
REGULAR_ENEMIES = {
    "Goblin Scout": create_goblin_scout,
    "Orc Warrior": create_orc_warrior,
}

ELITE_ENEMIES = {
    "Bandit Leader": create_bandit_leader,
    "Shadow Assassin": create_shadow_assassin,
    "Flame Elemental": create_flame_elemental,
}

BOSS_ENEMIES = {
    "Combo Bane": create_combo_bane_boss,
    "Arcane Overlord": create_arcane_overlord,
    "Shadow Lord": create_shadow_lord,
}


def get_enemy(enemy_type: EnemyType, name: str = None) -> Enemy:
    """Get a random enemy of the specified type, or a specific named enemy"""
    if enemy_type == EnemyType.REGULAR:
        enemies = REGULAR_ENEMIES
    elif enemy_type == EnemyType.ELITE:
        enemies = ELITE_ENEMIES
    elif enemy_type == EnemyType.BOSS:
        enemies = BOSS_ENEMIES
    else:
        return create_goblin_scout()  # Fallback
    
    if name and name in enemies:
        return enemies[name]()
    else:
        # Return random enemy of that type
        return random.choice(list(enemies.values()))()


def get_random_enemy() -> Enemy:
    """Get a completely random enemy"""
    enemy_type = random.choice(list(EnemyType))
    return get_enemy(enemy_type)