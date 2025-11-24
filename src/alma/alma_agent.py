import typer
import os  # ⬅️ Agregar este import
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from alma.core.database import db_manager
from alma.core.llm_client import llm_client

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
    """
    pass

@app.command()
def init():
    """Inicializa la base de datos de Alma Agent"""
    try:
        db_manager.init_database()
        llm_client.initialize()
        console.print("✅ [green]Base de datos de Alma Agent inicializada correctamente[/green]")
        console.print("✅ [green]Cliente LLM configurado[/green]")
    except Exception as e:
        console.print(f"❌ [red]Error inicializando Alma Agent: {e}[/red]")

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
        
        llm_status = "✅ Conectado" if llm_client.initialized else "❌ No configurado"
        
        status_info = f"""
🧠 **Memorias almacenadas**: {memory_count}
🔍 **Sesiones activas**: {active_sessions}
🤖 **Estado LLM**: {llm_status}
📊 **Base de datos**: Conectada
        """
        
        console.print(Panel(
            Markdown(status_info),
            title="[bold blue]Alma Agent Status[/bold blue]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"❌ [red]Error obteniendo estado: {e}[/red]")

@app.command()
def test_llm(prompt: str = typer.Argument("Hola Alma", help="Prompt para probar LLM")):
    """Prueba la conexión con el modelo LLM"""
    console.print(f"🧠 [bold]Probando LLM con prompt:[/bold] {prompt}")
    response = llm_client.query(prompt)
    console.print(Panel(response, title="🤖 Respuesta LLM", border_style="blue"))

@app.command()
def debug_env():
    """Muestra las variables de entorno para diagnóstico"""
    console.print("[bold]🔍 Variables de entorno:[/bold]")
    env_vars = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'), 
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': '***' if os.getenv('DB_PASSWORD') else None,
        'DEEPSEEK_API_KEY': '***' if os.getenv('DEEPSEEK_API_KEY') else None
    }
    
    for key, value in env_vars.items():
        status = "✅" if value else "❌"
        console.print(f"  {status} {key}: {value}")

    # Verificar también los valores por defecto que se usarían
    console.print("\n[bold]🔧 Valores que usaría DatabaseManager:[/bold]")
    test_params = {
        'host': os.getenv('DB_HOST', 'db'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'hood'),
        'user': os.getenv('DB_USER', 'alma'),
        'password': '***' if os.getenv('DB_PASSWORD') else '***'
    }
    console.print(f"  {test_params}")

if __name__ == "__main__":
    app()