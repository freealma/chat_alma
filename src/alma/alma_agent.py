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


@app.command()
def create_memory():
    """Crea memorias en la base de datos"""
    conn = get_db_connection()
    if conn is None:
        return
    finally:
        conn.close()


# Funcion para leer los scripts qe tenemos y sugerir mejoras
@app.command()