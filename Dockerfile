# Debian slim – home use, smallest practical image
FROM python:3.12-slim-bookworm

WORKDIR /app

# WeasyPrint runtime deps (Pango + deps); curl only for downloading Bulma at build
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libharfbuzz-subset0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY templates/ templates/
COPY static/ static/

# Bulma CSS inside image (no CDN at runtime)
RUN curl -sL -o /app/static/css/bulma.min.css \
    https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css

# Optional: run as non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER 1000

ENV APP_DIR=/app OUTPUT_DIR=/output
VOLUME /output

CMD ["python", "-m", "app.report"]
