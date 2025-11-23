#!/usr/bin/env python3
# src/alma/core/config.py
"""
Configuración centralizada para Alma
"""
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any

class AlmaConfig:
    """Configuración centralizada de Alma"""
    
    def __init__(self):
        # Rutas base
        self.base_dir = Path(__file__).parent.parent.parent
        self.db_path = self.base_dir / "db" / "alma.db"
        self.chunks_dir = self.base_dir / "data" / "chunks"
        
        # API Keys
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        
        # Configuración de modelos
        self.embedding_model = "deepseek-embedding"
        self.chat_model = "deepseek-chat"
        
        # Configuración de la base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializar esquema de la base de datos"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Schema para memorias de conversación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'memory',
                tags TEXT,
                category TEXT,
                importance INTEGER DEFAULT 2,
                use_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schema para chunks con embeddings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                token_count INTEGER DEFAULT 0,
                category TEXT,
                tags TEXT,
                embedding BLOB,
                embedding_model TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schema para conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                used_chunks TEXT,
                context_used TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def validate(self) -> bool:
        """Validar configuración"""
        if not self.deepseek_api_key:
            print("❌ DEEPSEEK_API_KEY no configurada")
            return False
        return True
    
    def get_db_connection(self):
        """Obtener conexión a la base de datos"""
        return sqlite3.connect(self.db_path)