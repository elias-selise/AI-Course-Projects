#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t kanban-app .

echo "Cleaning existing container..."
docker rm -f kanban-app || true

echo "Starting container..."
docker rm -f kanban-app >/dev/null 2>&1 || true
docker run -d --name kanban-app -p 8000:8000 \
  -v kanban-data:/data \
  -e KANBAN_DB_PATH=/data/kanban.db \
  --env-file .env \
  kanban-app || docker run -d --name kanban-app -p 8000:8000 \
  -v kanban-data:/data \
  -e KANBAN_DB_PATH=/data/kanban.db \
  kanban-app

echo "Kanban app is running at http://localhost:8000"
