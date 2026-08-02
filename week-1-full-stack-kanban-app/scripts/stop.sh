#!/bin/bash
echo "Stopping container..."
docker stop kanban-app || true
docker rm kanban-app || true
echo "Kanban app container stopped and removed."
