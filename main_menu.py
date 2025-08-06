import pygame
import sys
from lib.constants import *
from lib.profile import ProfileManager, Profile
from lib.run_system import RunManager
from lib.enhanced_game import EnhancedFightGame
from lib.card import Card, Suit
from lib.player import FightPlayer
from lib.skill_cards import get_random_skill_cards, get_skill_card, load_skill_card_image
from lib.equipment import get_all_equipment, get_equipment
import random


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.profile_manager = ProfileManager()
        
        # Menu states
        self.state = "main"  # "main", "profile_select", "create_profile", "region_select", "equipment_select", "pre_fight", "reward_select"
        self.current_profile = None
        self.selected_profile = None
        self.selected_region = None
        self.new_profile_name = ""
        self.typing = False
        
        # Menu buttons
        button_width = 200
        button_height = 50
        center_x = WINDOW_WIDTH // 2 - button_width // 2
        
        # Main menu buttons
        self.new_profile_button = pygame.Rect(center_x, 250, button_width, button_height)
        self.load_profile_button = pygame.Rect(center_x, 320, button_width, button_height)
        self.quit_button = pygame.Rect(center_x, 390, button_width, button_height)
        
        # Profile selection buttons
        self.back_button = pygame.Rect(50, WINDOW_HEIGHT - 80, 100, 40)
        self.delete_button = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 80, 100, 40)
        
        # Create profile input
        self.name_input_rect = pygame.Rect(center_x, 300, button_width, button_height)
        self.create_button = pygame.Rect(center_x, 370, button_width, button_height)
        self.cancel_button = pygame.Rect(center_x, 440, button_width, button_height)
        
        # Region selection
        self.region_buttons = []
        self.start_run_button = pygame.Rect(center_x, WINDOW_HEIGHT - 120, button_width, button_height)
        
        # Pre-fight buttons
        self.fight_button = pygame.Rect(center_x, 400, button_width, button_height)
        self.give_up_button = pygame.Rect(center_x, 470, button_width, button_height)
        
        # Pre-fight card preview
        self.preview_player = None
        self.preview_deck = None
        
        # Reward selection
        self.reward_cards = []
        self.reward_buttons = []
        
        # Equipment selection
        self.equipment_buttons = []
        self.selected_equipment = []
        self.confirm_equipment_button = pygame.Rect(center_x, WINDOW_HEIGHT - 80, button_width, button_height)
        
    def draw_button(self, rect, text, hover=False, disabled=False):
        """Draw a button with hover effects"""
        color = BUTTON_HOVER if hover else BUTTON_COLOR
        if disabled:
            color = (100, 100, 100)  # Gray for disabled
            
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, 2)
        
        text_surface = self.font.render(text, True, TEXT_COLOR if not disabled else (150, 150, 150))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_card(self, card, x, y):
        """Draw a card at the specified position"""
        pygame.draw.rect(self.screen, CARD_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(self.screen, TEXT_COLOR, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

        # Draw rank
        color = RED_COLOR if card.suit in [Suit.HEARTS, Suit.DIAMONDS] else BLACK_COLOR
        rank_text = self.small_font.render(card.rank, True, color)
        self.screen.blit(rank_text, (x + 5, y + 5))

        # Draw suit
        suit_text = self.small_font.render(card.suit.value, True, color)
        self.screen.blit(suit_text, (x + 5, y + 25))
        
    def draw_hand_preview(self, player, y_pos):
        """Draw player's hand for preview"""
        if not player or not player.hand:
            return
            
        num_cards = len(player.hand)
        if num_cards == 0:
            return
            
        # Calculate spacing to keep cards in a single line with overlap
        margin = 50
        available_width = WINDOW_WIDTH - 2 * margin
        
        if num_cards > 1:
            total_card_width = num_cards * CARD_WIDTH
            if total_card_width > available_width:
                overlap_needed = total_card_width - available_width
                card_spacing = -(overlap_needed // (num_cards - 1))
                card_spacing = max(card_spacing, -(CARD_WIDTH - 20))
            else:
                card_spacing = (available_width - total_card_width) // (num_cards - 1)
                card_spacing = min(card_spacing, 10)
        else:
            card_spacing = 0
        
        total_width = num_cards * CARD_WIDTH + (num_cards - 1) * card_spacing
        start_x = margin + (available_width - total_width) // 2
        
        for i, card in enumerate(player.hand):
            x = start_x + i * (CARD_WIDTH + card_spacing)
            y = y_pos
            self.draw_card(card, x, y)
        
    def draw_input_box(self, rect, text, active=False):
        """Draw an input box"""
        color = SELECTED_COLOR if active else CARD_COLOR
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, 2)
        
        text_surface = self.font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(midleft=(rect.x + 10, rect.centery))
        self.screen.blit(text_surface, text_rect)
        
    def draw_main_menu(self):
        """Draw the main menu"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("PDK Rogue", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.small_font.render("A Roguelike Deckbuilder", True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons
        self.draw_button(self.new_profile_button, "New Profile", 
                        self.new_profile_button.collidepoint(mouse_pos))
        
        has_profiles = len(self.profile_manager.list_profiles()) > 0
        self.draw_button(self.load_profile_button, "Load Profile", 
                        self.load_profile_button.collidepoint(mouse_pos),
                        not has_profiles)
        
        self.draw_button(self.quit_button, "Quit", 
                        self.quit_button.collidepoint(mouse_pos))
        
    def draw_profile_select(self):
        """Draw profile selection screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Select Profile", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # List profiles
        profiles = self.profile_manager.list_profiles()
        mouse_pos = pygame.mouse.get_pos()
        
        for i, profile_name in enumerate(profiles):
            y_pos = 120 + i * 60
            profile_rect = pygame.Rect(100, y_pos, WINDOW_WIDTH - 200, 50)
            
            # Load profile data for stats
            try:
                profile = self.profile_manager.load_profile(profile_name)
                stats_text = f"Runs: {profile.total_runs_completed} | Fights Won: {profile.total_fights_won}"
            except:
                stats_text = "Error loading profile"
            
            # Draw profile button
            hover = profile_rect.collidepoint(mouse_pos)
            self.draw_button(profile_rect, f"{profile_name} - {stats_text}", hover)
            
            # Handle click
            if hover and pygame.mouse.get_pressed()[0]:
                self.current_profile = self.profile_manager.load_profile(profile_name)
                self.state = "region_select"
                return
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def draw_create_profile(self):
        """Draw profile creation screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Create New Profile", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = self.small_font.render("Enter profile name:", True, TEXT_COLOR)
        instructions_rect = instructions.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(instructions, instructions_rect)
        
        # Name input
        mouse_pos = pygame.mouse.get_pos()
        self.draw_input_box(self.name_input_rect, self.new_profile_name, self.typing)
        
        # Buttons
        can_create = len(self.new_profile_name.strip()) > 0 and not self.profile_manager.profile_exists(self.new_profile_name.strip())
        self.draw_button(self.create_button, "Create", 
                        self.create_button.collidepoint(mouse_pos), not can_create)
        self.draw_button(self.cancel_button, "Cancel", 
                        self.cancel_button.collidepoint(mouse_pos))
        
    def draw_region_select(self):
        """Draw region selection screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render(f"Select Region - {self.current_profile.name}", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Profile stats
        stats_text = f"Runs: {self.current_profile.total_runs_completed} | Fights Won: {self.current_profile.total_fights_won}"
        stats_surface = self.small_font.render(stats_text, True, TEXT_COLOR)
        self.screen.blit(stats_surface, (20, 80))
        
        # List available regions
        regions = list(self.current_profile.unlocked_regions)
        mouse_pos = pygame.mouse.get_pos()
        
        for i, region_name in enumerate(regions):
            y_pos = 120 + i * 60
            region_rect = pygame.Rect(100, y_pos, WINDOW_WIDTH - 200, 50)
            
            hover = region_rect.collidepoint(mouse_pos)
            self.draw_button(region_rect, region_name, hover)
            
            # Handle click
            if hover and pygame.mouse.get_pressed()[0]:
                self.selected_region = region_name
                self.selected_equipment = []  # Reset equipment selection
                self.state = "equipment_select"
                return
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def draw_pre_fight(self):
        """Draw pre-fight decision screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        fight_num = self.run_manager.run_state.current_fight + 1
        title = self.font.render(f"Fight {fight_num}/{self.run_manager.run_state.total_fights}", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Current status
        lp_text = f"Life Points: {self.run_manager.run_state.life_points}"
        lp_surface = self.font.render(lp_text, True, TEXT_COLOR)
        lp_rect = lp_surface.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(lp_surface, lp_rect)
        
        # Show preview hand
        hand_label = self.small_font.render("Your hand:", True, TEXT_COLOR)
        self.screen.blit(hand_label, (50, 200))
        
        if self.preview_player:
            self.draw_hand_preview(self.preview_player, 220)
        
        # Instructions
        instructions = [
            "Choose your action:",
            "Fight: Risk losing 2 LP if defeated",
            "Give Up: Lose 1 LP and skip this fight"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, TEXT_COLOR)
            inst_rect = inst_surface.get_rect(center=(WINDOW_WIDTH // 2, 320 + i * 25))
            self.screen.blit(inst_surface, inst_rect)
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(self.fight_button, "Fight", 
                        self.fight_button.collidepoint(mouse_pos))
        self.draw_button(self.give_up_button, "Give Up", 
                        self.give_up_button.collidepoint(mouse_pos))
        
        # Back button (to return to region select)
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def draw_reward_select(self):
        """Draw reward selection screen after winning a fight"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Victory Reward!", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instruction = self.small_font.render("Choose a skill card to add to your inventory:", True, TEXT_COLOR)
        inst_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 90))
        self.screen.blit(instruction, inst_rect)
        
        # Current inventory status
        current_count = len(self.run_manager.run_state.skill_cards)
        max_count = self.run_manager.run_state.max_skill_cards
        inventory_text = f"Skill Card Inventory: {current_count}/{max_count}"
        inv_surface = self.small_font.render(inventory_text, True, TEXT_COLOR)
        self.screen.blit(inv_surface, (20, 120))
        
        # Show current inventory if any
        if current_count > 0:
            inv_label = self.small_font.render("Current Inventory:", True, TEXT_COLOR)
            self.screen.blit(inv_label, (20, 150))
            
            for i, card in enumerate(self.run_manager.run_state.skill_cards):
                y_pos = 170 + i * 20
                card_text = f"• {card.name}"
                card_surface = self.small_font.render(card_text, True, TEXT_COLOR)
                self.screen.blit(card_surface, (30, y_pos))
        
        # Draw reward cards as images in a horizontal layout
        self.reward_buttons = []
        mouse_pos = pygame.mouse.get_pos()
        
        card_width = 120
        card_height = 150
        card_spacing = 20
        
        # Center the cards horizontally
        total_width = len(self.reward_cards) * card_width + (len(self.reward_cards) - 1) * card_spacing
        start_x = (WINDOW_WIDTH - total_width) // 2
        start_y = 280
        
        for i, card in enumerate(self.reward_cards):
            x = start_x + i * (card_width + card_spacing)
            y = start_y
            
            card_rect = pygame.Rect(x, y, card_width, card_height)
            self.reward_buttons.append((card, card_rect))
            
            hover = card_rect.collidepoint(mouse_pos)
            can_select = self.run_manager.run_state.can_add_skill_card()
            
            # Try to load and display card image
            card_image = load_skill_card_image(card.name)
            if card_image:
                # Scale image to reward card size
                scaled_image = pygame.transform.scale(card_image, (card_width, card_height))
                
                # Apply effects based on state
                if not can_select:
                    # Gray out if inventory full
                    overlay = pygame.Surface((card_width, card_height))
                    overlay.fill((100, 100, 100))
                    overlay.set_alpha(150)
                    scaled_image = scaled_image.copy()
                    scaled_image.blit(overlay, (0, 0))
                elif hover:
                    # Highlight on hover
                    overlay = pygame.Surface((card_width, card_height))
                    overlay.fill((255, 255, 255))
                    overlay.set_alpha(60)
                    scaled_image = scaled_image.copy()
                    scaled_image.blit(overlay, (0, 0))
                
                self.screen.blit(scaled_image, card_rect)
                
                # Draw border
                border_color = SELECTED_COLOR if hover and can_select else TEXT_COLOR
                border_width = 3 if hover and can_select else 1
                pygame.draw.rect(self.screen, border_color, card_rect, border_width)
                
                # Draw card name below the image
                name_surface = self.small_font.render(card.name, True, TEXT_COLOR)
                name_rect = name_surface.get_rect(centerx=card_rect.centerx, y=card_rect.bottom + 5)
                self.screen.blit(name_surface, name_rect)
                
                # Draw description below name
                desc_surface = self.small_font.render(card.description[:50] + "..." if len(card.description) > 50 else card.description, True, TEXT_COLOR)
                desc_rect = desc_surface.get_rect(centerx=card_rect.centerx, y=name_rect.bottom + 3)
                self.screen.blit(desc_surface, desc_rect)
                
            else:
                # Fallback to button if image not found
                self.draw_button(card_rect, "", hover, not can_select)
                
                # Draw card info as text
                name_surface = self.font.render(card.name, True, TEXT_COLOR)
                desc_surface = self.small_font.render(card.description, True, TEXT_COLOR)
                rarity_surface = self.small_font.render(f"[{card.rarity.name}]", True, TEXT_COLOR)
                
                self.screen.blit(name_surface, (card_rect.x + 10, card_rect.y + 5))
                self.screen.blit(desc_surface, (card_rect.x + 10, card_rect.y + 30))
                self.screen.blit(rarity_surface, (card_rect.x + 10, card_rect.y + 50))
        
        # If inventory is full, show message and option to abandon cards
        if not self.run_manager.run_state.can_add_skill_card():
            full_text = "Inventory Full! Click on a current skill card to abandon it first."
            full_surface = self.small_font.render(full_text, True, (255, 100, 100))  # Red text
            full_rect = full_surface.get_rect(center=(WINDOW_WIDTH // 2, 250))
            self.screen.blit(full_surface, full_rect)
            
            # Make current inventory cards clickable for abandoning
            for i, card in enumerate(self.run_manager.run_state.skill_cards):
                y_pos = 170 + i * 20
                abandon_rect = pygame.Rect(200, y_pos - 2, 200, 20)
                if abandon_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (100, 100, 100), abandon_rect, 2)
        
        # Skip reward button
        skip_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 80, 200, 40)
        self.draw_button(skip_button, "Skip Reward", skip_button.collidepoint(mouse_pos))
        self.skip_reward_button = skip_button
        
    def draw_equipment_select(self):
        """Draw equipment selection screen before starting a run"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Select Equipment", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Equipment slots info
        available_slots = self.current_profile.equipment_slots
        used_slots = sum(eq.slot for eq in self.selected_equipment)
        slots_text = f"Equipment Slots: {used_slots}/{available_slots}"
        slots_surface = self.font.render(slots_text, True, TEXT_COLOR)
        self.screen.blit(slots_surface, (20, 90))
        
        # Instructions
        instruction = self.small_font.render("Select equipment to bring on your run:", True, TEXT_COLOR)
        self.screen.blit(instruction, (20, 120))
        
        # Show selected equipment
        if self.selected_equipment:
            selected_label = self.small_font.render("Selected:", True, TEXT_COLOR)
            self.screen.blit(selected_label, (20, 150))
            
            for i, equipment in enumerate(self.selected_equipment):
                y_pos = 170 + i * 20
                eq_text = f"• {equipment.name} (Slot: {equipment.slot})"
                eq_surface = self.small_font.render(eq_text, True, TEXT_COLOR)
                self.screen.blit(eq_surface, (30, y_pos))
        
        # Available equipment
        available_equipment = [get_equipment(name) for name in self.current_profile.unlocked_equipment]
        self.equipment_buttons = []
        mouse_pos = pygame.mouse.get_pos()
        
        start_y = 250
        for i, equipment in enumerate(available_equipment):
            y_pos = start_y + i * 80
            button_rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 70)
            self.equipment_buttons.append((equipment, button_rect))
            
            hover = button_rect.collidepoint(mouse_pos)
            
            # Check if already selected
            already_selected = any(eq.name == equipment.name for eq in self.selected_equipment)
            
            # Check if can be equipped (slots available)
            can_equip = (used_slots + equipment.slot <= available_slots) and not already_selected
            
            # Different colors for different states
            if already_selected:
                # Green for selected
                pygame.draw.rect(self.screen, (50, 150, 50), button_rect)
            elif can_equip and hover:
                # Hover color
                pygame.draw.rect(self.screen, BUTTON_HOVER, button_rect)
            elif can_equip:
                # Normal available
                pygame.draw.rect(self.screen, BUTTON_COLOR, button_rect)
            else:
                # Gray for unavailable
                pygame.draw.rect(self.screen, (100, 100, 100), button_rect)
            
            pygame.draw.rect(self.screen, TEXT_COLOR, button_rect, 2)
            
            # Draw equipment info
            name_surface = self.font.render(equipment.name, True, TEXT_COLOR)
            desc_surface = self.small_font.render(equipment.description, True, TEXT_COLOR)
            tier_surface = self.small_font.render(f"[{equipment.tier.name}] Slots: {equipment.slot}", True, TEXT_COLOR)
            
            self.screen.blit(name_surface, (button_rect.x + 10, button_rect.y + 5))
            self.screen.blit(desc_surface, (button_rect.x + 10, button_rect.y + 30))
            self.screen.blit(tier_surface, (button_rect.x + 10, button_rect.y + 50))
        
        # Confirm button
        can_confirm = True  # Can always confirm, even with no equipment
        self.draw_button(self.confirm_equipment_button, "Start Run", 
                        self.confirm_equipment_button.collidepoint(mouse_pos), not can_confirm)
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def create_preview_deck(self):
        """Create and deal cards for preview"""
        # Create deck
        deck = []
        for suit in Suit:
            for rank in Card.VALUE_MAP.keys():
                deck.append(Card(rank, suit))

        # Shuffle and deal
        random.shuffle(deck)

        # Discard first 8 cards
        discard_pile = deck[:8]
        deck = deck[8:]

        # Create preview player and deal 22 cards
        self.preview_player = FightPlayer("Player")
        self.preview_player.hand = deck[:22]
        self.preview_player.sort_hand()
        
        # Store remaining deck for actual fight
        self.preview_deck = deck
        
    def start_run(self, region_name):
        """Start a new run in the selected region"""
        # Create run manager
        self.run_manager = RunManager(self.current_profile, region_name)
        
        # Equip selected equipment
        for equipment in self.selected_equipment:
            self.run_manager.run_state.equip_item(equipment.name)
        
        self.run_manager.start_run()
        
        # Create preview deck and go to pre-fight screen
        self.create_preview_deck()
        self.state = "pre_fight"
        
    def check_run_status_and_continue(self):
        """Check run status and continue to next fight or end run"""
        if self.run_manager.run_state.is_run_complete():
            # Run completed
            self.run_manager.complete_run()
            self.profile_manager.save_profile(self.current_profile)
            print(f"Run completed! Won {self.run_manager.run_state.fights_won}/{self.run_manager.run_state.total_fights} fights")
            self.state = "region_select"
            return
            
        if self.run_manager.run_state.is_run_failed():
            # Run failed
            self.run_manager.fail_run()
            self.profile_manager.save_profile(self.current_profile)
            print(f"Run failed! LP reached 0. Final score: {self.run_manager.run_state.fights_won} fights won")
            self.state = "region_select"
            return
            
        # Create new preview deck and go to pre-fight screen
        self.create_preview_deck()
        self.state = "pre_fight"
        
    def start_actual_fight(self):
        """Start the actual combat"""
        # Use skill cards from run inventory, items from profile, equipment from run
        run_skill_cards = [card.name for card in self.run_manager.run_state.skill_cards]
        unlocked_items = list(self.current_profile.unlocked_items)
        run_equipment = [eq.name for eq in self.run_manager.run_state.equipped_equipment]
        
        # Start the enhanced combat game with pre-dealt cards
        combat_game = EnhancedFightGame(
            screen=self.screen,
            player_skill_cards=run_skill_cards,
            player_items=unlocked_items,
            player_equipment=run_equipment,
            player_starting_hp=10,
            ai_starting_hp=10,
            run_manager=self.run_manager,
            preview_player=self.preview_player,
            preview_deck=self.preview_deck
        )
        result = combat_game.run()
        
        # Handle fight result
        if result and result.name == "Player":
            # Player won - show reward screen
            self.run_manager.end_fight(True)
            self.show_victory_rewards()
        else:
            # Player lost - continue normally
            self.run_manager.end_fight(False)
            self.profile_manager.save_profile(self.current_profile)
            self.check_run_status_and_continue()
        
    def give_up_fight(self):
        """Give up current fight, lose 1 LP"""
        self.run_manager.run_state.life_points = max(0, self.run_manager.run_state.life_points - 1)
        self.run_manager.run_state.current_fight += 1
        self.run_manager.run_state.fights_lost += 1
        
        # Save profile and check run status
        self.profile_manager.save_profile(self.current_profile)
        self.check_run_status_and_continue()
        
    def show_victory_rewards(self):
        """Show reward selection after winning a fight"""
        # Generate 3 random skill cards
        current_cards = self.run_manager.run_state.get_skill_card_names()
        self.reward_cards = get_random_skill_cards(3, exclude=current_cards)
        
        # Go to reward selection screen
        self.state = "reward_select"
        
    def handle_click(self, pos):
        """Handle mouse clicks"""
        if self.state == "main":
            if self.new_profile_button.collidepoint(pos):
                self.state = "create_profile"
            elif self.load_profile_button.collidepoint(pos):
                self.state = "profile_select"
            elif self.quit_button.collidepoint(pos):
                pygame.quit()
                sys.exit()
                
        elif self.state == "profile_select":
            if self.back_button.collidepoint(pos):
                self.state = "main"
                
        elif self.state == "create_profile":
            if self.name_input_rect.collidepoint(pos):
                self.typing = True
            elif self.create_button.collidepoint(pos):
                name = self.new_profile_name.strip()
                if len(name) > 0 and not self.profile_manager.profile_exists(name):
                    self.current_profile = self.profile_manager.create_profile(name)
                    self.state = "region_select"
                    self.new_profile_name = ""
            elif self.cancel_button.collidepoint(pos):
                self.state = "main"
                self.new_profile_name = ""
                self.typing = False
                
        elif self.state == "region_select":
            if self.back_button.collidepoint(pos):
                self.state = "profile_select"
                self.current_profile = None
                
        elif self.state == "equipment_select":
            # Check equipment clicks
            for equipment, button_rect in self.equipment_buttons:
                if button_rect.collidepoint(pos):
                    # Check if already selected
                    already_selected = any(eq.name == equipment.name for eq in self.selected_equipment)
                    
                    if already_selected:
                        # Unselect equipment
                        self.selected_equipment = [eq for eq in self.selected_equipment if eq.name != equipment.name]
                    else:
                        # Check if we have slots available
                        used_slots = sum(eq.slot for eq in self.selected_equipment)
                        available_slots = self.current_profile.equipment_slots
                        
                        if used_slots + equipment.slot <= available_slots:
                            # Add equipment
                            self.selected_equipment.append(equipment)
                    return
            
            # Check confirm button
            if self.confirm_equipment_button.collidepoint(pos):
                self.start_run(self.selected_region)
                return
            
            # Check back button
            if self.back_button.collidepoint(pos):
                self.state = "region_select"
                return
                
        elif self.state == "pre_fight":
            if self.fight_button.collidepoint(pos):
                self.start_actual_fight()
            elif self.give_up_button.collidepoint(pos):
                self.give_up_fight()
            elif self.back_button.collidepoint(pos):
                self.state = "region_select"
                
        elif self.state == "reward_select":
            # Check reward card clicks
            for card, button_rect in self.reward_buttons:
                if button_rect.collidepoint(pos) and self.run_manager.run_state.can_add_skill_card():
                    # Add selected card to inventory
                    self.run_manager.run_state.add_skill_card_instance(card)
                    self.profile_manager.save_profile(self.current_profile)
                    self.check_run_status_and_continue()
                    return
            
            # Check skip reward button
            if hasattr(self, 'skip_reward_button') and self.skip_reward_button.collidepoint(pos):
                self.check_run_status_and_continue()
                return
            
            # Check inventory clicks for abandoning cards (if inventory is full)
            if not self.run_manager.run_state.can_add_skill_card():
                for i, card in enumerate(self.run_manager.run_state.skill_cards):
                    y_pos = 170 + i * 20
                    abandon_rect = pygame.Rect(200, y_pos - 2, 200, 20)
                    if abandon_rect.collidepoint(pos):
                        # Remove the clicked card
                        self.run_manager.run_state.remove_skill_card(card.name)
                        return
                
    def handle_keydown(self, event):
        """Handle keyboard input"""
        if self.state == "create_profile" and self.typing:
            if event.key == pygame.K_RETURN:
                name = self.new_profile_name.strip()
                if len(name) > 0 and not self.profile_manager.profile_exists(name):
                    self.current_profile = self.profile_manager.create_profile(name)
                    self.state = "region_select"
                    self.new_profile_name = ""
                    self.typing = False
            elif event.key == pygame.K_BACKSPACE:
                self.new_profile_name = self.new_profile_name[:-1]
            elif event.unicode.isprintable():
                self.new_profile_name += event.unicode
                
    def draw(self):
        """Draw the current screen"""
        if self.state == "main":
            self.draw_main_menu()
        elif self.state == "profile_select":
            self.draw_profile_select()
        elif self.state == "create_profile":
            self.draw_create_profile()
        elif self.state == "region_select":
            self.draw_region_select()
        elif self.state == "equipment_select":
            self.draw_equipment_select()
        elif self.state == "pre_fight":
            self.draw_pre_fight()
        elif self.state == "reward_select":
            self.draw_reward_select()
        
    def run(self):
        """Main menu loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                        
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PDK Rogue")
    
    menu = MainMenu(screen)
    menu.run() 