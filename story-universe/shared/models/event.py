# Event, TickEvent models for shared use

class Event:
    def __init__(self, id, type, timestamp, data):
        self.id = id
        self.type = type
        self.timestamp = timestamp
        self.data = data

class TickEvent(Event):
    def __init__(self, id, timestamp, data):
        super().__init__(id, "tick", timestamp, data)
