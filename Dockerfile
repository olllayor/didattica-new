FROM python:3.12.2-slim-bullseye

ENV PYTHONBUFFERED=1

ENV PORT=8000

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="/app/.venv/bin:/usr/local/bin:/usr/bin:$PATH"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://0.0.0.0:${PORT}/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:${PORT}"]


EXPOSE ${PORT}