# Build with --platform linux/arm64 for the AWS Graviton benchmark path.
# This image is ARM64-compatible; it is not a COOL image and must not be
# described as running on AWS or Graviton until benchmarked there.
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM python:3.12-slim AS runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PAGEREADY_FRONTEND_DIR=/app/frontend/dist

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY --from=frontend-builder /frontend/dist /app/frontend/dist

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "pageready.api:app", "--host", "0.0.0.0", "--port", "8000"]
