import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import json

from alma.core.llm_client import llm_client

console = Console()
code_app = typer.Typer(help="Análisis de código con Alma LLM")

@code_app.command("analyze")
def analyze_code(
    code: str = typer.Argument(..., help="Código a analizar"),
    language: str = typer.Option("python", help="Lenguaje de programación")
):
    """Analiza código en busca de vulnerabilidades de seguridad"""
    console.print(f"🔍 [bold]Analizando código {language}...[/bold]")
    
    # Mostrar el código formateado
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="📝 Código a analizar", border_style="blue"))
    
    # Realizar análisis
    results = llm_client.analyze_code(code, language)
    
    # Mostrar resultados
    if "vulnerabilities" in results:
        table = Table(title="📊 Resultados del Análisis de Seguridad")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("Puntuación Seguridad", f"{results.get('security_score', 0)}/100")
        table.add_row("Nivel de Riesgo", results.get('risk_level', 'desconocido'))
        
        console.print(table)
        
        # Mostrar vulnerabilidades
        if results.get('vulnerabilities'):
            console.print("\n[bold red]🚨 Vulnerabilidades Encontradas:[/bold red]")
            for i, vuln in enumerate(results['vulnerabilities'], 1):
                console.print(f"  {i}. {vuln}")
        
        # Mostrar sugerencias
        if results.get('suggestions'):
            console.print("\n[bold green]💡 Sugerencias de Mejora:[/bold green]")
            for i, suggestion in enumerate(results['suggestions'], 1):
                console.print(f"  {i}. {suggestion}")
                
    else:
        console.print("[yellow]⚠️  No se pudieron obtener resultados del análisis[/yellow]")

@code_app.command("review-file")
def review_file(
    file_path: str = typer.Argument(..., help="Ruta al archivo a analizar")
):
    """Analiza un archivo de código completo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Determinar lenguaje por extensión
        extension = file_path.split('.')[-1].lower()
        lang_map = {
            'py': 'python',
            'js': 'javascript', 
            'ts': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'php': 'php',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust'
        }
        language = lang_map.get(extension, 'python')
        
        analyze_code(code_content, language)
        
    except FileNotFoundError:
        console.print(f"[red]❌ Archivo no encontrado: {file_path}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error leyendo archivo: {e}[/red]")

# Registrar el subcomando
from alma.alma_agent import app
app.add_typer(code_app, name="code", help="Análisis de código con LLM")