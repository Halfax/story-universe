# MovementEngine: Handles character movement logic for Evo-X2 Narrative Engine
#
# Usage:
#   movement_engine = MovementEngine(character_manager)
#   movement = movement_engine.move_character()
#   if movement:
#       # Use movement['character_id'] and movement['new_location']
#
# This module is integrated into event_generator.py to generate movement events.

import random

class MovementEngine:
    def __init__(self, character_manager):
        """
        Initialize with a CharacterManager instance.
        """
        self.character_manager = character_manager

    def move_character(self):
        """
        Select a random character and move them to a random location.
        Returns a dict with character_id and new_location, or None if no characters.
        """
        characters = self.character_manager.get_characters()
        if not characters:
            return None
        char = random.choice(characters)
        # Example: Move to a random location (replace with real logic)
        possible_locations = [100, 200, 300]
        new_location = random.choice(possible_locations)
        return {
            'character_id': char.get('id') or char.get('character_id') or char.get('name'),
            'new_location': new_location
        }
