import typer
import os
import glob
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import json

from alma.core.llm_client import llm_client

console = Console()
code_app = typer.Typer(help="Análisis de código con Alma LLM")

def safe_analyze_code(code: str, language: str, show_code: bool = True) -> dict:
    """Análisis seguro de código con manejo de errores"""
    try:
        if show_code:
            # Mostrar el código formateado (solo si no es muy largo)
            if len(code) <= 2000:  # Mostrar solo si es razonable
                syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="📝 Código a analizar", border_style="blue"))
            else:
                console.print(f"[dim]📝 Analizando {len(code)} caracteres de código {language}...[/dim]")
        
        # Realizar análisis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Analizando con DeepSeek...", total=None)
            results = llm_client.analyze_code(code, language)
        
        return results
        
    except Exception as e:
        console.print(f"[red]❌ Error en análisis: {e}[/red]")
        return {"error": str(e)}

def display_analysis_results(results: dict, source: str = "código"):
    """Muestra los resultados del análisis de forma consistente"""
    if "error" in results:
        console.print(f"[red]❌ Error analizando {source}: {results['error']}[/red]")
        return
    
    if "vulnerabilities" in results:
        # Tabla de métricas
        table = Table(title=f"📊 Resultados del Análisis - {source}")
        table.add_column("Métrica", style="cyan", min_width=20)
        table.add_column("Valor", style="white", min_width=15)
        
        security_score = results.get('security_score', 0)
        risk_level = results.get('risk_level', 'desconocido')
        
        # Colores basados en puntuación
        score_color = "red" if security_score < 40 else "yellow" if security_score < 70 else "green"
        risk_color = "red" if risk_level == "alto" else "yellow" if risk_level == "medio" else "green"
        
        table.add_row("Puntuación Seguridad", f"[{score_color}]{security_score}/100[/{score_color}]")
        table.add_row("Nivel de Riesgo", f"[{risk_color}]{risk_level}[/{risk_color}]")
        
        console.print(table)
        
        # Vulnerabilidades
        vulnerabilities = results.get('vulnerabilities', [])
        if vulnerabilities:
            console.print("\n[bold red]🚨 Vulnerabilidades Encontradas:[/bold red]")
            for i, vuln in enumerate(vulnerabilities, 1):
                console.print(f"  {i}. {vuln}")
        else:
            console.print("\n[green]✅ No se encontraron vulnerabilidades críticas[/green]")
        
        # Sugerencias
        suggestions = results.get('suggestions', [])
        if suggestions:
            console.print("\n[bold green]💡 Sugerencias de Mejora:[/bold green]")
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"  {i}. {suggestion}")
                
    else:
        console.print("[yellow]⚠️  No se pudieron obtener resultados estructurados del análisis[/yellow]")
        if "raw_response" in results:
            console.print(Panel(results["raw_response"], title="Respuesta LLM", border_style="yellow"))

@code_app.command("analyze")
def analyze_code(
    code: str = typer.Argument(..., help="Código a analizar (usar 'file://ruta' para archivos)"),
    language: str = typer.Option("python", help="Lenguaje de programación"),
    show_code: bool = typer.Option(True, help="Mostrar código formateado")
):
    """Analiza código en busca de vulnerabilidades de seguridad"""
    # Soporte para file:// paths
    if code.startswith('file://'):
        file_path = code[7:]
        review_file(file_path)
        return
    
    console.print(f"🔍 [bold]Analizando código {language}...[/bold]")
    results = safe_analyze_code(code, language, show_code)
    display_analysis_results(results)

@code_app.command("review-file")
def review_file(
    file_path: str = typer.Argument(..., help="Ruta al archivo a analizar"),
    show_code: bool = typer.Option(True, help="Mostrar código formateado")
):
    """Analiza un archivo de código completo"""
    try:
        if not os.path.exists(file_path):
            console.print(f"[red]❌ Archivo no encontrado: {file_path}[/red]")
            return
        
        file_size = os.path.getsize(file_path)
        if file_size > 100000:  # 100KB
            console.print(f"[yellow]⚠️  Archivo muy grande ({file_size} bytes). Considera usar 'review-dir'[/yellow]")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Determinar lenguaje por extensión
        extension = Path(file_path).suffix.lower()[1:]  # Quitar el punto
        lang_map = {
            'py': 'python',
            'js': 'javascript', 
            'ts': 'typescript',
            'java': 'java',
            'cpp': 'cpp', 'cc': 'cpp', 'cxx': 'cpp',
            'c': 'c', 'h': 'c',
            'php': 'php',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            'html': 'html', 'htm': 'html',
            'css': 'css',
            'sql': 'sql',
            'sh': 'bash', 'bash': 'bash',
            'xml': 'xml',
            'json': 'json',
            'yaml': 'yaml', 'yml': 'yaml'
        }
        language = lang_map.get(extension, 'python')
        
        console.print(f"🔍 [bold]Analizando archivo: {file_path}[/bold]")
        console.print(f"[dim]📁 Lenguaje: {language}, Tamaño: {file_size} bytes[/dim]")
        
        results = safe_analyze_code(code_content, language, show_code)
        display_analysis_results(results, f"archivo {file_path}")
        
    except FileNotFoundError:
        console.print(f"[red]❌ Archivo no encontrado: {file_path}[/red]")
    except UnicodeDecodeError:
        console.print(f"[red]❌ Error de codificación en archivo: {file_path}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error procesando archivo: {e}[/red]")

@code_app.command("review-dir")
def review_directory(
    directory: str = typer.Argument(..., help="Directorio a analizar"),
    recursive: bool = typer.Option(True, help="Búsqueda recursiva"),
    file_pattern: str = typer.Option("*.py", help="Patrón de archivos (ej: *.py, *.js)")
):
    """Analiza todos los archivos de código en un directorio"""
    try:
        if not os.path.exists(directory):
            console.print(f"[red]❌ Directorio no encontrado: {directory}[/red]")
            return
        
        # Encontrar archivos
        pattern = os.path.join(directory, "**", file_pattern) if recursive else os.path.join(directory, file_pattern)
        files = glob.glob(pattern, recursive=recursive)
        
        if not files:
            console.print(f"[yellow]⚠️  No se encontraron archivos con patrón '{file_pattern}' en {directory}[/yellow]")
            return
        
        console.print(f"🔍 [bold]Analizando {len(files)} archivos en {directory}[/bold]")
        
        summary = {
            "total_files": len(files),
            "analyzed_files": 0,
            "vulnerabilities_found": 0,
            "high_risk_files": []
        }
        
        for file_path in files:
            try:
                # Saltar directorios y archivos muy grandes
                if os.path.isdir(file_path) or os.path.getsize(file_path) > 50000:
                    continue
                
                console.print(f"\n[bold]--- Analizando: {file_path} ---[/bold]")
                review_file(file_path, show_code=False)
                summary["analyzed_files"] += 1
                
            except Exception as e:
                console.print(f"[yellow]⚠️  Saltando {file_path}: {e}[/yellow]")
                continue
        
        # Resumen final
        console.print("\n" + "="*50)
        console.print("[bold green]📊 RESUMEN DEL ANÁLISIS[/bold green]")
        console.print(f"📁 Archivos totales: {summary['total_files']}")
        console.print(f"🔍 Archivos analizados: {summary['analyzed_files']}")
        console.print(f"🚨 Archivos con vulnerabilidades: {summary['vulnerabilities_found']}")
        
    except Exception as e:
        console.print(f"[red]❌ Error analizando directorio: {e}[/red]")

# Registrar el subcomando
from alma.alma_agent import app
app.add_typer(code_app, name="code", help="Análisis de código con LLM")