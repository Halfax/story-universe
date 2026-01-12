#!/bin/sh
# Entrypoint: start world clock, then launch Uvicorn
set -e
set -x  # Print commands for debugging

# Ensure src is on the Python path
export PYTHONPATH=/app

# Start the world clock in the background, log errors to a file and to stderr
python3 -u src/services/clock.py 2>&1 | tee /app/clock.log &

# Start the FastAPI server
exec uvicorn src.main:app --host 0.0.0.0 --port 8001