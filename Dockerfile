FROM python:3.11-slim

WORKDIR /alma

# Configurar DNS alternativo y instalar dependencias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar archivos de proyecto
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/
COPY data/ ./data/
COPY db/ ./db/
COPY meta/ ./meta/
COPY docs/ ./docs/

# Crear directorios necesarios
RUN mkdir -p data/chunks db

# Instalar el paquete
RUN pip install --no-cache-dir -e .

# Variables de entorno
ENV PYTHONPATH=/alma/src

# Volumen para datos persistentes
VOLUME ["/alma/db", "/alma/data"]

# Comando por defecto
CMD ["python", "-m", "alma"]