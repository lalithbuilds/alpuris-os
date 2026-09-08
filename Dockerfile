FROM python:3.12-slim as runner

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=9090 \
    HOST=0.0.0.0

WORKDIR /app

# Install system dependencies & healthcheck tool
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Security: Create non-root user
RUN groupadd -g 1000 metropolis && \
    useradd -u 1000 -g metropolis -s /bin/bash -m metropolis

# Copy project files
COPY . /app

# Ensure workspace and log directories have proper permissions
RUN mkdir -p /app/workspace /app/sandbox && \
    chown -R metropolis:metropolis /app

USER metropolis

EXPOSE 9090

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:9090/api/state || exit 1

ENTRYPOINT ["python3", "server.py"]
CMD ["--port", "9090", "--host", "0.0.0.0"]
