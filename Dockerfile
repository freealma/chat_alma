FROM python:3.11
WORKDIR /alma

# Copiar solo lo necesario para instalar
COPY pyproject.toml .

# Instalar sin scripts, solo dependencias
RUN pip install --no-cache-dir .