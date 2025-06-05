# Simple Dockerfile for quick deployment
FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy source
COPY src/ ./src/

# Run app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]