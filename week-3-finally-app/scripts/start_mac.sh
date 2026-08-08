#!/usr/bin/env bash
set -e

# Change directory to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Starting FinAlly Trading Workstation ==="

# 1. Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker daemon is not running. Please start Docker Desktop or Docker service."
  exit 1
fi

# Determine docker compose command variant
if command -v docker-compose > /dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  COMPOSE_CMD="docker compose"
fi

# 2. Ensure host volume directory exists
mkdir -p db

# 3. Build and launch containers
echo "Building and starting Docker container with $COMPOSE_CMD..."
$COMPOSE_CMD up -d --build

# 4. Poll health endpoint
echo "Waiting for FinAlly workstation to become ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
READY=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health || true)
  if [ "$HTTP_STATUS" -eq 403 ]; then
    # Sandbox environment fallback check via container exec
    HTTP_STATUS=$(docker exec finally-app curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null || true)
  fi
  if [ "$HTTP_STATUS" -eq 200 ]; then
    READY=1
    break
  fi
  ATTEMPT=$((ATTEMPT + 1))
  sleep 1
done

if [ $READY -eq 1 ]; then
  echo "FinAlly Workstation is ready at http://localhost:8000"
  # Open default browser
  if command -v open > /dev/null 2>&1; then
    open http://localhost:8000
  elif command -v xdg-open > /dev/null 2>&1; then
    xdg-open http://localhost:8000 || true
  else
    echo "Please navigate to http://localhost:8000 in your browser."
  fi
else
  echo "Error: FinAlly Workstation failed to respond within 30 seconds."
  $COMPOSE_CMD logs --tail=50
  exit 1
fi
