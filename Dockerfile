FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de proyecto
COPY pyproject.toml .
COPY src/ ./src/

# Instalar la aplicación en modo editable
RUN pip install --no-cache-dir -e .

# Mantener el contenedor vivo con bash
CMD ["bash"]