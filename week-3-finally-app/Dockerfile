# ==============================================================================
# Stage 1: Build Next.js Static Export Frontend
# ==============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package manifests & install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source code & execute static export build
COPY frontend/ ./
RUN npm run build

# ==============================================================================
# Stage 2: Final Production Python FastAPI Runtime
# ==============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Prevent Python buffering and bytecode write
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DB_PATH=/app/db/finally.db

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy backend dependency declarations and source code
COPY backend/pyproject.toml /app/backend/pyproject.toml
COPY backend/README.md /app/backend/README.md
COPY backend/app /app/backend/app

# Install Python backend dependencies using uv into system site-packages
WORKDIR /app/backend
RUN uv pip install --system -e .

# Copy built frontend static export from Stage 1 into FastAPI static directory
COPY --from=frontend-builder /app/frontend/out /app/backend/app/static

EXPOSE 8000

# Run Uvicorn server serving API and static frontend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
