import pygame
import random
from lib.card import Card, Suit
from lib.combo import identify_combo
from lib.player import Player, AIPlayer
from lib.constants import *
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        self.player = Player("Player")
        self.ai = AIPlayer("AI")
        self.current_player = None
        self.last_combo = None
        self.last_player = None
        self.selected_cards = []
        
        self.play_button = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT - 80, 100, 40)
        self.pass_button = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT - 80, 100, 40)
        
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
            if card.rank == '3' and card.suit == Suit.DIAMONDS:
                self.current_player = self.player
                break
        else:
            for card in self.ai.hand:
                if card.rank == '3' and card.suit == Suit.DIAMONDS:
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
        self.screen.blit(turn_text, (WINDOW_WIDTH//2 - 80, 20))
        
        # Draw last played combo
        if self.last_combo and self.last_player:
            combo_text = self.font.render(f"Last Play: {self.last_player.name} - {self.last_combo.type.name}", True, CARD_COLOR)
            self.screen.blit(combo_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))
            
            # Draw last played cards
            start_x = (WINDOW_WIDTH - 40 * len(self.last_combo.cards)) // 2
            for i, card in enumerate(self.last_combo.cards):
                self.draw_card(card, start_x + i * 40, WINDOW_HEIGHT//2 + 30, True)
    
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
        combo = self.ai.choose_play(self.last_combo, {
            'player_cards': len(self.player.hand),
            'ai_cards': len(self.ai.hand),
            'player_hp': self.player.hp,
            'ai_hp': self.ai.hp
        })
        
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
            text_rect = winner_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
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
