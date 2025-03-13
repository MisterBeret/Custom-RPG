"""
Battle UI handling for the RPG game.
Manages drawing the battle interface, menus, and interactive elements.
"""
import pygame
from constants import (
    BLACK, WHITE, GREEN, RED, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT,
    BATTLE_OPTIONS, MAX_LOG_SIZE, ORIGINAL_WIDTH, ORIGINAL_HEIGHT,
    ORANGE, BLUE, DARK_BLUE, PURPLE, YELLOW
)
from systems.battle.targeting_system import TargetingSystem
from utils.utils import scale_position, scale_dimensions, scale_font_size
from entities.player import Player

class BattleUI:
    """
    Handles drawing and interaction with battle UI elements.
    """
    def __init__(self, battle_system):
        """
        Initialize the battle UI handler.
        
        Args:
            battle_system: The parent battle system
        """
        self.battle_system = battle_system
        
        # Message display state
        self.full_message = battle_system.first_message
        self.displayed_message = ""
        self.message_index = 0
        self.text_timer = 0
        self.message_log = [battle_system.first_message]
        self.max_log_size = MAX_LOG_SIZE
        
        # Menu state
        self.in_targeting_mode = False
        self.in_spell_menu = False
        self.in_skill_menu = False
        self.in_ultimate_menu = False
        
        # Menu selection state
        self.selected_option = 0
        self.selected_spell_option = 0
        self.selected_skill_option = 0
        self.selected_ultimate_option = 0
        
        # Create targeting system
        self.targeting_system = TargetingSystem(battle_system.party, battle_system.enemies)
        
        # Passive message tracking
        self.pending_passive_message = ""
        self.has_pending_passive = False
    
    def set_message(self, message):
        """
        Set a new battle message and reset text animation.
        
        Args:
            message: The message to display
        """
        self.full_message = message
        self.displayed_message = ""
        self.message_index = 0
        self.text_timer = 0
        
        # Always add message to log, even if it's the same as a previous one
        self.message_log.append(message)
        # Keep only the most recent messages
        if len(self.message_log) > self.max_log_size:
            self.message_log.pop(0)
    
    def store_passive_message(self, message):
        """
        Store a passive ability message to be displayed later.
        
        Args:
            message: The passive ability message
        """
        self.pending_passive_message = message
        self.has_pending_passive = True
    
    def display_passive_message(self):
        """Display a pending passive message."""
        if self.has_pending_passive:
            self.set_message(self.pending_passive_message)
            self.has_pending_passive = False
            self.pending_passive_message = ""
    
    def update_text_animation(self):
        """Update the text scrolling animation."""
        # Only update text if we haven't displayed the full message yet
        if self.message_index < len(self.full_message):
            self.text_timer += self.battle_system.text_speed
            
            # Add characters one at a time but at a rate determined by text_speed
            # This creates smoother scrolling while maintaining the same overall speed
            while self.text_timer >= 4 and self.message_index < len(self.full_message):
                self.text_timer -= 4
                self.displayed_message += self.full_message[self.message_index]
                self.message_index += 1
                
    def is_text_complete(self):
        """
        Check if the current message text is fully displayed.
        
        Returns:
            bool: True if message is fully displayed
        """
        return self.message_index >= len(self.full_message)
    
    def complete_text(self):
        """Force text to complete immediately."""
        self.displayed_message = self.full_message
        self.message_index = len(self.full_message)
    
    def draw(self, screen):
        """
        Draw all battle UI elements.
        
        Args:
            screen: The pygame surface to draw on
        """
        self.draw_background(screen)
        self.draw_combatants(screen)
        self.draw_battle_ui(screen)
        
        # Draw targeting system if active
        if self.in_targeting_mode:
            self.targeting_system.draw(screen)
    
    def draw_background(self, screen):
        """
        Draw the battle background.
        
        Args:
            screen: The pygame surface to draw on
        """
        from systems.battle.battle_visualizer import draw_battle_background
        draw_battle_background(screen)
    
    def draw_combatants(self, screen):
        """
        Draw all battle participants (party members and enemies).
        
        Args:
            screen: The pygame surface to draw on
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Get animation state for character movements
        animations = self.battle_system.animations
        
        # Draw all party members
        for character in self.battle_system.party.active_members:
            if not character.is_defeated():
                # Calculate animation offsets
                offset_x = 0
                offset_y = 0
                
                if animations.character_attacking and character == animations.active_character:
                    # Move character toward enemy during attack
                    if animations.animation_timer < animations.animation_duration / 2:
                        # Move toward target
                        if hasattr(animations.target, 'battle_pos_x'):
                            # Direction vector
                            dx = animations.target.battle_pos_x - character.battle_pos_x
                            move_dist = int(30 * (current_width / ORIGINAL_WIDTH))
                            # Move in the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                        (animations.animation_timer / (animations.animation_duration / 2)))
                    else:
                        # Move back to position
                        if hasattr(animations.target, 'battle_pos_x'):
                            dx = animations.target.battle_pos_x - character.battle_pos_x
                            move_dist = int(30 * (current_width / ORIGINAL_WIDTH))
                            # Return from the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                        (1 - (animations.animation_timer - animations.animation_duration / 2) / 
                                        (animations.animation_duration / 2)))
                
                # Draw character with offset
                pygame.draw.rect(screen, character.color,
                                (character.rect.x + offset_x,
                                character.rect.y + offset_y,
                                character.rect.width,
                                character.rect.height))
                                
                # Draw character name above them
                name_font = pygame.font.SysFont('Arial', 14)
                name_text = name_font.render(character.name, True, WHITE)
                name_x = character.rect.centerx - name_text.get_width() // 2
                name_y = character.rect.top - name_text.get_height() - 5
                screen.blit(name_text, (name_x, name_y))
        
        # Draw all enemies
        for enemy in self.battle_system.enemies:
            if not enemy.is_defeated():
                # Calculate animation offsets
                offset_x = 0
                offset_y = 0
                
                if animations.enemy_attacking and enemy == animations.current_enemy:
                    # Move enemy toward character during attack
                    if animations.animation_timer < animations.animation_duration / 2:
                        # Move toward target
                        if hasattr(animations.target, 'battle_pos_x'):
                            # Direction vector
                            dx = animations.target.battle_pos_x - enemy.battle_pos_x
                            move_dist = int(30 * (current_width / ORIGINAL_WIDTH))
                            # Move in the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                        (animations.animation_timer / (animations.animation_duration / 2)))
                    else:
                        # Move back to position
                        if hasattr(animations.target, 'battle_pos_x'):
                            dx = animations.target.battle_pos_x - enemy.battle_pos_x
                            move_dist = int(30 * (current_width / ORIGINAL_WIDTH))
                            # Return from the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                        (1 - (animations.animation_timer - animations.animation_duration / 2) / 
                                        (animations.animation_duration / 2)))
                
                # Draw enemy with offset
                pygame.draw.rect(screen, enemy.color,
                                (enemy.rect.x + offset_x,
                                enemy.rect.y + offset_y,
                                enemy.rect.width,
                                enemy.rect.height))
        
        # Draw enemy names and health bars
        from systems.battle.battle_ui_helpers import draw_enemy_name_tags, draw_enemy_health_bars
        draw_enemy_name_tags(screen, self.battle_system.enemies)
        draw_enemy_health_bars(screen, self.battle_system.enemies)
        
        # Draw turn order indicator
        from systems.battle.battle_ui_party import draw_party_status, draw_turn_order_indicator
        
        # Create fonts for status display
        font_size = scale_font_size(24, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        small_font_size = scale_font_size(16, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        font = pygame.font.SysFont('Arial', font_size)
        small_font = pygame.font.SysFont('Arial', small_font_size)
        
        # Draw turn indicator and party status
        draw_turn_order_indicator(screen, self.battle_system)
        draw_party_status(screen, self.battle_system.party, self.battle_system.turn_order, font, small_font)
    
    def draw_battle_ui(self, screen):
        """
        Draw the battle UI elements.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Scale font sizes
        font_size = scale_font_size(24, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        small_font_size = scale_font_size(18, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        
        # Create the scaled fonts
        font = pygame.font.SysFont('Arial', font_size)
        small_font = pygame.font.SysFont('Arial', small_font_size)
        
        # Draw battle message log
        self._draw_message_log(screen, font)
        
        # Get animation state
        animations = self.battle_system.animations
        
        # Draw battle options or special menus
        current_character = self.battle_system.get_current_character()
        
        if (current_character and not self.battle_system.battle_over and 
            not animations.character_attacking and not animations.enemy_attacking and 
            not animations.character_fleeing and not animations.character_casting and 
            not animations.character_using_skill and not animations.character_using_ultimate and 
            animations.action_delay == 0):
            
            # Only display UI when the text is fully displayed AND not currently processing an action
            if self.is_text_complete() and not self.battle_system.actions.action_processing:
                if self.in_spell_menu:
                    self._draw_spell_menu(screen, font, small_font, current_character)
                elif self.in_skill_menu:
                    self._draw_skill_menu(screen, font, small_font, current_character)
                elif self.in_ultimate_menu:
                    self._draw_ultimate_menu(screen, font, small_font, current_character)
                else:
                    self._draw_battle_options(screen, font, current_character)
        
        # Display continue message if battle is over
        if self.battle_system.battle_over:
            # Only display the continue message when the text is fully displayed
            if self.is_text_complete():
                continue_text = font.render("Press ENTER to continue", True, WHITE)
                continue_x = (current_width // 2) - (continue_text.get_width() // 2)
                continue_y = int(500 * (current_height / ORIGINAL_HEIGHT))
                screen.blit(continue_text, (continue_x, continue_y))
    
    def _draw_message_log(self, screen, font):
        """
        Draw the battle message log.
        
        Args:
            screen: The pygame surface to draw on
            font: The font to use for messages
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Scale message box dimensions and position
        message_box_width = int(600 * (current_width / ORIGINAL_WIDTH))
        message_box_height = int((30 * len(self.message_log) + 20) * (current_height / ORIGINAL_HEIGHT))
        message_box_x = (current_width // 2) - (message_box_width // 2)
        message_box_y = int(70 * (current_height / ORIGINAL_HEIGHT))
        
        # Draw message box
        message_box_rect = pygame.Rect(
            message_box_x, 
            message_box_y, 
            message_box_width, 
            message_box_height
        )
        pygame.draw.rect(screen, (0, 0, 0, 200), message_box_rect)
        pygame.draw.rect(screen, WHITE, message_box_rect, max(1, int(2 * (current_width / ORIGINAL_WIDTH))))
        
        # Scale text positions
        message_x = message_box_x + int(10 * (current_width / ORIGINAL_WIDTH))
        message_y_base = message_box_y + int(10 * (current_height / ORIGINAL_HEIGHT))
        message_line_height = int(30 * (current_height / ORIGINAL_HEIGHT))
        
        # Draw all messages in the log
        for i, message in enumerate(self.message_log):
            # Calculate y position for this message
            message_y = message_y_base + i * message_line_height
            
            # Only the newest message scrolls, others are shown in full
            if i == len(self.message_log) - 1 and message == self.full_message:
                message_text = font.render(self.displayed_message, True, WHITE)
                screen.blit(message_text, (message_x, message_y))
                
                # Draw "..." when text is still being displayed
                if self.message_index < len(self.full_message):
                    typing_indicator = font.render("...", True, WHITE)
                    typing_x = message_box_x + message_box_width - typing_indicator.get_width() - int(10 * (current_width / ORIGINAL_WIDTH))
                    screen.blit(typing_indicator, (typing_x, message_y))
            else:
                message_text = font.render(message, True, GRAY)  # Older messages in gray
                screen.blit(message_text, (message_x, message_y))
    
    def _draw_battle_options(self, screen, font, character):
        """
        Draw the main battle options menu in a two-column layout.
        
        Args:
            screen: The pygame surface to draw on
            font: The font to use
            character: The current character whose turn it is
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Scale dimensions and position
        options_box_width, options_box_height = scale_dimensions(
            300, 160, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        options_box_x, options_box_y = scale_position(
            20, SCREEN_HEIGHT - 160 - 5, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, (0, 0, 0, 200), (options_box_x, options_box_y, options_box_width, options_box_height))
        border_width = max(1, int(2 * (current_width / ORIGINAL_WIDTH)))
        pygame.draw.rect(screen, WHITE, (options_box_x, options_box_y, options_box_width, options_box_height), border_width)
        
        # Draw character name
        char_text = font.render(f"{character.name}'s Turn", True, GREEN)
        header_x = options_box_x + (options_box_width // 2) - (char_text.get_width() // 2)
        header_y = options_box_y + int(10 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(char_text, (header_x, header_y))
        
        # Scale text positions
        left_column_x = options_box_x + int(30 * (current_width / ORIGINAL_WIDTH))
        right_column_x = options_box_x + int(160 * (current_width / ORIGINAL_WIDTH))
        option_y_base = options_box_y + int(40 * (current_height / ORIGINAL_HEIGHT))
        option_line_height = int(25 * (current_height / ORIGINAL_HEIGHT))
        
        # Draw battle options in two columns
        # Left column (first 4 options)
        for i in range(4):
            option_y = option_y_base + i * option_line_height
            option = BATTLE_OPTIONS[i]
            
            if i == self.selected_option:
                # Highlight selected option
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (left_column_x, option_y))
        
        # Right column (next 4 options)
        for i in range(4, 8):
            option_y = option_y_base + (i - 4) * option_line_height
            option = BATTLE_OPTIONS[i]
            
            if i == self.selected_option:
                # Highlight selected option
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (right_column_x, option_y))
    
    def _draw_spell_menu(self, screen, font, small_font, character):
        """
        Draw the spell selection menu.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
            character: The character casting spells
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Scale menu dimensions and position
        spell_box_width, spell_box_height = scale_dimensions(
            250, 200, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        spell_box_x, spell_box_y = scale_position(
            20, SCREEN_HEIGHT - 200 - 5, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, (0, 0, 0, 200), (spell_box_x, spell_box_y, spell_box_width, spell_box_height))
        border_width = max(1, int(2 * (current_width / ORIGINAL_WIDTH)))
        pygame.draw.rect(screen, PURPLE, (spell_box_x, spell_box_y, spell_box_width, spell_box_height), border_width)
        
        # Draw "Magic" header
        magic_text = font.render(f"{character.name}'s Magic", True, PURPLE)
        header_x = spell_box_x + (spell_box_width // 2) - (magic_text.get_width() // 2)
        header_y = spell_box_y + int(10 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(magic_text, (header_x, header_y))
        
        # Get spell list from character's spellbook
        spell_names = character.spellbook.get_spell_names()
        # Add "BACK" option at the end
        options = spell_names + ["BACK"]
        
        # Scale text positions
        option_x = spell_box_x + int(30 * (current_width / ORIGINAL_WIDTH))
        option_y_base = spell_box_y + int(40 * (current_height / ORIGINAL_HEIGHT))
        option_line_height = int(25 * (current_height / ORIGINAL_HEIGHT))
        sp_cost_x = spell_box_x + int(150 * (current_width / ORIGINAL_WIDTH))
        
        # Draw each spell with SP cost
        for i, spell_name in enumerate(options):
            option_y = option_y_base + i * option_line_height
            
            if spell_name == "BACK":
                # Draw BACK option
                if i == self.selected_spell_option:
                    option_text = font.render(f"> {spell_name}", True, WHITE)
                else:
                    option_text = font.render(f"  {spell_name}", True, GRAY)
                screen.blit(option_text, (option_x, option_y))
            else:
                # Get the spell data
                spell = character.spellbook.get_spell(spell_name)
                
                # Determine text color based on whether character has enough SP
                has_sp = character.sp >= spell.sp_cost
                
                if i == self.selected_spell_option:
                    # Selected spell
                    if has_sp:
                        name_color = WHITE  # Can cast
                    else:
                        name_color = RED    # Can't cast (not enough SP)
                    option_text = font.render(f"> {spell_name}", True, name_color)
                else:
                    # Unselected spell
                    if has_sp:
                        name_color = GRAY   # Can cast
                    else:
                        name_color = RED    # Can't cast (not enough SP)
                    option_text = font.render(f"  {spell_name}", True, name_color)
                
                # Draw spell name
                screen.blit(option_text, (option_x, option_y))
                
                # Draw SP cost
                sp_text = small_font.render(f"{spell.sp_cost} SP", True, BLUE)
                screen.blit(sp_text, (sp_cost_x, option_y))
        
        # Draw spell description for selected spell
        if self.selected_spell_option < len(spell_names):
            spell = character.spellbook.get_spell(options[self.selected_spell_option])
            if spell:
                desc_y = option_y_base + len(options) * option_line_height + int(10 * (current_height / ORIGINAL_HEIGHT))
                desc_text = small_font.render(spell.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))
    
    def _draw_skill_menu(self, screen, font, small_font, character):
        """
        Draw the skill selection menu.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
            character: The character using skills
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Scale menu dimensions and position
        skill_box_width, skill_box_height = scale_dimensions(
            250, 200, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        skill_box_x, skill_box_y = scale_position(
            20, SCREEN_HEIGHT - 200 - 5, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, (0, 0, 0, 200), (skill_box_x, skill_box_y, skill_box_width, skill_box_height))
        border_width = max(1, int(2 * (current_width / ORIGINAL_WIDTH)))
        pygame.draw.rect(screen, YELLOW, (skill_box_x, skill_box_y, skill_box_width, skill_box_height), border_width)
        
        # Draw "Skills" header
        skills_text = font.render(f"{character.name}'s Skills", True, YELLOW)
        header_x = skill_box_x + (skill_box_width // 2) - (skills_text.get_width() // 2)
        header_y = skill_box_y + int(10 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(skills_text, (header_x, header_y))
        
        # Get skill list from character's skillset
        skill_names = character.skillset.get_skill_names()
        # Add "BACK" option at the end
        options = skill_names + ["BACK"]
        
        # Scale text positions
        option_x = skill_box_x + int(30 * (current_width / ORIGINAL_WIDTH))
        option_y_base = skill_box_y + int(40 * (current_height / ORIGINAL_HEIGHT))
        option_line_height = int(25 * (current_height / ORIGINAL_HEIGHT))
        cost_x = skill_box_x + int(150 * (current_width / ORIGINAL_WIDTH))
        
        # Draw each skill with cost
        for i, skill_name in enumerate(options):
            option_y = option_y_base + i * option_line_height
            
            if skill_name == "BACK":
                # Draw BACK option
                if i == self.selected_skill_option:
                    option_text = font.render(f"> {skill_name}", True, WHITE)
                else:
                    option_text = font.render(f"  {skill_name}", True, GRAY)
                screen.blit(option_text, (option_x, option_y))
            else:
                # Get the skill data
                skill = character.skillset.get_skill(skill_name)
                
                # Determine text color based on whether character has enough resources
                has_resources = True
                if skill.cost_type == "sp" and character.sp < skill.sp_cost:
                    has_resources = False
                elif skill.cost_type == "hp" and character.hp <= skill.hp_cost:
                    has_resources = False
                elif skill.cost_type == "both" and (character.sp < skill.sp_cost or character.hp <= skill.hp_cost):
                    has_resources = False
                
                if i == self.selected_skill_option:
                    # Selected skill
                    if has_resources:
                        name_color = WHITE  # Can use
                    else:
                        name_color = RED    # Can't use (not enough resources)
                    option_text = font.render(f"> {skill_name}", True, name_color)
                else:
                    # Unselected skill
                    if has_resources:
                        name_color = GRAY   # Can use
                    else:
                        name_color = RED    # Can't use (not enough resources)
                    option_text = font.render(f"  {skill_name}", True, name_color)
                
                # Draw skill name
                screen.blit(option_text, (option_x, option_y))
                
                # Draw cost if applicable
                if skill.cost_type != "none":
                    if skill.cost_type == "sp":
                        cost_text = small_font.render(f"{skill.sp_cost} SP", True, BLUE)
                    elif skill.cost_type == "hp":
                        cost_text = small_font.render(f"{skill.hp_cost} HP", True, ORANGE)
                    elif skill.cost_type == "both":
                        cost_text = small_font.render(f"{skill.hp_cost}HP/{skill.sp_cost}SP", True, PURPLE)
                    screen.blit(cost_text, (cost_x, option_y))
        
        # Draw skill description for selected skill
        if self.selected_skill_option < len(skill_names):
            skill = character.skillset.get_skill(options[self.selected_skill_option])
            if skill:
                desc_y = option_y_base + len(options) * option_line_height + int(10 * (current_height / ORIGINAL_HEIGHT))
                desc_text = small_font.render(skill.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))

    def _draw_ultimate_menu(self, screen, font, small_font, character):
        """
        Draw the ultimate ability selection menu.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
            character: The character using ultimates
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Scale menu dimensions and position
        ultimate_box_width, ultimate_box_height = scale_dimensions(
            250, 200, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        ultimate_box_x, ultimate_box_y = scale_position(
            20, SCREEN_HEIGHT - 200 - 5, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, (0, 0, 0, 200), (ultimate_box_x, ultimate_box_y, ultimate_box_width, ultimate_box_height))
        border_width = max(1, int(2 * (current_width / ORIGINAL_WIDTH)))
        pygame.draw.rect(screen, RED, (ultimate_box_x, ultimate_box_y, ultimate_box_width, ultimate_box_height), border_width)
        
        # Draw "Ultimate" header
        ultimate_text = font.render(f"{character.name}'s Ultimates", True, RED)
        header_x = ultimate_box_x + (ultimate_box_width // 2) - (ultimate_text.get_width() // 2)
        header_y = ultimate_box_y + int(10 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(ultimate_text, (header_x, header_y))
        
        # Get ultimate list from character's ultimates
        ultimate_names = character.ultimates.get_ultimate_names()
        # Add "BACK" option at the end
        options = ultimate_names + ["BACK"]
        
        # Scale text positions
        option_x = ultimate_box_x + int(30 * (current_width / ORIGINAL_WIDTH))
        option_y_base = ultimate_box_y + int(40 * (current_height / ORIGINAL_HEIGHT))
        option_line_height = int(25 * (current_height / ORIGINAL_HEIGHT))
        status_x = ultimate_box_x + int(150 * (current_width / ORIGINAL_WIDTH))
        
        # Draw each ultimate with availability status
        for i, ultimate_name in enumerate(options):
            option_y = option_y_base + i * option_line_height
            
            if ultimate_name == "BACK":
                # Draw BACK option
                if i == self.selected_ultimate_option:
                    option_text = font.render(f"> {ultimate_name}", True, WHITE)
                else:
                    option_text = font.render(f"  {ultimate_name}", True, GRAY)
                screen.blit(option_text, (option_x, option_y))
            else:
                # Get the ultimate data
                ultimate = character.ultimates.get_ultimate(ultimate_name)
                
                # Determine text color based on whether ultimate is available
                is_available = ultimate.available
                
                if i == self.selected_ultimate_option:
                    # Selected ultimate
                    if is_available:
                        name_color = WHITE  # Can use
                    else:
                        name_color = RED    # Can't use (already used)
                    option_text = font.render(f"> {ultimate_name}", True, name_color)
                else:
                    # Unselected ultimate
                    if is_available:
                        name_color = GRAY   # Can use
                    else:
                        name_color = RED    # Can't use (already used)
                    option_text = font.render(f"  {ultimate_name}", True, name_color)
                
                # Draw ultimate name
                screen.blit(option_text, (option_x, option_y))
                
                # Draw availability status
                status_text = small_font.render("READY" if is_available else "USED", True, 
                                            GREEN if is_available else RED)
                screen.blit(status_text, (status_x, option_y))
        
        # Draw ultimate description for selected ultimate
        if self.selected_ultimate_option < len(ultimate_names):
            ultimate = character.ultimates.get_ultimate(options[self.selected_ultimate_option])
            if ultimate:
                desc_y = option_y_base + len(options) * option_line_height + int(10 * (current_height / ORIGINAL_HEIGHT))
                desc_text = small_font.render(ultimate.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))

    def handle_targeting_input(self, event):
        """
        Handle input when in targeting mode.
        
        Args:
            event: The pygame event to process
            
        Returns:
            bool: True if input was handled, False otherwise
        """
        if not self.in_targeting_mode or event.type != pygame.KEYDOWN:
            return False
            
        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            # Navigate between targets
            if event.key == pygame.K_LEFT:
                self.targeting_system.previous_target()
            else:
                self.targeting_system.next_target()
            return True
            
        elif event.key == pygame.K_TAB:
            # Switch between targeting enemies and allies
            self.targeting_system.switch_target_group()
            
            # Update message based on target group
            character = self.battle_system.animations.active_character
            if self.targeting_system.target_group == self.targeting_system.ENEMIES:  
                self.battle_system.set_message(f"{character.name} is targeting an enemy")
            else:
                self.battle_system.set_message(f"{character.name} is targeting an ally")
            return True
            
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Select the current target
            target = self.targeting_system.get_selected_target()
            if target:
                # Process the action based on current menu state
                actions = self.battle_system.actions
                
                if self.in_spell_menu and actions.current_spell:
                    # Cast spell on target
                    actions.cast_spell(actions.active_character, target, actions.current_spell)
                    self.in_spell_menu = False
                elif self.in_skill_menu and actions.current_skill:
                    # Use skill on target
                    actions.use_skill(actions.active_character, target, actions.current_skill)
                    self.in_skill_menu = False
                elif self.in_ultimate_menu and actions.current_ultimate:
                    # Use ultimate on target
                    actions.use_ultimate(actions.active_character, target, actions.current_ultimate)
                    self.in_ultimate_menu = False
                else:
                    # Regular attack
                    actions.perform_attack(actions.active_character, target)
                
                # Disable targeting mode
                self.in_targeting_mode = False
                self.targeting_system.stop_targeting()
            return True
            
        elif event.key == pygame.K_ESCAPE:
            # Cancel targeting and return to battle menu
            self.in_targeting_mode = False
            self.targeting_system.stop_targeting()
            self.battle_system.actions.action_processing = False  # Reset to allow new actions
            
            # Reset any special menu states
            self.in_spell_menu = False
            self.in_skill_menu = False
            self.in_ultimate_menu = False
            
            # Restore the previous message from log
            if len(self.message_log) > 0:
                self.full_message = self.message_log[-1]
                self.displayed_message = self.full_message
                self.message_index = len(self.full_message)
            return True
            
        return False

    def handle_menu_navigation(self, event, character):
        """
        Handle navigation in the various battle menus.
        
        Args:
            event: The pygame event to process
            character: The active character
            
        Returns:
            bool: True if input was handled, False otherwise
        """
        if event.type != pygame.KEYDOWN:
            return False
            
        # Handle spell menu navigation
        if self.in_spell_menu:
            spell_options = character.spellbook.get_spell_names() + ["BACK"]
            
            if event.key == pygame.K_UP:
                self.selected_spell_option = (self.selected_spell_option - 1) % len(spell_options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_spell_option = (self.selected_spell_option + 1) % len(spell_options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_spell = spell_options[self.selected_spell_option]
                
                if selected_spell == "BACK":
                    # Return to main battle menu
                    self.in_spell_menu = False
                    self.battle_system.actions.action_processing = False
                else:
                    # Try to cast the spell
                    spell = character.spellbook.get_spell(selected_spell)
                    
                    # Check if player has enough SP
                    if character.sp < spell.sp_cost:
                        self.battle_system.set_message(f"Not enough SP to cast {selected_spell}!")
                        return True
                    
                    # Determine if this spell needs a target
                    if spell.effect_type == "damage":
                        # Enter targeting mode
                        self.in_targeting_mode = True
                        self.targeting_system.start_targeting(
                            character, self.targeting_system.ENEMIES
                        )
                        self.battle_system.actions.current_spell = spell
                        self.battle_system.set_message(f"Select a target for {spell.name}")
                    elif spell.effect_type == "healing":
                        # Enter targeting mode for allies
                        self.in_targeting_mode = True
                        self.targeting_system.start_targeting(
                            character, self.targeting_system.ALLIES
                        )
                        self.battle_system.actions.current_spell = spell
                        self.battle_system.set_message(f"Select a target for {spell.name}")
                    else:
                        # Non-targeted spell
                        self.battle_system.actions.cast_spell(character, character, spell)  # Self-target
                        self.in_spell_menu = False
                return True
            elif event.key == pygame.K_ESCAPE:
                # Exit spell menu
                self.in_spell_menu = False
                self.battle_system.actions.action_processing = False
                return True
        
        # Handle skill menu navigation
        elif self.in_skill_menu:
            skill_options = character.skillset.get_skill_names() + ["BACK"]
            
            if event.key == pygame.K_UP:
                self.selected_skill_option = (self.selected_skill_option - 1) % len(skill_options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_skill_option = (self.selected_skill_option + 1) % len(skill_options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_skill = skill_options[self.selected_skill_option]
                
                if selected_skill == "BACK":
                    # Return to main battle menu
                    self.in_skill_menu = False
                    self.battle_system.actions.action_processing = False
                else:
                    # Similar logic to spell menu for the rest of skill handling
                    # ...
                    pass
                return True
        
        # Handle ultimate menu navigation
        elif self.in_ultimate_menu:
            ultimate_options = character.ultimates.get_ultimate_names() + ["BACK"]
            
            if event.key == pygame.K_UP:
                self.selected_ultimate_option = (self.selected_ultimate_option - 1) % len(ultimate_options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_ultimate_option = (self.selected_ultimate_option + 1) % len(ultimate_options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_ultimate = ultimate_options[self.selected_ultimate_option]
                
                if selected_ultimate == "BACK":
                    # Return to main battle menu
                    self.in_ultimate_menu = False
                    self.battle_system.actions.action_processing = False
                else:
                    # Similar logic to spell menu for the rest of ultimate handling
                    # ...
                    pass
                return True
        
        # Handle main battle menu navigation
        else:
            # Only handle if it's the player's turn and no animation is active
            if not self.battle_system.is_player_turn():
                return False
                
            if self.battle_system.animations.character_attacking or \
                self.battle_system.animations.character_defending or \
                self.battle_system.animations.character_fleeing:
                return False
                
            # Only accept inputs when text is fully displayed
            if not self.is_text_complete():
                # If message is still scrolling, pressing any key will display it immediately
                self.complete_text()
                return True
                
            # Handle main battle menu navigation
            if event.key == pygame.K_UP:
                # Move up in the same column with wrap-around
                if self.selected_option >= 4:  # Right column
                    # Move up in right column (wrap to bottom if at top)
                    current_position = self.selected_option - 4
                    new_position = (current_position - 1) % 4
                    self.selected_option = 4 + new_position
                else:  # Left column
                    # Move up in left column (wrap to bottom if at top)
                    self.selected_option = (self.selected_option - 1) % 4
                return True
            elif event.key == pygame.K_DOWN:
                # Move down in the same column with wrap-around
                if self.selected_option >= 4:  # Right column
                    # Move down in right column
                    current_position = self.selected_option - 4
                    new_position = (current_position + 1) % 4
                    self.selected_option = 4 + new_position
                else:  # Left column
                    # Move down in left column
                    self.selected_option = (self.selected_option + 1) % 4
                return True
            elif event.key == pygame.K_LEFT:
                # Move to left column from right, or wrap around to right column from left
                if self.selected_option >= 4:  # Right column to left
                    self.selected_option -= 4
                else:  # Left column to right (wrap around)
                    self.selected_option += 4
                return True
            elif event.key == pygame.K_RIGHT:
                # Move to right column from left, or wrap around to left column from right
                if self.selected_option < 4:  # Left column to right
                    self.selected_option += 4
                else:  # Right column to left (wrap around)
                    self.selected_option -= 4
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_action = BATTLE_OPTIONS[self.selected_option]
                self.battle_system.actions.process_action(selected_action, character)
                return True
        
        return False