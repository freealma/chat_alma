import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio
import os
import uuid
import psycopg2
import openai
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

# =============================================================================
# CONFIGURACIÓN Y CLASES CORE
# =============================================================================

console = Console()
app = FastAPI(title="Alma Agent", version="2.0")
cli = typer.Typer(name="alma", help="🤖 Alma Agent - Sistema autónomo con memoria")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatabaseManager:
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'hood'),
            'user': os.getenv('DB_USER', 'alma'),
            'password': os.getenv('DB_PASSWORD', 'umamia')
        }
        console.print(f"[dim]🔧 Conectando a DB: {self.conn_params['host']}:{self.conn_params['port']}/{self.conn_params['database']}[/dim]")
    
    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.conn_params)
            return conn
        except Exception as e:
            console.print(f"[red]❌ Error conectando a DB: {e}[/red]")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        finally:
            conn.close()
    
    def execute_command(self, query: str, params: tuple = None) -> int:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Inicializa las tablas del sistema Alma"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                # Verificar schema alma
                cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'alma'")
                schema_exists = cur.fetchone()
                
                schema = 'alma' if schema_exists else 'public'
                console.print(f"[dim]📁 Usando schema: {schema}[/dim]")
                
                # Tabla de memorias (mejorada)
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.memories (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        memory_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        context TEXT,
                        importance INTEGER DEFAULT 1,
                        usage_count INTEGER DEFAULT 0,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB DEFAULT '{{}}'
                    )
                """)
                
                # Tabla de logs del agente
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.agent_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        action_type VARCHAR(50) NOT NULL,
                        action_details JSONB NOT NULL,
                        input_context TEXT,
                        output_result TEXT,
                        success BOOLEAN DEFAULT true,
                        learning_insights TEXT,
                        memory_refs INTEGER[]
                    )
                """)
                
                # Tabla de conversaciones
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.conversations (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_message TEXT NOT NULL,
                        agent_response TEXT NOT NULL,
                        context_summary TEXT,
                        memory_used INTEGER[],
                        new_memories_created INTEGER[]
                    )
                """)
                
                conn.commit()
                console.print(f"✅ [green]Tablas creadas en schema: {schema}[/green]")
                
        except Exception as e:
            console.print(f"❌ [red]Error inicializando base de datos: {e}[/red]")
            raise

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
        self.model = "gpt-4"
    
    def is_configured(self):
        return self.api_key is not None and len(self.api_key) > 10
    
    def chat_completion(self, messages: List[Dict], temperature: float = 0.7) -> str:
        if not self.is_configured():
            return "❌ OpenAI no configurado. Configura OPENAI_API_KEY en el entorno."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"[red]Error OpenAI: {e}[/red]")
            return f"Error: {str(e)}"

class MemorySystem:
    def __init__(self, db: DatabaseManager, llm: OpenAIClient):
        self.db = db
        self.llm = llm
    
    def create_memory(self, content: str, memory_type: str = "observation", 
                     importance: int = 1, context: str = None) -> int:
        query = """
            INSERT INTO alma.memories 
            (memory_type, content, context, importance, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        
        metadata = {
            "auto_generated": True,
            "created_via": "memory_system",
            "usage_count": 0
        }
        
        result = self.db.execute_query(query, (memory_type, content, context, importance, json.dumps(metadata)))
        return result[0][0] if result else None
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        search_query = """
            SELECT id, memory_type, content, importance, usage_count
            FROM alma.memories 
            WHERE content ILIKE %s OR context ILIKE %s
            ORDER BY importance DESC, usage_count DESC
            LIMIT %s
        """
        
        results = self.db.execute_query(search_query, (f'%{query}%', f'%{query}%', limit))
        
        return [
            {
                "id": r[0],
                "type": r[1],
                "content": r[2],
                "importance": r[3],
                "usage_count": r[4]
            }
            for r in results
        ]
    
    def get_relevant_memories(self, context: str, limit: int = 5) -> List[Dict]:
        """Obtiene memorias relevantes para un contexto"""
        memories = self.search_memories(context, limit * 2)
        
        if not memories:
            return []
        
        # Usar LLM para seleccionar las más relevantes
        prompt = f"Contexto: {context}\n\nMemorias disponibles:\n{json.dumps(memories, indent=2)}\n\nSelecciona las {limit} memorias más relevantes para el contexto. Responde SOLO con una lista de IDs: [1, 2, 3]"
        
        response = self.llm.chat_completion([
            {"role": "system", "content": "Eres un asistente que selecciona memorias relevantes."},
            {"role": "user", "content": prompt}
        ])
        
        try:
            # Intentar parsear la respuesta como lista de IDs
            relevant_ids = json.loads(response)
            
            # Actualizar contadores de uso
            for memory_id in relevant_ids:
                self._update_memory_usage(memory_id)
            
            return [m for m in memories if m["id"] in relevant_ids]
        except:
            # Fallback: tomar las primeras memorias
            return memories[:limit]
    
    def _update_memory_usage(self, memory_id: int):
        """Actualiza el contador de uso de una memoria"""
        query = """
            UPDATE alma.memories 
            SET usage_count = usage_count + 1, 
                last_accessed = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        self.db.execute_command(query, (memory_id,))
    
    def optimize_memory(self) -> int:
        """Optimiza la memoria basado en uso y antigüedad"""
        query = """
            UPDATE alma.memories 
            SET importance = GREATEST(1, importance - 1)
            WHERE last_accessed < CURRENT_TIMESTAMP - INTERVAL '30 days'
            AND usage_count < 3
        """
        return self.db.execute_command(query)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de memoria"""
        queries = {
            'total_memories': "SELECT COUNT(*) FROM alma.memories",
            'high_importance': "SELECT COUNT(*) FROM alma.memories WHERE importance >= 4",
            'avg_usage': "SELECT AVG(usage_count) FROM alma.memories",
            'recent_memories': "SELECT COUNT(*) FROM alma.memories WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'"
        }
        
        stats = {}
        for key, query in queries.items():
            result = self.db.execute_query(query)
            stats[key] = result[0][0] if result else 0
        
        return stats

class MemoryAgent:
    def __init__(self, memory_system: MemorySystem, llm: OpenAIClient):
        self.memory = memory_system
        self.llm = llm
    
    async def process_message(self, message: str, session_id: str = None, use_memory: bool = True) -> Dict[str, Any]:
        """Procesa un mensaje usando memoria contextual"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 1. Obtener memorias relevantes
        relevant_memories = []
        if use_memory:
            relevant_memories = self.memory.get_relevant_memories(message, limit=5)
        
        # 2. Construir contexto con memorias
        memory_context = self._build_memory_context(relevant_memories)
        
        # 3. Generar respuesta usando LLM
        response = self._generate_response(message, memory_context, session_id)
        
        # 4. Extraer y guardar nuevos aprendizajes
        new_memories = self._extract_learnings(message, response, session_id)
        
        # 5. Registrar en logs
        self._log_interaction(session_id, message, response, relevant_memories, new_memories)
        
        return {
            "response": response,
            "session_id": session_id,
            "memories_used": [m["id"] for m in relevant_memories],
            "new_memories": new_memories,
            "confidence": 0.9
        }
    
    def _build_memory_context(self, memories: List[Dict]) -> str:
        if not memories:
            return "No hay memorias relevantes disponibles."
        
        context = "Memorias relevantes:\n"
        for memory in memories:
            context += f"- [{memory['type']}] {memory['content']} (Importancia: {memory['importance']})\n"
        
        return context
    
    def _generate_response(self, message: str, memory_context: str, session_id: str) -> str:
        prompt = f"Eres Alma, un agente inteligente con sistema de memoria.\n\n{memory_context}\n\nInstrucciones:\n- Usa las memorias relevantes para enriquecer tu respuesta\n- Sé conciso pero útil\n- Aprende de cada interacción\n- Responde en el mismo idioma del usuario\n\nUsuario: {message}\nAlma:"
        
        return self.llm.chat_completion([
            {"role": "system", "content": "Eres un agente inteligente con memoria contextual."},
            {"role": "user", "content": prompt}
        ])
    
    def _extract_learnings(self, user_message: str, agent_response: str, session_id: str) -> List[int]:
        """Extrae aprendizajes de la interacción"""
        prompt = f"De esta interacción, extrae 1-2 aprendizajes clave para la memoria del agente:\n\nUsuario: {user_message}\nAgente: {agent_response}\n\nResponde SOLO en formato JSON:\n{{\"learnings\": [{{\"content\": \"texto del aprendizaje\", \"type\": \"observation|insight|fact\", \"importance\": 1-5}}]}}"
        
        response = self.llm.chat_completion([
            {"role": "system", "content": "Extrae aprendizajes clave de conversaciones."},
            {"role": "user", "content": prompt}
        ])
        
        new_memory_ids = []
        try:
            learnings_data = json.loads(response)
            for learning in learnings_data.get("learnings", []):
                memory_id = self.memory.create_memory(
                    content=learning["content"],
                    memory_type=learning["type"],
                    importance=learning["importance"],
                    context=f"Aprendido de sesión: {session_id}"
                )
                if memory_id:
                    new_memory_ids.append(memory_id)
        except:
            # Crear memoria por defecto si no se puede parsear
            memory_id = self.memory.create_memory(
                content=f"Interacción sobre: {user_message[:100]}...",
                memory_type="observation",
                importance=2,
                context=f"Sesión: {session_id}"
            )
            if memory_id:
                new_memory_ids.append(memory_id)
        
        return new_memory_ids
    
    def _log_interaction(self, session_id: str, user_message: str, agent_response: str, 
                        used_memories: List[Dict], new_memories: List[int]):
        """Registra la interacción en logs"""
        try:
            query = """
                INSERT INTO alma.agent_logs 
                (action_type, action_details, input_context, output_result, memory_refs)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            action_details = {
                "session_id": session_id,
                "used_memories_count": len(used_memories),
                "new_memories_count": len(new_memories)
            }
            
            memory_refs = [m["id"] for m in used_memories]
            self.memory.db.execute_command(
                query,
                ("chat_interaction", json.dumps(action_details), user_message, agent_response, memory_refs)
            )
        except Exception as e:
            console.print(f"[yellow]⚠️  Error registrando log: {e}[/yellow]")
    
    def learn_from_recent_logs(self) -> int:
        """Aprende automáticamente de logs recientes"""
        try:
            # Obtener logs de los últimos 3 días
            query = """
                SELECT input_context, output_result 
                FROM alma.agent_logs 
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '3 days'
                ORDER BY timestamp DESC 
                LIMIT 20
            """
            
            logs = self.memory.db.execute_query(query)
            new_memories_count = 0
            
            for user_msg, agent_resp in logs:
                memories = self._extract_learnings(user_msg, agent_resp, "auto_learning")
                new_memories_count += len(memories)
            
            return new_memories_count
        except Exception as e:
            console.print(f"[yellow]⚠️  Error en aprendizaje automático: {e}[/yellow]")
            return 0
    
    def generate_initial_memories(self, count: int) -> int:
        """Genera memorias iniciales automáticamente"""
        base_memories = [
            ("Soy Alma, un agente inteligente con sistema de memoria", "self_knowledge", 5),
            ("Aprendo de cada interacción con los usuarios", "capability", 4),
            ("Puedo recordar información importante de conversaciones pasadas", "capability", 4),
            ("Uso mi memoria para proporcionar respuestas contextuales", "process", 3),
            ("Mi objetivo es ser útil y aprender continuamente", "goal", 4),
            ("Puedo analizar código y proporcionar sugerencias de seguridad", "capability", 4),
            ("Mantengo un registro de mis interacciones para mejorar", "process", 3),
        ]
        
        created = 0
        for content, mem_type, importance in base_memories:
            if created >= count:
                break
            self.memory.create_memory(content, mem_type, importance)
            created += 1
        
        # Generar memorias adicionales usando LLM si es necesario
        if created < count:
            additional_needed = count - created
            prompt = f"Genera {additional_needed} memorias iniciales útiles para un agente AI llamado Alma. Las memorias deben ser conocimientos generales útiles para asistir usuarios. Responde SOLO en formato JSON: {{\"memories\": [{{\"content\": \"texto de la memoria\", \"type\": \"fact|observation|principle\", \"importance\": 1-5}}]}}"
            
            response = self.llm.chat_completion([
                {"role": "system", "content": "Genera memorias útiles para un agente AI."},
                {"role": "user", "content": prompt}
            ])
            
            try:
                memories_data = json.loads(response)
                for memory in memories_data.get("memories", [])[:additional_needed]:
                    self.memory.create_memory(
                        memory["content"],
                        memory["type"],
                        memory["importance"]
                    )
                    created += 1
            except:
                pass
        
        return created
    
    def analyze_behavior(self, days: int = 7) -> Dict[str, Any]:
        """Analiza el comportamiento del agente"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_interactions,
                    AVG(LENGTH(output_result)) as avg_response_length,
                    COUNT(DISTINCT session_id) as unique_sessions
                FROM alma.agent_logs 
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '%s days'
            """
            
            result = self.memory.db.execute_query(query, (days,))
            if result:
                total_interactions, avg_length, unique_sessions = result[0]
                
                # Obtener memorias creadas en el período
                mem_query = "SELECT COUNT(*) FROM alma.memories WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '%s days'"
                mem_result = self.memory.db.execute_query(mem_query, (days,))
                new_memories = mem_result[0][0] if mem_result else 0
                
                return {
                    "period_days": days,
                    "total_interactions": total_interactions or 0,
                    "unique_sessions": unique_sessions or 0,
                    "avg_response_length": round(avg_length or 0, 2),
                    "new_memories_created": new_memories,
                    "memory_usage_rate": round((total_interactions or 0) / max(new_memories, 1), 2)
                }
        except Exception as e:
            console.print(f"[yellow]⚠️  Error analizando comportamiento: {e}[/yellow]")
        
        return {"error": "No se pudieron obtener análisis"}

# =============================================================================
# INICIALIZACIÓN GLOBAL
# =============================================================================

db = DatabaseManager()
llm = OpenAIClient()
memory_system = MemorySystem(db, llm)
memory_agent = MemoryAgent(memory_system, llm)

# =============================================================================
# MODELOS PYDANTIC PARA FASTAPI
# =============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_memory: bool = True

class ChatResponse(BaseModel):
    response: str
    session_id: str
    memories_used: List[int]
    new_memories: List[int]
    confidence: float

class MemoryRequest(BaseModel):
    content: str
    memory_type: str = "observation"
    importance: int = 1
    context: Optional[str] = None

# =============================================================================
# ENDPOINTS FASTAPI
# =============================================================================

@app.get("/")
async def root():
    return {"message": "Alma Agent API", "status": "running", "version": "2.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "database_connected": True,
        "openai_configured": llm.is_configured(),
        "service": "Alma Agent"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat principal con el agente que usa memoria"""
    try:
        result = await memory_agent.process_message(
            request.message, 
            request.session_id,
            use_memory=request.use_memory
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories/search")
async def search_memories(query: str, limit: int = 10):
    """Busca memorias relevantes"""
    memories = memory_system.search_memories(query, limit)
    return {"memories": memories}

@app.post("/memories")
async def create_memory(memory: MemoryRequest):
    """Crea una nueva memoria"""
    memory_id = memory_system.create_memory(
        content=memory.content,
        memory_type=memory.memory_type,
        importance=memory.importance,
        context=memory.context
    )
    return {"memory_id": memory_id, "status": "created"}

@app.get("/agent/insights")
async def get_agent_insights(days: int = 7):
    """Obtiene insights del comportamiento del agente"""
    insights = memory_agent.analyze_behavior(days)
    return insights

# =============================================================================
# COMANDOS CLI
# =============================================================================

@cli.command()
def init_db():
    """Inicializa la base de datos (crea tablas)"""
    try:
        db.init_database()
        console.print("✅ [green]Base de datos inicializada correctamente[/green]")
    except Exception as e:
        console.print(f"❌ [red]Error inicializando base de datos: {e}[/red]")

@cli.command()
def chat():
    """Modo chat interactivo con el agente"""
    console.print(Panel("🤖 Alma Agent - Modo Chat Interactivo", style="blue"))
    console.print("[dim]Escribe 'exit' para salir[/dim]")
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]Tú[/bold cyan]")
            
            if user_input.lower() in ['exit', 'quit', 'salir']:
                break
            if not user_input.strip():
                continue
                
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Procesando...", total=None)
                result = asyncio.run(memory_agent.process_message(user_input, session_id))
            
            console.print(Panel(
                result['response'],
                title="[green]Alma[/green]",
                border_style="green"
            ))
            
            # Mostrar metadatos de memoria
            if result['memories_used']:
                console.print(f"[dim]📚 Memorias usadas: {len(result['memories_used'])}[/dim]")
            if result['new_memories']:
                console.print(f"[dim]💡 Nuevas memorias creadas: {len(result['new_memories'])}[/dim]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Sesión terminada[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
def auto_learn():
    """Ejecuta ciclo de aprendizaje automático"""
    console.print("🧠 [bold]Iniciando aprendizaje automático...[/bold]")
    
    new_memories = memory_agent.learn_from_recent_logs()
    console.print(f"✅ [green]Creadas {new_memories} nuevas memorias[/green]")
    
    optimized = memory_system.optimize_memory()
    console.print(f"🔧 [blue]Memoria optimizada: {optimized} ajustes[/blue]")

@cli.command()
def memory_stats():
    """Muestra estadísticas del sistema de memoria"""
    stats = memory_system.get_memory_stats()
    
    table = Table(title="📊 Estadísticas de Memoria")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="white")
    
    table.add_row("Total Memorias", str(stats['total_memories']))
    table.add_row("Memorias Alta Importancia", str(stats['high_importance']))
    table.add_row("Uso Promedio", f"{stats['avg_usage']:.2f}")
    table.add_row("Memorias Última Semana", str(stats['recent_memories']))
    
    console.print(table)

@cli.command()
def generate_memories():
    """Genera memorias iniciales automáticamente hasta llegar a 100"""
    current_count = memory_system.get_memory_stats()['total_memories']
    target = 100
    
    if current_count >= target:
        console.print(f"✅ [green]Ya tienes {current_count} memorias (meta: {target})[/green]")
        return
        
    needed = target - current_count
    console.print(f"🧠 [bold]Generando {needed} memorias iniciales...[/bold]")
    
    created = memory_agent.generate_initial_memories(needed)
    console.print(f"✅ [green]Creadas {created} nuevas memorias automáticamente[/green]")

@cli.command()
def serve(
    host: str = os.getenv('HOST', '0.0.0.0'),
    port: int = int(os.getenv('PORT', '8000'))
):
    """Inicia el servidor FastAPI"""
    console.print(f"🚀 [bold]Iniciando Alma Agent en {host}:{port}[/bold]")
    
    if not llm.is_configured():
        console.print("[yellow]⚠️  OPENAI_API_KEY no configurada - Algunas funciones no estarán disponibles[/yellow]")
    else:
        console.print("✅ [green]OpenAI configurado[/green]")
    
    uvicorn.run(
        "alma.main:app", 
        host=host, 
        port=port, 
        reload=True,
        log_level="info"
    )

@cli.command()
def check_config():
    """Verifica la configuración actual"""
    console.print("[bold]🔧 Configuración Actual:[/bold]")
    
    config_table = {
        "Database Host": db.conn_params['host'],
        "Database Port": db.conn_params['port'],
        "Database Name": db.conn_params['database'],
        "Database User": db.conn_params['user'],
        "OpenAI API Key": "✅ Configurada" if llm.is_configured() else "❌ No configurada"
    }
    
    for key, value in config_table.items():
        console.print(f"  {key}: {value}")

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    cli()