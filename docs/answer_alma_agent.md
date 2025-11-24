# 🚀 Alma Agent - Plan de Desarrollo para Agente Pentester Copiloto

¡Excelente idea! Vamos a construir Alma Agent paso a paso. Te propongo una arquitectura escalable que empiece simple y crezca en complejidad.

## 🎯 **Plan de Desarrollo por Fases**

### **Fase 1: Base Sólida (Semana 1)**
- Estructura modular con Typer
- Conexión a PostgreSQL para memorias
- Comandos básicos de pentesting

### **Fase 2: Integración LLM (Semana 2)**
- Conexión con DeepSeek vía LangChain
- Sistema de memoria contextual
- Reasoning básico

### **Fase 3: Autonomía (Semana 3-4)**
- Tool calling automático
- Planificación de tareas
- Ejecución en bucle

## 📁 **Estructura Mejorada**

```txt
src/alma/
├── __init__.py
├── __main__.py              # Punto de entrada
├── alma_agent.py           # CLI principal
├── core/                   # Núcleo del agente
│   ├── __init__.py
│   ├── database.py         # Conexión DB y modelos
│   ├── llm_client.py       # Cliente DeepSeek/LangChain
│   └── memory.py           # Sistema de memorias
├── commands/               # Comandos Typer
│   ├── __init__.py
│   ├── pentest/           # Comandos de pentesting
│   │   ├── __init__.py
│   │   ├── scan_network.py
│   │   ├── analyze_code.py
│   │   └── vuln_assessment.py
│   ├── memory_ops.py      # Operaciones con memoria
│   └── code_review.py     # Análisis de código
└── tools/                 # Herramientas reutilizables
    ├── __init__.py
    ├── file_utils.py
    ├── network_utils.py
    └── security_tools.py
```

## 🔧 **Implementación Paso a Paso**

### **1. `pyproject.toml` Mejorado**

```toml
[project]
name = "alma-agent"
version = "0.1.0"
description = "Alma Agent - Copiloto Pentester Inteligente"
authors = [
    {name = "Tu Nombre", email = "tu@email.com"},
]

dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "psycopg2-binary>=2.9.0",
    "langchain>=0.1.0",
    "langchain-community>=0.0.10",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
]

[project.scripts]
alma = "alma.__main__:app"

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
```

### **2. `src/alma/__main__.py`**

```python
from alma.alma_agent import app
import alma.commands  # Registra todos los comandos

if __name__ == "__main__":
    app()
```

### **3. `src/alma/core/database.py`**

```python
import psycopg2
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'db'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'alma'),
            'user': os.getenv('DB_USER', 'alma'),
            'password': os.getenv('DB_PASSWORD', 'umamia')
        }
    
    def get_connection(self):
        """Establece conexión con la base de datos"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            raise ConnectionError(f"Error conectando a la base de datos: {e}")
    
    def init_database(self):
        """Inicializa las tablas necesarias para Alma Agent"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Tabla de memorias del agente
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS alma_memories (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        memory_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        context TEXT,
                        importance INTEGER DEFAULT 1
                    )
                """)
                
                # Tabla de sesiones de pentesting
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pentest_sessions (
                        id SERIAL PRIMARY KEY,
                        session_name VARCHAR(255) NOT NULL,
                        target TEXT,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'active',
                        findings JSONB
                    )
                """)
                
                conn.commit()
        finally:
            conn.close()

# Instancia global
db_manager = DatabaseManager()
```

### **4. `src/alma/alma_agent.py`**

```python
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from alma.core.database import db_manager
from alma.core.llm_client import AlmaLLMClient

app = typer.Typer(
    name="alma",
    help="🤖 Alma Agent - Tu copiloto pentester inteligente",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]}
)

console = Console()

@app.callback()
def main():
    """
    Alma Agent - Sistema de inteligencia para pentesting asistido
    
    Características principales:
    • 🧠 Memoria contextual con PostgreSQL
    • 🔍 Análisis automático de código
    • 🌐 Herramientas de escaneo de red
    • 🤖 Integración con DeepSeek vía LangChain
    """
    pass

@app.command()
def init():
    """Inicializa la base de datos de Alma Agent"""
    try:
        db_manager.init_database()
        console.print("✅ [green]Base de datos de Alma Agent inicializada correctamente[/green]")
    except Exception as e:
        console.print(f"❌ [red]Error inicializando base de datos: {e}[/red]")

@app.command()
def status():
    """Muestra el estado actual de Alma Agent"""
    try:
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM alma_memories")
            memory_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM pentest_sessions WHERE status = 'active'")
            active_sessions = cur.fetchone()[0]
        
        status_info = f"""
🧠 **Memorias almacenadas**: {memory_count}
🔍 **Sesiones activas**: {active_sessions}
🤖 **Estado LLM**: Por configurar
📊 **Base de datos**: Conectada
        """
        
        console.print(Panel(
            Markdown(status_info),
            title="[bold blue]Alma Agent Status[/bold blue]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"❌ [red]Error obteniendo estado: {e}[/red]")

# Registrar comandos de forma modular
def register_commands():
    """Registra todos los comandos modularmente"""
    # Esto se hará automáticamente al importar los módulos
    pass

if __name__ == "__main__":
    app()
```

### **5. Primer Comando: `src/alma/commands/memory_ops.py`**

```python
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from datetime import datetime
import json

from alma.core.database import db_manager

console = Console()
memory_app = typer.Typer(help="Operaciones con el sistema de memoria de Alma")

@memory_app.command("create")
def create_memory(
    content: str = typer.Argument(..., help="Contenido de la memoria"),
    memory_type: str = typer.Option("observation", help="Tipo de memoria"),
    importance: int = typer.Option(1, help="Importancia (1-5)"),
    context: str = typer.Option("", help="Contexto adicional")
):
    """Crea una nueva memoria en la base de datos de Alma"""
    try:
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO alma_memories 
                (memory_type, content, metadata, context, importance)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                memory_type,
                content,
                json.dumps({"importance": importance, "auto_generated": False}),
                context,
                importance
            ))
            
            memory_id, created_at = cur.fetchone()
            conn.commit()
            
            console.print(f"✅ [green]Memoria creada exitosamente (ID: {memory_id})[/green]")
            console.print(f"📅 Creada: {created_at}")
            console.print(f"📝 Contenido: {content}")
            
    except Exception as e:
        console.print(f"❌ [red]Error creando memoria: {e}[/red]")

@memory_app.command("list")
def list_memories(
    memory_type: str = typer.Option(None, help="Filtrar por tipo"),
    limit: int = typer.Option(10, help="Límite de resultados")
):
    """Lista las memorias almacenadas por Alma"""
    try:
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            if memory_type:
                cur.execute("""
                    SELECT id, created_at, memory_type, content, importance 
                    FROM alma_memories 
                    WHERE memory_type = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (memory_type, limit))
            else:
                cur.execute("""
                    SELECT id, created_at, memory_type, content, importance 
                    FROM alma_memories 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
            
            memories = cur.fetchall()
            
            if memories:
                table = Table(title="🧠 Memorias de Alma Agent")
                table.add_column("ID", style="cyan")
                table.add_column("Fecha", style="green")
                table.add_column("Tipo", style="magenta")
                table.add_column("Contenido", style="white")
                table.add_column("Importancia", style="yellow")
                
                for memory in memories:
                    content_preview = memory[3][:50] + "..." if len(memory[3]) > 50 else memory[3]
                    table.add_row(
                        str(memory[0]),
                        memory[1].strftime("%Y-%m-%d %H:%M"),
                        memory[2],
                        content_preview,
                        "⭐" * memory[4]
                    )
                
                console.print(table)
            else:
                console.print("[yellow]No hay memorias almacenadas[/yellow]")
                
    except Exception as e:
        console.print(f"❌ [red]Error listando memorias: {e}[/red]")

@memory_app.command("search")
def search_memories(query: str = typer.Argument(..., help="Término de búsqueda")):
    """Busca en las memorias de Alma por contenido"""
    try:
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, created_at, memory_type, content, importance 
                FROM alma_memories 
                WHERE content ILIKE %s 
                ORDER BY importance DESC, created_at DESC
            """, (f'%{query}%',))
            
            results = cur.fetchall()
            
            if results:
                console.print(f"🔍 [bold]Resultados para '{query}':[/bold]")
                for memory in results:
                    console.print(f"  • [cyan]{memory[0]}[/cyan] [{memory[1].strftime('%Y-%m-%d')}] {memory[3]}")
            else:
                console.print(f"[yellow]No se encontraron memorias para '{query}'[/yellow]")
                
    except Exception as e:
        console.print(f"❌ [red]Error buscando memorias: {e}[/red]")

# Registrar el subcomando en la app principal
from alma.alma_agent import app
app.add_typer(memory_app, name="memory", help="Sistema de memoria de Alma")
```

### **6. Docker Compose Mejorado**

```yaml
services:
  alma-agent:
    build: .
    container_name: alma_agent
    volumes:
      - ./src:/app/src
      - ./logs:/app/logs
    working_dir: /app
    stdin_open: true
    tty: true
    networks:
      - srv_srv-network
    environment:
      - DB_HOST=psql
      - DB_PORT=5432
      - DB_NAME=hood
      - DB_USER=alma
      - DB_PASSWORD=umamia
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    command: ["alma", "--help"]

networks:
  srv_srv-network:
    external: true
```

## 🚀 **Para Empezar YA**

```bash
# 1. Construir e iniciar
docker compose up -d alma-agent

# 2. Inicializar base de datos
docker compose exec alma-agent alma init

# 3. Ver estado
docker compose exec alma-agent alma status

# 4. Usar el sistema de memoria
docker compose exec alma-agent alma memory create "El servidor web usa Apache 2.4" --memory-type observation --importance 3
docker compose exec alma-agent alma memory list
```

## 🎯 **Próximos Pasos Sugeridos**

1. **Semana 1**: Comando de análisis de código (`code_review.py`)
2. **Semana 2**: Integración DeepSeek (`llm_client.py`) 
3. **Semana 3**: Comandos de escaneo de red (`scan_network.py`)
4. **Semana 4**: Modo agente autónomo

**¿Por dónde quieres empezar?** ¿Prefieres que desarrollemos primero el sistema de memoria o algún comando específico de pentesting?