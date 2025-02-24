FROM python:3.12.2-slim-bullseye

ENV PYTHONBUFFERED=1

ENV PORT=8000

WORKDIR /app

# Install uv - following uv installation instructions for linux
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://install.astral.sh/uv.sh | sh

# Make uv executable available in PATH - adjust if install location is different
ENV PATH="/root/.local/bin:$PATH"

COPY . /app/

# Install dependencies using uv instead of pip
RUN uv pip install --no-cache-dir -r requirements.txt

# Healthcheck (assuming you'll implement a /health/ endpoint in Django)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://0.0.0.0:${PORT}/health/ || exit 1

CMD gunicorn server.wsgi:application --bind 0.0.0.0:"${PORT}"

EXPOSE ${PORT}

