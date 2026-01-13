# Event Protocol Specification

## Overview
The Event Protocol defines how components in the Story Universe system communicate and share state changes. This document specifies the event format, types, and handling rules.

## Event Structure

### Base Event
All events must include these fields:

```typescript
{
  "id": "evt_1234567890_abc123",
  "type": "event_type_here",
  "timestamp": 1642000000.123,
  "source": "component_name",
  "data": {},
  "metadata": {
    "causationId": "previous_event_id",
    "correlationId": "correlation_uuid"
  }
}
```

### Required Fields
- `id`: Unique event identifier (format: `evt_<timestamp>_<random>`)
- `type`: Event type (see "Standard Event Types" below)
- `timestamp`: Unix timestamp with millisecond precision
- `source`: Originating component (e.g., "narrative_engine", "world_browser")
- `data`: Event-specific payload

### Standard Event Types

#### System Events
- `system.tick`: World clock tick
- `system.heartbeat`: Component status update
- `system.error`: Error notification

#### World Events
- `world.state_update`: World state change
- `world.character_moved`: Character location change
- `world.object_modified`: Object state change

#### Narrative Events
- `narrative.event_generated`: New narrative event
- `narrative.arc_updated`: Story arc progression
- `narrative.decision_made`: Character decision

## Event Flow

1. **Generation**
   - Components generate events in response to state changes
   - Each event gets a unique ID and timestamp
   - Related events share a correlationId

2. **Validation**
   - Chronicle Keeper validates events against schema
   - Continuity Validator checks for narrative consistency
   - Invalid events are rejected with an error response

3. **Persistence**
   - Valid events are stored in the event log
   - World state is updated atomically

4. **Broadcast**
   - Events are published to all subscribers
   - Components update their local state accordingly

## Implementation Notes

### Error Handling
- Invalid events should include an `error` field with details
- Failed event processing should trigger a `system.error` event
- Components should implement retry logic for transient failures

### Performance Considerations
- Batch events when possible
- Use delta updates for large state objects
- Consider event compression for high-volume traffic

### Security
- Validate all incoming events
- Sanitize event data before processing
- Implement rate limiting to prevent abuse

## Examples

### System Tick
```json
{
  "id": "evt_1642000000_abc123",
  "type": "system.tick",
  "timestamp": 1642000000.123,
  "source": "chronicle_keeper",
  "data": {
    "tick_number": 42,
    "world_time": "2023-01-01T12:00:00Z"
  }
}
```

### Character Moved
```json
{
  "id": "evt_1642000001_def456",
  "type": "world.character_moved",
  "timestamp": 1642000001.456,
  "source": "narrative_engine",
  "data": {
    "character_id": "char_123",
    "from_location": "loc_tavern",
    "to_location": "loc_market",
    "reason": "quest_objective"
  },
  "metadata": {
    "correlationId": "quest_789"
  }
}
```

## Versioning
- Protocol version is included in the Chronicle Keeper API response
- Breaking changes require a major version bump
- Components should handle unknown event types gracefully

Note: The repository layout was flattened on 2026-01-13. See [docs/REPO_LAYOUT_CHANGE.md](docs/REPO_LAYOUT_CHANGE.md).
