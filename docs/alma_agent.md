Rol > Eres alma copiloto agente, quiero que me ayudes como programador senir en python para crear un agente copiloto pentester.

# Alma Agent CLI

Vamos a consruir el agente alma confunciones para crear memorias y leer el codigo conectado a deepseek a travez de lang chain, luego iremos iendo como le agregamos funciones y autonomia

Quiero aprender mas sobre agentes pero empezemos por algo

---

## Dependencias :

 - `typer`
 - `langchain`
 - `python`
 - `postgreSQL`

### `pyproject.toml`

```toml
[project]
name = "alma"
version = "1.0.0"
dependencies = [
    "requests",
    "numpy", 
    "langchain",
    "llama-index",
]

[project.scripts]
alma = "alma.__main__:main"

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

---

## Estructura fisica :

```txt
.
├── docker-compose.yaml
├── Dockerfile
├── docs
│   └── alma_agent.md
├── meta
│   └── schema.sql
├── pyproject.toml
├── README.md
└── src
    └── alma
        ├── alma_agent.py           # Script principal parser con typer
        ├── commands                # Comandos del agente
        │   ├── create_memory.py    # Comando para crear memorias
        │   ├── __init__.py
        │   └── read_scripts.py     # Comando para leer scripts y sugerir mejoras
        ├── __init__.py
        └── __main__.py
```

---

## Configuracion :

### `docker-compose.yaml`

El docker compose deberia ser algo asi para poder conectarse a la bse de datos qe tenemos

```yaml
services:
  trece:
    build: .
    container_name: alma_agent
    volumes:
      - ./src:/app/src
    working_dir: /app
    stdin_open: true
    tty: true
    networks:
      - srv-network
    environment:
      - DATABASE_URL=postgresql://alma:umamia@psql:5433/alma
    command: ["bash"]

networks:
  srv-network:
    external: true
    name: srv_srv-network
```

---

## Scripts `alma_agent.py`

### Coneccion a la db :

El script deberia arrancar asi conectandose a la DB e ir integrandole nuevos comandos con typer en la carpeta commands uno por uno para qe los pueda leer mas adelante.

```python
import typer
import psycopg2
import os
from datetime import datetime

app = typer.Typer(
    name="alma-agent",
    help="Alma Agent CLI - Herramienta para interactuar con el agente Alma",
    rich_markup_mode="rich"
)
console = Console()

def get_db_connection():
    """Establece conexión con la base de datos usando Docker internal networking"""
    try:
        # En la red de Docker, nos conectamos al servicio 'db' por nombre
        conn = psycopg2.connect(
            host='db',
            port='5432',
            database='alma', 
            user='alma',
            password='umamia'
        )
        return conn
    except Exception as e:
        console.print(f"[red]Error conectando a la base de datos: {e}[/red]")
        console.print("[yellow]Nota: Asegúrate de que los parámetros de conexión en get_db_connection() sean correctos para tu setup[/yellow]")
        return None
```

---

### Subcarpeta con comandos todos aislados corriendo independientes.

Carpeta `src/alma/commands` contendra todos los comandos de alma mas adelante crearemos `src/alma/tools`

Ejemplo de comandos :

```python
@app.command()
def create_memory():
    """Crea memorias en la base de datos"""
    conn = get_db_connection()
    if conn is None:
        return
    finally:
        conn.close()
```

---