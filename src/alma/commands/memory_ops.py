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

# En src/alma/commands/memory_ops.py - agregar al final:

@memory_app.command("plan-roadmap")
def plan_roadmap():
    """Usa las memorias existentes para planificar el crecimiento del agente"""
    try:
        # Obtener memorias recientes y importantes
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT content, memory_type, importance, created_at
                FROM alma_memories 
                WHERE importance >= 3
                ORDER BY importance DESC, created_at DESC 
                LIMIT 8
            """)
            important_memories = cur.fetchall()
        
        if not important_memories:
            console.print("[yellow]⚠️  No hay memorias importantes para analizar[/yellow]")
            console.print("[dim]Usa 'alma memory create' con --importance 3+ para crear memorias relevantes[/dim]")
            return
        
        # Construir contexto
        memory_context = "MEMORIAS IMPORTANTES PARA PLANIFICAR:\n"
        for content, mem_type, importance, created_at in important_memories:
            memory_context += f"- {mem_type} (⭐{importance}): {content}\n"
        
        prompt = f"""
Basado en las MEMORIAS IMPORTANTES de Alma Agent, crea un plan de crecimiento:

{memory_context}

GENERA UN ROADMAP PRÁCTICO:
1. **Próximas 2-3 features** que resolverían estos patrones
2. **Mejoras de autonomía** específicas para estos casos de uso  
3. **Capacidades de reasoning** que ayudarían aquí
4. **Sistema de memoria** mejorado para estos escenarios

Mantén el foco en AUTONOMÍA y UTILIDAD PRÁCTICA.
"""
        
        console.print("🧠 [bold]Planificando con memorias importantes...[/bold]")
        response = llm_client.query(prompt, context=memory_context)
        
        # Guardar este plan como memoria de alta importancia
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO alma_memories 
                (memory_type, content, importance, context)
                VALUES (%s, %s, %s, %s)
            """, (
                "roadmap_plan", 
                f"Plan de crecimiento basado en {len(important_memories)} memorias importantes:\n{response}",
                5,
                "Planificación automática basada en experiencia"
            ))
            conn.commit()
        
        console.print(Panel(
            response, 
            title="📈 Roadmap Basado en Experiencia", 
            border_style="green"
        ))
        console.print("[green]✅ Plan guardado en memorias[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error en planificación: {e}[/red]")

# Registrar el subcomando en la app principal
from alma.alma_agent import app
app.add_typer(memory_app, name="memory", help="Sistema de memoria de Alma")