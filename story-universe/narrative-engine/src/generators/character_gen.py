# Character loader and state manager for Evo-X2 Narrative Engine
import requests

PI_API_CHARACTERS = "http://192.168.0.215:8001/world/characters"

class CharacterManager:
    def __init__(self):
        self.characters = []

    def fetch_characters(self):
        try:
            resp = requests.get(PI_API_CHARACTERS, timeout=5)
            resp.raise_for_status()
            self.characters = resp.json()
            print(f"[Evo-X2] Loaded {len(self.characters)} characters from Pi.")
        except Exception as e:
            print(f"[Evo-X2] Failed to load characters: {e}")
        return self.characters

    def get_characters(self):
        return self.characters
