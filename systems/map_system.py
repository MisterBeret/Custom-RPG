"""
Map system for RPG game.
"""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

class MapArea:
    """
    Represents a single map area in the game world.
    """
    def __init__(self, name, background_color=(0, 0, 0)):
        """
        Initialize a new map area.
        
        Args:
            name (str): The name of this map area
            background_color (tuple): RGB color tuple for the background
        """
        self.name = name
        self.background_color = background_color
        self.entities = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Connections to other maps (None if no connection)
        self.connections = {
            "north": None,
            "east": None,
            "south": None,
            "west": None
        }
        
    def add_entity(self, entity):
        """
        Add an entity to this map area.
        
        Args:
            entity: The entity to add
        """
        self.entities.add(entity)
        
    def add_enemy(self, enemy):
        """
        Add an enemy to this map area.
        
        Args:
            enemy: The enemy to add
        """
        self.enemies.add(enemy)
        self.entities.add(enemy)
        
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
        # Fill the background
        screen.fill(self.background_color)
        
        # Draw boundary walls for edges that don't have connections
        line_thickness = 5
        
        if not self.connections["north"]:
            # Draw top boundary
            pygame.draw.line(screen, WHITE, (0, 0), (SCREEN_WIDTH, 0), line_thickness)
            
        if not self.connections["east"]:
            # Draw right boundary
            pygame.draw.line(screen, WHITE, (SCREEN_WIDTH - line_thickness, 0), 
                            (SCREEN_WIDTH - line_thickness, SCREEN_HEIGHT), line_thickness)
            
        if not self.connections["south"]:
            # Draw bottom boundary
            pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT - line_thickness), 
                            (SCREEN_WIDTH, SCREEN_HEIGHT - line_thickness), line_thickness)
            
        if not self.connections["west"]:
            # Draw left boundary
            pygame.draw.line(screen, WHITE, (0, 0), (0, SCREEN_HEIGHT), line_thickness)
        
        # Draw map name at the top
        font = pygame.font.SysFont('Arial', 24)
        name_text = font.render(self.name, True, WHITE)
        name_x = SCREEN_WIDTH // 2 - name_text.get_width() // 2
        screen.blit(name_text, (name_x, 10))
        
        # Draw all entities in this map
        self.entities.draw(screen)
        
    def update(self, player=None):
        """
        Update all entities in this map area.
        
        Args:
            player: The player entity (optional)
        """
        # Update enemies
        self.enemies.update()
        
        # If player is provided and in this map, check for edge transitions
        if player and player in self.entities:
            return self.check_map_transition(player)
            
        return None
        
    def check_map_transition(self, player):
        """
        Check if player is at a map edge that should trigger a transition.
        
        Args:
            player: The player entity
            
        Returns:
            tuple: (new_map, position) if transition should occur, None otherwise
        """
        # Check for north edge transition
        if player.rect.top <= 0 and self.connections["north"]:
            return (self.connections["north"], "south")
            
        # Check for east edge transition
        if player.rect.right >= SCREEN_WIDTH and self.connections["east"]:
            return (self.connections["east"], "west")
            
        # Check for south edge transition
        if player.rect.bottom >= SCREEN_HEIGHT and self.connections["south"]:
            return (self.connections["south"], "north")
            
        # Check for west edge transition
        if player.rect.left <= 0 and self.connections["west"]:
            return (self.connections["west"], "east")
            
        return None


class MapSystem:
    """
    Manages multiple map areas and transitions between them.
    """
    def __init__(self):
        """
        Initialize the map system.
        """
        self.maps = {}
        self.current_map = None
        
    def add_map(self, map_id, map_area):
        """
        Add a map area to the system.
        
        Args:
            map_id (str): Unique identifier for this map
            map_area (MapArea): The map area to add
        """
        self.maps[map_id] = map_area
        
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
        # Remove player from current map entities
        if self.current_map:
            self.current_map.entities.remove(player)
        
        # Add player to new map entities
        new_map.add_entity(player)
        
        # Position player at the appropriate edge of the new map
        if entry_side == "north":
            player.rect.centerx = SCREEN_WIDTH // 2
            player.rect.top = 5  # A small offset from the edge
        elif entry_side == "east":
            player.rect.centery = SCREEN_HEIGHT // 2
            player.rect.right = SCREEN_WIDTH - 5
        elif entry_side == "south":
            player.rect.centerx = SCREEN_WIDTH // 2
            player.rect.bottom = SCREEN_HEIGHT - 5
        elif entry_side == "west":
            player.rect.centery = SCREEN_HEIGHT // 2
            player.rect.left = 5
        
        # Set the new map as current
        self.current_map = new_map