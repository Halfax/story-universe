#!/bin/sh
# Entrypoint: start world clock, then launch Uvicorn
set -e
set -x  # Print commands for debugging

# Ensure src is on the Python path
export PYTHONPATH=/app

# Start the world clock in the background, log errors to a file and to stderr
python3 -u src/services/clock.py 2>&1 | tee /app/clock.log &

# Start the FastAPI server
UVICORN_HOST=${CHRONICLE_HOST:-0.0.0.0}
UVICORN_PORT=${CHRONICLE_PORT:-8001}
exec uvicorn src.main:app --host "$UVICORN_HOST" --port "$UVICORN_PORT"