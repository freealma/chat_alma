"""
---
name: alma.py
title: "Alma - Funcionalidad Principal con LangChain"
version: 0.0.4
changelog: "Respuestas más naturales, contexto inteligente, optimización de recursos"
path: src/alma/alma.py
description: "Funcionalidad principal del paquete Alma con mejoras de UX"
functions: [get_api_key, setup_langchain_agent, main, call_deepseek_natural]
functions_descriptions:
  - get_api_key: "Obtiene la clave API de las variables de entorno"
  - setup_langchain_agent: "Configura el agente de LangChain con herramientas y memoria"
  - main: "Función principal que maneja la interacción del usuario"
  - call_deepseek_natural: "Llama a DeepSeek con prompt mejorado para respuestas naturales"
tags: [alma, cli, deepseek, memoria, langchain, ux-improved]
---
"""
#!/usr/bin/env python3
import os
import sys
from .memory import MemoryManager

# Imports compatibles con LangChain
try:
    from langchain.agents import initialize_agent, AgentType
    from langchain.llms import OpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.tools import Tool
    from langchain.prompts import PromptTemplate
    
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangChain no disponible: {e}")
    print("🔧 Usando modo estándar optimizado")
    LANGCHAIN_AVAILABLE = False

def get_api_key():
    """Obtiene API key de variables de entorno"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY no encontrada")
        print("   Asegúrate de tener un archivo .env con DEEPSEEK_API_KEY=tu_key")
        exit(1)
    return api_key

def call_deepseek_natural(api_key, message, context_summary):
    """Llama a DeepSeek con prompt mejorado para respuestas naturales"""
    import requests
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_msg = f"""Eres Alma, un asistente especializado en hacking y programación.

{context_summary}

**Instrucciones importantes:**
- Responde de forma NATURAL y conversacional
- Integra el conocimiento de forma orgánica, NO lo listes
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
        "max_tokens": 600,            # Respuestas más concisas
        "frequency_penalty": 0.5,     # Evita repeticiones
        "presence_penalty": 0.3,      # Introduce variedad
        "stream": False
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=data, 
            headers=headers, 
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error: {e}"

def setup_langchain_agent(api_key, memory_manager):
    """Configura el agente de LangChain con herramientas mejoradas"""
    if not LANGCHAIN_AVAILABLE:
        return None
    
    try:
        # Wrapper personalizado para DeepSeek
        class DeepSeekLLM:
            def __init__(self, api_key, temperature=0.8, max_tokens=600):
                self.api_key = api_key
                self.temperature = temperature
                self.max_tokens = max_tokens
            
            def __call__(self, prompt):
                import requests
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": False
                }
                
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    json=data, 
                    headers=headers, 
                    timeout=30
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
        
        llm = DeepSeekLLM(api_key=api_key)
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Herramientas mejoradas
        def search_memories_tool(query: str) -> str:
            """Herramienta mejorada para buscar en memorias"""
            try:
                context_summary = memory_manager.get_context_summary(query)
                return context_summary if context_summary else "No hay contexto relevante."
            except Exception as e:
                return f"Error buscando memorias: {e}"
        
        def add_memory_tool(content: str) -> str:
            """Herramienta para agregar memorias"""
            try:
                success = memory_manager.add_memory(content)
                return "✅ Memoria guardada" if success else "❌ Error guardando memoria"
            except Exception as e:
                return f"Error: {e}"
        
        def list_memories_tool(query: str = "") -> str:
            """Herramienta para listar memorias"""
            try:
                memories = memory_manager.search_memories_simple("", limit=8)
                if not memories:
                    return "No hay memorias guardadas."
                
                result = "Memorias recientes:\n"
                for i, mem in enumerate(memories, 1):
                    preview = mem['content'][:60].replace('\n', ' ')
                    result += f"{i}. {preview}...\n"
                return result
            except Exception as e:
                return f"Error: {e}"
        
        tools = [
            Tool(
                name="BuscarContexto",
                func=search_memories_tool,
                description="Buscar conocimiento relevante para la consulta actual"
            ),
            Tool(
                name="GuardarConocimiento",
                func=add_memory_tool, 
                description="Guardar información importante para uso futuro"
            ),
            Tool(
                name="VerMemorias",
                func=list_memories_tool,
                description="Mostrar resumen de memorias recientes"
            )
        ]
        
        # Crear agente
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=False,  # Menos verbosidad
            handle_parsing_errors=True
        )
        
        return agent
        
    except Exception as e:
        print(f"❌ Error configurando LangChain: {e}")
        return None

def main():
    """Función principal con UX mejorada"""
    api_key = get_api_key()
    memory_manager = MemoryManager(api_key=api_key)
    
    # Configurar LangChain solo si está disponible
    agent = None
    if LANGCHAIN_AVAILABLE:
        print("🔧 Configurando agente...")
        agent = setup_langchain_agent(api_key, memory_manager)
    
    print("🤖 Alma CLI v0.0.4 - Chat con Memoria Inteligente")
    print("💬 Respuestas naturales con contexto integrado")
    print("📝 Comandos: /add, /memories, /exit, /searchmode, /metrics")
    print()
    
    use_smart_search = True
    
    while True:
        try:
            user_input = input("🧑 Tú: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'salir']:
                print("👋 ¡Hasta luego!")
                break
            
            # Comandos especiales
            if user_input == '/searchmode':
                use_smart_search = not use_smart_search
                mode = "inteligente" if use_smart_search else "rápido"
                print(f"🔍 Modo búsqueda: {mode}")
                continue
            
            if user_input == '/metrics':
                metrics = memory_manager.get_learning_metrics()
                print("\n📊 Métricas de aprendizaje:")
                for key, value in metrics.items():
                    print(f"   {key}: {value}")
                print()
                continue
            
            if user_input.startswith('/add '):
                content = user_input[5:].strip()
                if content:
                    memory_manager.add_memory(content)
                    print("✅ Guardado")
                continue
            
            if user_input == '/memories':
                memories = memory_manager.search_memories_simple("", limit=8)
                print("\n📚 Resumen de conocimientos:")
                for i, mem in enumerate(memories, 1):
                    preview = mem['content'][:70].replace('\n', ' ')
                    print(f"  {i}. {preview}...")
                print()
                continue
            
            if not user_input:
                continue
            
            # Procesar mensaje
            if agent and LANGCHAIN_AVAILABLE:
                print("💭 Procesando...")
                try:
                    response = agent.run(input=user_input)
                    print(f"🤖 Alma: {response}\n")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print("🔄 Usando modo estándar...")
                    _process_natural_mode(api_key, memory_manager, user_input, use_smart_search)
            else:
                _process_natural_mode(api_key, memory_manager, user_input, use_smart_search)
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def _process_natural_mode(api_key, memory_manager, user_input, use_smart_search):
    """Procesar mensaje con modo natural mejorado"""
    print("💭 Buscando contexto...")
    
    # Obtener resumen de contexto en lugar de memorias crudas
    context_summary = memory_manager.get_context_summary(user_input)
    
    if context_summary:
        print(f"   📚 {context_summary}")
    else:
        print("   💡 Sin contexto específico")
    
    print("💭 Generando respuesta...")
    
    try:
        response = call_deepseek_natural(api_key, user_input, context_summary)
        print(f"🤖 Alma: {response}\n")
        
        # Crear memoria automáticamente si es valioso
        memory_manager.create_memory_from_conversation(user_input, response)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()