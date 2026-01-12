#!/bin/sh
# Entrypoint: start world clock, then launch Uvicorn
set -e

# Ensure src is on the Python path
export PYTHONPATH=/app
# Start the world clock in the background
python3 -u src/services/clock.py &

# Start the FastAPI server
exec uvicorn src.main:app --host 0.0.0.0 --port 8001
