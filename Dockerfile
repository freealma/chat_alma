FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema incluyendo bash y curl
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    typer \
    rich \
    psycopg2-binary \
    openai \
    fastapi \
    uvicorn \
    python-multipart \
    pydantic \
    python-dotenv

COPY src/ ./src/

ENV PYTHONPATH=/app/src

# Podemos dejar el comando por defecto como bash
CMD ["bash"]