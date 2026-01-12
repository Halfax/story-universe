
# Deployment Guide: Tri-Machine Story Universe

This guide explains how to set up, run, and operate the distributed story universe system across all three nodes.

---

## What is this?
This is a persistent, distributed narrative simulation system. Each machine has a unique role:
- **Chronicle Keeper (Pi):** Canonical database, event validation, world clock, API
- **Narrative Engine (Evo-X2):** Event/lore generation, simulation, log aggregation
- **World Browser (Alienware):** Visualization, UI, world exploration

---

## Quick Start Table

| Node              | Role                | Main Command to Start                |
|-------------------|---------------------|--------------------------------------|
| Pi (Chronicle Keeper) | Canonical DB, API, Clock | `docker run ...` or `uvicorn ...`   |
| Evo-X2 (Narrative Engine) | Event/Lore Generation | `python src/log_collector.py`       |
| Alienware (World Browser) | Visualization/UI      | `python src/main.py`                |

---

## 1. Chronicle Keeper (Raspberry Pi 5)

### What it does
- Maintains the canonical world database (SQLite/DuckDB)
- Runs the FastAPI service for event ingestion and world state queries
- Validates all events for continuity and lore
- Broadcasts world clock ticks and accepted events via ZeroMQ

### Prerequisites
- Raspberry Pi OS (Bookworm/Bullseye recommended)
- Python 3.11+
- Docker (recommended)
- Git

### Setup & Run
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd story-universe/chronicle-keeper
   ```
2. **Install dependencies (if not using Docker):**
   ```sh
   pip install -r requirements.txt
   ```
3. **Build and run with Docker (recommended):**
   ```sh
   sudo docker build -t chronicle-keeper .
   sudo docker run -d --name chronicle-keeper --restart unless-stopped -p 8001:8001 -p 5555:5555 chronicle-keeper
   ```
4. **Enable auto-start on reboot:**
   ```sh
   sudo chmod +x scripts/start_on_boot.sh
   sudo scripts/install_cron.sh
   ```
5. **View logs:**
   ```sh
   sudo docker logs -f chronicle-keeper
   ```
6. **Run tests:**
   ```sh
   cd ../../
   narrative-engine/venv/Scripts/python -m pytest story-universe/chronicle-keeper/tests
   ```

#### Manual (non-Docker) run:
```sh
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

#### Notes
- The world clock and tick broadcasting start automatically.
- Only the world clock thread binds to ZeroMQ port 5555 (PUB socket).
- Use `CHRONICLE_KEEPER_DB_PATH` env var to override DB location.

---

## 2. Narrative Engine (Evo-X2 Max+)

### What it does
- Generates new events, lore, and world updates
- Subscribes to world clock ticks from the Pi
- Sends events to the Pi for validation and logging

### Prerequisites
- Windows 11 or Linux
- Python 3.11+
- Git

### Setup & Run
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd story-universe/narrative-engine
   ```
2. **Set up Python environment:**
   ```sh
   python -m venv venv
   venv/Scripts/activate  # or source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the log collector:**
   ```sh
   python src/log_collector.py
   ```
4. **(Optional) Start narrative engine:**
   - Implement and run the event generator/subscriber as described in the roadmap.

---

## 3. World Browser (Alienware/UYScuti)

### What it does
- Visualizes the evolving universe (maps, timelines, character webs)
- Provides UI for exploring and editing the world

### Prerequisites
- Windows 11 or Linux
- Python 3.11+
- PySide6 (for UI)
- Git

### Setup & Run
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd story-universe/world-browser
   ```
2. **Set up Python environment:**
   ```sh
   python -m venv venv
   venv/Scripts/activate  # or source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the browser:**
   ```sh
   cd src
   python -m ui.main_window
   ```
   > **Note:** This is required so that relative imports work correctly. Do not run main_window.py directly.

---

## Networking & Messaging
- All nodes must be on the same network or have open ports for ZeroMQ and API communication.
- Update IPs and ports in config files as needed.
- For ZeroMQ, ensure firewall rules allow port 5555.
- Only one process should bind to 5555 (the Pi world clock thread).

---

## Troubleshooting
- Check logs for errors (see `central_logs.txt` or container logs)
- Ensure all dependencies are installed
- For DB issues, verify `CHRONICLE_KEEPER_DB_PATH` and permissions
- For messaging, ensure ZeroMQ ports are open and not firewalled
- For Docker, you may need to use `sudo` on Pi OS

---

## Advanced: Systemd Alternative (Pi)
If you prefer `systemd` over `cron.d` for auto-start, create a unit file and enable it. (See AGENTS.md for details.)

---

## Support & Contact
- See AGENTS.md for architecture and conventions
- For issues, open a GitHub issue or contact the maintainer
