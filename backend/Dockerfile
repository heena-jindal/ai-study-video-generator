FROM python:3.12-slim

# Install system dependencies required by Manim, Cairo, and Piper
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    ffmpeg \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up non-root user for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Piper voice model during build
RUN python -m piper.download_voices en_US-lessac-medium

COPY . .

# Ensure appuser owns the application directory for temp file outputs
RUN chown -R appuser:appuser /app
USER appuser

# Hugging Face Spaces expects traffic on port 7860
EXPOSE 7860

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860", "--timeout", "600", "--workers", "1"]
