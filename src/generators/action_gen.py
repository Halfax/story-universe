"""Action generation based on `CharacterManager` data.

This generator selects a character and picks an action influenced by
available traits. It intentionally keeps logic simple; replace with
domain-specific rules as needed.
"""
from typing import Any, Dict, Optional
import random


class ActionGenerator:
    """Generates simple actions for characters.

    Parameters
    - `character_manager`: an object exposing `get_characters()` and other helpers.
    """

    def __init__(self, character_manager: Any) -> None:
        self.character_manager = character_manager

    def generate_action(self) -> Optional[Dict[str, Any]]:
        """Return an action dict for a selected character, or `None` if no characters.

        Returned dict shape:
            { 'character_id': str, 'action': str, 'traits': list }
        """
        characters = self.character_manager.get_characters()
        if not characters:
            return None
        char = random.choice(characters)

        # Traits may be list or dict; normalize to list of simple values where possible
        traits = char.get('traits') or []
        if isinstance(traits, dict):
            # convert dict to simple key list
            traits = list(traits.keys())

        if traits:
            trait = random.choice(traits)
            if trait == 'brave':
                action = 'explore'
            elif trait == 'cautious':
                action = 'hide'
            elif trait == 'aggressive':
                action = 'attack'
            else:
                action = 'wait'
        else:
            action = random.choice(['explore', 'hide', 'attack', 'wait'])

        return {
            'character_id': char.get('id') or char.get('character_id') or char.get('name'),
            'action': action,
            'traits': traits
        }
