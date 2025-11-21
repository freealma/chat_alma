"""
---
name: alma.py
title: "Alma - Funcionalidad Principal"
version: 0.0.2
changelog: "Agregado soporte para búsqueda mejorada con LLM"
path: src/alma/alma.py
description: "Funcionalidad principal del paquete Alma"
functions: [get_api_key, call_deepseek, main]
functions_descriptions:
  - get_api_key: "Obtiene la clave API de las variables de entorno"
  - call_deepseek: "Llama a la API de DeepSeek con el mensaje y el contexto de memorias"
  - main: "Función principal que maneja la interacción del usuario y el flujo del programa"
tags: [alma, cli, deepseek, memoria]
---
"""
#!/usr/bin/env python3
import os
import requests
from .memory import MemoryManager

def get_api_key():
    """Obtiene API key de variables de entorno"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY no encontrada")
        print("   Asegúrate de tener un archivo .env con DEEPSEEK_API_KEY=tu_key")
        exit(1)
    return api_key

def call_deepseek(api_key, message, context_memories):
    """Llama a la API de DeepSeek"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Preparar contexto
    context = "MEMORIAS RELEVANTES:\n"
    for memory in context_memories:
        context += f"- {memory['content']}\n"
    
    system_msg = f"""Eres Alma, un asistente especializado en hacking y programación.

{context}

Responde de manera técnica y útil, basándote en la información anterior cuando sea relevante."""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": message}
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
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error: {e}"

def main():
    """Función principal"""
    api_key = get_api_key()
    
    # ✅ CAMBIO IMPORTANTE: Pasar api_key al MemoryManager
    memory_manager = MemoryManager(api_key=api_key)
    
    print("🤖 Alma CLI v0.0.2")
    print("💬 Chat con memoria persistente")
    print("📝 Comandos: /add, /memories, /exit, /searchmode")
    print("🔍 Modos de búsqueda: simple (rápido) | smart (con LLM)")
    print()
    
    # Variable para controlar el modo de búsqueda
    use_smart_search = True  # Por defecto usar búsqueda inteligente
    
    # Forzar flush del output
    import sys
    sys.stdout.flush()
    
    while True:
        try:
            user_input = input("🧑 Tú: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'salir']:
                print("👋 ¡Hasta luego!")
                break
            
            # ✅ NUEVO COMANDO: Cambiar modo de búsqueda
            if user_input == '/searchmode':
                use_smart_search = not use_smart_search
                mode = "smart (con LLM)" if use_smart_search else "simple (rápido)"
                print(f"🔍 Modo de búsqueda cambiado a: {mode}")
                continue
            
            # Comando para agregar memoria
            if user_input.startswith('/add '):
                content = user_input[5:].strip()
                if content:
                    memory_manager.add_memory(content)
                    print("✅ Memoria guardada")
                continue
            
            # Comando para listar memorias
            if user_input == '/memories':
                # ✅ USAR BÚSQUEDA MEJORADA también para listar
                memories = memory_manager.search_memories_enhanced("", limit=10, use_llm=use_smart_search)
                print("\n📚 Últimas memorias:")
                for i, mem in enumerate(memories, 1):
                    print(f"  {i}. {mem['content'][:80]}... (usos: {mem['use_count']})")
                print()
                continue
            
            # Chat normal
            if not user_input:
                continue
            
            print("🔍 Buscando memorias relevantes...")
            
            # ✅ CAMBIO PRINCIPAL: Usar búsqueda mejorada
            search_mode = "smart" if use_smart_search else "simple"
            print(f"   Modo: {search_mode}")
            
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
            response = call_deepseek(api_key, user_input, memories)
            
            print(f"🤖 Alma: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()