# Use Python 3.11.4 slim image
FROM python:3.11.4-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies for compiling Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    rustc \
    cargo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# (Optional) Upgrade Rust to latest toolchain for 2024 edition support
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && . "$HOME/.cargo/env"

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command to run your app
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8001"]
