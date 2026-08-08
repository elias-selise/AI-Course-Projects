# Stage 1: Build static Next.js frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci || npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Fast Python backend with uv & static frontend serving
FROM python:3.12-slim AS runner
WORKDIR /app

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy backend pyproject.toml and source code
COPY backend/pyproject.toml backend/README.md* ./backend/
COPY backend/app ./backend/app

# Install Python dependencies using uv
WORKDIR /app/backend
RUN uv sync --frozen || uv sync

# Copy frontend static export output into backend static path
COPY --from=frontend-builder /app/frontend/out /app/frontend/out
COPY --from=frontend-builder /app/frontend/out /app/backend/app/static

# Expose port 8000
EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
