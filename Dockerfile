FROM python:3.11-slim

WORKDIR /alma

# SOLUCIÓN: Solo actualizar repositorios, sqlite3 ya viene con Python
RUN apt-get update && apt-get clean

# Copiar TODO el proyecto
COPY pyproject.toml .
COPY src/ ./src/
COPY data/ ./data/
COPY meta/ ./meta/

RUN pip install --no-cache-dir -e .
RUN mkdir -p db

# Por defecto ejecuta el chat
CMD ["alma"]