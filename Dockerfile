FROM python:3.11-slim

WORKDIR /alma

RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar TODO el proyecto
COPY pyproject.toml .
COPY src/ ./src/
COPY data/ ./data/
COPY meta/ ./meta/

RUN pip install --no-cache-dir -e .
RUN mkdir -p db

# Por defecto ejecuta el chat
CMD ["alma"]