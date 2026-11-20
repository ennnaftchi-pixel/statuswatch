FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# 1. Update OS packages (fixes zlib1g)
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN addgroup --system app && adduser --system --ingroup app app

COPY pyproject.toml README.md ./
COPY app ./app

# 2. Upgrade pip & setuptools, then remove pip's vendored SBOM to prevent Trivy false-positives
RUN pip install --no-cache-dir -U pip setuptools \
    && rm -f /usr/local/lib/python3.12/site-packages/pip/_vendor/bom.cdx.json \
    && pip install --no-cache-dir .

COPY templates ./templates
COPY static ./static

USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
