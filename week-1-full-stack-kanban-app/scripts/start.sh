#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t kanban-app .

echo "Cleaning existing container..."
docker rm -f kanban-app || true

echo "Starting container..."
docker run -d --name kanban-app -p 8000:8000 --env-file .env kanban-app || docker run -d --name kanban-app -p 8000:8000 kanban-app

echo "Kanban app is running at http://localhost:8000"
