#!/usr/bin/env python3
# src/alma/core/chat.py
"""
Módulo para manejo de conversaciones con DeepSeek
"""
import requests
import json
from typing import List, Dict

from .config import AlmaConfig
from .rag import RAGSystem

class DeepSeekChat:
    """Manejador de chat con DeepSeek API"""
    
    def __init__(self, config: AlmaConfig, rag_system: RAGSystem):
        self.config = config
        self.rag_system = rag_system
    
    def call_api(self, message: str, context: str = "") -> str:
        """Llamar a la API de DeepSeek"""
        headers = {
            "Authorization": f"Bearer {self.config.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        system_msg = f"""You are Alma, a technical assistant specialized in hacking and programming.

Context: {context}

Instructions:
- Respond in English only
- Be technical and concise
- Integrate context naturally without listing sources
- Focus on practical solutions"""
        
        data = {
            "model": self.config.chat_model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 800
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
            return f"❌ API Error: {e}"
    
    def save_conversation(self, user_input: str, ai_response: str, context: str = ""):
        """Guardar conversación en base de datos"""
        conn = self.config.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO conversations (user_input, ai_response, context_used)
                VALUES (?, ?, ?)
            ''', (user_input, ai_response, context))
            conn.commit()
        except Exception as e:
            print(f"❌ Error guardando conversación: {e}")
        finally:
            conn.close()
    
    def process_message(self, user_input: str) -> str:
        """Procesar mensaje y generar respuesta"""
        # Obtener contexto
        context = self.rag_system.get_context(user_input)
        
        # Generar respuesta
        response = self.call_api(user_input, context)
        
        # Guardar conversación
        self.save_conversation(user_input, response, context)
        
        return response