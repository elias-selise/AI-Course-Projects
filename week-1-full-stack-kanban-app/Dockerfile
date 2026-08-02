# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Runtime Backend
FROM python:3.12-slim
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy backend requirements and install dependencies
COPY backend/pyproject.toml ./backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx python-dotenv

# Copy backend code
COPY backend/ ./

# Copy built static frontend into backend static folder
COPY --from=frontend-builder /app/frontend/out ./static

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
