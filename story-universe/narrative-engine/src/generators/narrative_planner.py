# NarrativePlanner: Handles basic narrative planning and story arc generation
#
# Usage:
#   planner = NarrativePlanner(character_manager)
#   plan = planner.generate_plan()
#   if plan:
#       # Use plan['arc'], plan['characters'], plan['summary']
#
# This module is intended for integration into event_generator.py to generate narrative planning events.

import random

class NarrativePlanner:
    def __init__(self, character_manager):
        """
        Initialize with a CharacterManager instance.
        """
        self.character_manager = character_manager

    def generate_plan(self):
        """
        Generate a simple narrative arc involving 1-3 characters.
        Returns a dict with arc, characters, and summary, or None if no characters.
        """
        characters = self.character_manager.get_characters()
        if not characters:
            return None
        involved = random.sample(characters, min(len(characters), random.choice([1,2,3])))
        arc = random.choice(["quest", "conflict", "alliance", "mystery"])
        summary = f"{'/'.join([str(c.get('name') or c.get('id')) for c in involved])} in a {arc} arc."
        return {
            'arc': arc,
            'characters': [c.get('id') or c.get('character_id') or c.get('name') for c in involved],
            'summary': summary
        }
