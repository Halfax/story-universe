# MovementEngine: Handles character movement logic for Evo-X2 Narrative Engine
#
# Usage:
#   movement_engine = MovementEngine(character_manager)
#   movement = movement_engine.move_character()
#   if movement:
#       # Use movement['character_id'] and movement['new_location']
#
# This module is integrated into event_generator.py to generate movement events.

"""MovementEngine: simple movement logic using `CharacterManager`.

This module provides a lightweight placeholder for movement events.
Replace `possible_locations` with real location lookup logic.
"""
from typing import Any, Dict, Optional
import random


class MovementEngine:
    def __init__(self, character_manager: Any) -> None:
        """Initialize with a `CharacterManager`-like object."""
        self.character_manager = character_manager

    def move_character(self) -> Optional[Dict[str, Any]]:
        """Select a random character and assign them a new location.

        Returns a dict: { 'character_id': str, 'new_location': Any } or None.
        """
        characters = self.character_manager.get_characters()
        if not characters:
            return None
        char = random.choice(characters)

        # TODO: Replace with a real location selection strategy
        possible_locations = [100, 200, 300]
        new_location = random.choice(possible_locations)

        return {
            'character_id': char.get('id') or char.get('character_id') or char.get('name'),
            'new_location': new_location
        }
