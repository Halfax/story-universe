# RelationshipEngine: Handles character relationship tracking and updates
#
# Usage:
#   relationship_engine = RelationshipEngine(character_manager)
#   update = relationship_engine.update_relationships()
#   if update:
#       # Use update['character_id'], update['target_id'], update['change']
#
# This module is intended for integration into event_generator.py to generate relationship events.

import random

class RelationshipEngine:
    def __init__(self, character_manager):
        """
        Initialize with a CharacterManager instance.
        """
        self.character_manager = character_manager

    def update_relationships(self):
        """
        Randomly select two characters and update their relationship.
        Returns a dict with character_id, target_id, and change, or None if not enough characters.
        """
        characters = self.character_manager.get_characters()
        if not characters or len(characters) < 2:
            return None
        char1, char2 = random.sample(characters, 2)
        # Example: Randomly increase or decrease relationship
        change = random.choice(["improve", "worsen"])
        return {
            'character_id': char1.get('id') or char1.get('character_id') or char1.get('name'),
            'target_id': char2.get('id') or char2.get('character_id') or char2.get('name'),
            'change': change
        }
