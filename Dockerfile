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

COPY main.py main_company.py main_sharepoint.py main_activity.py run_reports.py .
COPY app/ app/
COPY templates/ templates/
COPY static/ static/
COPY data/ data/

# Bulma CSS inside image (no CDN at runtime)
RUN curl -sL -o /app/static/css/bulma.min.css \
    https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css

ENV APP_DIR=/app OUTPUT_DIR=/output
VOLUME /output

# Run any report: python run_reports.py [licensing|company|sharepoint] [data_path]
# Examples: run_reports.py licensing  |  run_reports.py company /data/by-company.json
CMD ["python", "run_reports.py", "licensing"]
