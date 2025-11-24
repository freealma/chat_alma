import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from datetime import datetime
import json

from alma.core.database import db_manager
from alma.core.llm_client import llm_client

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