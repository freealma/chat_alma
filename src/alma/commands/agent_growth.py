import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from alma.core.database import db_manager
from alma.core.llm_client import llm_client

console = Console()
growth_app = typer.Typer(help="Crecimiento y autonomía de Alma Agent")

@growth_app.command("suggest-features")
def suggest_features(
    component: str = typer.Option("all", help="Componente: memory, llm, cli, reasoning, all")
):
    """Sugiere features para hacer Alma Agent más autónomo"""
    
    component_prompts = {
        "memory": """
Analiza cómo mejorar el SISTEMA DE MEMORIA para autonomía:
- Memoria contextual entre sesiones
- Aprendizaje de interacciones pasadas  
- Priorización automática de información
- Búsqueda semántica en memorias
- Relacionar memorias entre sí
""",
        "llm": """
Analiza cómo mejorar el CLIENTE LLM para autonomía:
- Mejor prompt engineering para reasoning
- Context management entre llamadas
- Tool calling automático
- Chain-of-thought prompting
- Gestión de conversaciones largas
""",
        "cli": """
Analiza cómo mejorar la INTERFAZ CLI para autonomía:
- Comandos más inteligentes y contextuales
- Autocompletado basado en historial
- Modo conversacional interactivo
- Ejecución automática de tareas complejas
- Sugerencias de comandos relevantes
""",
        "reasoning": """
Analiza cómo implementar REASONING para autonomía:
- Análisis de objetivos del usuario
- Planificación de pasos automática
- Selección de herramientas apropiadas
- Evaluación de resultados
- Aprendizaje de éxitos/fracasos
""",
        "all": """
Analiza ALMA AGENT completo y sugiere roadmap de AUTONOMÍA:
1. Próximas 3-5 features clave para autonomía
2. Mejoras arquitectónicas prioritarias  
3. Sistema de aprendizaje continuo
4. Capacidades de reasoning necesarias
5. Integración entre componentes
"""
    }
    
    prompt = component_prompts.get(component, component_prompts["all"])
    
    console.print(f"🧠 [bold]Buscando mejoras de autonomía para: {component}[/bold]")
    
    response = llm_client.query(prompt)
    console.print(Panel(
        response, 
        title=f"🚀 Roadmap de Autonomía - {component.upper()}",
        border_style="green"
    ))

@growth_app.command("analyze-usage")
def analyze_usage():
    """Analiza el uso real de Alma Agent para sugerir mejoras"""
    try:
        # Obtener estadísticas de uso real
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            # Contar memorias por tipo
            cur.execute("""
                SELECT memory_type, COUNT(*) as count, 
                       AVG(importance) as avg_importance
                FROM alma_memories 
                GROUP BY memory_type 
                ORDER BY count DESC
            """)
            memory_stats = cur.fetchall()
            
            # Últimas memorias
            cur.execute("""
                SELECT memory_type, content, importance
                FROM alma_memories 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_memories = cur.fetchall()
        
        # Construir contexto de uso
        usage_context = "ESTADÍSTICAS DE USO:\n"
        for mem_type, count, avg_imp in memory_stats:
            usage_context += f"- {mem_type}: {count} memorias (importancia avg: {avg_imp:.1f})\n"
        
        usage_context += "\nMEMORIAS RECIENTES:\n"
        for mem_type, content, importance in recent_memories:
            preview = content[:100] + "..." if len(content) > 100 else content
            usage_context += f"- {mem_type} ({importance}): {preview}\n"
        
        prompt = f"""
Basado en el USO REAL de Alma Agent, sugiere mejoras prioritarias:

{usage_context}

ANALIZA:
1. ¿Qué tipos de memoria se usan más? ¿Qué indica esto?
2. ¿Qué features faltan basado en los patrones de uso?
3. ¿Cómo podemos hacer el agente más útil para estos casos?
4. ¿Qué datos deberíamos empezar a recolectar para mejor aprendizaje?
"""
        
        console.print("📊 [bold]Analizando patrones de uso real...[/bold]")
        response = llm_client.query(prompt, context=usage_context)
        
        console.print(Panel(
            response, 
            title="📈 Mejoras Basadas en Uso Real", 
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Error analizando uso: {e}[/red]")

@growth_app.command("tech-debt")
def analyze_tech_debt():
    """Identifica technical debt que impide el crecimiento"""
    prompt = """
Analiza el código de Alma Agent y identifica TECHNICAL DEBT que impide el crecimiento:

ENFÓCATE EN:
- Acoplamiento que dificulta agregar nuevas features
- Falta de abstracciones para escalar
- Decisiones técnicas que limitan autonomía
- Dependencias problemáticas
- Arquitectura que no escala

IGNORA:
- Vulnerabilidades de seguridad menores
- Estilo de código cosmético
- Optimizaciones prematuras
"""
    
    console.print("🔧 [bold]Buscando technical debt que bloquea crecimiento...[/bold]")
    response = llm_client.query(prompt)
    
    console.print(Panel(
        response, 
        title="🏗️ Technical Debt Crítico", 
        border_style="yellow"
    ))

@growth_app.command("analyze-patterns")
def analyze_patterns():
    """Analiza patrones de uso y sugiere mejoras basadas en datos reales"""
    try:
        conn = db_manager.get_connection()
        with conn.cursor() as cur:
            # Patrones por tipo de memoria
            cur.execute("""
                SELECT memory_type, 
                       COUNT(*) as count,
                       AVG(importance) as avg_importance,
                       AVG(COALESCE((metadata->>'usage_count')::int, 0)) as avg_usage
                FROM alma_memories 
                GROUP BY memory_type 
                ORDER BY count DESC
            """)
            type_patterns = cur.fetchall()
            
            # Memorias más útiles (alta importancia + alto uso)
            cur.execute("""
                SELECT content, memory_type, importance,
                       COALESCE((metadata->>'usage_count')::int, 0) as usage_count
                FROM alma_memories 
                WHERE importance >= 4 
                ORDER BY usage_count DESC, importance DESC
                LIMIT 5
            """)
            top_memories = cur.fetchall()
        
        # Construir análisis
        analysis = "PATRONES DE USO DETECTADOS:\n\n"
        
        analysis += "📊 DISTRIBUCIÓN POR TIPO:\n"
        for mem_type, count, avg_imp, avg_use in type_patterns:
            analysis += f"- {mem_type}: {count} memorias (importancia: {avg_imp:.1f}, usos: {avg_use:.1f})\n"
        
        analysis += "\n🏆 MEMORIAS MÁS ÚTILES:\n"
        for content, mem_type, importance, usage in top_memories:
            preview = content[:80] + "..." if len(content) > 80 else content
            analysis += f"- ⭐{importance} ({usage} usos): {preview}\n"
        
        prompt = f"""
        Analiza estos patrones de uso real de Alma Agent y sugiere mejoras específicas:

        {analysis}

        ENFÓCATE EN:
        1. ¿Qué tipos de memoria son más útiles? ¿Por qué?
        2. ¿Qué features deberíamos desarrollar basado en estos patrones?
        3. ¿Cómo podemos mejorar el sistema de memoria?
        4. ¿Qué datos nos faltan recolectar?
        """
        
        console.print("🔍 [bold]Analizando patrones de uso real...[/bold]")
        response = llm_client.query(prompt, context=analysis)
        
        console.print(Panel(
            response, 
            title="📈 Análisis de Patrones de Uso", 
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Error analizando patrones: {e}[/red]")

# Registrar en app principal
from alma.alma_agent import app
app.add_typer(growth_app, name="growth", help="Crecimiento y autonomía del agente")