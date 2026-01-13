"""
Tests for the EventValidator class.
"""
import unittest
from datetime import datetime, timezone
from uuid import uuid4, UUID

from services.event_validator import EventValidator, EventValidationError

class TestEventValidator(unittest.TestCase):
    """Test cases for EventValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = EventValidator(strict=True)
        self.valid_uuid = str(uuid4())
        self.valid_timestamp = int(datetime.now(timezone.utc).timestamp())
        
    def test_validate_minimal_valid_event(self):
        """Test validation of a minimal valid event."""
        event = {
            "id": self.valid_uuid,
            "type": "character.move",
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "data": {
                "character_id": str(uuid4()),
                "from_location_id": str(uuid4()),
                "to_location_id": str(uuid4())
            }
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_missing_required_field(self):
        """Test validation fails when required field is missing."""
        event = {
            "id": self.valid_uuid,
            # Missing 'type' field
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "data": {}
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertFalse(is_valid)
        self.assertIn("Base validation failed", errors[0])
    
    def test_validate_invalid_uuid(self):
        """Test validation fails with invalid UUID."""
        event = {
            "id": "not-a-uuid",
            "type": "character.move",
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "data": {
                "character_id": str(uuid4()),
                "from_location_id": str(uuid4()),
                "to_location_id": str(uuid4())
            }
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertFalse(is_valid)
        self.assertIn("Invalid UUID format for id", errors[0])
    
    def test_validate_event_specific_schema(self):
        """Test validation against event-specific schema."""
        event = {
            "id": self.valid_uuid,
            "type": "character.move",
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "data": {
                # Missing required fields: from_location_id, to_location_id
                "character_id": str(uuid4())
            }
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertFalse(is_valid)
        self.assertIn("Data validation failed", errors[0])
    
    def test_validate_future_timestamp(self):
        """Test validation fails for future timestamps."""
        future_timestamp = self.valid_timestamp + 3600  # 1 hour in future
        
        event = {
            "id": self.valid_uuid,
            "type": "character.move",
            "timestamp": future_timestamp,
            "source": "test_source",
            "data": {
                "character_id": str(uuid4()),
                "from_location_id": str(uuid4()),
                "to_location_id": str(uuid4())
            }
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertFalse(is_valid)
        self.assertIn("Event timestamp is in the future", errors[0])
    
    def test_validate_unknown_event_type_strict_mode(self):
        """Test validation in strict mode with unknown event type."""
        event = {
            "id": self.valid_uuid,
            "type": "unknown.event.type",
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "data": {}
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertFalse(is_valid)
        self.assertIn("Unknown event type", errors[0])
    
    def test_validate_unknown_event_type_non_strict_mode(self):
        """Test validation in non-strict mode with unknown event type."""
        validator = EventValidator(strict=False)
        
        event = {
            "id": self.valid_uuid,
            "type": "unknown.event.type",
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "data": {}
        }
        
        is_valid, errors = validator.validate(event)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_metadata_fields(self):
        """Test validation of metadata fields."""
        event = {
            "id": self.valid_uuid,
            "type": "character.move",
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "metadata": {
                "causationId": "not-a-uuid",
                "correlationId": "also-not-a-uuid"
            },
            "data": {
                "character_id": str(uuid4()),
                "from_location_id": str(uuid4()),
                "to_location_id": str(uuid4())
            }
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertFalse(is_valid)
        self.assertIn("Invalid UUID format for metadata.causationId", errors[0])
        self.assertIn("Invalid UUID format for metadata.correlationId", errors[1])
    
    def test_validate_character_move_semantics(self):
        """Test semantic validation for character.move events."""
        location_id = str(uuid4())
        event = {
            "id": self.valid_uuid,
            "type": "character.move",
            "timestamp": self.valid_timestamp,
            "source": "test_source",
            "data": {
                "character_id": str(uuid4()),
                "from_location_id": location_id,
                "to_location_id": location_id  # Same as from_location_id
            }
        }
        
        is_valid, errors = self.validator.validate(event)
        self.assertFalse(is_valid)
        self.assertIn("Source and destination locations cannot be the same", errors[0])

if __name__ == '__main__':
    unittest.main()
