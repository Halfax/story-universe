# Event Validator

The Event Validator is a middleware component that validates events against defined schemas and rules before they reach the Continuity Validator. It ensures that all events conform to the expected structure and contain valid data.

## Features

- **Schema Validation**: Validates events against JSON Schema definitions
- **Type Checking**: Ensures all fields are of the correct type
- **Required Fields**: Verifies all required fields are present
- **UUID Validation**: Validates UUID formats for ID fields
- **Timestamp Validation**: Ensures timestamps are not in the future
- **Semantic Validation**: Performs event-specific validations
- **Strict Mode**: Option to allow or reject unknown event types

## Usage

```python
from src.services.event_validator import validator

# Example event
event = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "character.move",
    "timestamp": 1640995200,
    "source": "test_source",
    "data": {
        "character_id": "550e8400-e29b-41d4-a716-446655440001",
        "from_location_id": "550e8400-e29b-41d4-a716-446655440002",
        "to_location_id": "550e8400-e29b-41d4-a716-446655440003"
    }
}

# Validate the event
is_valid, errors = validator.validate(event)

if is_valid:
    print("Event is valid!")
else:
    print("Validation errors:", errors)
```

## Event Schema

All events must adhere to the base event schema:

```json
{
  "type": "object",
  "required": ["id", "type", "timestamp", "source", "data"],
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "type": {"type": "string", "pattern": "^[a-z]+\\\\.(?:[a-z]+\\\\.)*[a-z]+$"},
    "timestamp": {"type": "integer", "minimum": 1577836800},
    "source": {"type": "string", "pattern": "^[a-z0-9_-]+$"},
    "data": {"type": "object"},
    "metadata": {
      "type": "object",
      "properties": {
        "causationId": {"type": "string", "format": "uuid"},
        "correlationId": {"type": "string", "format": "uuid"},
        "schemaVersion": {"type": "string", "pattern": "^\\\\d+\\\\.\\\\d+\\\\.\\\\d+$"}
      }
    }
  }
}
```

## Event Types

### character.move

Moves a character from one location to another.

**Schema**:
```json
{
  "type": "object",
  "required": ["character_id", "from_location_id", "to_location_id"],
  "properties": {
    "character_id": {"type": "string", "format": "uuid"},
    "from_location_id": {"type": "string", "format": "uuid"},
    "to_location_id": {"type": "string", "format": "uuid"},
    "method": {"type": "string", "enum": ["walk", "teleport", "portal"]},
    "time_taken": {"type": "integer", "minimum": 0}
  }
}
```

### character.update

Updates a character's attributes.

**Schema**:
```json
{
  "type": "object",
  "required": ["character_id"],
  "properties": {
    "character_id": {"type": "string", "format": "uuid"},
    "name": {"type": "string", "minLength": 1, "maxLength": 100},
    "traits": {
      "type": "object",
      "additionalProperties": {"type": "string"}
    },
    "status": {"type": "string", "enum": ["active", "inactive", "deceased"]}
  }
}
```

### world.tick

Advances the world clock.

**Schema**:
```json
{
  "type": "object",
  "required": ["tick_number"],
  "properties": {
    "tick_number": {"type": "integer", "minimum": 0},
    "world_time": {"type": "integer", "minimum": 0}
  }
}
```

## Error Handling

The validator returns a tuple of `(is_valid, errors)` where:

- `is_valid`: `True` if the event is valid, `False` otherwise
- `errors`: A list of error messages if validation fails

## Extending the Validator

To add a new event type:

1. Add a new schema to the `EVENT_SCHEMAS` dictionary in `event_validator.py`
2. Add any semantic validations to the `_validate_semantics` method
3. Add tests for the new event type

## Testing

Run the tests with:

```bash
python -m unittest discover -s tests
```

## Dependencies

- Python 3.7+
- jsonschema

## License

[Your License Here]
