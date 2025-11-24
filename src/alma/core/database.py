import psycopg2
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'db'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'alma'),
            'user': os.getenv('DB_USER', 'alma'),
            'password': os.getenv('DB_PASSWORD', 'umamia')
        }
    
    def get_connection(self):
        """Establece conexión con la base de datos"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            raise ConnectionError(f"Error conectando a la base de datos: {e}")
    
    def init_database(self):
        """Inicializa las tablas necesarias para Alma Agent"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Tabla de memorias del agente
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS alma_memories (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        memory_type VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        context TEXT,
                        importance INTEGER DEFAULT 1
                    )
                """)
                
                # Tabla de sesiones de pentesting
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pentest_sessions (
                        id SERIAL PRIMARY KEY,
                        session_name VARCHAR(255) NOT NULL,
                        target TEXT,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'active',
                        findings JSONB
                    )
                """)
                
                conn.commit()
        finally:
            conn.close()

# Instancia global
db_manager = DatabaseManager()