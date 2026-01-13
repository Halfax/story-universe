"""
Event Validation Middleware for Chronicle Keeper
-----------------------------------------------
This module provides event validation against schemas and basic rules
before they reach the Continuity Validator.
"""

from typing import Dict, List, Optional, Any, Tuple
import re
from datetime import datetime
from uuid import UUID, uuid4

# Base event schema that all events must adhere to
BASE_EVENT_SCHEMA = {
    "type": "object",
    "required": ["id", "type", "timestamp", "source", "data"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "type": {"type": "string", "pattern": "^[a-z]+\\.(?:[a-z]+\\.)*[a-z]+$"},
        "timestamp": {"type": "integer", "minimum": 1577836800},  # 2020-01-01
        "source": {"type": "string", "pattern": "^[a-z0-9_-]+$"},
        "data": {"type": "object"},
        "metadata": {
            "type": "object",
            "properties": {
                "causationId": {"type": "string", "format": "uuid"},
                "correlationId": {"type": "string", "format": "uuid"},
                "schemaVersion": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
            },
        },
    },
}

# Event type specific schemas
EVENT_SCHEMAS = {
    "character.move": {
        "type": "object",
        "required": ["character_id", "from_location_id", "to_location_id"],
        "properties": {
            "character_id": {"type": "string", "format": "uuid"},
            "from_location_id": {"type": "string", "format": "uuid"},
            "to_location_id": {"type": "string", "format": "uuid"},
            "method": {"type": "string", "enum": ["walk", "teleport", "portal"]},
            "time_taken": {"type": "integer", "minimum": 0},
        },
    },
    "character.update": {
        "type": "object",
        "required": ["character_id"],
        "properties": {
            "character_id": {"type": "string", "format": "uuid"},
            "name": {"type": "string", "minLength": 1, "maxLength": 100},
            "traits": {"type": "object", "additionalProperties": {"type": "string"}},
            "status": {"type": "string", "enum": ["active", "inactive", "deceased"]},
        },
    },
    "world.tick": {
        "type": "object",
        "required": ["tick_number"],
        "properties": {
            "tick_number": {"type": "integer", "minimum": 0},
            "world_time": {"type": "integer", "minimum": 0},
        },
    },
}


class EventValidationError(ValueError):
    """Raised when an event fails validation."""

    def __init__(self, message: str, errors: Optional[Dict] = None):
        super().__init__(message)
        self.errors = errors or {}


class EventValidator:
    """Validates events against schemas and basic rules."""

    def __init__(self, strict: bool = True):
        """Initialize the validator.

        Args:
            strict: If True, only known event types are allowed.
        """
        self.strict = strict

    def validate(self, event: Dict) -> Tuple[bool, List[str]]:
        """Validate an event against its schema.

        Args:
            event: The event to validate.

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Check base schema first
        base_errors = self._validate_against_schema(event, BASE_EVENT_SCHEMA)
        if base_errors:
            errors.extend([f"Base validation failed: {e}" for e in base_errors])
            return False, errors

        # Get event type and check if it's known
        event_type = event.get("type")

        if not event_type:
            errors.append("Missing required field: type")
            return False, errors

        # If strict mode, only allow known event types
        if self.strict and event_type not in EVENT_SCHEMAS:
            errors.append(f"Unknown event type: {event_type}")
            return False, errors

        # Validate against event-specific schema if it exists
        if event_type in EVENT_SCHEMAS:
            schema_errors = self._validate_against_schema(
                event.get("data", {}), EVENT_SCHEMAS[event_type]
            )
            if schema_errors:
                errors.extend([f"Data validation failed: {e}" for e in schema_errors])

        # Additional semantic validations
        self._validate_semantics(event, errors)

        return len(errors) == 0, errors

    def _validate_against_schema(self, data: Any, schema: Dict) -> List[str]:
        """Validate data against a JSON Schema."""
        from jsonschema import validate, ValidationError

        try:
            validate(instance=data, schema=schema)
            return []
        except ValidationError as e:
            return [str(e)]

    def _validate_semantics(self, event: Dict, errors: List[str]) -> None:
        """Perform semantic validations that can't be expressed in JSON Schema."""
        event_type = event.get("type", "")
        data = event.get("data", {})

        # Check timestamp is not in the future (with 5s leeway for clock skew)
        import time as _time

        now = int(_time.time())
        try:
            et = int(event.get("timestamp", 0))
        except Exception:
            et = event.get("timestamp", 0)
        if et > now + 5:
            errors.append("Event timestamp is in the future")

        # Check UUID formats
        for field in ["id", "metadata.causationId", "metadata.correlationId"]:
            value = self._get_nested(event, field.split("."))
            if value and not self._is_valid_uuid(value):
                errors.append(f"Invalid UUID format for {field}: {value}")

        # Event type specific validations
        if event_type == "character.move":
            if data.get("from_location_id") == data.get("to_location_id"):
                errors.append("Source and destination locations cannot be the same")

    @staticmethod
    def _get_nested(data: Dict, keys: List[str]) -> Any:
        """Safely get a value from a nested dictionary."""
        result = data
        for key in keys:
            if not isinstance(result, dict) or key not in result:
                return None
            result = result[key]
        return result

    @staticmethod
    def _is_valid_uuid(uuid_string: str) -> bool:
        """Check if a string is a valid UUID."""
        try:
            UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False


# Singleton instance for easy import
validator = EventValidator()
