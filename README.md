# PDK Rogue

A roguelike deckbuilder that combines the strategic depth of 跑得快 with progression systems inspired by Slay the Spire and Balatro.

## Core Concept

Battle through procedurally generated paths using poker cards and skill-based combat, collecting powerful abilities and items to tackle increasingly challenging regions and enemies.

### Key Features
- **Unique Combat System**: Based on 跑得快 rules with a twist - passing costs HP
- **Roguelike Progression**: Choose your path, face elite enemies and bosses, unlock new content
- **Strategic Loadouts**: Collect skill cards and items, but carefully select what to bring on each run
- **Regional Variety**: Each region has unique rules that change combat dynamics
- **Meta-progression**: Unlock new cards, items, and regions as you play

## Gameplay Overview

### Combat Mechanics
- Players and enemies are dealt cards from a shuffled poker deck (with X cards discarded)
- Take turns playing card combinations strategically
- **Pass = Take 1 damage** - This creates constant pressure to keep playing
- Win by either:
  - Reducing opponent's HP to 0
  - Being first to empty your hand

### Card Combinations
- **Basic**: Singles, Pairs, Triples
- **Straights**: 5+ consecutive cards
- **Consecutive Pairs**: 334455 (3+ pairs in sequence)
- **Triple with Single**: 3 of a kind + 1 kicker
- **Triple with Pair**: 3 of a kind + 1 pair
- **Quad with Two Singles**: 4 of a kind + 2 kickers
- **Quad with Two Pairs**: 4 of a kind + 2 pairs
- **Planes**: Consecutive triples (333444)
- **Planes with attachments**: 333444+56 or 333444+5566
- **Bombs**: Four of a kind (beats everything except higher bombs)

### Progression System
1. **During Runs**: 
   - Start a run with X max Life Points
   - Win fights → Earn skill cards
   - Lose fights → Lose 2 life points
   - Surrender at the beginning of a fight → Lose 1 life points
   - Win fight without taking damage → Gain 1 life points (cannot exceed your max life points)
   - Force enemy to pass all hands → Gain 1 life points (cannot exceed your max life points)
   - Random encounter rewards → Skill cards and/or Temporary items (valid only during current run)
   - Complete runs → Earn equipment for permanent collection, unlock new skill cards and temporary items that may appear in next run
   - Complete region → Unlock additional equipment slots or gain 1 max life points permanently
2. **Before Each Run**:
   - Select equipment to take with you (limited by unlocked slots)
   - Choose which region and which path to challenge
3. **Difficulty Scaling**: Higher difficulties = fewer equipment slots, stronger enemies

### Skill Cards & Items
- **Skill Cards**: Active abilities used during combat (e.g., "Double next combo damage", "Peek at enemy's cards")
- **Temporary Items**: Run-specific buffs gained from encounters
- **Equipment**: Permanent passive effects selected before each run (e.g., "50% chance to avoid first damage", "Draw extra card when below 5 HP")
- **Synergies**: Discover powerful combinations between skills, equipment, and regional rules

## Regions & Enemies

### Regional Modifiers (Examples)
- **Amazon River**: Straights deal double damage

### Enemy Types
- **Basic Enemies**
- **Elite Enemies**: Have their own skill cards and enhanced AI
- **Bosses**: Multi-phase battles with unique mechanics and abilities

## Development Roadmap

### Core Game Systems
- Implement 跑得快 card game rules and combination detection
- Create Basic AI play logic
- Build combat system with HP, pass damage, and win conditions
- Develop skill card system with in-combat activation
- Design equipment system with pre-run selection interface
- Map Design (regions and runs in a region)
- What else?

### Roguelike Structure
- Map generation with branching paths and node types for each run (combat, elite, shop, event, boss)
- Node rewards system (skill cards, temporary items, gold)
- Shop system for purchasing skill cards, temporary items, and e.g., play cards (buy a 2 so every game in this run you start with an extra 2)
- Random event encounters with choices and consequences
- Region completion rewards and progression tracking

### Content & Progression
- Design and implement 5 unique regions with distinct modifiers
- Create 50 skill cards with varied effects
- Create 30 items with varied effects
- Design 15 equipments with passive abilities
- Design and Create Elite AI skill cards and play logic
- Design and Create multi-phase Boss AI mechanics, abilities, and play logic
- Balance card distributions, enemy HP, and damage values

### Meta-Progression Systems
- Player profile with collection tracking, achievement system
- Equipment unlock system based on achievements/milestones
- Equipment slot unlocking through gameplay progression
- Run statistics (e.g., how many wins/loses, how often pass, how often beat by emptying hands/eliminating enemy hp, etc)

### UI/UX Development
- Main menu and game state management
- Equipment selection screen with loadout management
- In-game HUD showing HP, current combo, skill cards
- Path selection interface with node preview
- Combat animations and visual feedback
- Card hover states and combination indicators

### Polish & Optimization
- Sound effects and background music
- Visual effects for combos and skill activations
- Performance optimization for smooth gameplay
- Save system for mid-run persistence
- Settings menu (audio, visual options, keybindings)
- Tutorial system for new players

## Design Philosophy

PDK Rogue aims to create depth through simple, interconnected systems:
- **Easy to learn**: If you know basic card games, you can play
- **Hard to master**: Skill expression through combo timing, resource management, and deck building
- **Meaningful choices**: Every card played, every path taken matters
- **Emergent complexity**: Simple rules combine into complex strategies

## Code Architecture

### Core Systems Design

#### Game State Management
```
GameState
├── RunState (current run progress)
│   ├── CurrentRegion
│   ├── CurrentNode
│   ├── PlayerStats (Life Points, gold, etc.)
│   ├── SkillCardInventory
│   ├── EquipedEquipment
│   └── TemporaryItems
├── MetaState (persistent progress)
│   ├── UnlockedEquipment
│   ├── UnlockedRegions
│   ├── EquipmentSlots
│   └── PlayerStatistics
└── CombatState
    ├── PlayerHand
    ├── EnemyHand
    ├── AbandonedHand
    ├── LastPlayedHand
    ├── PlayerHP
    └── CombatModifiers
```

#### Combat Engine
- **CardEngine**: Handles card distribution, shuffling, and dealing
- **ComboDetector**: Identifies valid card combinations from selected cards
- **CombatResolver**: Processes turns, damage calculation, and win conditions
- **AIController**: Modular AI system with different strategies per enemy type

#### Progression Systems
- **RunManager**: Handles node traversal, rewards, and run completion
- **EquipmentManager**: Pre-run loadout selection and equipment effects
- **SkillCardManager**: In-combat skill usage and cooldowns
- **UnlockSystem**: Tracks and grants meta-progression rewards

### Data Structures

#### Card System
```python
class Card:
    rank: str
    suit: Suit
    value: int  # Numerical value for comparison

class Combo:
    cards: List[Card]
    type: ComboType
    base_damage: int
    
class SkillCard:
    id: str
    name: str
    energy_cost: int
    effect: SkillEffect
    cooldown: int
    
class Equipment:
    id: str
    name: str
    slot_type: EquipmentSlot
    passive_effects: List[PassiveEffect]
```

#### Enemy Design
```python
class Enemy:
    hp: int
    base_damage: int
    ai_strategy: AIStrategy
    skill_cards: List[SkillCard]
    
class Elite(Enemy):
    phase_transitions: List[PhaseTransition]
    
class Boss(Enemy):
    phases: List[BossPhase]
    region_specific_mechanics: List[Mechanic]
```

### Modular Systems

#### Regional Modifiers
- Interface for regional rules that modify combat
- Examples: DamageMultiplier, ComboBonus, SpecialTriggers
- Easy to add new regions without changing core combat

#### Skill/Equipment Effects
- Effect interface with standard hooks (on_play, on_damage, on_turn_start, etc.)
- Composable effects for complex interactions
- Effect stacking and priority system

#### Save System
- Serialize RunState for mid-run saves
- Separate MetaState persistence
- Version migration support for updates

