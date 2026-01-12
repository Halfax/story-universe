# Story Universe

A distributed narrative simulation system that creates and manages a persistent, evolving story world across multiple devices.

## Overview

Story Universe is composed of three main components that work together to create a living, breathing narrative world:

1. **Chronicle Keeper** - The source of truth for world state and events
2. **Narrative Engine** - Generates and processes story events
3. **World Browser** - Visualizes and interacts with the world

## Documentation

- [Architecture](ARCHITECTURE.md) - High-level system design and component interactions
- [Deployment Guide](DEPLOYMENT.md) - Setup and configuration for all components
- [Agents](AGENTS.md) - Development guidelines and coding standards
- [Visualization](VISUALIZATION.md) - World visualization and UI components

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Node.js (for World Browser UI)

### Setup

1. **Chronicle Keeper**
   ```bash
   cd story-universe/chronicle-keeper
   docker build -t chronicle-keeper .
   docker run -p 8001:8001 chronicle-keeper
   ```

2. **Narrative Engine**
   ```bash
   cd story-universe/narrative-engine
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   python -m src.main
   ```

3. **World Browser**
   ```bash
   cd story-universe/world-browser
   npm install
   npm run dev
   ```

## Development

### Project Structure

```
story-universe/
├── chronicle-keeper/    # Core service for world state
├── narrative-engine/    # Event generation and processing
├── world-browser/      # Visualization and UI
└── shared/             # Shared code and models
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your License Here]

---

For detailed documentation, see the [documentation directory](./docs).
