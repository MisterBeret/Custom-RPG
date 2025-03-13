"""
Battle action handling for the RPG game.
This module handles executing different battle actions such as attacks, spells, skills, etc.
"""
import random

class BattleActions:
    """
    Handles processing of all combat actions for both players and enemies.
    Works with BattleSystem to execute player commands and enemy AI decisions.
    """
    def __init__(self, battle_system):
        """
        Initialize the battle actions processor.
        
        Args:
            battle_system: The parent battle system
        """
        self.battle_system = battle_system
        
        # Action state tracking
        self.action_processing = False
        self.active_character = None
        self.target = None
        
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
    
    def process_action(self, action, character=None):
        """
        Process a player action.
        
        Args:
            action: The action to process ("ATTACK", "DEFEND", "MOVE", etc.)
            character: The character performing the action (uses current turn character if None)
        """
        # Use the active character if none is provided
        if character is None:
            character = self.battle_system.get_current_character()
            
        if not character or self.action_processing:
            return
            
        self.action_processing = True
        self.active_character = character
        
        # Execute the requested action
        if action == "ATTACK":
            self._handle_attack(character)
        elif action == "DEFEND":
            self._handle_defend(character)
        elif action == "MOVE":
            self._handle_flee(character)
        elif action == "ITEM":
            # Enter inventory selection mode (handled externally)
            self.action_processing = False
        elif action == "SKILL":
            self._handle_skill(character)
        elif action == "MAGIC":
            self._handle_magic(character)
        elif action == "ULTIMATE":
            self._handle_ultimate(character)
        elif action == "STATUS":
            self._handle_status(character)
    
    def _handle_attack(self, character):
        """Handle attack command initiation."""
        # In multi-enemy battles, enter targeting mode
        if len(self.battle_system.enemies) > 1:
            self.battle_system.ui.in_targeting_mode = True
            self.battle_system.ui.targeting_system.start_targeting(
                character, 
                self.battle_system.ui.targeting_system.ENEMIES
            )
            self.battle_system.set_message(f"{character.name} is targeting an enemy")
            self.action_processing = False  # Allow targeting input
        else:
            # With just one enemy, attack it directly
            self.perform_attack(character, self.battle_system.enemies[0])
    
    def _handle_defend(self, character):
        """Handle defend command."""
        character.defend()
        self.battle_system.animations.character_defending = True
        self.battle_system.set_message(
            f"{character.name} is defending! Incoming damage reduced and evasion increased!"
        )
        
        # Reset action delay timer
        self.battle_system.animations.action_delay = 0
    
    def _handle_flee(self, character):
        """Handle flee/move command."""
        self.battle_system.animations.character_fleeing = True
        self.battle_system.animations.animation_timer = 0
        self.battle_system.animations.active_character = character
        self.battle_system.set_message(f"{character.name} tried to flee!")
    
    def _handle_skill(self, character):
        """Handle skill command initiation."""
        skill_names = character.skillset.get_skill_names()
        if skill_names:
            self.battle_system.ui.in_skill_menu = True
            self.battle_system.ui.selected_skill_option = 0
            self.battle_system.ui.active_character = character
            self.action_processing = False  # Allow skill selection
        else:
            self.battle_system.set_message(f"{character.name} doesn't know any skills!")
            self.action_processing = False
    
    def _handle_magic(self, character):
        """Handle magic command initiation."""
        spell_names = character.spellbook.get_spell_names()
        if spell_names:
            self.battle_system.ui.in_spell_menu = True
            self.battle_system.ui.selected_spell_option = 0
            self.battle_system.ui.active_character = character
            self.action_processing = False  # Allow spell selection
        else:
            self.battle_system.set_message(f"{character.name} doesn't know any spells!")
            self.action_processing = False
    
    def _handle_ultimate(self, character):
        """Handle ultimate command initiation."""
        ultimate_names = character.ultimates.get_ultimate_names()
        if ultimate_names:
            self.battle_system.ui.in_ultimate_menu = True
            self.battle_system.ui.selected_ultimate_option = 0
            self.battle_system.ui.active_character = character
            self.action_processing = False  # Allow ultimate selection
        else:
            self.battle_system.set_message(f"{character.name} doesn't have any ultimate abilities!")
            self.action_processing = False
    
    def _handle_status(self, character):
        """Handle status command."""
        self.battle_system.set_message(
            f"{character.name} STATUS - HP: {character.hp}/{character.max_hp}, SP: {character.sp}/{character.max_sp}"
        )
        self.action_processing = False
    
    def perform_attack(self, attacker, target):
        """
        Execute an attack from one character to a target.
        
        Args:
            attacker: The attacking character/enemy
            target: The target of the attack
        """
        # Start attack animation
        self.battle_system.animations.character_attacking = True
        self.battle_system.animations.animation_timer = 0
        self.battle_system.animations.active_character = attacker
        self.battle_system.animations.target = target
        self.action_processing = True
        
        # Calculate and use hit chance
        hit_chance = self.battle_system.mechanics.calculate_hit_chance(attacker, target)
        attack_hits = random.random() < hit_chance
        
        if attack_hits:
            # Calculate damage
            damage = self.battle_system.mechanics.calculate_damage(attacker, target)
            
            # Store damage for application after animation
            self.battle_system.animations.pending_damage = damage
            
            # Set message based on attacker and target
            attacker_name = attacker.name
            target_name = target.name
            
            self.battle_system.animations.pending_message = f"{attacker_name} attacked {target_name} for {damage} damage!"
        else:
            # Attack missed
            attacker_name = attacker.name
            target_name = target.name
            self.battle_system.animations.pending_message = f"{attacker_name}'s attack on {target_name} missed!"
            self.battle_system.animations.pending_damage = 0
    
    def cast_spell(self, caster, target, spell):
        """
        Cast a spell from a character to a target.
        
        Args:
            caster: The character casting the spell
            target: The target of the spell
            spell: The spell being cast
        """
        # Start spell casting animation
        self.battle_system.animations.character_casting = True
        self.battle_system.animations.animation_timer = 0
        self.battle_system.animations.active_character = caster
        self.battle_system.animations.target = target
        self.battle_system.animations.current_spell = spell
        self.action_processing = True
        
        # Apply SP cost
        caster.use_sp(spell.sp_cost)
        
        # Handle spell effects based on type
        if spell.effect_type == "damage":
            # Calculate magic damage
            damage = self.battle_system.mechanics.calculate_magic_damage(caster, target, spell.base_power)
            
            # Store damage for application after animation
            self.battle_system.animations.pending_damage = damage
            
            # Set message
            caster_name = caster.name
            target_name = target.name
            self.battle_system.animations.pending_message = f"{caster_name} cast {spell.name} on {target_name} for {damage} magic damage!"
        
        elif spell.effect_type == "healing":
            # Calculate healing amount (add intelligence to base power)
            healing_amount = spell.base_power + caster.intelligence
            
            # Store healing info for application after animation
            self.battle_system.animations.pending_damage = -healing_amount  # Negative indicates healing
            
            # Set message
            caster_name = caster.name
            target_name = target.name
            self.battle_system.animations.pending_message = f"{caster_name} cast {spell.name} on {target_name} to restore HP!"
    
    def use_skill(self, user, target, skill):
        """
        Use a skill from a character on a target.
        
        Args:
            user: The character using the skill
            target: The target of the skill
            skill: The skill being used
        """
        # Start skill animation
        self.battle_system.animations.character_using_skill = True
        self.battle_system.animations.animation_timer = 0
        self.battle_system.animations.active_character = user
        self.battle_system.animations.target = target
        self.battle_system.animations.current_skill = skill
        self.action_processing = True
        
        # Apply resource costs
        if skill.cost_type == "sp" or skill.cost_type == "both":
            user.use_sp(skill.sp_cost)
            
        if skill.cost_type == "hp" or skill.cost_type == "both":
            self.battle_system.mechanics.apply_damage(user, skill.hp_cost, "self-inflicted")
        
        # Handle skill effects based on type
        if skill.effect_type == "analyze":
            # Get target stats
            target_stats = (
                f"{target.name} stats:\n"
                f"HP: {target.hp}/{target.max_hp}\n"
                f"ATK: {target.attack}\n"
                f"DEF: {target.defense}\n"
                f"SPD: {target.spd}\n"
                f"ACC: {target.acc}\n"
                f"RES: {target.resilience}"
            )
            
            # Set message
            user_name = user.name
            target_name = target.name
            self.battle_system.animations.pending_message = f"{user_name} used {skill.name} on {target_name}! {target_stats}"
            self.battle_system.animations.pending_damage = 0
    
    def use_ultimate(self, user, target, ultimate):
        """
        Use an ultimate ability from a character on a target.
        
        Args:
            user: The character using the ultimate
            target: The target of the ultimate
            ultimate: The ultimate ability being used
        """
        # Start ultimate animation
        self.battle_system.animations.character_using_ultimate = True
        self.battle_system.animations.animation_timer = 0
        self.battle_system.animations.active_character = user
        self.battle_system.animations.target = target
        self.battle_system.animations.current_ultimate = ultimate
        self.action_processing = True
        
        # Mark ultimate as used
        ultimate.available = False
        
        # Handle ultimate effects based on type
        if ultimate.effect_type == "damage":
            # Calculate damage with power multiplier
            damage = int(user.attack * ultimate.power_multiplier)
            
            # Store damage for application after animation
            self.battle_system.animations.pending_damage = damage
            
            # Set message
            user_name = user.name
            target_name = target.name
            self.battle_system.animations.pending_message = f"{user_name} used {ultimate.name} on {target_name} for a massive {damage} damage!"
    
    def process_enemy_turn(self):
        """Process the current enemy's turn in battle."""
        # Get the current enemy
        current_enemy = self.battle_system.get_current_enemy()
        if not current_enemy:
            return
        
        # Start enemy attack animation
        self.battle_system.animations.enemy_attacking = True
        self.battle_system.animations.animation_timer = 0
        self.battle_system.animations.current_enemy = current_enemy
        self.action_processing = True
        
        # Choose a target from active party members
        valid_targets = [c for c in self.battle_system.party.active_members if not c.is_defeated()]
        if not valid_targets:
            # No valid targets, end battle
            self.battle_system.battle_over = True
            self.battle_system.victory = False
            self.battle_system.set_message("Defeat! All party members have fallen!")
            return
        
        # Select random target for now (could be more strategic in the future)
        target = random.choice(valid_targets)
        self.battle_system.animations.target = target
        
        # Calculate hit chance and determine if attack hits
        hit_chance = self.battle_system.mechanics.calculate_hit_chance(current_enemy, target)
        attack_hits = random.random() < hit_chance
        
        if attack_hits:
            # Calculate damage
            damage = self.battle_system.mechanics.calculate_damage(current_enemy, target)
            self.battle_system.animations.pending_damage = damage
            
            # Prepare message
            enemy_name = current_enemy.name
            target_name = target.name
            
            if target.defending:
                original_damage = damage * 2  # Approximate original damage
                self.battle_system.animations.pending_message = f"{enemy_name} attacked {target_name}! Defense reduced damage from {original_damage} to {damage}!"
            else:
                self.battle_system.animations.pending_message = f"{enemy_name} attacked {target_name} for {damage} damage!"
        else:
            # Attack missed
            enemy_name = current_enemy.name
            target_name = target.name
            
            if target.defending:
                self.battle_system.animations.pending_message = f"{enemy_name}'s attack on {target_name} missed! Their defensive stance helped them evade!"
            else:
                self.battle_system.animations.pending_message = f"{enemy_name}'s attack on {target_name} missed!"
                
            self.battle_system.animations.pending_damage = 0
    
    def select_target(self, attacker, potential_targets, target_type="random"):
        """
        Select a target for an action based on specified strategy.
        
        Args:
            attacker: The attacking entity
            potential_targets: List of potential targets
            target_type: Targeting strategy ("random", "weakest", "strongest", etc.)
            
        Returns:
            The selected target
        """
        if not potential_targets:
            return None
            
        if target_type == "random":
            return random.choice(potential_targets)
        elif target_type == "weakest":
            return min(potential_targets, key=lambda t: t.hp)
        elif target_type == "strongest":
            return max(potential_targets, key=lambda t: t.attack)
        elif target_type == "lowest_hp_percent":
            return min(potential_targets, key=lambda t: t.hp / t.max_hp)
        else:
            # Default to random
            return random.choice(potential_targets)