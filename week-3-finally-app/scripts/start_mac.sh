#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
fi

mkdir -p db

BUILD_FLAG=""
if [ "$1" == "--build" ]; then
  BUILD_FLAG="--build"
fi

echo "Starting FinAlly AI Trading Workstation Docker container..."
docker compose up -d $BUILD_FLAG

echo "FinAlly is running!"
echo "Access the application at: http://localhost:8000"

if command -v open >/dev/null 2>&1; then
  open http://localhost:8000
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:8000
fi
