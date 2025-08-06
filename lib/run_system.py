from dataclasses import dataclass, field
from typing import List, Optional, Any
from lib.profile import Profile
from lib.skill_cards import get_skill_card, SkillCard
from lib.items import get_item, Item
from lib.equipment import get_equipment, Equipment


@dataclass
class RunState:
    """Current run state"""
    profile: Profile
    region: str
    current_fight: int = 0
    total_fights: int = 5  # For now, fixed number of fights
    life_points: int = 10
    max_life_points: int = 10
    skill_cards: List[SkillCard] = field(default_factory=list)
    temporary_items: List[Item] = field(default_factory=list)
    equipped_equipment: List[Equipment] = field(default_factory=list)
    fights_won: int = 0
    fights_lost: int = 0
    
    def __post_init__(self):
        # Initialize with profile's max life points
        self.max_life_points = 10  # Base HP, will be modified by equipment
        self.life_points = self.max_life_points
    
    def add_skill_card(self, skill_card_name: str) -> bool:
        """Add a skill card to the run"""
        if skill_card_name in self.profile.unlocked_skill_cards:
            skill_card = get_skill_card(skill_card_name)
            if skill_card and len(self.skill_cards) < 5:
                self.skill_cards.append(skill_card)
                return True
        return False
    
    def add_item(self, item_name: str) -> bool:
        """Add an item to the run"""
        if item_name in self.profile.unlocked_items:
            item = get_item(item_name)
            if item and len(self.temporary_items) < 5:
                self.temporary_items.append(item)
                return True
        return False
    
    def equip_item(self, equipment_name: str) -> bool:
        """Equip an item for this run"""
        if equipment_name in self.profile.unlocked_equipment:
            equipment = get_equipment(equipment_name)
            if equipment:
                # Check if we have enough slots
                used_slots = sum(eq.slot for eq in self.equipped_equipment)
                if used_slots + equipment.slot <= self.profile.equipment_slots:
                    self.equipped_equipment.append(equipment)
                    # Apply equipment effects
                    equipment.on_equip(self)
                    return True
        return False
    
    def unequip_item(self, equipment_name: str) -> bool:
        """Unequip an item"""
        for i, equipment in enumerate(self.equipped_equipment):
            if equipment.name == equipment_name:
                equipment.on_unequip(self)
                self.equipped_equipment.pop(i)
                return True
        return False
    
    def take_damage(self, damage: int) -> int:
        """Take damage, applying equipment effects"""
        modified_damage = damage
        for equipment in self.equipped_equipment:
            modified_damage = equipment.on_damage_taken(self, modified_damage)
        
        self.life_points = max(0, self.life_points - modified_damage)
        return modified_damage
    
    def deal_damage(self, damage: int) -> int:
        """Deal damage, applying equipment effects"""
        modified_damage = damage
        for equipment in self.equipped_equipment:
            modified_damage = equipment.on_damage_dealt(self, modified_damage)
        return modified_damage
    
    def win_fight(self):
        """Called when a fight is won"""
        self.fights_won += 1
        self.current_fight += 1
        
        # Trigger item effects
        for item in self.temporary_items:
            item.on_trigger(self, "fight_won")
        
        # Apply equipment effects
        for equipment in self.equipped_equipment:
            equipment.on_fight_end(self)
    
    def lose_fight(self):
        """Called when a fight is lost"""
        self.fights_lost += 1
        self.current_fight += 1
        self.life_points = max(0, self.life_points - 2)  # Lose 2 HP
        
        # Apply equipment effects
        for equipment in self.equipped_equipment:
            equipment.on_fight_end(self)
    
    def is_run_complete(self) -> bool:
        """Check if the run is complete"""
        return self.current_fight >= self.total_fights
    
    def is_run_failed(self) -> bool:
        """Check if the run has failed (no HP left)"""
        return self.life_points <= 0
    
    def get_available_skill_cards(self) -> List[str]:
        """Get list of skill cards available for this profile"""
        return list(self.profile.unlocked_skill_cards)
    
    def get_available_items(self) -> List[str]:
        """Get list of items available for this profile"""
        return list(self.profile.unlocked_items)
    
    def get_available_equipment(self) -> List[str]:
        """Get list of equipment available for this profile"""
        return list(self.profile.unlocked_equipment)


class RunManager:
    """Manages the current run"""
    
    def __init__(self, profile: Profile, region: str):
        self.run_state = RunState(profile, region)
        self.current_fight = None
    
    def start_run(self):
        """Start the run"""
        # Apply equipment effects at run start
        for equipment in self.run_state.equipped_equipment:
            equipment.on_equip(self.run_state)
    
    def start_fight(self):
        """Start the next fight"""
        # Apply equipment effects at fight start
        for equipment in self.run_state.equipped_equipment:
            equipment.on_fight_start(self.run_state)
        
        # For now, just return the fight number
        # Later this will create actual enemy encounters
        return self.run_state.current_fight + 1
    
    def end_fight(self, won: bool):
        """End the current fight"""
        if won:
            self.run_state.win_fight()
        else:
            self.run_state.lose_fight()
        
        # Check if run should end
        if self.run_state.is_run_complete():
            self.complete_run()
        elif self.run_state.is_run_failed():
            self.fail_run()
    
    def complete_run(self):
        """Complete the run successfully"""
        # Update profile stats
        self.run_state.profile.total_runs_completed += 1
        self.run_state.profile.total_fights_won += self.run_state.fights_won
        
        # Unlock new content based on performance
        if self.run_state.fights_won >= 3:
            # Unlock new skill card
            new_skill = "Damage Boost"
            if new_skill not in self.run_state.profile.unlocked_skill_cards:
                self.run_state.profile.unlock_skill_card(new_skill)
        
        if self.run_state.fights_won >= 4:
            # Unlock new region
            new_region = "Forest Path"
            if new_region not in self.run_state.profile.unlocked_regions:
                self.run_state.profile.unlock_region(new_region)
    
    def fail_run(self):
        """Fail the run"""
        # Update profile stats
        self.run_state.profile.total_fights_won += self.run_state.fights_won
    
    def get_run_summary(self) -> dict:
        """Get a summary of the run"""
        return {
            "region": self.run_state.region,
            "fights_won": self.run_state.fights_won,
            "fights_lost": self.run_state.fights_lost,
            "total_fights": self.run_state.total_fights,
            "life_points": self.run_state.life_points,
            "max_life_points": self.run_state.max_life_points,
            "skill_cards": [card.name for card in self.run_state.skill_cards],
            "items": [item.name for item in self.run_state.temporary_items],
            "equipment": [eq.name for eq in self.run_state.equipped_equipment],
        } 