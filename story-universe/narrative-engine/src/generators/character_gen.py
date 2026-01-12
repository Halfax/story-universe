"""Character loader and state manager for the Evo‑X2 Narrative Engine.

Responsibilities:
- Fetch character list from the Chronicle Keeper API
- Provide lookup helpers for generators

This module exposes `CharacterManager` which keeps a local cache of
characters and provides simple query methods.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import time
import requests
from src.config import CHRONICLE_BASE


class CharacterManager:
    """Maintains a cached list of characters from the Chronicle Keeper.

    Usage:
        cm = CharacterManager()
        cm.fetch_characters()
        chars = cm.get_characters()
        c = cm.get_character("1")
    """

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or CHRONICLE_BASE
        self._endpoint = f"{self.base_url}/world/characters"
        self.characters: List[Dict[str, Any]] = []
        self._last_fetch: Optional[float] = None

    def fetch_characters(self, force: bool = False, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """Fetch the character list from the Pi API and update the cache.

        If `force` is False, this will skip fetching when the cache is populated.
        Returns the cached list (possibly empty on error).
        """
        if self.characters and not force:
            return self.characters

        try:
            resp = requests.get(self._endpoint, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            # Expecting a list; be defensive
            if isinstance(data, list):
                self.characters = data
            else:
                # If the API returned a dict wrapper, try to extract common keys
                if isinstance(data, dict) and "characters" in data:
                    self.characters = data["characters"]
                else:
                    self.characters = []

            self._last_fetch = time.time()
            print(f"[Evo-X2] Loaded {len(self.characters)} characters from Pi.")
        except Exception as e:
            print(f"[Evo-X2] Failed to load characters: {e}")
        return self.characters

    def get_characters(self) -> List[Dict[str, Any]]:
        """Return the locally cached characters."""
        return self.characters

    def get_character(self, char_id: Any) -> Optional[Dict[str, Any]]:
        """Return a single character by id (string or int), or None if not found."""
        sid = str(char_id)
        for c in self.characters:
            # characters may store id under different keys; try common ones
            for key in ("id", "character_id", "uuid"):
                if key in c and str(c[key]) == sid:
                    return c
        return None

    def find_by_trait(self, trait_name: str, trait_value: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Find characters that have a trait name (and optional value).

        Example: `find_by_trait('occupation', 'farmer')`.
        """
        results: List[Dict[str, Any]] = []
        for c in self.characters:
            traits = c.get("traits") or c.get("attributes") or {}
            # traits may be a dict or list of dicts
            if isinstance(traits, dict):
                if trait_name in traits:
                    if trait_value is None or traits[trait_name] == trait_value:
                        results.append(c)
            elif isinstance(traits, list):
                for t in traits:
                    if isinstance(t, dict) and t.get("name") == trait_name:
                        if trait_value is None or t.get("value") == trait_value:
                            results.append(c)
                            break
        return results

    def refresh(self, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """Force a reload from the API and return the new cache."""
        return self.fetch_characters(force=True, timeout=timeout)

