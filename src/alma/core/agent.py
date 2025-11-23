#!/usr/bin/env python3
#src/alma/core/agent.py
"""
Agente principal que orquesta todos los módulos
"""
import argparse
from typing import List, Dict

from .config import AlmaConfig
from .embedding import DeepSeekEmbedder
from .rag import RAGSystem
from .chat import DeepSeekChat

class AlmaAgent:
    """Agente principal de Alma"""
    
    def __init__(self):
        self.config = AlmaConfig()
        self.embedder = DeepSeekEmbedder(self.config)
        self.rag_system = RAGSystem(self.config)
        self.chat = DeepSeekChat(self.config, self.rag_system)
    
    def validate_setup(self) -> bool:
        """Validar configuración"""
        return self.config.validate()
    
    def generate_embeddings(self):
        """Generar embeddings para chunks"""
        print("🔄 Generando embeddings...")
        self.embedder.generate_all_embeddings()
    
    def chat_mode(self):
        """Modo chat interactivo"""
        if not self.validate_setup():
            return
        
        print("🤖 Alma RAG System")
        print("💬 Chat mode - Type your message or /help")
        
        while True:
            try:
                user_input = input("🧑 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    break
                elif user_input == '/help':
                    self._show_help()
                elif user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    self._handle_chat(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def _show_help(self):
        """Mostrar ayuda de comandos"""
        print("\n📝 Commands:")
        print("  /embeddings - Generate embeddings")
        print("  /metrics    - Show system metrics")
        print("  /exit       - Exit")
        print()
    
    def _handle_command(self, command: str):
        """Manejar comandos especiales"""
        if command == '/embeddings':
            self.generate_embeddings()
        elif command == '/metrics':
            self._show_metrics()
    
    def _handle_chat(self, user_input: str):
        """Manejar mensaje de chat"""
        print("💭 Processing...")
        response = self.chat.process_message(user_input)
        print(f"🤖 Alma: {response}\n")
    
    def _show_metrics(self):
        """Mostrar métricas del sistema"""
        conn = self.config.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
        embedded_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversation_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n📊 System Metrics:")
        print(f"  Chunks: {chunk_count}")
        print(f"  Embedded: {embedded_count}")
        print(f"  Conversations: {conversation_count}")
        print()