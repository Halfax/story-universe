# FactionEngine: Handles basic faction logic and events
#
# Usage:
#   faction_engine = FactionEngine(character_manager)
#   event = faction_engine.generate_faction_event()
#   if event:
#       # Use event['faction'], event['action'], event['summary']
#
# This module is intended for integration into event_generator.py to generate faction-related events.

"""FactionEngine: simple faction events generator.

This module currently uses a static faction list. In future it can
derive factions from `CharacterManager` (e.g., character.faction).
"""
from typing import Any, Dict, Optional
import random


class FactionEngine:
    def __init__(self, character_manager: Any) -> None:
        """Initialize with a `CharacterManager`-like object."""
        self.character_manager = character_manager
        # static placeholder factions for prototyping
        self.factions = ["Red Order", "Blue Syndicate", "Green League"]

    def generate_faction_event(self) -> Optional[Dict[str, Any]]:
        """Generate a simple faction event.

        Returns a dict with keys: `faction`, `action`, `target`, `summary`.
        """
        if not self.factions:
            return None
        faction = random.choice(self.factions)
        action = random.choice(["recruits", "declares war on", "forms alliance with"])
        target = random.choice([f for f in self.factions if f != faction])
        summary = f"Faction {faction} {action} {target}."
        return {
            'faction': faction,
            'action': action,
            'target': target,
            'summary': summary
        }
