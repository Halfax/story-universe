"""NarrativePlanner: generate simple story arcs using character data.

This is a lightweight planner that selects a small set of characters and
returns a short description of a potential narrative arc. Replace or
extend with multi-step planning logic as needed.
"""
from typing import Any, Dict, Optional
import random


class NarrativePlanner:
    def __init__(self, character_manager: Any) -> None:
        """Initialize with a `CharacterManager`-like object."""
        self.character_manager = character_manager

    def generate_plan(self) -> Optional[Dict[str, Any]]:
        """Create a minimal narrative plan involving 1-3 characters.

        Returns a dict: { 'arc', 'characters', 'summary' } or None.
        """
        characters = self.character_manager.get_characters()
        if not characters:
            return None

        n = min(len(characters), random.choice([1, 2, 3]))
        involved = random.sample(characters, n)
        arc = random.choice(["quest", "conflict", "alliance", "mystery"])
        summary = f"{'/'.join([str(c.get('name') or c.get('id')) for c in involved])} in a {arc} arc."
        return {
            'arc': arc,
            'characters': [c.get('id') or c.get('character_id') or c.get('name') for c in involved],
            'summary': summary
        }
