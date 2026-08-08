#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Stopping FinAlly AI Trading Workstation..."
docker compose down

echo "FinAlly container stopped. SQLite database persisted in db/ directory."
