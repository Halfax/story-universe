# Chronicle Keeper

Chronicle Keeper is the core service responsible for maintaining the canonical world state, managing the world clock, and handling event broadcasting in the Story Universe system.

## Features

- **World Clock Management**: Maintains and advances the canonical world time
- **Event Broadcasting**: Publishes world events to subscribers using ZeroMQ
- **Persistence**: Stores world state and events in a SQLite database
- **REST API**: Provides HTTP endpoints for querying and modifying the world state
- **Metrics**: Collects and reports performance and operational metrics

## Recent Improvements

### Enhanced Tick Publisher
- Added automatic reconnection with exponential backoff
- Thread-safe publishing with connection state tracking
- Comprehensive metrics collection (messages sent, errors, reconnects)
- Graceful shutdown handling
- Improved error recovery and logging

### World Clock Service
- Rewritten as a robust, monitorable service
- Configurable tick intervals
- Detailed metrics and status reporting
- Graceful startup and shutdown
- Backward-compatible API

## Configuration

Environment variables:

- `CHRONICLE_KEEPER_DB_PATH`: Path to SQLite database file (default: `/data/chronicle.db`)
- `CHRONICLE_HOST`: Host to bind the HTTP server to (default: `0.0.0.0`)
- `CHRONICLE_PORT`: Port for the HTTP server (default: `8001`)
- `ZMQ_PUB_BIND_ADDR`: ZeroMQ publisher bind address (default: `tcp://*:5555`)
- `TICK_PUBLISHER_RECONNECT_DELAY`: Delay between reconnection attempts in seconds (default: `5.0`)

## API Endpoints

- `GET /ping`: Health check endpoint
- `POST /event`: Submit a new world event
- `GET /world/state`: Get current world state
- `GET /world/characters`: List all characters
- `GET /world/locations`: List all locations
- `GET /world/events/recent`: Get recent events with filtering

## Usage

### Starting the Service

```bash
# Using Docker (recommended)
docker run -d --name chronicle-keeper \
  -p 8001:8001 \
  -p 5555:5555 \
  -v /path/to/data:/data \
  chronicle-keeper

# Or directly with Python
python -m src.main
```

### Python API

```python
from src.services.clock import start_world_clock, get_clock_status, stop_world_clock

# Start the world clock with a 5-second tick interval
start_world_clock(tick_interval=5.0)

# Get current status
status = get_clock_status()
print(f"Ticks processed: {status['metrics']['ticks_processed']}")

# Stop the clock when done
stop_world_clock()
```

### Subscribing to Events

```python
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")  # Default address
socket.setsockopt_string(zmq.SUBSCRIBE, "system:")

while True:
    topic, message = socket.recv_multipart()
    event = json.loads(message)
    print(f"[{topic}] {event}")
```

## Development

### Dependencies

- Python 3.8+
- ZeroMQ
- SQLite
- FastAPI (for HTTP API)

### Running Tests

```bash
python -m pytest tests/
```

### Building Docker Image

```bash
docker build -t chronicle-keeper .
```

## License

[Your License Here]
