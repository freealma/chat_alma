import psycopg2
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json
from rich.console import Console

console = Console()

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'db'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'hood'),  # ⬅️ CORREGIR: 'hood' no 'app'
            'user': os.getenv('DB_USER', 'alma'),
            'password': os.getenv('DB_PASSWORD', 'umamia')
        }
        console.print(f"[dim]🔧 Parámetros DB: {self.connection_params['host']}:{self.connection_params['port']}/{self.connection_params['database']}[/dim]")
    
    def get_connection(self):
        """Establece conexión con la base de datos"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            # Verificar conexión
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user")
                db, user = cur.fetchone()
                console.print(f"[dim]📊 Conectado a: {db} como {user}[/dim]")
            return conn
        except Exception as e:
            console.print(f"[red]❌ Error conectando a DB: {e}[/red]")
            console.print(f"[dim]Intentando conectar a: {self.connection_params}[/dim]")
            raise ConnectionError(f"Error conectando a la base de datos: {e}")
    
    def init_database(self):
        """Inicializa las tablas necesarias para Alma Agent"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Verificar si existe el schema 'alma', si no usar 'public'
                cur.execute("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = 'alma'
                """)
                schema_exists = cur.fetchone()
                
                schema = 'alma' if schema_exists else 'public'
                console.print(f"[dim]📁 Usando schema: {schema}[/dim]")
                
                # Tabla de memorias del agente
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.alma_memories (
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
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.pentest_sessions (
                        id SERIAL PRIMARY KEY,
                        session_name VARCHAR(255) NOT NULL,
                        target TEXT,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'active',
                        findings JSONB
                    )
                """)
                
                conn.commit()
                console.print(f"✅ [green]Tablas creadas en schema: {schema}[/green]")
                
                # Verificar que se crearon
                cur.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND table_name IN ('alma_memories', 'pentest_sessions')
                """, (schema,))
                
                tables_created = cur.fetchall()
                console.print(f"✅ [green]Tablas verificadas: {[t[0] for t in tables_created]}[/green]")
                
        except Exception as e:
            console.print(f"❌ [red]Error inicializando base de datos: {e}[/red]")
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_memory_priority(self, memory_id: int, access_type: str = "read"):
        """Actualiza dinámicamente la prioridad de una memoria basado en uso"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                # Obtener memoria actual
                cur.execute("""
                    SELECT importance, metadata 
                    FROM alma_memories 
                    WHERE id = %s
                """, (memory_id,))
                memory = cur.fetchone()
                
                if not memory:
                    return
                
                current_importance = memory[0]
                metadata = memory[1] or {}
                
                # Actualizar contadores de uso en metadata
                usage_count = metadata.get('usage_count', 0) + 1
                last_accessed = datetime.now().isoformat()
                
                # Calcular nueva importancia (máx 5, mín 1)
                new_importance = min(5, current_importance + 0.1)  # Incremento pequeño por uso
                
                # Si es muy antigua y no se usa, disminuir importancia
                days_since_creation = (datetime.now() - memory[2]).days if len(memory) > 2 else 0
                if days_since_creation > 30 and usage_count < 3:
                    new_importance = max(1, current_importance - 0.5)
                
                # Actualizar memoria
                cur.execute("""
                    UPDATE alma_memories 
                    SET importance = %s, 
                        metadata = jsonb_set(COALESCE(metadata, '{}'::jsonb), '{usage_count}', %s),
                        metadata = jsonb_set(metadata, '{last_accessed}', %s)
                    WHERE id = %s
                """, (new_importance, usage_count, f'"{last_accessed}"', memory_id))
                
                conn.commit()
                
        except Exception as e:
            console.print(f"[yellow]⚠️  Error actualizando prioridad: {e}[/yellow]")

# ⬇️⬇️⬇️ IMPORTANTE: Crear la instancia aquí ⬇️⬇️⬇️
db_manager = DatabaseManager()