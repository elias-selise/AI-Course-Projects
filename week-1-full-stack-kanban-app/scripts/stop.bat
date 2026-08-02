@echo off
echo Stopping container...
docker stop kanban-app
docker rm kanban-app
echo Kanban app container stopped and removed.
