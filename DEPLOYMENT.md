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
3. **Initialize the database:**
   ```sh
   python src/main.py  # First run will create DB tables
   ```
4. **Run the server:**
   ```sh
   uvicorn src.main:app --host 0.0.0.0 --port 8001
   ```
   Or, with Docker:
   ```sh
   docker run -p 8001:8001 chronicle-keeper
   ```
5. **(Optional) Start world clock and messaging:**
   - The world clock and messaging are started automatically if integrated in main.py.

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
