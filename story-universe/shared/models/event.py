# Event, TickEvent models for shared use

class Event:
    def __init__(self, id, type, timestamp, data):
        self.id = id
        self.type = type
        self.timestamp = timestamp
        self.data = data

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            type=d.get("type"),
            timestamp=d.get("timestamp"),
            data=d.get("data", {}),
        )

class TickEvent(Event):
    def __init__(self, id, timestamp, data):
        super().__init__(id, "tick", timestamp, data)

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            timestamp=d.get("timestamp"),
            data=d.get("data", {}),
        )
