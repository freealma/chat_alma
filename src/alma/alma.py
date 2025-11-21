"""
---
name: alma.py
title: "Alma - Funcionalidad Principal con LangChain"
version: 0.1.1
changelog: "Actualizado a dependencias compatibles"
path: src/alma/alma.py
description: "Funcionalidad principal del paquete Alma con LangChain"
functions: [get_api_key, setup_langchain_agent, main]
functions_descriptions:
  - get_api_key: "Obtiene la clave API de las variables de entorno"
  - setup_langchain_agent: "Configura el agente de LangChain con herramientas y memoria"
  - main: "Función principal que maneja la interacción del usuario"
tags: [alma, cli, deepseek, memoria, langchain]
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
    print("🔧 Usando modo fallback sin LangChain")
    LANGCHAIN_AVAILABLE = False

def get_api_key():
    """Obtiene API key de variables de entorno"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY no encontrada")
        print("   Asegúrate de tener un archivo .env con DEEPSEEK_API_KEY=tu_key")
        exit(1)
    return api_key

def setup_langchain_agent(api_key, memory_manager):
    """Configura el agente de LangChain con herramientas personalizadas"""
    if not LANGCHAIN_AVAILABLE:
        return None
    
    try:
        # Para DeepSeek, necesitamos crear un wrapper personalizado
        # ya que LangChain no tiene soporte nativo
        class DeepSeekLLM:
            def __init__(self, api_key, temperature=0.7, max_tokens=1000):
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
        
        # Usar el wrapper personalizado de DeepSeek
        llm = DeepSeekLLM(api_key=api_key)
        
        # Memoria conversacional
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Herramientas personalizadas
        def search_memories_tool(query: str) -> str:
            """Herramienta para buscar en memorias"""
            try:
                memories = memory_manager.search_memories_enhanced(query, use_llm=True)
                if memories:
                    context = "MEMORIAS RELEVANTES:\n"
                    for memory in memories:
                        context += f"- {memory['content'][:150]}...\n"
                    return context
                return "No se encontraron memorias relevantes."
            except Exception as e:
                return f"Error buscando memorias: {e}"
        
        def add_memory_tool(content: str) -> str:
            """Herramienta para agregar memorias"""
            try:
                success = memory_manager.add_memory(content)
                return "✅ Memoria guardada exitosamente" if success else "❌ Error guardando memoria"
            except Exception as e:
                return f"Error agregando memoria: {e}"
        
        def list_memories_tool(query: str = "") -> str:
            """Herramienta para listar memorias"""
            try:
                memories = memory_manager.search_memories_enhanced("", limit=10, use_llm=False)
                if not memories:
                    return "No hay memorias guardadas."
                
                result = "📚 Últimas memorias:\n"
                for i, mem in enumerate(memories, 1):
                    result += f"  {i}. {mem['content'][:80]}... (usos: {mem['use_count']})\n"
                return result
            except Exception as e:
                return f"Error listando memorias: {e}"
        
        # Definir herramientas
        tools = [
            Tool(
                name="BuscarMemorias",
                func=search_memories_tool,
                description="Buscar en memorias previas para obtener contexto relevante"
            ),
            Tool(
                name="AgregarMemoria",
                func=add_memory_tool, 
                description="Guardar información importante en las memorias"
            ),
            Tool(
                name="ListarMemorias",
                func=list_memories_tool,
                description="Mostrar las memorias recientes guardadas"
            )
        ]
        
        # Crear agente
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent
        
    except Exception as e:
        print(f"❌ Error configurando LangChain: {e}")
        return None

def main():
    """Función principal"""
    api_key = get_api_key()
    memory_manager = MemoryManager(api_key=api_key)
    
    # Configurar LangChain solo si está disponible
    agent = None
    if LANGCHAIN_AVAILABLE:
        print("🔧 Configurando agente LangChain...")
        agent = setup_langchain_agent(api_key, memory_manager)
    
    print("🤖 Alma CLI v0.1.1" + (" con LangChain" if agent else " (Modo Estándar)"))
    print("💬 Chat con memoria persistente")
    print("📝 Comandos: /add, /memories, /exit, /searchmode, /metrics")
    
    if agent:
        print("🔧 Modo LangChain: razonamiento automático con herramientas")
    else:
        print("🔧 Modo Estándar: sistema de memorias original")
    
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
                mode = "smart (con LLM)" if use_smart_search else "simple (rápido)"
                print(f"🔍 Modo de búsqueda cambiado a: {mode}")
                continue
            
            if user_input == '/metrics':
                metrics = memory_manager.get_learning_metrics()
                print("\n📊 Métricas del Sistema de Aprendizaje:")
                for key, value in metrics.items():
                    print(f"   {key}: {value}")
                print()
                continue
            
            if user_input.startswith('/add '):
                content = user_input[5:].strip()
                if content:
                    memory_manager.add_memory(content)
                    print("✅ Memoria guardada")
                continue
            
            if user_input == '/memories':
                memories = memory_manager.search_memories_enhanced("", limit=10, use_llm=use_smart_search)
                print("\n📚 Últimas memorias:")
                for i, mem in enumerate(memories, 1):
                    print(f"  {i}. {mem['content'][:80]}... (usos: {mem['use_count']})")
                print()
                continue
            
            if not user_input:
                continue
            
            # Procesar mensaje
            if agent and LANGCHAIN_AVAILABLE:
                # Usar LangChain si está disponible
                print("🤖 Procesando con LangChain...")
                try:
                    response = agent.run(input=user_input)
                    print(f"🤖 Alma: {response}\n")
                except Exception as e:
                    print(f"❌ Error en LangChain: {e}")
                    print("🔄 Cayendo a modo estándar...")
                    _process_with_standard_mode(api_key, memory_manager, user_input, use_smart_search)
            else:
                # Usar modo estándar
                _process_with_standard_mode(api_key, memory_manager, user_input, use_smart_search)
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def _process_with_standard_mode(api_key, memory_manager, user_input, use_smart_search):
    """Procesar mensaje usando el sistema estándar (sin LangChain)"""
    import requests
    
    print("🔍 Buscando memorias relevantes...")
    memories = memory_manager.search_memories_enhanced(
        user_input, 
        use_llm=use_smart_search
    )
    
    if memories and use_smart_search:
        print(f"   ✅ Memorias encontradas (re-rankeadas por relevancia)")
    elif memories:
        print(f"   ✅ {len(memories)} memorias encontradas")
    else:
        print("   ℹ️  No se encontraron memorias relevantes")
    
    print("🤖 Generando respuesta...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Preparar contexto
    context = "MEMORIAS RELEVANTES:\n"
    for memory in memories:
        context += f"- {memory['content']}\n"
    
    system_msg = f"""Eres Alma, un asistente especializado en hacking y programación.

{context}

Responde de manera técnica y útil, basándote en la información anterior cuando sea relevante."""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
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
        final_response = response.json()['choices'][0]['message']['content']
        print(f"🤖 Alma: {final_response}\n")
        
        # Intentar crear memoria automáticamente (sistema de aprendizaje)
        memory_manager.create_memory_from_conversation(user_input, final_response)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()