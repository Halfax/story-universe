# Character basics for shared use

class Character:
    def __init__(self, id, name, age, traits, location_id, status):
        self.id = id
        self.name = name
        self.age = age
        self.traits = traits
        self.location_id = location_id
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "traits": self.traits,
            "location_id": self.location_id,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            name=d.get("name"),
            age=d.get("age"),
            traits=d.get("traits", {}),
            location_id=d.get("location_id"),
            status=d.get("status", "alive"),
        )
