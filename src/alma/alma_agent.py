import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from alma.core.database import db_manager
from alma.core.llm_client import llm_client  # ⬅️ CORREGIDO: importar la instancia

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
        llm_client.initialize()  # ⬅️ Inicializar LLM también
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

# Comando para probar LLM
@app.command()
def test_llm(prompt: str = typer.Argument("Hola Alma", help="Prompt para probar LLM")):
    """Prueba la conexión con el modelo LLM"""
    console.print(f"🧠 [bold]Probando LLM con prompt:[/bold] {prompt}")
    response = llm_client.query(prompt)
    console.print(Panel(response, title="🤖 Respuesta LLM", border_style="blue"))

# Registrar comandos de forma modular
def register_commands():
    """Registra todos los comandos modularmente"""
    # Esto se hará automáticamente al importar los módulos
    pass

if __name__ == "__main__":
    app()