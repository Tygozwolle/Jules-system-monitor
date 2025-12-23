FROM python:3.9-slim

# Install system dependencies
# gcc and python3-dev are often required for psutil compilation if no wheel is available
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY system_monitor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest

COPY system_monitor/ .
COPY tests/ /app/tests/

# Privileged mode is often required for hardware access, 
# but that is a runtime flag (--privileged).
# The user must provide it when running the container.

CMD ["python", "-u", "main.py"]
