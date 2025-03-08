"""
Party management UI for the RPG game.
"""
import pygame
from constants import (BLACK, WHITE, GREEN, RED, GRAY, BLUE, YELLOW, PURPLE,
                      ORIGINAL_WIDTH, ORIGINAL_HEIGHT, DIALOGUE)
from utils import scale_position, scale_dimensions, scale_font_size
from systems.character_creator import CharacterCreator
from entities.player import Player

class PartyManagementUI:
    """
    Manages the UI for party management.
    """
    # UI States
    MAIN_MENU = 0
    CREATE_CHARACTER = 1
    EDIT_CHARACTER = 2
    VIEW_PARTY = 3
    MANAGE_PARTY = 4
    SELECT_CLASS = 5
    NAME_INPUT = 6
    SELECT_CHARACTER = 7  # For selecting characters from a list
    REMOVE_CHARACTER = 8  # For confirming character removal
    
    def __init__(self, party, character_creator):
        """
        Initialize the party management UI.
        
        Args:
            party: The player's party
            character_creator: CharacterCreator instance for creating/editing characters
        """
        self.party = party
        self.character_creator = character_creator
        self.current_state = self.MAIN_MENU
        self.selected_option = 0
        self.selected_character = None
        self.selected_class_id = None
        self.temp_name = ""
        self.name_input_active = False
        self.message = ""
        self.back_state = self.MAIN_MENU  # State to return to on back action
        
        # Define menu options for each state
        self.main_menu_options = [
            "Create Character",
            "View Party",
            "Manage Party",
            "Exit"
        ]
        
        self.view_party_options = ["Back"]
        self.manage_party_options = ["Change Leader", "Edit Character", "Remove Character", "Back"]
        
        # Available character classes
        self.class_options = ["commoner", "warrior", "mage"]
    
    def handle_input(self, event):
        """
        Handle input events for the party UI.
        
        Args:
            event: The pygame event
            
        Returns:
            bool: True if UI should be closed, False otherwise
        """
        if event.type == pygame.KEYDOWN:
            # Handle different states
            if self.current_state == self.MAIN_MENU:
                return self._handle_main_menu_input(event)
            elif self.current_state == self.CREATE_CHARACTER:
                return self._handle_create_character_input(event)
            elif self.current_state == self.EDIT_CHARACTER:
                return self._handle_edit_character_input(event)
            elif self.current_state == self.VIEW_PARTY:
                return self._handle_view_party_input(event)
            elif self.current_state == self.MANAGE_PARTY:
                return self._handle_manage_party_input(event)
            elif self.current_state == self.SELECT_CLASS:
                return self._handle_select_class_input(event)
            elif self.current_state == self.NAME_INPUT:
                return self._handle_name_input(event)
            elif self.current_state == self.SELECT_CHARACTER:
                return self._handle_select_character_input(event)
            elif self.current_state == self.REMOVE_CHARACTER:
                return self._handle_remove_character_input(event)
                
        return False
    
    def _handle_main_menu_input(self, event):
        """Handle input for the main menu state."""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.main_menu_options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.main_menu_options)
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Create Character
                self.current_state = self.CREATE_CHARACTER
                self.selected_option = 0
                self.selected_class_id = self.class_options[0]
                self.temp_name = "New Character"
                self.message = "Select a character class"
            elif self.selected_option == 1:  # View Party
                self.current_state = self.VIEW_PARTY
                self.selected_option = 0
                self.message = "Party Members"
            elif self.selected_option == 2:  # Manage Party
                self.current_state = self.MANAGE_PARTY
                self.selected_option = 0
                self.message = "Select a management option"
            elif self.selected_option == 3:  # Exit
                return True  # Signal to close the UI
        elif event.key == pygame.K_ESCAPE:
            return True  # Exit the UI
            
        return False
    
    def _handle_create_character_input(self, event):
        """Handle input for the create character state."""
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.MAIN_MENU
            self.selected_option = 0
            self.message = ""
        elif event.key == pygame.K_RETURN:
            # Switch to name input mode
            self.current_state = self.NAME_INPUT
            self.name_input_active = True
            self.back_state = self.CREATE_CHARACTER
            self.message = "Enter character name"
        elif event.key == pygame.K_LEFT:
            # Select previous class
            idx = self.class_options.index(self.selected_class_id)
            idx = (idx - 1) % len(self.class_options)
            self.selected_class_id = self.class_options[idx]
        elif event.key == pygame.K_RIGHT:
            # Select next class
            idx = self.class_options.index(self.selected_class_id)
            idx = (idx + 1) % len(self.class_options)
            self.selected_class_id = self.class_options[idx]
            
        return False
    
    def _handle_select_character_input(self, event):
        """Handle input for the character selection state."""
        members = self.party.get_all_members()
        
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.back_state
            self.selected_option = 0
            self.message = ""
        elif event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(members)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(members)
        elif event.key == pygame.K_RETURN:
            # Select the character
            if 0 <= self.selected_option < len(members):
                self.selected_character = members[self.selected_option]
                
                if self.back_state == self.EDIT_CHARACTER:
                    # Go to edit character screen
                    self.current_state = self.EDIT_CHARACTER
                    self.selected_option = 0
                    self.message = f"Editing {self.selected_character.name}"
                elif self.back_state == self.REMOVE_CHARACTER:
                    # Go to removal confirmation
                    self.current_state = self.REMOVE_CHARACTER
                    self.selected_option = 1  # Default to "No"
                    self.message = f"Remove {self.selected_character.name} from party?"
                elif self.back_state == self.MANAGE_PARTY:
                    # Change leader
                    if self.selected_character in self.party.active_members:
                        idx = self.party.active_members.index(self.selected_character)
                        if self.party.set_leader(idx):
                            self.message = f"{self.selected_character.name} is now the party leader!"
                        else:
                            self.message = "Failed to set new leader!"
                    else:
                        self.message = "Leader must be an active party member!"
                        
                    # Return to manage party screen
                    self.current_state = self.MANAGE_PARTY
                    self.selected_option = 0
            
        return False
        
    def _handle_remove_character_input(self, event):
        """Handle input for the character removal confirmation state."""
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.MANAGE_PARTY
            self.selected_option = 0
            self.message = ""
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            # Toggle between Yes/No
            self.selected_option = 1 - self.selected_option
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Yes
                # Remove the character
                if self.selected_character:
                    if self.party.remove_member(self.selected_character):
                        self.message = f"{self.selected_character.name} removed from party!"
                    else:
                        self.message = "Failed to remove character!"
                
            # Return to manage party screen
            self.current_state = self.MANAGE_PARTY
            self.selected_option = 0
            
        return False
        
    def _handle_edit_character_input(self, event):
        """Handle input for the edit character state."""
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.MANAGE_PARTY
            self.selected_option = 0
            self.message = "Select a management option"
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Change Name
                self.current_state = self.NAME_INPUT
                self.name_input_active = True
                self.back_state = self.EDIT_CHARACTER
                self.temp_name = self.selected_character.name
                self.message = "Enter new name"
            elif self.selected_option == 1:  # Change Class
                self.current_state = self.SELECT_CLASS
                self.selected_option = 0
                self.back_state = self.EDIT_CHARACTER
                self.message = "Select a new class"
            elif self.selected_option == 2:  # Back
                self.current_state = self.MANAGE_PARTY
                self.selected_option = 0
                self.message = "Select a management option"
        elif event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 3  # 3 options
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 3  # 3 options
            
        return False
        
    def _handle_view_party_input(self, event):
        """Handle input for the view party state."""
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
            self.current_state = self.MAIN_MENU
            self.selected_option = 0
            self.message = ""
            
        return False
        
    def _handle_manage_party_input(self, event):
        """Handle input for the manage party state."""
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.MAIN_MENU
            self.selected_option = 0
            self.message = ""
        elif event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.manage_party_options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.manage_party_options)
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Change Leader
                # Show character selection for leader
                if len(self.party.active_members) > 1:
                    self.current_state = self.SELECT_CHARACTER
                    self.selected_option = 0
                    self.back_state = self.MANAGE_PARTY
                    self.message = "Select new party leader"
                else:
                    self.message = "Need more party members!"
            elif self.selected_option == 1:  # Edit Character
                if len(self.party.get_all_members()) > 0:
                    # Show character selection for editing
                    self.current_state = self.SELECT_CHARACTER
                    self.selected_option = 0
                    self.back_state = self.EDIT_CHARACTER
                    self.message = "Select character to edit"
                else:
                    self.message = "No characters to edit!"
            elif self.selected_option == 2:  # Remove Character
                if len(self.party.get_all_members()) > 1:
                    # Show character selection for removal
                    self.current_state = self.SELECT_CHARACTER
                    self.selected_option = 0
                    self.back_state = self.REMOVE_CHARACTER
                    self.message = "Select character to remove"
                else:
                    self.message = "Cannot remove last character!"
            elif self.selected_option == 3:  # Back
                self.current_state = self.MAIN_MENU
                self.selected_option = 0
                self.message = ""
                
        return False
    
    def _handle_select_class_input(self, event):
        """Handle input for the class selection state."""
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.back_state
            self.selected_option = 0
        elif event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.class_options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.class_options)
        elif event.key == pygame.K_RETURN:
            # Apply the selected class
            self.selected_class_id = self.class_options[self.selected_option]
            
            if self.back_state == self.CREATE_CHARACTER:
                # Return to create character screen
                self.current_state = self.CREATE_CHARACTER
                self.message = f"Class selected: {self.selected_class_id.capitalize()}"
            elif self.back_state == self.EDIT_CHARACTER:
                # Apply class change to character
                if self.selected_character:
                    success = self.character_creator.edit_character(
                        self.selected_character, 
                        new_class_id=self.selected_class_id
                    )
                    if success:
                        self.message = f"Changed class to {self.selected_class_id.capitalize()}"
                    else:
                        self.message = "Failed to change class!"
                
                # Return to edit character screen
                self.current_state = self.EDIT_CHARACTER
                
        return False
    
    def _handle_name_input(self, event):
        """Handle input for the name input state."""
        if event.key == pygame.K_ESCAPE:
            self.current_state = self.back_state
            self.name_input_active = False
        elif event.key == pygame.K_BACKSPACE:
            self.temp_name = self.temp_name[:-1]
        elif event.key == pygame.K_RETURN:
            # Apply the entered name
            if self.temp_name:
                if self.back_state == self.CREATE_CHARACTER:
                    # Create new character with entered name and selected class
                    character = self.character_creator.create_character(
                        self.temp_name, 
                        self.selected_class_id,
                        level=1
                    )
                    
                    if character:
                        self.message = f"Created {self.temp_name} as a {self.selected_class_id.capitalize()}"
                    else:
                        self.message = "Failed to create character!"
                        
                    # Return to main menu
                    self.current_state = self.MAIN_MENU
                    self.selected_option = 0
                    
                elif self.back_state == self.EDIT_CHARACTER:
                    # Apply name change to character
                    if self.selected_character:
                        success = self.character_creator.edit_character(
                            self.selected_character, 
                            new_name=self.temp_name
                        )
                        if success:
                            self.message = f"Changed name to {self.temp_name}"
                        else:
                            self.message = "Failed to change name!"
                    
                    # Return to edit character screen
                    self.current_state = self.EDIT_CHARACTER
                    
            self.name_input_active = False
            
        else:
            # Add the character if it's valid (letters, numbers, spaces)
            if event.unicode.isalnum() or event.unicode.isspace():
                # Limit name length
                if len(self.temp_name) < 20:
                    self.temp_name += event.unicode
                    
        return False
    
    def draw(self, screen):
        """
        Draw the party management UI.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Draw semi-transparent overlay 
        overlay = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with 80% opacity
        screen.blit(overlay, (0, 0))
        
        # Scale font sizes
        title_font_size = scale_font_size(32, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        font_size = scale_font_size(24, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        small_font_size = scale_font_size(18, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        
        title_font = pygame.font.SysFont('Arial', title_font_size)
        font = pygame.font.SysFont('Arial', font_size)
        small_font = pygame.font.SysFont('Arial', small_font_size)
        
        # Draw title
        title_text = "Party Management"
        title_surface = title_font.render(title_text, True, WHITE)
        title_x = (current_width - title_surface.get_width()) // 2
        title_y = int(50 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(title_surface, (title_x, title_y))
        
        # Draw message if any
        if self.message:
            msg_surface = font.render(self.message, True, YELLOW)
            msg_x = (current_width - msg_surface.get_width()) // 2
            msg_y = int(100 * (current_height / ORIGINAL_HEIGHT))
            screen.blit(msg_surface, (msg_x, msg_y))
        
        # Draw appropriate content based on current state
        if self.current_state == self.MAIN_MENU:
            self._draw_main_menu(screen, font, current_width, current_height)
        elif self.current_state == self.CREATE_CHARACTER:
            self._draw_create_character(screen, font, small_font, current_width, current_height)
        elif self.current_state == self.VIEW_PARTY:
            self._draw_view_party(screen, font, small_font, current_width, current_height)
        elif self.current_state == self.MANAGE_PARTY:
            self._draw_manage_party(screen, font, current_width, current_height)
        elif self.current_state == self.SELECT_CLASS:
            self._draw_select_class(screen, font, small_font, current_width, current_height)
        elif self.current_state == self.EDIT_CHARACTER:
            self._draw_edit_character(screen, font, small_font, current_width, current_height)
        elif self.current_state == self.NAME_INPUT:
            self._draw_name_input(screen, font, current_width, current_height)
        elif self.current_state == self.SELECT_CHARACTER:
            self._draw_select_character(screen, font, small_font, current_width, current_height)
        elif self.current_state == self.REMOVE_CHARACTER:
            self._draw_remove_character(screen, font, small_font, current_width, current_height)
            
    def _draw_main_menu(self, screen, font, current_width, current_height):
        """Draw the main menu UI."""
        option_y_base = int(150 * (current_height / ORIGINAL_HEIGHT))
        option_spacing = int(40 * (current_height / ORIGINAL_HEIGHT))
        
        for i, option in enumerate(self.main_menu_options):
            if i == self.selected_option:
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
                
            option_x = (current_width - option_text.get_width()) // 2
            option_y = option_y_base + i * option_spacing
            screen.blit(option_text, (option_x, option_y))
            
    def _draw_create_character(self, screen, font, small_font, current_width, current_height):
        """Draw the character creation UI."""
        # Draw class options
        class_options_y = int(150 * (current_height / ORIGINAL_HEIGHT))
        class_spacing = int(200 * (current_width / ORIGINAL_WIDTH))
        class_center_x = current_width // 2
        
        # Draw class selection instructions
        instructions = "← Use arrow keys to select class →"
        instr_surface = small_font.render(instructions, True, WHITE)
        instr_x = (current_width - instr_surface.get_width()) // 2
        instr_y = class_options_y - int(30 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(instr_surface, (instr_x, instr_y))
        
        # Draw the class options
        for i, class_id in enumerate(self.class_options):
            class_name = class_id.capitalize()
            class_x = class_center_x + (i - 1) * class_spacing
            
            # Highlight selected class
            if class_id == self.selected_class_id:
                # Draw selection box
                text_width = font.size(class_name)[0]
                box_width = text_width + int(20 * (current_width / ORIGINAL_WIDTH))
                box_height = int(40 * (current_height / ORIGINAL_HEIGHT))
                box_x = class_x - box_width // 2
                box_y = class_options_y - int(10 * (current_height / ORIGINAL_HEIGHT))
                
                pygame.draw.rect(screen, BLUE, (box_x, box_y, box_width, box_height), 2)
                
                class_surface = font.render(class_name, True, WHITE)
            else:
                class_surface = font.render(class_name, True, GRAY)
                
            class_surface_x = class_x - class_surface.get_width() // 2
            screen.blit(class_surface, (class_surface_x, class_options_y))
            
        # Draw class description
        from data.character_classes import commoner, warrior, mage
        class_map = {"commoner": commoner, "warrior": warrior, "mage": mage}
        selected_class = class_map.get(self.selected_class_id)
        
        if selected_class:
            desc_y = class_options_y + int(50 * (current_height / ORIGINAL_HEIGHT))
            
            # Show class stats
            for i, (stat, value) in enumerate(selected_class.base_stats.items()):
                stat_text = f"{stat.upper()}: {value}"
                stat_surface = small_font.render(stat_text, True, WHITE)
                stat_x = class_center_x - stat_surface.get_width() // 2
                stat_y = desc_y + i * int(25 * (current_height / ORIGINAL_HEIGHT))
                screen.blit(stat_surface, (stat_x, stat_y))
                
        # Draw current name
        name_y = int(350 * (current_height / ORIGINAL_HEIGHT))
        name_text = f"Name: {self.temp_name}"
        name_surface = font.render(name_text, True, WHITE)
        name_x = (current_width - name_surface.get_width()) // 2
        screen.blit(name_surface, (name_x, name_y))
        
        # Draw create button
        button_y = int(400 * (current_height / ORIGINAL_HEIGHT))
        button_text = "Press ENTER to name character"
        button_surface = font.render(button_text, True, GREEN)
        button_x = (current_width - button_surface.get_width()) // 2
        screen.blit(button_surface, (button_x, button_y))
        
        # Draw back instruction
        back_y = int(450 * (current_height / ORIGINAL_HEIGHT))
        back_text = "Press ESC to go back"
        back_surface = small_font.render(back_text, True, GRAY)
        back_x = (current_width - back_surface.get_width()) // 2
        screen.blit(back_surface, (back_x, back_y))
        
    def _draw_view_party(self, screen, font, small_font, current_width, current_height):
        """Draw the party view UI."""
        # Draw party members
        members_y_base = int(150 * (current_height / ORIGINAL_HEIGHT))
        member_spacing = int(60 * (current_height / ORIGINAL_HEIGHT))
        
        # Active members
        active_title = font.render("Active Members:", True, WHITE)
        active_x = (current_width - active_title.get_width()) // 2
        screen.blit(active_title, (active_x, members_y_base))
        
        if not self.party.active_members:
            no_active = small_font.render("No active members", True, GRAY)
            no_active_x = (current_width - no_active.get_width()) // 2
            no_active_y = members_y_base + member_spacing
            screen.blit(no_active, (no_active_x, no_active_y))
        else:
            for i, member in enumerate(self.party.active_members):
                # Highlight leader
                is_leader = (member == self.party.leader)
                color = YELLOW if is_leader else WHITE
                leader_mark = " (Leader)" if is_leader else ""
                
                member_text = f"{member.name}{leader_mark} - Level {member.level} {member.character_class.name}"
                member_surface = small_font.render(member_text, True, color)
                member_x = (current_width - member_surface.get_width()) // 2
                member_y = members_y_base + member_spacing + i * int(30 * (current_height / ORIGINAL_HEIGHT))
                screen.blit(member_surface, (member_x, member_y))
                
        # Reserve members
        reserve_y = members_y_base + member_spacing * 6
        reserve_title = font.render("Reserve Members:", True, WHITE)
        reserve_x = (current_width - reserve_title.get_width()) // 2
        screen.blit(reserve_title, (reserve_x, reserve_y))
        
        if not self.party.reserve_members:
            no_reserve = small_font.render("No reserve members", True, GRAY)
            no_reserve_x = (current_width - no_reserve.get_width()) // 2
            no_reserve_y = reserve_y + member_spacing
            screen.blit(no_reserve, (no_reserve_x, no_reserve_y))
        else:
            for i, member in enumerate(self.party.reserve_members):
                member_text = f"{member.name} - Level {member.level} {member.character_class.name}"
                member_surface = small_font.render(member_text, True, WHITE)
                member_x = (current_width - member_surface.get_width()) // 2
                member_y = reserve_y + member_spacing + i * int(30 * (current_height / ORIGINAL_HEIGHT))
                screen.blit(member_surface, (member_x, member_y))
                
        # Draw back instruction
        back_y = int(450 * (current_height / ORIGINAL_HEIGHT))
        back_text = "Press ENTER or ESC to go back"
        back_surface = small_font.render(back_text, True, GRAY)
        back_x = (current_width - back_surface.get_width()) // 2
        screen.blit(back_surface, (back_x, back_y))
        
    def _draw_manage_party(self, screen, font, current_width, current_height):
        """Draw the party management UI."""
        option_y_base = int(150 * (current_height / ORIGINAL_HEIGHT))
        option_spacing = int(40 * (current_height / ORIGINAL_HEIGHT))
        
        for i, option in enumerate(self.manage_party_options):
            if i == self.selected_option:
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
                
            option_x = (current_width - option_text.get_width()) // 2
            option_y = option_y_base + i * option_spacing
            screen.blit(option_text, (option_x, option_y))
    
    def _draw_select_character(self, screen, font, small_font, current_width, current_height):
        """Draw the character selection UI."""
        # Get the list of members
        members = self.party.get_all_members()
        
        option_y_base = int(150 * (current_height / ORIGINAL_HEIGHT))
        option_spacing = int(40 * (current_height / ORIGINAL_HEIGHT))
        
        for i, member in enumerate(members):
            # Highlight leader and selected character
            is_leader = (member == self.party.leader)
            is_selected = (i == self.selected_option)
            
            leader_mark = " (Leader)" if is_leader else ""
            prefix = "> " if is_selected else "  "
            
            member_text = f"{prefix}{member.name}{leader_mark} - Level {member.level} {member.character_class.name}"
            
            if is_selected:
                member_surface = font.render(member_text, True, WHITE)
            else:
                member_surface = font.render(member_text, True, GRAY)
                
            member_x = (current_width - member_surface.get_width()) // 2
            member_y = option_y_base + i * option_spacing
            screen.blit(member_surface, (member_x, member_y))
            
        # Draw back instruction
        back_y = int(450 * (current_height / ORIGINAL_HEIGHT))
        back_text = "Press ESC to go back"
        back_surface = small_font.render(back_text, True, GRAY)
        back_x = (current_width - back_surface.get_width()) // 2
        screen.blit(back_surface, (back_x, back_y))
        
    def _draw_select_class(self, screen, font, small_font, current_width, current_height):
        """Draw the class selection UI."""
        option_y_base = int(150 * (current_height / ORIGINAL_HEIGHT))
        option_spacing = int(40 * (current_height / ORIGINAL_HEIGHT))
        
        for i, class_id in enumerate(self.class_options):
            class_name = class_id.capitalize()
            
            if i == self.selected_option:
                option_text = font.render(f"> {class_name}", True, WHITE)
            else:
                option_text = font.render(f"  {class_name}", True, GRAY)
                
            option_x = (current_width - option_text.get_width()) // 2
            option_y = option_y_base + i * option_spacing
            screen.blit(option_text, (option_x, option_y))
            
        # Draw class description
        from data.character_classes import commoner, warrior, mage
        class_map = {"commoner": commoner, "warrior": warrior, "mage": mage}
        selected_class = class_map.get(self.class_options[self.selected_option])
        
        if selected_class:
            desc_y = option_y_base + len(self.class_options) * option_spacing + int(20 * (current_height / ORIGINAL_HEIGHT))
            
            # Show class stats
            stats_title = small_font.render("Base Stats:", True, YELLOW)
            stats_x = (current_width - stats_title.get_width()) // 2
            screen.blit(stats_title, (stats_x, desc_y))
            
            for i, (stat, value) in enumerate(selected_class.base_stats.items()):
                stat_text = f"{stat.upper()}: {value}"
                stat_surface = small_font.render(stat_text, True, WHITE)
                stat_x = (current_width - stat_surface.get_width()) // 2
                stat_y = desc_y + int(25 * (current_height / ORIGINAL_HEIGHT)) + i * int(20 * (current_height / ORIGINAL_HEIGHT))
                screen.blit(stat_surface, (stat_x, stat_y))
            
        # Draw back instruction
        back_y = int(450 * (current_height / ORIGINAL_HEIGHT))
        back_text = "Press ESC to go back"
        back_surface = small_font.render(back_text, True, GRAY)
        back_x = (current_width - back_surface.get_width()) // 2
        screen.blit(back_surface, (back_x, back_y))
        
    def _draw_edit_character(self, screen, font, small_font, current_width, current_height):
        """Draw the character editing UI."""
        if not self.selected_character:
            # Should not happen, but handle it gracefully
            error_text = "No character selected!"
            error_surface = font.render(error_text, True, RED)
            error_x = (current_width - error_surface.get_width()) // 2
            error_y = int(150 * (current_height / ORIGINAL_HEIGHT))
            screen.blit(error_surface, (error_x, error_y))
            return
            
        # Draw character info
        char_y = int(150 * (current_height / ORIGINAL_HEIGHT))
        char_text = f"Editing: {self.selected_character.name} - Level {self.selected_character.level} {self.selected_character.character_class.name}"
        char_surface = font.render(char_text, True, WHITE)
        char_x = (current_width - char_surface.get_width()) // 2
        screen.blit(char_surface, (char_x, char_y))
        
        # Draw edit options
        option_y_base = int(200 * (current_height / ORIGINAL_HEIGHT))
        option_spacing = int(40 * (current_height / ORIGINAL_HEIGHT))
        options = ["Change Name", "Change Class", "Back"]
        
        for i, option in enumerate(options):
            if i == self.selected_option:
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
                
            option_x = (current_width - option_text.get_width()) // 2
            option_y = option_y_base + i * option_spacing
            screen.blit(option_text, (option_x, option_y))
            
        # Draw back instruction
        back_y = int(450 * (current_height / ORIGINAL_HEIGHT))
        back_text = "Press ESC to go back"
        back_surface = small_font.render(back_text, True, GRAY)
        back_x = (current_width - back_surface.get_width()) // 2
        screen.blit(back_surface, (back_x, back_y))
        
    def _draw_name_input(self, screen, font, current_width, current_height):
        """Draw the name input UI."""
        input_y = int(200 * (current_height / ORIGINAL_HEIGHT))
        
        # Draw name input box
        input_width = int(300 * (current_width / ORIGINAL_WIDTH))
        input_height = int(40 * (current_height / ORIGINAL_HEIGHT))
        input_x = (current_width - input_width) // 2
        
        # Draw input box
        pygame.draw.rect(screen, WHITE, (input_x, input_y, input_width, input_height), 2)
        
        # Draw current name
        name_surface = font.render(self.temp_name, True, WHITE)
        name_x = input_x + int(10 * (current_width / ORIGINAL_WIDTH))
        name_y = input_y + int(5 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(name_surface, (name_x, name_y))
        
        # Draw cursor if input is active
        if self.name_input_active:
            cursor_x = name_x + name_surface.get_width() + int(2 * (current_width / ORIGINAL_WIDTH))
            cursor_height = int(30 * (current_height / ORIGINAL_HEIGHT))
            cursor_y = name_y + int(2 * (current_height / ORIGINAL_HEIGHT))
            
            # Make cursor blink
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.line(screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)
                
        # Draw instructions
        instr_y = input_y + input_height + int(20 * (current_height / ORIGINAL_HEIGHT))
        instr_text = "Press ENTER to confirm or ESC to cancel"
        instr_surface = font.render(instr_text, True, WHITE)
        instr_x = (current_width - instr_surface.get_width()) // 2
        screen.blit(instr_surface, (instr_x, instr_y))
        
    def _draw_remove_character(self, screen, font, small_font, current_width, current_height):
        """Draw the character removal confirmation UI."""
        if not self.selected_character:
            # Should not happen, but handle it gracefully
            error_text = "No character selected!"
            error_surface = font.render(error_text, True, RED)
            error_x = (current_width - error_surface.get_width()) // 2
            error_y = int(150 * (current_height / ORIGINAL_HEIGHT))
            screen.blit(error_surface, (error_x, error_y))
            return
            
        # Draw character info
        char_y = int(150 * (current_height / ORIGINAL_HEIGHT))
        char_text = f"Remove {self.selected_character.name} from party?"
        char_surface = font.render(char_text, True, WHITE)
        char_x = (current_width - char_surface.get_width()) // 2
        screen.blit(char_surface, (char_x, char_y))
        
        # Draw yes/no options
        option_y = int(250 * (current_height / ORIGINAL_HEIGHT))
        option_spacing = int(200 * (current_width / ORIGINAL_WIDTH))
        options = ["Yes", "No"]
        
        for i, option in enumerate(options):
            is_selected = (i == self.selected_option)
            
            # Position options side by side
            option_x = (current_width // 2) - (option_spacing // 2) + i * option_spacing - int(50 * (current_width / ORIGINAL_WIDTH))
            
            if is_selected:
                # Highlight selected option
                option_text = font.render(f"[{option}]", True, i == 0 and RED or GREEN)
            else:
                option_text = font.render(f" {option} ", True, GRAY)
                
            # Center the text at the option position
            option_x = option_x - option_text.get_width() // 2
            screen.blit(option_text, (option_x, option_y))