"""
Map system for RPG game.
"""
import pygame
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, WHITE
from utils import scale_position, scale_dimensions, scale_font_size
from entities.enemy import Enemy
from systems.encounter_system import EncounterManager

class MapArea:
    """
    Represents a single map area in the game world.
    """
    def __init__(self, name, background_color=(0, 0, 0), map_id=None):
        """
        Initialize a new map area.
        
        Args:
            name (str): The name of this map area
            background_color (tuple): RGB color tuple for the background
            map_id (str): Unique identifier for this map area
        """
        self.name = name
        self.background_color = background_color
        self.map_id = map_id if map_id else name.lower().replace(" ", "_")
        self.entities = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        
        # Connections to other maps (None if no connection)
        self.connections = {
            "north": None,
            "east": None,
            "south": None,
            "west": None
        }
        
        # Enemy encounter settings
        self.encounter_chance = 0.1  # Default 10% chance per step
        self.steps_since_last_encounter = 0
        self.min_steps_between_encounters = 10  # Minimum steps before another encounter
        
    def add_entity(self, entity):
        """
        Add an entity to this map area.
        
        Args:
            entity: The entity to add
        """
        self.entities.add(entity)
        
        # If it's an NPC, add to the NPCs group
        from entities.npc import NPC
        if isinstance(entity, NPC):
            self.npcs.add(entity)
        
    def connect(self, direction, target_map):
        """
        Connect this map to another in the specified direction.
        
        Args:
            direction (str): The direction ("north", "east", "south", "west")
            target_map (MapArea): The map area to connect to
        """
        if direction in self.connections:
            self.connections[direction] = target_map
            
            # Set up the reverse connection automatically
            reverse_directions = {
                "north": "south",
                "south": "north",
                "east": "west",
                "west": "east"
            }
            
            # Only set the reverse if it's not already set
            reverse_dir = reverse_directions[direction]
            if target_map.connections[reverse_dir] is None:
                target_map.connections[reverse_dir] = self
        
    def draw(self, screen):
        """
        Draw this map area, including boundaries and entities.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Fill the background
        screen.fill(self.background_color)
        
        # Scale border thickness based on current resolution
        line_thickness = max(1, int(5 * (current_width / ORIGINAL_WIDTH)))
        
        # Draw boundary walls for edges that don't have connections
        if not self.connections["north"]:
            # Draw top boundary
            pygame.draw.line(screen, WHITE, (0, 0), (current_width, 0), line_thickness)
            
        if not self.connections["east"]:
            # Draw right boundary
            pygame.draw.line(screen, WHITE, (current_width - line_thickness, 0), 
                            (current_width - line_thickness, current_height), line_thickness)
            
        if not self.connections["south"]:
            # Draw bottom boundary
            pygame.draw.line(screen, WHITE, (0, current_height - line_thickness), 
                            (current_width, current_height - line_thickness), line_thickness)
            
        if not self.connections["west"]:
            # Draw left boundary
            pygame.draw.line(screen, WHITE, (0, 0), (0, current_height), line_thickness)
        
        # Scale and draw the map name
        font_size = scale_font_size(24, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        font = pygame.font.SysFont('Arial', font_size)
        name_text = font.render(self.name, True, WHITE)
        name_x = current_width // 2 - name_text.get_width() // 2
        name_y = int(10 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(name_text, (name_x, name_y))
        
        # Update scaling for all entities 
        for entity in self.entities:
            if hasattr(entity, 'update_scale'):
                entity.update_scale(current_width, current_height)
        
        # Draw all entities in this map
        self.entities.draw(screen)
        
    def update(self, player=None, encounter_manager=None):
        """
        Update all entities in this map area and check for map transitions and encounters.
        
        Args:
            player: The player entity (optional)
            encounter_manager: The encounter manager for generating random encounters
        
        Returns:
            tuple or None: (new_map, position) if transition should occur, or 
                        [Enemy] if encounter triggered, None otherwise
        """
        # Get current screen dimensions
        if player:
            current_width, current_height = pygame.display.get_surface().get_size()
        
        # If player is provided and in this map, check for map transitions and encounters
        if player and player in self.entities:
            # Check if player has moved since last frame
            player_moved = (
                player.rect.x != getattr(player, 'last_x', player.rect.x) or
                player.rect.y != getattr(player, 'last_y', player.rect.y)
            )
            
            # Store current position for next frame
            player.last_x = player.rect.x
            player.last_y = player.rect.y
            
            # If player moved, increment step counter and check for encounters
            if player_moved:
                self.steps_since_last_encounter += 1
                
                # Only check for random encounters if we've taken enough steps since the last one
                if (self.steps_since_last_encounter >= self.min_steps_between_encounters and 
                    encounter_manager and random.random() < self.encounter_chance):
                    
                    # Generate an encounter for this map
                    enemy_specs = encounter_manager.generate_encounter_for_map(self.map_id)
                    if enemy_specs:
                        # Reset step counter
                        self.steps_since_last_encounter = 0
                        
                        # Create enemies from specs
                        encounter_enemies = []
                        for spec in enemy_specs:
                            # Create the enemy off-screen initially (position will be set by battle system)
                            enemy = Enemy.create_from_spec(spec, -100, -100)
                            enemy.update_scale(current_width, current_height)
                            encounter_enemies.append(enemy)
                            
                        # Return the list of enemies to trigger a battle
                        return encounter_enemies
            
            # Check for map transitions
            return self.check_map_transition(player, current_width, current_height)
        
        return None
    
    def check_boundary_collision(self, player, screen_width, screen_height):
        """
        Check if player is colliding with map boundaries and prevent movement past them.
        
        Args:
            player: The player entity
            screen_width: Current screen width
            screen_height: Current screen height
        """
        line_thickness = max(1, int(5 * (screen_width / ORIGINAL_WIDTH)))
        
        # Check collision with north boundary
        if player.rect.top <= 0 and not self.connections["north"]:
            player.rect.top = line_thickness
            
        # Check collision with east boundary
        if player.rect.right >= screen_width and not self.connections["east"]:
            player.rect.right = screen_width - line_thickness
            
        # Check collision with south boundary
        if player.rect.bottom >= screen_height and not self.connections["south"]:
            player.rect.bottom = screen_height - line_thickness
            
        # Check collision with west boundary
        if player.rect.left <= 0 and not self.connections["west"]:
            player.rect.left = line_thickness
        
    def check_map_transition(self, player, screen_width, screen_height):
        """
        Check if player is at a map edge that should trigger a transition.
        
        Args:
            player: The player entity
            screen_width: Current screen width
            screen_height: Current screen height
            
        Returns:
            tuple: (new_map, position) if transition should occur, None otherwise
        """
        # Check for north edge transition
        if player.rect.top <= 0 and self.connections["north"]:
            return (self.connections["north"], "south")
            
        # Check for east edge transition
        if player.rect.right >= screen_width and self.connections["east"]:
            return (self.connections["east"], "west")
            
        # Check for south edge transition
        if player.rect.bottom >= screen_height and self.connections["south"]:
            return (self.connections["south"], "north")
            
        # Check for west edge transition
        if player.rect.left <= 0 and self.connections["west"]:
            return (self.connections["west"], "east")
            
        return None


class MapSystem:
    """
    Manages multiple map areas and transitions between them.
    """
    def __init__(self, encounter_manager=None):
        """
        Initialize the map system.
        
        Args:
            encounter_manager: The encounter manager for random encounters
        """
        self.maps = {}
        self.current_map = None
        self.encounter_manager = encounter_manager
        
    def add_map(self, map_id, map_area):
        """
        Add a map area to the system.
        
        Args:
            map_id (str): Unique identifier for this map
            map_area (MapArea): The map area to add
        """
        self.maps[map_id] = map_area
        # Set the map_id on the map_area for consistency
        map_area.map_id = map_id
        
    def set_current_map(self, map_id):
        """
        Set the current active map.
        
        Args:
            map_id (str): The ID of the map to set as current
            
        Returns:
            bool: True if map was found and set, False otherwise
        """
        if map_id in self.maps:
            self.current_map = self.maps[map_id]
            return True
        return False
        
    def get_current_map(self):
        """
        Get the current active map.
        
        Returns:
            MapArea: The current map
        """
        return self.current_map
        
    def connect_maps(self, map_id1, direction, map_id2):
        """
        Connect two maps in the specified direction.
        
        Args:
            map_id1 (str): ID of the first map
            direction (str): Direction from map1 to map2
            map_id2 (str): ID of the second map
            
        Returns:
            bool: True if connection was made, False otherwise
        """
        if map_id1 in self.maps and map_id2 in self.maps:
            self.maps[map_id1].connect(direction, self.maps[map_id2])
            return True
        return False
        
    def transition_player(self, player, new_map, entry_side):
        """
        Move the player to a new map, positioning them at the appropriate edge.
        
        Args:
            player: The player entity
            new_map (MapArea): The destination map
            entry_side (str): The side the player is entering from
        """
        # Get current screen dimensions
        current_width, current_height = pygame.display.get_surface().get_size()
        
        # Remove player from current map entities
        if self.current_map:
            self.current_map.entities.remove(player)
        
        # Add player to new map entities
        new_map.add_entity(player)
        
        # Calculate the border thickness
        line_thickness = max(1, int(5 * (current_width / ORIGINAL_WIDTH)))
        
        # Position player at the appropriate edge of the new map
        if entry_side == "north":
            player.rect.centerx = current_width // 2
            player.rect.top = line_thickness + 1  # Just inside the boundary
        elif entry_side == "east":
            player.rect.centery = current_height // 2
            player.rect.right = current_width - line_thickness - 1
        elif entry_side == "south":
            player.rect.centerx = current_width // 2
            player.rect.bottom = current_height - line_thickness - 1
        elif entry_side == "west":
            player.rect.centery = current_height // 2
            player.rect.left = line_thickness + 1
        
        # Update player's original position to match the new scaled position
        scale_factor_x = ORIGINAL_WIDTH / current_width
        scale_factor_y = ORIGINAL_HEIGHT / current_height
        player.original_x = player.rect.x * scale_factor_x
        player.original_y = player.rect.y * scale_factor_y
        
        # Set the new map as current
        self.current_map = new_map