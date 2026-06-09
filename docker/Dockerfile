FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md /app/
COPY serverforge /app/serverforge
COPY sql /app/sql
RUN pip install --no-cache-dir .

CMD ["python", "-m", "serverforge"]
