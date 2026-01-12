# Action generation based on character traits for Evo-X2 Narrative Engine
import random

class ActionGenerator:
    def __init__(self, character_manager):
        self.character_manager = character_manager

    def generate_action(self):
        characters = self.character_manager.get_characters()
        if not characters:
            return None
        char = random.choice(characters)
        # Example: Use a 'traits' field if present, otherwise random
        traits = char.get('traits', [])
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
