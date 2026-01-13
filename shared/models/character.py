from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from .schemas import CharacterSchema


class Character(CharacterSchema):
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        return cls.model_validate(data)

    def apply_delta(self, delta: Dict[str, Any]) -> None:
        for k, v in delta.items():
            if isinstance(v, (int, float)):
                self.attributes[k] = self.attributes.get(k, 0) + v
            else:
                self.attributes[k] = v
        self.updated_at = datetime.utcnow().isoformat()
