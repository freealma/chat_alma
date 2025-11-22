FROM python:3.11-slim

WORKDIR /alma

RUN apt-get update && apt-get install -y \
    sqlite3 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --no-cache-dir -e .
RUN mkdir -p db

CMD ["alma"]