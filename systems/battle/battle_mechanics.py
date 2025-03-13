class BattleMechanics:
    def _calculate_hit_chance(self, attacker, defender):
        """
        Calculate the chance to hit based on attacker's ACC and defender's SPD.
        
        Args:
            attacker: The attacking entity
            defender: The defending entity
            
        Returns:
            float: The chance to hit as a decimal between 0 and 1
        """
        # Base formula: When ACC equals SPD, hit chance is 0.9 (90%)
        # For each point ACC is higher than SPD, hit chance increases by 0.05
        # For each point ACC is lower than SPD, hit chance decreases by 0.2
        
        if attacker.acc >= defender.spd:
            # High accuracy case - 90% base hit chance, +5% per point above opponent's speed
            hit_chance = 0.9 + (attacker.acc - defender.spd) * 0.05
            # Cap at 99% hit chance (always a small chance to miss)
            hit_chance = min(0.99, hit_chance)
        else:
            # Low accuracy case - lose 20% hit chance per point below opponent's speed
            hit_chance = 0.9 - (defender.spd - attacker.acc) * 0.2
            # Minimum 10% hit chance (always a small chance to hit)
            hit_chance = max(0.1, hit_chance)
    
        # If defender is defending, reduce hit chance by 25%
        if defender.defending:
            hit_chance = max(0, hit_chance - 0.25)
        
        return hit_chance
    
    def _calculate_damage(self, attacker, defender):
        """
        Calculate damage based on attacker's ATK and defender's DEF stats.
        
        Args:
            attacker: The attacking entity
            defender: The defending entity
        
        Returns:
            int: The calculated damage amount (minimum 0)
        """
        # Calculate base damage as attacker's attack minus defender's defense
        damage = max(1, attacker.attack - defender.defense)
    
        # If defender is defending, reduce all damage by 50% (rounded up)
        if defender.defending:
            import math
            damage = math.ceil(damage / 2)
    
        return damage
    
    def _calculate_magic_damage(self, caster, target, base_power):
        """
        Calculate magic damage based on caster's INT and target's RES stats.
    
        Args:
            caster: The entity casting the spell
            target: The target of the spell
            base_power: Base power of the spell
        
        Returns:
            int: The calculated magic damage amount (minimum 0)
        """
        # Magic damage formula: (caster's INT + spell base power) - target's RES
        damage = max(1, (caster.intelligence + base_power) - target.resilience)

        # If target is defending, reduce all damage by 50% (rounded up)
        if target.defending:
            import math
            damage = math.ceil(damage / 2)
    
        return damage
        
    def _check_all_enemies_defeated(self):
        """
        Check if all enemies are defeated.
        
        Returns:
            bool: True if all enemies are defeated, False otherwise
        """
        return all(enemy.is_defeated() for enemy in self.enemies)
    
    def _check_all_party_defeated(self):
        """
        Check if all party members are defeated.
        
        Returns:
            bool: True if all party members are defeated, False otherwise
        """
        return all(character.is_defeated() for character in self.party.active_members)
        
    def apply_damage(self, target, amount, damage_type="physical", attacker=None, battle_system=None):
        """
        Apply damage to a target, handling defense and passive ability triggers.
        
        Args:
            target: The entity receiving damage
            amount: Amount of damage to apply
            damage_type: Type of damage ("physical", "magical", etc.)
            attacker: The entity causing the damage (for passive triggers)
            battle_system: Reference to battle system (for passive effects)
            
        Returns:
            tuple: (actual_damage, passive_triggered, passive_message)
        """
        # Store original health to calculate actual damage dealt
        original_hp = target.hp
        
        # Apply defense reduction for defending targets
        if target.defending and damage_type == "physical":
            # Defenders take 50% damage (rounded up)
            import math
            amount = math.ceil(amount / 2)
        
        # Apply damage to target
        target.hp -= amount
        if target.hp < 0:
            target.hp = 0
            
        # Calculate actual damage dealt (may be less if target had low HP)
        actual_damage = original_hp - target.hp
        
        # Check for passive ability triggers if needed
        passive_triggered = False
        passive_message = ""
        
        if attacker and battle_system and amount > 0:
            # Only check for passive triggers if the target has a passives attribute
            if hasattr(target, 'passives'):
                passive_triggered, passive_message = target.passives.trigger_passive(
                    trigger_type="on_hit",
                    battle_system=battle_system,
                    entity=target,
                    target=attacker
                )
        
        # Return the results
        return actual_damage, passive_triggered, passive_message
        
    def apply_healing(self, target, amount, source=None):
        """
        Apply healing to a target.
        
        Args:
            target: The entity receiving healing
            amount: Amount of healing to apply
            source: The source of healing (character, item, etc.)
            
        Returns:
            int: The actual amount healed
        """
        # Store original HP to calculate actual healing
        original_hp = target.hp
        
        # Apply healing (capped at max_hp)
        target.hp = min(target.hp + amount, target.max_hp)
        
        # Calculate actual healing done (may be less if target was nearly full HP)
        actual_healing = target.hp - original_hp
        
        return actual_healing