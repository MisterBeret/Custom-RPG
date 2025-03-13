"""
Battle animation handling for the RPG game.
Manages all visual animations during battle including attacks, spells, and movement.
"""
import pygame
import random
from constants import (
    BLACK, WHITE, GREEN, RED, BLUE, YELLOW, PURPLE,
    ATTACK_ANIMATION_DURATION, FLEE_ANIMATION_DURATION,
    SPELL_ANIMATION_DURATION, ACTION_DELAY_DURATION,
    ORIGINAL_WIDTH, ORIGINAL_HEIGHT
)
from entities.player import Player

class BattleAnimations:
    """
    Handles battle animations and visual effects.
    """
    def __init__(self, battle_system):
        """
        Initialize the battle animations handler.
        
        Args:
            battle_system: The parent battle system
        """
        self.battle_system = battle_system
        
        # Animation state variables
        self.animation_timer = 0
        self.counter_animation_timer = 0
        self.action_delay = 0
        
        # Animation durations
        self.animation_duration = ATTACK_ANIMATION_DURATION
        self.flee_animation_duration = FLEE_ANIMATION_DURATION
        self.spell_animation_duration = SPELL_ANIMATION_DURATION
        self.action_delay_duration = ACTION_DELAY_DURATION
        
        # Flag for different animations
        self.character_attacking = False
        self.character_defending = False
        self.character_casting = False
        self.character_using_skill = False
        self.character_using_ultimate = False
        self.character_fleeing = False
        self.enemy_attacking = False
        self.character_countering = False
        
        # Active animation entities
        self.active_character = None
        self.target = None
        self.current_enemy = None
        
        # Current action data
        self.current_spell = None
        self.current_skill = None
        self.current_ultimate = None
        
        # Store pending effects
        self.pending_damage = 0
        self.pending_message = ""
        
        # Passive ability tracking
        self.counter_triggered = False
        self.counter_message = ""
        
        # Visual effects
        self.effects = []
    
    def update(self):
        """Update all active animations and effects."""
        # Skip animation updates if UI is showing text
        if not self.battle_system.ui.is_text_complete():
            return
            
        # Handle counter passive effect after enemy attack message is shown
        if self.counter_triggered:
            current_combatant = self.battle_system.turn_order.get_current()
            if not isinstance(current_combatant, Player):
                # Handle counter attack
                self.character_countering = True
                self.counter_animation_timer = 0
                self.counter_triggered = False
        
        # Handle counter-attack animation
        elif self.character_countering:
            self._update_counter_animation()
            
        # Update various animation types
        elif self.character_attacking:
            self._update_attack_animation()
        elif self.character_defending:
            self._update_defense_animation()
        elif self.character_casting:
            self._update_spell_animation()
        elif self.character_using_skill:
            self._update_skill_animation()
        elif self.character_using_ultimate:
            self._update_ultimate_animation()
        elif self.character_fleeing:
            self._update_flee_animation()
        elif self.enemy_attacking:
            self._update_enemy_attack_animation()
            
        # Update visual effects
        self._update_effects()
        
    def start_attack_animation(self, attacker, target):
        """
        Start the attack animation.
        
        Args:
            attacker: The attacking entity
            target: The target entity
        """
        self.character_attacking = True
        self.animation_timer = 0
        self.active_character = attacker
        self.target = target
    
    def start_defense_animation(self, character):
        """
        Start the defense animation.
        
        Args:
            character: The character defending
        """
        self.character_defending = True
        self.action_delay = 0
        self.active_character = character
    
    def start_spell_animation(self, caster, target, spell):
        """
        Start the spell casting animation.
        
        Args:
            caster: The spell caster
            target: The spell target
            spell: The spell being cast
        """
        self.character_casting = True
        self.animation_timer = 0
        self.active_character = caster
        self.target = target
        self.current_spell = spell
        
        # Add visual effect based on spell type
        if spell.effect_type == "damage":
            self._add_effect("fire", target)
        elif spell.effect_type == "healing":
            self._add_effect("heal", target)
    
    def start_skill_animation(self, user, target, skill):
        """
        Start the skill usage animation.
        
        Args:
            user: The skill user
            target: The target entity
            skill: The skill being used
        """
        self.character_using_skill = True
        self.animation_timer = 0
        self.active_character = user
        self.target = target
        self.current_skill = skill
        
        # Add visual effect based on skill type
        if skill.effect_type == "analyze":
            self._add_effect("analyze", target)
    
    def start_ultimate_animation(self, user, target, ultimate):
        """
        Start the ultimate ability animation.
        
        Args:
            user: The ultimate user
            target: The target entity
            ultimate: The ultimate being used
        """
        self.character_using_ultimate = True
        self.animation_timer = 0
        self.active_character = user
        self.target = target
        self.current_ultimate = ultimate
        
        # Add multiple visual effects for ultimate
        if ultimate.effect_type == "damage":
            for _ in range(5):  # Multiple effects for ultimates
                self._add_effect("ultimate", target, offset=True)
    
    def start_flee_animation(self, character):
        """
        Start the flee animation.
        
        Args:
            character: The character fleeing
        """
        self.character_fleeing = True
        self.animation_timer = 0
        self.active_character = character
    
    def _update_counter_animation(self):
        """Update counter-attack animation."""
        self.counter_animation_timer += 1
        if self.counter_animation_timer >= self.animation_duration:
            self.character_countering = False
            self.counter_animation_timer = 0
            
            # Now that counter animation is complete, display the message
            self.battle_system.ui.set_message(self.counter_message)
            
            # Check if enemy was defeated by the counter
            if self.target and self.target.is_defeated():
                # Check if all enemies are defeated
                if self.battle_system.mechanics.check_all_enemies_defeated(self.battle_system.enemies):
                    self.battle_system.victory = True
                    self.battle_system.battle_over = True
                    self.battle_system.ui.set_message("Victory! All enemies defeated!")
                else:
                    # Remove the defeated enemy from turn order
                    self.battle_system.turn_order.remove_combatant(self.target)
            else:
                # Only advance turn if counter didn't defeat target
                current_combatant = self.battle_system.turn_order.advance()
                self.battle_system.actions.action_processing = False
    
    def _update_attack_animation(self):
        """Update attack animation."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_duration:
            self.character_attacking = False
            self.animation_timer = 0
            
            # Apply damage to target
            if self.target and self.pending_damage > 0:
                # Check for passive triggers when taking damage
                actual_damage, passive_triggered, passive_message = (
                    self.battle_system.mechanics.apply_damage(
                        self.target, 
                        self.pending_damage,
                        damage_type="physical",
                        attacker=self.active_character,
                        battle_system=self.battle_system
                    )
                )
                
                # Store counter information if passive was triggered
                if passive_triggered:
                    self.counter_triggered = True
                    self.counter_message = passive_message
            
            # Display the attack message
            self.battle_system.ui.set_message(self.pending_message)
            
            # Check if target was defeated
            if self.target and self.target.is_defeated():
                # Award XP to attacker
                if hasattr(self.target, 'xp'):
                    xp_gained = self.target.xp
                    self.active_character.gain_experience(xp_gained)
                    self.battle_system.ui.message_log.append(f"{self.active_character.name} gained {xp_gained} XP!")
                
                # Check if all enemies are defeated
                if self.battle_system.mechanics.check_all_enemies_defeated(self.battle_system.enemies):
                    self.battle_system.victory = True
                    self.battle_system.battle_over = True
                    self.battle_system.ui.set_message("Victory! All enemies defeated!")
                    return
                else:
                    # Remove the defeated enemy from turn order
                    self.battle_system.turn_order.remove_combatant(self.target)
            
            # End current character's turn if not already done
            if self.active_character:
                self.active_character.end_turn()
            
            # Advance to next combatant if battle is not over
            if not self.battle_system.battle_over:
                current_combatant = self.battle_system.turn_order.advance()
                self.battle_system.actions.action_processing = False
    
    def _update_defense_animation(self):
        """Update defense animation."""
        self.action_delay += 1
        if self.action_delay >= self.action_delay_duration:
            self.action_delay = 0
            self.character_defending = False
            
            # End current character's turn
            if self.active_character:
                self.active_character.end_turn()
            
            # Advance to next combatant
            current_combatant = self.battle_system.turn_order.advance()
            self.battle_system.actions.action_processing = False
    
    def _update_spell_animation(self):
        """Update spell casting animation."""
        self.animation_timer += 1
        if self.animation_timer >= self.spell_animation_duration:
            self.character_casting = False
            self.animation_timer = 0
            
            # Apply spell effect to target
            if self.target:
                if self.pending_damage > 0:
                    # Damage spell
                    actual_damage, passive_triggered, passive_message = (
                        self.battle_system.mechanics.apply_damage(
                            self.target, 
                            self.pending_damage,
                            damage_type="magical",
                            attacker=self.active_character,
                            battle_system=self.battle_system
                        )
                    )
                    
                    # Handle passive response if triggered
                    if passive_triggered:
                        self.counter_triggered = True
                        self.counter_message = passive_message
                        
                elif self.pending_damage < 0:
                    # Healing spell (negative damage)
                    actual_healing = self.battle_system.mechanics.apply_healing(
                        self.target, 
                        -self.pending_damage  # Convert back to positive
                    )
                    
                    # Update the message with actual healing amount
                    message = self.pending_message
                    message = message.replace("to restore HP", f"restoring {actual_healing} HP")
                    self.pending_message = message
            
            # Display the spell message
            self.battle_system.ui.set_message(self.pending_message)
            
            # Check if target was defeated (for damage spells)
            if self.target and self.target.is_defeated():
                # Award XP to caster
                if hasattr(self.target, 'xp'):
                    xp_gained = self.target.xp
                    self.active_character.gain_experience(xp_gained)
                    self.battle_system.ui.message_log.append(f"{self.active_character.name} gained {xp_gained} XP!")
                
                # Check if all enemies are defeated
                if self.battle_system.mechanics.check_all_enemies_defeated(self.battle_system.enemies):
                    self.battle_system.victory = True
                    self.battle_system.battle_over = True
                    self.battle_system.ui.set_message("Victory! All enemies defeated!")
                    return
                else:
                    # Remove the defeated enemy from turn order
                    self.battle_system.turn_order.remove_combatant(self.target)
            
            # End current character's turn
            if self.active_character:
                self.active_character.end_turn()
            
            # Advance to next combatant if battle is not over
            if not self.battle_system.battle_over:
                current_combatant = self.battle_system.turn_order.advance()
                self.battle_system.actions.action_processing = False
    
    def _update_skill_animation(self):
        """Update skill usage animation."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_duration:
            self.character_using_skill = False
            self.animation_timer = 0
            
            # Display the skill message
            self.battle_system.ui.set_message(self.pending_message)
            
            # End current character's turn
            if self.active_character:
                self.active_character.end_turn()
            
            # Advance to next combatant
            current_combatant = self.battle_system.turn_order.advance()
            self.battle_system.actions.action_processing = False
    
    def _update_ultimate_animation(self):
        """Update ultimate ability animation."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_duration:
            self.character_using_ultimate = False
            self.animation_timer = 0
            
            # Apply ultimate effect to target
            if self.target and self.pending_damage > 0:
                actual_damage, passive_triggered, passive_message = (
                    self.battle_system.mechanics.apply_damage(
                        self.target, 
                        self.pending_damage,
                        damage_type="ultimate",
                        attacker=self.active_character,
                        battle_system=self.battle_system
                    )
                )
                
                # Handle passive response if triggered
                if passive_triggered:
                    self.counter_triggered = True
                    self.counter_message = passive_message
            
            # Display the ultimate message
            self.battle_system.ui.set_message(self.pending_message)
            
            # Check if target was defeated
            if self.target and self.target.is_defeated():
                # Award XP to character
                if hasattr(self.target, 'xp'):
                    xp_gained = self.target.xp
                    self.active_character.gain_experience(xp_gained)
                    self.battle_system.ui.message_log.append(f"{self.active_character.name} gained {xp_gained} XP!")
                
                # Check if all enemies are defeated
                if self.battle_system.mechanics.check_all_enemies_defeated(self.battle_system.enemies):
                    self.battle_system.victory = True
                    self.battle_system.battle_over = True
                    self.battle_system.ui.set_message("Victory! All enemies defeated!")
                    return
                else:
                    # Remove the defeated enemy from turn order
                    self.battle_system.turn_order.remove_combatant(self.target)
            
            # End current character's turn
            if self.active_character:
                self.active_character.end_turn()
            
            # Advance to next combatant if battle is not over
            if not self.battle_system.battle_over:
                current_combatant = self.battle_system.turn_order.advance()
                self.battle_system.actions.action_processing = False
    
    def _update_enemy_attack_animation(self):
        """Update enemy attack animation."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_duration:
            self.enemy_attacking = False
            self.animation_timer = 0
            
            # Apply damage to target (only if attack didn't miss)
            if "missed" not in self.pending_message and self.target and self.pending_damage > 0:
                # We pass the battle system and current enemy for potential passive triggers
                actual_damage, passive_triggered, passive_message = (
                    self.battle_system.mechanics.apply_damage(
                        self.target, 
                        self.pending_damage,
                        damage_type="physical",
                        attacker=self.current_enemy,
                        battle_system=self.battle_system
                    )
                )
                
                # Store passive information if triggered
                if passive_triggered:
                    self.counter_triggered = True
                    self.counter_message = passive_message
            
            # Display the standard attack message
            self.battle_system.ui.set_message(self.pending_message)
            
            # Check if target was defeated
            if self.target and self.target.is_defeated():
                # Check if all party members are defeated
                if self.battle_system.mechanics.check_all_party_defeated(self.battle_system.party.active_members):
                    self.battle_system.battle_over = True
                    self.battle_system.victory = False
                    self.battle_system.ui.set_message("Defeat! All party members have fallen!")
                    return
                else:
                    # Remove the defeated character from turn order
                    self.battle_system.turn_order.remove_combatant(self.target)
            
            # End current enemy's turn
            if self.current_enemy:
                self.current_enemy.end_turn()
            
            # Advance to next combatant if battle is not over and no counter was triggered
            if not self.battle_system.battle_over and not self.counter_triggered:
                current_combatant = self.battle_system.turn_order.advance()
                self.battle_system.actions.action_processing = False
    
    def _update_flee_animation(self):
        """Update flee animation."""
        self.animation_timer += 1
        if self.animation_timer >= self.flee_animation_duration:
            self.character_fleeing = False
            self.animation_timer = 0
            self.battle_system.ui.set_message(f"{self.active_character.name} fled from battle!")
            self.battle_system.battle_over = True
            self.battle_system.fled = True
            self.battle_system.actions.action_processing = False
    
    def _add_effect(self, effect_type, target, offset=False):
        """
        Add a visual effect.
        
        Args:
            effect_type: The type of effect to add
            target: The target entity
            offset: Whether to add random offset
        """
        # Create basic effect parameters
        effect = {
            'type': effect_type,
            'position': (target.rect.centerx, target.rect.centery),
            'size': 20,
            'duration': 15,
            'current_frame': 0,
            'color': WHITE
        }
        
        # Customize based on effect type
        if effect_type == "fire":
            effect['size'] = 30
            effect['duration'] = 20
            effect['color'] = RED
        elif effect_type == "heal":
            effect['size'] = 40
            effect['duration'] = 25
            effect['color'] = GREEN
        elif effect_type == "analyze":
            effect['size'] = 25
            effect['duration'] = 15
            effect['color'] = BLUE
        elif effect_type == "ultimate":
            effect['size'] = 35
            effect['duration'] = 30
            effect['color'] = PURPLE
            
            # Add random offset for multiple effects
            if offset:
                offset_x = random.randint(-50, 50)
                offset_y = random.randint(-50, 50)
                effect['position'] = (target.rect.centerx + offset_x, target.rect.centery + offset_y)
        
        # Add to effects list
        self.effects.append(effect)
    
    def _update_effects(self):
        """Update all visual effects."""
        # Update each effect
        for effect in self.effects[:]:  # Use a copy for safe removal
            effect['current_frame'] += 1
            if effect['current_frame'] >= effect['duration']:
                self.effects.remove(effect)
    
    def draw(self, screen):
        """
        Draw all active visual effects.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Draw each effect
        for effect in self.effects:
            # Calculate effect parameters
            progress = effect['current_frame'] / effect['duration']
            size = int(effect['size'] * (1 - progress * 0.5))  # Maintain size longer
            alpha = int(255 * (1 - progress))
            
            # Create a surface for the effect
            effect_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Draw different effects based on type
            if effect['type'] == "fire":
                self._draw_fire_effect(effect_surface, size, alpha)
            elif effect['type'] == "heal":
                self._draw_heal_effect(effect_surface, size, alpha)
            elif effect['type'] == "analyze":
                self._draw_analyze_effect(effect_surface, size, alpha)
            elif effect['type'] == "ultimate":
                self._draw_ultimate_effect(effect_surface, size, alpha)
            else:
                # Default effect
                pygame.draw.circle(effect_surface, (*effect['color'], alpha), (size, size), size)
            
            # Draw the effect at the target position
            position = effect['position']
            screen.blit(effect_surface, (position[0] - size, position[1] - size))
    
    def _draw_fire_effect(self, surface, size, alpha):
        """
        Draw a fire spell effect.
        
        Args:
            surface: The surface to draw on
            size: The effect size
            alpha: The effect alpha (transparency)
        """
        # Draw multiple overlapping circles for a fire effect
        fire_colors = [
            (255, 50, 0, alpha),     # Orange-red
            (255, 150, 0, alpha),    # Orange
            (255, 220, 0, alpha)     # Yellow
        ]
        
        for i, color in enumerate(fire_colors):
            circle_size = size * (0.8 - i * 0.2)
            offset_y = int(size * 0.1 * i)  # Offset for flame shape
            pygame.draw.circle(surface, color, (size, size - offset_y), int(circle_size))
        
        # Add some random sparks
        for _ in range(5):
            spark_x = random.randint(size // 2, size + size // 2)
            spark_y = random.randint(size // 2, size + size // 2)
            spark_size = random.randint(1, 3)
            pygame.draw.circle(surface, (255, 255, 200, alpha), (spark_x, spark_y), spark_size)
    
    def _draw_heal_effect(self, surface, size, alpha):
        """
        Draw a healing spell effect.
        
        Args:
            surface: The surface to draw on
            size: The effect size
            alpha: The effect alpha (transparency)
        """
        # Create glowing effect with circles
        glow_color = (100, 255, 150, alpha)
        pygame.draw.circle(surface, glow_color, (size, size), size)
        
        # Add some particles
        for _ in range(8):
            particle_size = size // 4
            angle = random.random() * 6.28  # Random angle in radians
            distance = random.random() * size * 0.8
            
            # Calculate particle position
            px = int(size + math.cos(angle) * distance)
            py = int(size + math.sin(angle) * distance)
            
            # Draw particle
            pygame.draw.circle(surface, (150, 255, 200, alpha), (px, py), particle_size)
        
        # Draw plus sign
        line_width = max(1, size // 8)
        pygame.draw.line(surface, (255, 255, 255, alpha), 
                        (size, size - size//2), (size, size + size//2), line_width)
        pygame.draw.line(surface, (255, 255, 255, alpha), 
                        (size - size//2, size), (size + size//2, size), line_width)
    
    def _draw_analyze_effect(self, surface, size, alpha):
        """
        Draw an analyze skill effect.
        
        Args:
            surface: The surface to draw on
            size: The effect size
            alpha: The effect alpha (transparency)
        """
        # Draw scanning lines
        for i in range(0, size * 2, size // 4):
            pygame.draw.line(surface, (0, 150, 255, alpha), (0, i), (size * 2, i), 1)
        
        # Draw targeting reticle
        pygame.draw.circle(surface, (200, 200, 255, alpha), (size, size), size, 2)
        pygame.draw.circle(surface, (200, 200, 255, alpha), (size, size), size // 2, 1)
        
        # Draw crosshairs
        pygame.draw.line(surface, (255, 255, 255, alpha), 
                        (size, size - size//2), (size, size + size//2), 1)
        pygame.draw.line(surface, (255, 255, 255, alpha), 
                        (size - size//2, size), (size + size//2, size), 1)
    
    def _draw_ultimate_effect(self, surface, size, alpha):
        """
        Draw an ultimate ability effect.
        
        Args:
            surface: The surface to draw on
            size: The effect size
            alpha: The effect alpha (transparency)
        """
        # Draw energetic burst
        for i in range(3):
            color = (255, 50 + i * 50, 50, alpha)
            radius = size * (1 - i * 0.2)
            pygame.draw.circle(surface, color, (size, size), int(radius))
        
        # Draw some energy lines
        for _ in range(8):
            angle = random.random() * 6.28  # Random angle in radians
            length = size * 1.5
            
            # Calculate line endpoints
            x1 = int(size + math.cos(angle) * (size / 3))
            y1 = int(size + math.sin(angle) * (size / 3))
            x2 = int(size + math.cos(angle) * length)
            y2 = int(size + math.sin(angle) * length)
            
            # Draw energy line
            pygame.draw.line(surface, (255, 255, 100, alpha), (x1, y1), (x2, y2), 2)
        
        # Add some bright particles
        for _ in range(12):
            px = random.randint(0, size * 2)
            py = random.randint(0, size * 2)
            particle_size = random.randint(1, 4)
            
            pygame.draw.circle(surface, (255, 255, 255, alpha), (px, py), particle_size)