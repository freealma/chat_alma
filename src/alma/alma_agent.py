import typer
import os
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
    # ⬇️ Inicializar LLM automáticamente al inicio
    llm_client.ensure_initialized()

@app.command()
def init():
    """Inicializa la base de datos de Alma Agent"""
    try:
        db_manager.init_database()
        if llm_client.initialize():  # ⬅️ Ahora retorna bool
            console.print("✅ [green]Cliente DeepSeek LLM configurado y conectado[/green]")
        else:
            console.print("[yellow]⚠️  Cliente LLM no pudo inicializarse[/yellow]")
            
        console.print("✅ [green]Base de datos de Alma Agent inicializada correctamente[/green]")
            
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
        
        # ⬇️ Usar el método is_initialized() en lugar de acceder directamente al atributo
        llm_status = "✅ Conectado" if llm_client.is_initialized() else "❌ No configurado"
        
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
    
    # ⬇️ Asegurar inicialización antes de la consulta
    if not llm_client.ensure_initialized():
        console.print("[red]❌ No se pudo inicializar DeepSeek LLM[/red]")
        return
        
    response = llm_client.query(prompt)
    console.print(Panel(
        Markdown(response),  # ⬅️ Usar Markdown para mejor formato
        title="🤖 Respuesta DeepSeek", 
        border_style="blue"
    ))

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

if __name__ == "__main__":
    app()