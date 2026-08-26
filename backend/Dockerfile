# Render's native Python buildpack can't apt-get install system packages
# (confirmed - multiple people asking Render support this exact question,
# answer is consistently "use Docker"). Manim needs Cairo + Pango at the
# system level, which pip alone can't provide. This Dockerfile is what
# makes Manim actually deployable on Render at all.

FROM python:3.12-slim

# System dependencies Manim needs to render animations:
# - build-essential + python3-dev: needed to compile pycairo's C extension
# - libcairo2-dev, libpango1.0-dev: the actual graphics/text rendering libs
# - ffmpeg: stitches Manim's rendered frames into video (Render's native
#   env has this preinstalled already, but we're in Docker now, so we
#   control everything ourselves -- install it explicitly for parity
#   between local Docker testing and the deployed environment)
# - pkg-config: needed for pycairo's build to find the Cairo library
#
# Deliberately NOT installing texlive/LaTeX -- Manim only needs it for
# MathTex (rendered math notation). We're using plain Text objects
# instead, which avoids adding several GB to this image for no benefit
# at this project's scope.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    ffmpeg \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the voice model into the image at BUILD time, not runtime. Piper's
# model is small (~60MB), but downloading it on every cold start on
# Render's free tier would add real latency to the first request after
# any spin-down -- same category of lesson as lazy-loading in Study
# Companion, just solved differently here since this download only needs
# to happen ONCE, at build time, not per-request.
RUN python -m piper.download_voices en_US-lessac-medium

COPY . .

# Render sets $PORT dynamically -- same lesson as Study Companion, binding
# to a fixed port here would cause the exact same port-scan-timeout issue
# we hit last time.
#
# --timeout 300: gunicorn's DEFAULT worker timeout is 30 seconds -- fine
# for a quick /explain call, but Manim rendering + TTS generation for a
# whole video could genuinely take minutes. Without raising this, gunicorn
# would kill the worker mid-render on any real request. This is a new
# consideration this project introduces that Study Companion never needed.
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300