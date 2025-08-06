import pygame
import random
from lib.constants import *
from lib.card import Card, Suit
from lib.combo import identify_combo
from lib.player import FightPlayer, SmartAIPlayer
from lib.skill_cards import get_skill_card, SkillCard
from lib.items import get_item, Item
from lib.equipment import get_equipment, Equipment
from typing import List, Optional, Dict, Any


class EnhancedFightGame:
    def __init__(self, screen, 
                 player_skill_cards: List[str] = None,
                 player_items: List[str] = None,
                 player_equipment: List[str] = None,
                 player_starting_hp: int = 10,
                 ai_starting_hp: int = 10,
                 region_modifiers: Dict[str, Any] = None,
                 run_manager = None,
                 preview_player = None,
                 preview_deck = None):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 18)

        # Initialize players
        self.player = FightPlayer("Player")
        self.ai = SmartAIPlayer("AI")
        self.current_player = None
        self.last_combo = None
        self.last_player = None
        self.selected_cards = []

        # Game state
        self.game_over = False
        self.winner = None
        self.player_card_rects = []
        self.discard_pile = []

        # Roguelike systems
        self.player_skill_cards = []
        self.player_items = []
        self.player_equipment = []
        self.region_modifiers = region_modifiers or {}
        self.run_manager = run_manager
        self.preview_player = preview_player
        self.preview_deck = preview_deck
        
        # Initialize starting HP
        self.player.hp = player_starting_hp
        self.ai.hp = ai_starting_hp

        # Load skill cards, items, and equipment
        if player_skill_cards:
            for card_name in player_skill_cards:
                skill_card = get_skill_card(card_name)
                if skill_card:
                    self.player_skill_cards.append(skill_card)
        
        if player_items:
            for item_name in player_items:
                item = get_item(item_name)
                if item:
                    self.player_items.append(item)
        
        if player_equipment:
            for equipment_name in player_equipment:
                equipment = get_equipment(equipment_name)
                if equipment:
                    self.player_equipment.append(equipment)
                    # Apply equipment effects
                    equipment.on_equip(self)

        # UI elements
        self.play_button = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 80, 100, 40)
        self.pass_button = pygame.Rect(WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT - 80, 100, 40)
        
        # Skill card buttons (will be created dynamically)
        self.skill_card_buttons = []
        self.item_buttons = []
        self.equipment_buttons = []
        
        # Game state tracking
        self.extra_turns = 0
        self.last_combo_damage_bonus = 0
        self.first_damage_taken = False

        self.init_game()

    def init_game(self):
        # Use pre-dealt cards if available
        if self.preview_player and self.preview_deck:
            # Use pre-dealt hand from preview
            self.player.hand = self.preview_player.hand
            # Deal AI hand from remaining deck
            self.ai.hand = self.preview_deck[22:]
            # Set discard pile (first 8 cards were already discarded during preview)
            self.discard_pile = []
        else:
            # Create deck normally
            deck = []
            for suit in Suit:
                for rank in Card.VALUE_MAP.keys():
                    deck.append(Card(rank, suit))

            # Shuffle and deal
            random.shuffle(deck)

            # Discard first 8 cards
            self.discard_pile = deck[:8]
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

        # Apply equipment effects at fight start
        for equipment in self.player_equipment:
            equipment.on_fight_start(self)

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

    def draw_hand(self, player, y_pos, show_cards=True):
        self.player_card_rects = []
        num_cards = len(player.hand)
        
        if num_cards == 0:
            return
            
        # Calculate spacing to keep cards in a single line with overlap
        # Leave some margin on each side
        margin = 100
        available_width = WINDOW_WIDTH - 2 * margin
        
        # Allow cards to overlap - use negative spacing if needed
        if num_cards > 1:
            # Calculate how much overlap we need
            total_card_width = num_cards * CARD_WIDTH
            if total_card_width > available_width:
                # Need overlap - calculate negative spacing
                overlap_needed = total_card_width - available_width
                card_spacing = -(overlap_needed // (num_cards - 1))
                # Ensure we don't overlap too much (keep at least 20px visible per card)
                card_spacing = max(card_spacing, -(CARD_WIDTH - 20))
            else:
                # No overlap needed - use positive spacing
                card_spacing = (available_width - total_card_width) // (num_cards - 1)
                card_spacing = min(card_spacing, 10)  # Max 10px spacing
        else:
            card_spacing = 0
        
        # Calculate starting x position to center the cards
        total_width = num_cards * CARD_WIDTH + (num_cards - 1) * card_spacing
        start_x = margin + (available_width - total_width) // 2
        
        for i, card in enumerate(player.hand):
            x = start_x + i * (CARD_WIDTH + card_spacing)
            y = y_pos

            self.draw_card(card, x, y, show_cards)
            if show_cards:
                self.player_card_rects.append((card, pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)))

    def draw_button(self, rect, text, hover=False, disabled=False):
        color = BUTTON_HOVER if hover else BUTTON_COLOR
        if disabled:
            color = (100, 100, 100)
            
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, 2)
        
        text_surface = self.font.render(text, True, TEXT_COLOR if not disabled else (150, 150, 150))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_skill_cards(self):
        """Draw skill card buttons"""
        if not self.player_skill_cards:
            return
            
        # Draw skill cards section
        skill_title = self.small_font.render("Skill Cards:", True, TEXT_COLOR)
        self.screen.blit(skill_title, (WINDOW_WIDTH - 200, 100))
        
        self.skill_card_buttons = []
        for i, skill_card in enumerate(self.player_skill_cards):
            y_pos = 130 + i * 30
            button_rect = pygame.Rect(WINDOW_WIDTH - 200, y_pos, 180, 25)
            self.skill_card_buttons.append((skill_card, button_rect))
            
            # Check if skill card can be used
            can_use = skill_card.can_use(self)
            hover = button_rect.collidepoint(pygame.mouse.get_pos())
            
            self.draw_button(button_rect, skill_card.name, hover, not can_use)

    def draw_items(self):
        """Draw item buttons"""
        if not self.player_items:
            return
            
        # Draw items section
        item_title = self.small_font.render("Items:", True, TEXT_COLOR)
        self.screen.blit(item_title, (WINDOW_WIDTH - 200, 250))
        
        self.item_buttons = []
        for i, item in enumerate(self.player_items):
            y_pos = 280 + i * 30
            button_rect = pygame.Rect(WINDOW_WIDTH - 200, y_pos, 180, 25)
            self.item_buttons.append((item, button_rect))
            
            # Check if item can be used
            can_use = item.can_use(self) if item.item_type == "Active" else False
            hover = button_rect.collidepoint(pygame.mouse.get_pos())
            
            display_text = f"{item.name}"
            if item.item_type == "Active" and item.uses is not None:
                display_text += f" ({item.uses})"
            
            self.draw_button(button_rect, display_text, hover, not can_use)

    def draw_equipment(self):
        """Draw equipped equipment info"""
        if not self.player_equipment:
            return
            
        # Draw equipment section
        equip_title = self.small_font.render("Equipment:", True, TEXT_COLOR)
        self.screen.blit(equip_title, (WINDOW_WIDTH - 200, 400))
        
        self.equipment_buttons = []
        for i, equipment in enumerate(self.player_equipment):
            y_pos = 430 + i * 30
            button_rect = pygame.Rect(WINDOW_WIDTH - 200, y_pos, 180, 25)
            self.equipment_buttons.append((equipment, button_rect))
            
            # Check if equipment can be used
            can_use = hasattr(equipment, 'can_use') and equipment.can_use(self)
            hover = button_rect.collidepoint(pygame.mouse.get_pos())
            
            display_text = f"• {equipment.name}"
            if can_use:
                display_text += " (Use)"
            
            self.draw_button(button_rect, display_text, hover, not can_use)

    def draw_game_info(self):
        # Draw HP and LP
        hp_text = f"Player HP: {self.player.hp}"
        if self.run_manager:
            hp_text += f" | LP: {self.run_manager.run_state.life_points}"
            # Also show fight progress
            fight_text = f"Fight: {self.run_manager.run_state.current_fight + 1}/{self.run_manager.run_state.total_fights}"
            fight_surface = self.font.render(fight_text, True, CARD_COLOR)
            self.screen.blit(fight_surface, (20, WINDOW_HEIGHT - 130))
            
        player_hp_text = self.font.render(hp_text, True, CARD_COLOR)
        ai_hp_text = self.font.render(f"AI HP: {self.ai.hp}", True, CARD_COLOR)
        self.screen.blit(player_hp_text, (20, WINDOW_HEIGHT - 100))
        self.screen.blit(ai_hp_text, (20, 20))

        # Draw last played combo as actual cards
        if self.last_combo:
            # Draw "Last:" label
            last_label = self.font.render("Last:", True, CARD_COLOR)
            self.screen.blit(last_label, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 20))
            
            # Draw the actual cards
            num_cards = len(self.last_combo.cards)
            card_spacing = 5
            total_width = num_cards * CARD_WIDTH + (num_cards - 1) * card_spacing
            start_x = WINDOW_WIDTH // 2 - total_width // 2
            
            for i, card in enumerate(self.last_combo.cards):
                x = start_x + i * (CARD_WIDTH + card_spacing)
                y = WINDOW_HEIGHT // 2 + 10
                self.draw_card(card, x, y, show_face=True)

        # Draw current player
        current_text = self.font.render(f"Current: {self.current_player.name}", True, CARD_COLOR)
        self.screen.blit(current_text, (WINDOW_WIDTH // 2 - 50, 20))

        # Draw discard pile count
        discard_text = self.small_font.render(f"Discard: {len(self.discard_pile)}", True, TEXT_COLOR)
        self.screen.blit(discard_text, (20, WINDOW_HEIGHT - 30))

    def handle_card_click(self, mouse_pos):
        # Find the topmost card that collides with the mouse position
        # Check cards in reverse order (last drawn = topmost)
        top_card = None
        for card, rect in reversed(self.player_card_rects):
            if rect.collidepoint(mouse_pos):
                top_card = card
                break

        if top_card:
            top_card.selected = not top_card.selected

    def get_selected_cards(self):
        return [card for card in self.player.hand if card.selected]

    def resort_hand(self, player):
        """Resort the player's hand after modifications"""
        player.sort_hand()

    def play_cards(self, player, cards):
        if not cards:
            return False

        combo = identify_combo(cards)
        if not combo:
            return False

        if self.last_combo and not combo.can_beat(self.last_combo):
            return False

        # Apply damage bonus from items/equipment
        if self.last_combo and combo.can_beat(self.last_combo):
            damage = 1 + self.last_combo_damage_bonus
            self.last_combo_damage_bonus = 0  # Reset bonus
            
            # Apply equipment damage modification
            damage = self.deal_damage(damage)
            
            # Determine target (opponent)
            target = self.ai if player == self.player else self.player
            target.hp -= damage

        # Remove cards from hand
        for card in cards:
            player.hand.remove(card)
            card.selected = False

        # Add to discard pile
        self.discard_pile.extend(cards)

        # Update game state
        self.last_combo = combo
        self.last_player = player

        # Trigger item effects for straight played
        if combo.type.name == "STRAIGHT":
            for item in self.player_items:
                item.on_trigger(self, "straight_played")

        return True

    def pass_turn(self):
        if self.last_player != self.current_player:
            damage = 1
            
            # Apply equipment damage modification
            damage = self.take_damage(damage)
            
            self.current_player.hp -= damage

        # Switch turns
        self.current_player = self.ai if self.current_player == self.player else self.player

        # If the last player gets the turn back, clear the table
        if self.last_player == self.current_player:
            self.last_combo = None

        # Handle extra turns
        if self.extra_turns > 0:
            self.extra_turns -= 1
            self.current_player = self.player

    def take_damage(self, damage: int) -> int:
        """Take damage, applying equipment effects"""
        modified_damage = damage
        
        # Check if this is first damage
        if not self.first_damage_taken:
            self.first_damage_taken = True
            # Trigger passive items for first damage
            for item in self.player_items:
                if item.on_trigger(self, "first_damage"):
                    return 0  # Damage blocked
        
        # Apply equipment effects
        for equipment in self.player_equipment:
            modified_damage = equipment.on_damage_taken(self, modified_damage)
        
        return modified_damage

    def deal_damage(self, damage: int) -> int:
        """Deal damage, applying equipment effects"""
        modified_damage = damage
        for equipment in self.player_equipment:
            modified_damage = equipment.on_damage_dealt(self, modified_damage)
        return modified_damage

    def use_skill_card(self, skill_card: SkillCard) -> bool:
        """Use a skill card"""
        if not skill_card.can_use(self):
            return False
        
        success = skill_card.use(self)
        if success:
            # Resort hand after skill card use
            self.resort_hand(self.player)
            if skill_card.one_time_use:
                self.player_skill_cards.remove(skill_card)
        return success

    def use_item(self, item: Item) -> bool:
        """Use an active item"""
        if item.item_type != "Active" or not item.can_use(self):
            return False
        
        success = item.use(self)
        if success:
            # Resort hand after item use
            self.resort_hand(self.player)
            if item.uses is not None and item.uses <= 0:
                self.player_items.remove(item)
        return success

    def use_equipment(self, equipment: Equipment) -> bool:
        """Use equipment that has a use method (like Gambler's Dice)"""
        if not hasattr(equipment, 'can_use') or not hasattr(equipment, 'use'):
            return False
        
        if not equipment.can_use(self):
            return False
        
        success = equipment.use(self)
        if success:
            # Resort hand after equipment use
            self.resort_hand(self.player)
        return success

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
        self.draw_hand(self.ai, 100, show_cards=False)
        self.draw_hand(self.player, WINDOW_HEIGHT - 250, show_cards=True)

        # Draw game info
        self.draw_game_info()

        # Draw skill cards, items, and equipment
        self.draw_skill_cards()
        self.draw_items()
        self.draw_equipment()

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

                        # Check skill card clicks
                        for skill_card, button_rect in self.skill_card_buttons:
                            if button_rect.collidepoint(mouse_pos):
                                self.use_skill_card(skill_card)
                                break

                        # Check item clicks
                        for item, button_rect in self.item_buttons:
                            if button_rect.collidepoint(mouse_pos):
                                self.use_item(item)
                                break

                        # Check equipment clicks
                        if hasattr(self, 'equipment_buttons'):
                            for equipment, button_rect in self.equipment_buttons:
                                if button_rect.collidepoint(mouse_pos):
                                    self.use_equipment(equipment)
                                    break

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

        return self.winner 