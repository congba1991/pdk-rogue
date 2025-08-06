import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Set, Dict, Any
from lib.card import Rarity, EquipmentTier


@dataclass
class Profile:
    """Player profile with meta-progression data"""
    name: str
    equipment_slots: int = 1
    unlocked_skill_cards: Set[str] = field(default_factory=set)
    unlocked_items: Set[str] = field(default_factory=set)
    unlocked_equipment: Set[str] = field(default_factory=set)
    unlocked_regions: Set[str] = field(default_factory=set)
    total_runs_completed: int = 0
    total_fights_won: int = 0
    achievements: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Initialize with minimal starter content for new players
        if not self.unlocked_regions:
            self.unlocked_regions = {"Tutorial"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for saving"""
        data = asdict(self)
        # Convert sets to lists for JSON serialization
        data['unlocked_skill_cards'] = list(self.unlocked_skill_cards)
        data['unlocked_items'] = list(self.unlocked_items)
        data['unlocked_equipment'] = list(self.unlocked_equipment)
        data['unlocked_regions'] = list(self.unlocked_regions)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create profile from dictionary"""
        # Convert lists back to sets
        data['unlocked_skill_cards'] = set(data.get('unlocked_skill_cards', []))
        data['unlocked_items'] = set(data.get('unlocked_items', []))
        data['unlocked_equipment'] = set(data.get('unlocked_equipment', []))
        data['unlocked_regions'] = set(data.get('unlocked_regions', []))
        return cls(**data)
    
    def unlock_skill_card(self, card_name: str):
        """Unlock a new skill card"""
        self.unlocked_skill_cards.add(card_name)
    
    def unlock_item(self, item_name: str):
        """Unlock a new item"""
        self.unlocked_items.add(item_name)
    
    def unlock_equipment(self, equipment_name: str):
        """Unlock new equipment"""
        self.unlocked_equipment.add(equipment_name)
    
    def unlock_region(self, region_name: str):
        """Unlock a new region"""
        self.unlocked_regions.add(region_name)
    
    def unlock_equipment_slot(self):
        """Unlock an additional equipment slot"""
        self.equipment_slots += 1
    
    def add_achievement(self, achievement_id: str, data: Any = None):
        """Add an achievement"""
        self.achievements[achievement_id] = data


class ProfileManager:
    """Manages profile creation, loading, and saving"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
    
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        profiles = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                profiles.append(filename[:-5])  # Remove .json extension
        return profiles
    
    def create_profile(self, name: str) -> Profile:
        """Create a new profile"""
        profile = Profile(name)
        self.save_profile(profile)
        return profile
    
    def load_profile(self, name: str) -> Profile:
        """Load an existing profile"""
        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Profile '{name}' not found")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Profile.from_dict(data)
    
    def save_profile(self, profile: Profile):
        """Save a profile to disk"""
        filepath = os.path.join(self.profiles_dir, f"{profile.name}.json")
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
    
    def delete_profile(self, name: str):
        """Delete a profile"""
        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def profile_exists(self, name: str) -> bool:
        """Check if a profile exists"""
        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        return os.path.exists(filepath) 