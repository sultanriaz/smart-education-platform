FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GATEWAY_PORT=18080

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency list and install requirements
COPY requirements.backend.txt /app/requirements.backend.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.backend.txt

# Copy source code, libraries, and microservices
COPY libs /app/libs
COPY services /app/services
COPY infra /app/infra
COPY .env.example /app/.env
COPY run.py /app/run.py

# Expose API gateway port (dynamically maps to $PORT on PaaS)
EXPOSE 18080

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:${GATEWAY_PORT:-18080}/health || exit 1

# Start the unified microservices supervisor and API gateway
CMD ["python", "run.py", "--services-only", "--gateway-only"]
