# WorldState container for shared use

class WorldState:
    def __init__(self, characters, locations, factions, events, rules):
        self.characters = characters
        self.locations = locations
        self.factions = factions
        self.events = events
        self.rules = rules
