# Multi-stage build for full-stack deployment
FROM node:18-alpine AS frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY medical-claim-frontend/package*.json ./
COPY medical-claim-frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install
COPY medical-claim-frontend/ ./
RUN pnpm run build

# Python backend stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY medical_claim_processor/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY medical_claim_processor/src/ ./src/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./src/static/

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Render uses PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the application
CMD ["python", "src/main.py"]
