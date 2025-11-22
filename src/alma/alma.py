"""
---
name: alma.py  
title: "Alma - CLI Principal con Optimización Integrada"
version: 0.0.6
changelog: "Fix: LLM real en lugar de respuesta simulada, mejor manejo de comandos"
path: src/alma/alma.py
description: "CLI principal con llamadas reales a DeepSeek"
functions: [main, chat_mode, optimize_mode, metrics_mode, call_deepseek_natural]
functions_descriptions:
  - main: "Función principal con argparse"
  - chat_mode: "Modo chat interactivo con LLM real"
  - optimize_mode: "Modo optimización"
  - metrics_mode: "Mostrar métricas del sistema"
  - call_deepseek_natural: "Llamada real a la API de DeepSeek"
tags: [alma, cli, deepseek, memory, optimization]
---
"""
#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from .memory import MemoryManager

# Imports compatibles con LangChain
try:
    from langchain.agents import initialize_agent, AgentType
    from langchain.llms import OpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.tools import Tool
    
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain no disponible, usando modo estándar")

def get_api_key():
    """Obtiene API key de variables de entorno"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY no encontrada")
        print("   Asegúrate de tener un archivo .env con DEEPSEEK_API_KEY=tu_key")
        sys.exit(1)
    return api_key

def call_deepseek_natural(api_key: str, message: str, context_summary: str) -> str:
    """
    Llama a la API REAL de DeepSeek para generar respuestas naturales
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # System prompt mejorado para respuestas naturales
    system_msg = f"""Eres Alma, un asistente especializado en hacking y programación.

Contexto disponible:
{context_summary}

**Instrucciones importantes:**
- Responde de forma NATURAL y conversacional
- Integra el conocimiento del contexto de forma orgánica, NO lo listes
- Evita frases como "basándome en mis memorias" o "según mi conocimiento"
- Enfócate en dar la respuesta útil directamente
- Sé conciso pero completo
- Mantén un tono técnico pero accesible

Si la información del contexto es relevante, úsala sin mencionar explícitamente de dónde viene."""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": message}
        ],
        "temperature": 0.8,           # Más creatividad
        "max_tokens": 800,            # Respuestas adecuadas
        "frequency_penalty": 0.5,     # Evita repeticiones
        "presence_penalty": 0.3,      # Introduce variedad
        "stream": False
    }
    
    try:
        print("🔄 Consultando a DeepSeek...")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=data, 
            headers=headers, 
            timeout=30
        )
        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content']
        return result
    except Exception as e:
        return f"❌ Error al contactar DeepSeek: {e}"

def setup_langchain_agent(api_key: str, memory_manager: MemoryManager):
    """Configura el agente de LangChain con herramientas reales"""
    if not LANGCHAIN_AVAILABLE:
        return None
    
    try:
        # Wrapper personalizado para DeepSeek
        class DeepSeekLLM:
            def __init__(self, api_key, temperature=0.7, max_tokens=800):
                self.api_key = api_key
                self.temperature = temperature
                self.max_tokens = max_tokens
            
            def __call__(self, prompt):
                return call_deepseek_natural(self.api_key, prompt, "")
        
        llm = DeepSeekLLM(api_key=api_key)
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Herramientas reales
        def search_memories_tool(query: str) -> str:
            """Herramienta real para buscar en memorias"""
            try:
                context_summary = memory_manager.get_context_summary(query)
                return context_summary if context_summary else "No hay contexto relevante para esta consulta."
            except Exception as e:
                return f"Error buscando memorias: {e}"
        
        def add_memory_tool(content: str) -> str:
            """Herramienta real para agregar memorias"""
            try:
                success = memory_manager.add_memory(content)
                return "✅ Memoria guardada exitosamente" if success else "❌ Error guardando memoria"
            except Exception as e:
                return f"Error: {e}"
        
        def list_memories_tool(query: str = "") -> str:
            """Herramienta real para listar memorias"""
            try:
                memories = memory_manager.search_memories_simple("", limit=8)
                if not memories:
                    return "No hay memorias guardadas actualmente."
                
                result = "📚 Memorias recientes:\n"
                for i, mem in enumerate(memories, 1):
                    preview = mem['content'][:60].replace('\n', ' ').strip()
                    result += f"{i}. {preview}...\n"
                return result
            except Exception as e:
                return f"Error: {e}"
        
        tools = [
            Tool(
                name="BuscarContexto",
                func=search_memories_tool,
                description="Buscar conocimiento relevante en las memorias para la consulta actual"
            ),
            Tool(
                name="GuardarConocimiento", 
                func=add_memory_tool,
                description="Guardar información importante en las memorias para uso futuro"
            ),
            Tool(
                name="VerMemorias",
                func=list_memories_tool,
                description="Mostrar un resumen de las memorias recientes guardadas"
            )
        ]
        
        # Crear agente real
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=False,
            handle_parsing_errors=True
        )
        
        return agent
        
    except Exception as e:
        print(f"❌ Error configurando LangChain: {e}")
        return None

def chat_mode(memory_manager, use_langchain=True):
    """Modo chat interactivo CON LLM REAL"""
    api_key = get_api_key()
    agent = None
    
    if LANGCHAIN_AVAILABLE and use_langchain:
        print("🔧 Configurando agente LangChain...")
        agent = setup_langchain_agent(api_key, memory_manager)
        mode = "LangChain"
    else:
        mode = "Estándar"
    
    print(f"🤖 Alma CLI v0.0.6 - Chat con Memoria ({mode})")
    print("💬 Escribe tu mensaje o /help para comandos")
    print()
    
    while True:
        try:
            user_input = input("🧑 Tú: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'salir']:
                print("👋 ¡Hasta luego!")
                break
            
            if user_input == '/help':
                print("\n📝 Comandos disponibles:")
                print("  /add <texto>      - Guardar memoria")
                print("  /memories         - Listar memorias recientes")
                print("  /metrics          - Mostrar métricas del sistema")
                print("  /optimize         - Ejecutar optimización manual")
                print("  /exit             - Salir")
                print()
                continue
            
            if user_input.startswith('/add '):
                content = user_input[5:].strip()
                if content:
                    success = memory_manager.add_memory(content)
                    print("✅ Memoria guardada" if success else "❌ Error guardando memoria")
                continue
            
            if user_input == '/memories':
                memories = memory_manager.search_memories_simple("", limit=8)
                print("\n📚 Memorias recientes:")
                for i, mem in enumerate(memories, 1):
                    preview = mem['content'][:70].replace('\n', ' ').strip()
                    print(f"  {i}. {preview}...")
                print()
                continue
            
            if user_input == '/metrics':
                metrics = memory_manager.get_learning_metrics()
                print("\n📊 Métricas del sistema:")
                for key, value in metrics.items():
                    print(f"  {key}: {value}")
                print()
                continue
            
            if user_input == '/optimize':
                print("🔧 Ejecutando optimización manual...")
                memory_manager.run_post_chat_optimization({'manual': True})
                continue
            
            if not user_input:
                continue
            
            # Procesar mensaje normal CON LLM REAL
            _process_message(api_key, memory_manager, user_input, agent)
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def _process_message(api_key: str, memory_manager: MemoryManager, user_input: str, agent=None):
    """Procesar un mensaje individual CON LLM REAL"""
    print("💭 Buscando contexto relevante...")
    
    # Obtener contexto real
    context_summary = memory_manager.get_context_summary(user_input)
    
    if context_summary:
        print(f"   📚 {context_summary}")
    else:
        print("   💡 Sin contexto específico disponible")
    
    # Generar respuesta REAL con DeepSeek
    try:
        if agent and LANGCHAIN_AVAILABLE:
            print("🤖 Procesando con LangChain...")
            response = agent.run(input=user_input)
        else:
            print("🤖 Generando respuesta...")
            response = call_deepseek_natural(api_key, user_input, context_summary)
        
        print(f"🤖 Alma: {response}\n")
        
        # Crear memoria automáticamente si es valioso
        memory_manager.create_memory_from_conversation(user_input, response)
        
    except Exception as e:
        print(f"❌ Error generando respuesta: {e}")

def optimize_mode(memory_manager, batch_size=10):
    """Modo optimización manual"""
    print("🔧 Ejecutando optimización manual...")
    
    try:
        from .memory_optimizer import MemoryOptimizer
        optimizer = MemoryOptimizer(memory_manager.db_path, memory_manager.api_key)
        
        print(f"📦 Procesando lotes de {batch_size} memorias...")
        results = optimizer.full_optimization(batch_size=batch_size)
        
        print("\n✅ Optimización manual completada")
        return results
        
    except ImportError as e:
        print(f"❌ Optimizador no disponible: {e}")
        return None

def metrics_mode(memory_manager):
    """Mostrar métricas detalladas"""
    metrics = memory_manager.get_learning_metrics()
    
    print("📊 MÉTRICAS DETALLADAS DEL SISTEMA")
    print("=" * 40)
    
    print("🤖 Sistema de Aprendizaje:")
    for key, value in metrics.items():
        if key not in ['conversation_patterns', 'last_adaptation']:
            print(f"  {key}: {value}")
    
    print("\n💾 Base de Datos:")
    memories = memory_manager.search_memories_simple("", limit=1000)
    total_memories = len(memories)
    memory_types = {}
    
    for memory in memories:
        mem_type = memory.get('memory_type', 'unknown')
        memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
    
    print(f"  Total memorias: {total_memories}")
    for mem_type, count in memory_types.items():
        print(f"  - {mem_type}: {count}")
    
    print(f"\n🔄 Última optimización: {metrics.get('last_optimization', 'N/A')}")

def main():
    """Función principal con argparse"""
    parser = argparse.ArgumentParser(
        description='Alma - Asistente con Memoria y Optimización Automática',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Modos de uso:
  alma                          # Modo chat interactivo (default)
  alma --optimize               # Solo optimización
  alma --metrics               # Solo métricas
  alma --batch 15              # Optimización con lote específico

Ejemplos:
  alma --optimize --batch 20    # Optimizar 20 memorias
  alma --metrics               # Ver estadísticas
  alma --no-langchain          # Chat sin LangChain
        '''
    )
    
    parser.add_argument('--optimize', action='store_true', help='Modo optimización')
    parser.add_argument('--metrics', action='store_true', help='Mostrar métricas')
    parser.add_argument('--batch', type=int, default=10, help='Tamaño de lote para optimización')
    parser.add_argument('--no-langchain', action='store_true', help='Deshabilitar LangChain')
    parser.add_argument('--db-path', default='/alma/db/alma.db', help='Ruta de la base de datos')
    
    args = parser.parse_args()
    
    # Configurar memory manager
    api_key = get_api_key()
    memory_manager = MemoryManager(db_path=args.db_path, api_key=api_key)
    
    if args.metrics:
        metrics_mode(memory_manager)
    elif args.optimize:
        optimize_mode(memory_manager, batch_size=args.batch)
    else:
        # Modo chat por defecto
        chat_mode(memory_manager, use_langchain=not args.no_langchain)

if __name__ == "__main__":
    main()