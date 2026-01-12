# Event Protocol & API Contracts

## Event Types

### 1. System Events
- `system:tick`: World time advancement
- `system:error`: System-level errors

### 2. World Events
- `world:entity:created`: New entity created
- `world:entity:updated`: Entity updated
- `world:entity:deleted`: Entity deleted

### 3. Narrative Events
- `narrative:event:triggered`: Narrative progression events

## Common Event Structure
```json
{
  "type": "event_type",
  "timestamp": 1642000000.0,
  "data": {}
}
```

## API Endpoints

### Events
- `GET /api/v1/events`: List events with filters
- `POST /api/v1/events`: Submit new event

### Entities
- `GET /api/v1/entities/:type`: List entities
- `POST /api/v1/entities/:type`: Create entity
- `GET /api/v1/entities/:type/:id`: Get entity
- `PUT /api/v1/entities/:type/:id`: Update entity
- `DELETE /api/v1/entities/:type/:id`: Delete entity

## Next Steps
1. Define detailed schemas for each entity type
2. Implement validation middleware
3. Add authentication/authorization
4. Set up event persistence
5. Add documentation for each endpoint
