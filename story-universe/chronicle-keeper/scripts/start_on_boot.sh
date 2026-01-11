#!/bin/sh
# Startup helper for chronicle-keeper container.
# Ensures the container is started once Docker is ready.

sleep 20

CONTAINER="chronicle-keeper"
IMAGE="chronicle-keeper"

# If container already running, nothing to do
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  exit 0
fi

# If container exists but stopped, start it
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  docker start "${CONTAINER}"
  exit 0
fi

# Otherwise run the container (detached, restart unless stopped, with both API and ZeroMQ ports exposed)
docker run -d --name "${CONTAINER}" --restart unless-stopped -p 8001:8001 -p 5555:5555 "${IMAGE}"
# This ensures both the FastAPI server (8001) and ZeroMQ PUB (5555) are accessible on boot.
