# Deployment Guide: Tri-Machine Story Universe

This guide explains how to deploy each component to its target machine.

---

## 1. Chronicle Keeper (Pi, Pi OS)

### Prerequisites
- Raspberry Pi OS (Bookworm/Bullseye recommended)
- Python 3.11+
- Docker (optional, for containerized deployment)
- Git

### Steps
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd story-universe/chronicle-keeper
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   Or, to use Docker:
   ```sh
   docker build -t chronicle-keeper .
   ```
3. **Database initialization:**
   - If using Docker, database tables are created automatically during the build—no manual step required.
   - If running locally (not in Docker), you can initialize the database with:
     ```sh
     python src/main.py  # First run will create DB tables
     ```
4. **Run or Restart the server:**
   ```sh
   uvicorn src.main:app --host 0.0.0.0 --port 8001
   ```
   Or, with Docker (recommended for deployment):
   - The container uses a robust entrypoint script (start_with_clock.sh) that starts both the world clock and the API server together, guaranteeing distributed ticks and logs always work.
   - If you need to restart or update the container, use the following steps:
     1. **Stop and remove any existing container:**
        ```sh
        sudo docker stop chronicle-keeper || true
        sudo docker rm chronicle-keeper || true
        ```
     2. **Rebuild the Docker image (after code changes or git pull):**
        ```sh
        sudo docker build -t chronicle-keeper .
        ```
     3. **Start the container with both API and ZeroMQ ports exposed:**
        ```sh
        sudo docker run -d --name chronicle-keeper -p 8001:8001 -p 5555:5555 chronicle-keeper
        ```
   - To view logs from the running container (including world clock output):
     ```sh
     sudo docker logs -f chronicle-keeper
     ```
5. **World Clock and Tick Broadcasting:**
   - The world clock and tick broadcasting start automatically when you run the server (no manual step required).
   - **ZeroMQ Binding Rule:** Only the world clock thread binds to port 5555 (as a PUB socket). All other event/tick publishers connect to this PUB socket—they do not bind.
   - This is required for distributed event/tick flow to Evo-X2 and other nodes.
   - If you do not see ticks/events on other machines, ensure the server is running and port 5555 is open, and that only one process binds to 5555.

---

## 2. Narrative Engine (Evo-X2, Windows 11)

### Prerequisites
- Windows 11
- Python 3.11+
- Git

### Steps
1. **Clone the repository:**
   ```powershell
   git clone <your-repo-url>
   cd story-universe\narrative-engine
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the log collector:**
   ```powershell
   python src\log_collector.py
   ```
4. **(Optional) Start narrative engine:**
   - Implement and run the event generator/subscriber as described in the roadmap.

---

## 3. World Browser (Alienware, Windows 11)

### Prerequisites
- Windows 11
- Python 3.11+
- PySide6 or other UI framework (see requirements.txt)
- Git

### Steps
1. **Clone the repository:**
   ```powershell
   git clone <your-repo-url>
   cd story-universe\world-browser
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the UI:**
   ```powershell
   python src\main.py
   ```

---

## Notes
- Update `<your-repo-url>` with your actual repository URL.
- Ensure network connectivity between machines (Pi, Evo-X2, Alienware) for messaging and API calls.
- For ZeroMQ, ensure firewall rules allow the required ports (default: 5555).
- For Docker, you may need to use `sudo` on Pi OS.
- All logs from Pi and other nodes will be collected centrally on Evo-X2.
