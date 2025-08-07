import pygame
import sys
from lib.constants import *
from lib.enhanced_game import EnhancedFightGame
from lib.skill_cards import get_all_skill_cards, SKILL_CARDS
from lib.items import get_all_items, ITEMS
from lib.equipment import get_all_equipment, EQUIPMENT
from lib.enemies import EnemyType, REGULAR_ENEMIES, ELITE_ENEMIES, BOSS_ENEMIES


class TestFightConfig:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Configuration state
        self.selected_skill_cards = []
        self.selected_items = []
        self.selected_equipment = []
        self.player_starting_hp = 5
        self.ai_starting_hp = 5
        self.region = "Tutorial"
        self.enemy_type = EnemyType.REGULAR
        self.enemy_name = None
        
        # UI state
        self.current_section = "main"  # main, skill_cards, items, equipment, stats, enemies
        self.scroll_offset = 0
        
        # Available options
        self.available_skill_cards = list(SKILL_CARDS.keys())
        self.available_items = list(ITEMS.keys())
        self.available_equipment = list(EQUIPMENT.keys())
        
        # UI elements
        button_width = 200
        button_height = 40
        center_x = WINDOW_WIDTH // 2 - button_width // 2
        
        self.start_fight_button = pygame.Rect(center_x, WINDOW_HEIGHT - 60, button_width, button_height)
        self.back_button = pygame.Rect(50, WINDOW_HEIGHT - 60, 100, 40)
        
    def draw_button(self, rect, text, hover=False, disabled=False):
        """Draw a button with hover effects"""
        color = BUTTON_HOVER if hover else BUTTON_COLOR
        if disabled:
            color = (100, 100, 100)
            
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, 2)
        
        text_surface = self.font.render(text, True, TEXT_COLOR if not disabled else (150, 150, 150))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_selection_box(self, rect, text, selected=False, hover=False):
        """Draw a selection box for items"""
        color = SELECTED_COLOR if selected else CARD_COLOR
        if hover:
            color = BUTTON_HOVER
            
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, 2)
        
        text_surface = self.small_font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(midleft=(rect.x + 10, rect.centery))
        self.screen.blit(text_surface, text_rect)
        
    def draw_main_menu(self):
        """Draw the main configuration menu"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Test Fight Configuration", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Configuration summary
        y_pos = 100
        enemy_display = self.enemy_name or f"Random {self.enemy_type.value.title()}"
        summary_items = [
            f"Region: {self.region}",
            f"Player HP: {self.player_starting_hp}",
            f"AI HP: {self.ai_starting_hp}",
            f"Enemy: {enemy_display}",
            f"Skill Cards: {len(self.selected_skill_cards)}",
            f"Items: {len(self.selected_items)}",
            f"Equipment: {len(self.selected_equipment)}"
        ]
        
        for item in summary_items:
            text = self.font.render(item, True, TEXT_COLOR)
            self.screen.blit(text, (50, y_pos))
            y_pos += 30
        
        # Configuration buttons
        y_pos = 300
        button_width = 250
        button_height = 40
        center_x = WINDOW_WIDTH // 2 - button_width // 2
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Skill cards button
        skill_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        self.draw_button(skill_rect, f"Configure Skill Cards ({len(self.selected_skill_cards)})", 
                        skill_rect.collidepoint(mouse_pos))
        y_pos += 50
        
        # Items button
        items_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        self.draw_button(items_rect, f"Configure Items ({len(self.selected_items)})", 
                        items_rect.collidepoint(mouse_pos))
        y_pos += 50
        
        # Equipment button
        equip_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        self.draw_button(equip_rect, f"Configure Equipment ({len(self.selected_equipment)})", 
                        equip_rect.collidepoint(mouse_pos))
        y_pos += 50
        
        # Stats button
        stats_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        self.draw_button(stats_rect, "Configure Stats", 
                        stats_rect.collidepoint(mouse_pos))
        y_pos += 50
        
        # Enemy button
        enemy_display = self.enemy_name or f"Random {self.enemy_type.value.title()}"
        enemy_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        self.draw_button(enemy_rect, f"Configure Enemy ({enemy_display})", 
                        enemy_rect.collidepoint(mouse_pos))
        
        # Start fight button
        can_start = len(self.selected_skill_cards) <= 5 and len(self.selected_items) <= 5
        self.draw_button(self.start_fight_button, "Start Test Fight", 
                        self.start_fight_button.collidepoint(mouse_pos), not can_start)
        
    def draw_skill_cards_selection(self):
        """Draw skill cards selection screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Select Skill Cards (Max 5)", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Selected count
        count_text = self.font.render(f"Selected: {len(self.selected_skill_cards)}/5", True, TEXT_COLOR)
        self.screen.blit(count_text, (50, 60))
        
        # List skill cards
        y_pos = 100
        mouse_pos = pygame.mouse.get_pos()
        
        for i, card_name in enumerate(self.available_skill_cards):
            if y_pos > WINDOW_HEIGHT - 100:
                break
                
            rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 30)
            selected = card_name in self.selected_skill_cards
            hover = rect.collidepoint(mouse_pos)
            
            self.draw_selection_box(rect, card_name, selected, hover)
            
            y_pos += 35
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def draw_items_selection(self):
        """Draw items selection screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Select Items (Max 5)", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Selected count
        count_text = self.font.render(f"Selected: {len(self.selected_items)}/5", True, TEXT_COLOR)
        self.screen.blit(count_text, (50, 60))
        
        # List items
        y_pos = 100
        mouse_pos = pygame.mouse.get_pos()
        
        for i, item_name in enumerate(self.available_items):
            if y_pos > WINDOW_HEIGHT - 100:
                break
                
            rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 30)
            selected = item_name in self.selected_items
            hover = rect.collidepoint(mouse_pos)
            
            self.draw_selection_box(rect, item_name, selected, hover)
            
            y_pos += 35
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def draw_equipment_selection(self):
        """Draw equipment selection screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Select Equipment", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Selected count
        count_text = self.font.render(f"Selected: {len(self.selected_equipment)}", True, TEXT_COLOR)
        self.screen.blit(count_text, (50, 60))
        
        # List equipment
        y_pos = 100
        mouse_pos = pygame.mouse.get_pos()
        
        for i, equip_name in enumerate(self.available_equipment):
            if y_pos > WINDOW_HEIGHT - 100:
                break
                
            rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 30)
            selected = equip_name in self.selected_equipment
            hover = rect.collidepoint(mouse_pos)
            
            self.draw_selection_box(rect, equip_name, selected, hover)
            
            y_pos += 35
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def draw_stats_configuration(self):
        """Draw stats configuration screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Configure Stats", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)
        
        # HP configuration
        y_pos = 100
        
        # Player HP
        player_hp_text = self.font.render(f"Player Starting HP: {self.player_starting_hp}", True, TEXT_COLOR)
        self.screen.blit(player_hp_text, (50, y_pos))
        
        # HP adjustment buttons
        button_width = 40
        button_height = 30
        mouse_pos = pygame.mouse.get_pos()
        
        # Player HP buttons
        dec_player_rect = pygame.Rect(300, y_pos, button_width, button_height)
        inc_player_rect = pygame.Rect(350, y_pos, button_width, button_height)
        
        self.draw_button(dec_player_rect, "-", dec_player_rect.collidepoint(mouse_pos))
        self.draw_button(inc_player_rect, "+", inc_player_rect.collidepoint(mouse_pos))
        
        y_pos += 50
        
        # AI HP
        ai_hp_text = self.font.render(f"AI Starting HP: {self.ai_starting_hp}", True, TEXT_COLOR)
        self.screen.blit(ai_hp_text, (50, y_pos))
        
        # AI HP buttons
        dec_ai_rect = pygame.Rect(300, y_pos, button_width, button_height)
        inc_ai_rect = pygame.Rect(350, y_pos, button_width, button_height)
        
        self.draw_button(dec_ai_rect, "-", dec_ai_rect.collidepoint(mouse_pos))
        self.draw_button(inc_ai_rect, "+", inc_ai_rect.collidepoint(mouse_pos))
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))
        
    def start_test_fight(self):
        """Start the test fight with current configuration"""
        # Create the enhanced fight game with current configuration
        fight_game = EnhancedFightGame(
            screen=self.screen,
            player_skill_cards=self.selected_skill_cards,
            player_items=self.selected_items,
            player_equipment=self.selected_equipment,
            player_starting_hp=self.player_starting_hp,
            ai_starting_hp=self.ai_starting_hp,
            enemy_type=self.enemy_type,
            enemy_name=self.enemy_name
        )
        
        # Run the fight
        winner = fight_game.run()
        
        # Return to configuration after fight ends
        return winner
        
    def draw(self):
        """Draw the current screen"""
        if self.current_section == "main":
            self.draw_main_menu()
        elif self.current_section == "skill_cards":
            self.draw_skill_cards_selection()
        elif self.current_section == "items":
            self.draw_items_selection()
        elif self.current_section == "equipment":
            self.draw_equipment_selection()
        elif self.current_section == "stats":
            self.draw_stats_configuration()
        elif self.current_section == "enemies":
            self.draw_enemy_selection()
        
    def run(self):
        """Main configuration loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_section != "main":
                            self.current_section = "main"
                        else:
                            running = False
                            
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = event.pos
                        
                        # Handle main menu clicks
                        if self.current_section == "main":
                            button_width = 250
                            button_height = 40
                            center_x = WINDOW_WIDTH // 2 - button_width // 2
                            
                            # Skill cards button
                            skill_rect = pygame.Rect(center_x, 300, button_width, button_height)
                            if skill_rect.collidepoint(mouse_pos):
                                self.current_section = "skill_cards"
                                
                            # Items button
                            items_rect = pygame.Rect(center_x, 350, button_width, button_height)
                            if items_rect.collidepoint(mouse_pos):
                                self.current_section = "items"
                                
                            # Equipment button
                            equip_rect = pygame.Rect(center_x, 400, button_width, button_height)
                            if equip_rect.collidepoint(mouse_pos):
                                self.current_section = "equipment"
                                
                            # Stats button
                            stats_rect = pygame.Rect(center_x, 450, button_width, button_height)
                            if stats_rect.collidepoint(mouse_pos):
                                self.current_section = "stats"
                                
                            # Enemy button
                            enemy_rect = pygame.Rect(center_x, 500, button_width, button_height)
                            if enemy_rect.collidepoint(mouse_pos):
                                self.current_section = "enemies"
                                
                            # Start fight button
                            if self.start_fight_button.collidepoint(mouse_pos):
                                can_start = len(self.selected_skill_cards) <= 5 and len(self.selected_items) <= 5
                                if can_start:
                                    winner = self.start_test_fight()
                                    print(f"Test fight ended. Winner: {winner.name if winner else 'None'}")
                        
                        # Handle skill cards selection
                        elif self.current_section == "skill_cards":
                            y_pos = 100
                            for i, card_name in enumerate(self.available_skill_cards):
                                if y_pos > WINDOW_HEIGHT - 100:
                                    break
                                    
                                rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 30)
                                if rect.collidepoint(mouse_pos):
                                    if card_name in self.selected_skill_cards:
                                        self.selected_skill_cards.remove(card_name)
                                    elif len(self.selected_skill_cards) < 5:
                                        self.selected_skill_cards.append(card_name)
                                    break
                                    
                                y_pos += 35
                            
                            # Back button
                            if self.back_button.collidepoint(mouse_pos):
                                self.current_section = "main"
                        
                        # Handle items selection
                        elif self.current_section == "items":
                            y_pos = 100
                            for i, item_name in enumerate(self.available_items):
                                if y_pos > WINDOW_HEIGHT - 100:
                                    break
                                    
                                rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 30)
                                if rect.collidepoint(mouse_pos):
                                    if item_name in self.selected_items:
                                        self.selected_items.remove(item_name)
                                    elif len(self.selected_items) < 5:
                                        self.selected_items.append(item_name)
                                    break
                                    
                                y_pos += 35
                            
                            # Back button
                            if self.back_button.collidepoint(mouse_pos):
                                self.current_section = "main"
                        
                        # Handle equipment selection
                        elif self.current_section == "equipment":
                            y_pos = 100
                            for i, equip_name in enumerate(self.available_equipment):
                                if y_pos > WINDOW_HEIGHT - 100:
                                    break
                                    
                                rect = pygame.Rect(50, y_pos, WINDOW_WIDTH - 100, 30)
                                if rect.collidepoint(mouse_pos):
                                    if equip_name in self.selected_equipment:
                                        self.selected_equipment.remove(equip_name)
                                    else:
                                        self.selected_equipment.append(equip_name)
                                    break
                                    
                                y_pos += 35
                            
                            # Back button
                            if self.back_button.collidepoint(mouse_pos):
                                self.current_section = "main"
                        
                        # Handle stats configuration
                        elif self.current_section == "stats":
                            button_width = 40
                            button_height = 30
                            
                            # Player HP buttons
                            dec_player_rect = pygame.Rect(300, 100, button_width, button_height)
                            inc_player_rect = pygame.Rect(350, 100, button_width, button_height)
                            
                            if dec_player_rect.collidepoint(mouse_pos) and self.player_starting_hp > 1:
                                self.player_starting_hp -= 1
                            elif inc_player_rect.collidepoint(mouse_pos) and self.player_starting_hp < 20:
                                self.player_starting_hp += 1
                            else:
                                # AI HP buttons
                                dec_ai_rect = pygame.Rect(300, 150, button_width, button_height)
                                inc_ai_rect = pygame.Rect(350, 150, button_width, button_height)
                                
                                if dec_ai_rect.collidepoint(mouse_pos) and self.ai_starting_hp > 1:
                                    self.ai_starting_hp -= 1
                                elif inc_ai_rect.collidepoint(mouse_pos) and self.ai_starting_hp < 20:
                                    self.ai_starting_hp += 1
                                elif self.back_button.collidepoint(mouse_pos):
                                    self.current_section = "main"
                        
                        # Handle enemy selection
                        elif self.current_section == "enemies":
                            button_width = 200
                            button_height = 40
                            center_x = WINDOW_WIDTH // 2 - button_width // 2
                            
                            # Calculate positions dynamically (same as draw method)
                            y_pos = 120
                            
                            # Regular enemies button
                            regular_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
                            if regular_rect.collidepoint(mouse_pos):
                                self.enemy_type = EnemyType.REGULAR
                                self.enemy_name = None
                            y_pos += 50
                            
                            # Regular enemy sub-buttons
                            if self.enemy_type == EnemyType.REGULAR:
                                for enemy_name in REGULAR_ENEMIES.keys():
                                    enemy_rect = pygame.Rect(center_x + 20, y_pos, button_width - 40, 30)
                                    if enemy_rect.collidepoint(mouse_pos):
                                        self.enemy_name = enemy_name
                                    y_pos += 35
                            
                            # Elite enemies button
                            elite_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
                            if elite_rect.collidepoint(mouse_pos):
                                self.enemy_type = EnemyType.ELITE
                                self.enemy_name = None
                            y_pos += 50
                            
                            # Elite enemy sub-buttons
                            if self.enemy_type == EnemyType.ELITE:
                                for enemy_name in ELITE_ENEMIES.keys():
                                    enemy_rect = pygame.Rect(center_x + 20, y_pos, button_width - 40, 30)
                                    if enemy_rect.collidepoint(mouse_pos):
                                        self.enemy_name = enemy_name
                                    y_pos += 35
                            
                            # Boss enemies button
                            boss_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
                            if boss_rect.collidepoint(mouse_pos):
                                self.enemy_type = EnemyType.BOSS
                                self.enemy_name = None
                            y_pos += 50
                            
                            # Boss enemy sub-buttons
                            if self.enemy_type == EnemyType.BOSS:
                                for enemy_name in BOSS_ENEMIES.keys():
                                    enemy_rect = pygame.Rect(center_x + 20, y_pos, button_width - 40, 30)
                                    if enemy_rect.collidepoint(mouse_pos):
                                        self.enemy_name = enemy_name
                                    y_pos += 35
                            
                            # Back button
                            if self.back_button.collidepoint(mouse_pos):
                                self.current_section = "main"
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        
    def draw_enemy_selection(self):
        """Draw enemy selection screen"""
        self.screen.fill(BG_COLOR)
        
        # Title
        title = self.font.render("Select Enemy Type", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Current selection
        current_text = f"Current: {self.enemy_type.value.title()}"
        if self.enemy_name:
            current_text += f" - {self.enemy_name}"
        current_surface = self.font.render(current_text, True, TEXT_COLOR)
        self.screen.blit(current_surface, (50, 80))
        
        # Enemy type buttons
        y_pos = 120
        button_width = 200
        button_height = 40
        center_x = WINDOW_WIDTH // 2 - button_width // 2
        mouse_pos = pygame.mouse.get_pos()
        
        # Regular enemies
        regular_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        regular_selected = self.enemy_type == EnemyType.REGULAR
        self.draw_button(regular_rect, "Regular Enemies", 
                        regular_rect.collidepoint(mouse_pos) or regular_selected)
        y_pos += 50
        
        if regular_selected:
            for enemy_name in REGULAR_ENEMIES.keys():
                enemy_rect = pygame.Rect(center_x + 20, y_pos, button_width - 40, 30)
                selected = self.enemy_name == enemy_name
                self.draw_button(enemy_rect, enemy_name, 
                               enemy_rect.collidepoint(mouse_pos) or selected)
                y_pos += 35
        
        # Elite enemies  
        elite_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        elite_selected = self.enemy_type == EnemyType.ELITE
        self.draw_button(elite_rect, "Elite Enemies", 
                        elite_rect.collidepoint(mouse_pos) or elite_selected)
        y_pos += 50
        
        if elite_selected:
            for enemy_name in ELITE_ENEMIES.keys():
                enemy_rect = pygame.Rect(center_x + 20, y_pos, button_width - 40, 30)
                selected = self.enemy_name == enemy_name
                self.draw_button(enemy_rect, enemy_name, 
                               enemy_rect.collidepoint(mouse_pos) or selected)
                y_pos += 35
        
        # Boss enemies
        boss_rect = pygame.Rect(center_x, y_pos, button_width, button_height)
        boss_selected = self.enemy_type == EnemyType.BOSS
        self.draw_button(boss_rect, "Boss Enemies", 
                        boss_rect.collidepoint(mouse_pos) or boss_selected)
        y_pos += 50
        
        if boss_selected:
            for enemy_name in BOSS_ENEMIES.keys():
                enemy_rect = pygame.Rect(center_x + 20, y_pos, button_width - 40, 30)
                selected = self.enemy_name == enemy_name
                self.draw_button(enemy_rect, enemy_name, 
                               enemy_rect.collidepoint(mouse_pos) or selected)
                y_pos += 35
        
        # Back button
        self.draw_button(self.back_button, "Back", self.back_button.collidepoint(mouse_pos))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PDK Rogue - Test Fight")
    
    config = TestFightConfig(screen)
    config.run() 