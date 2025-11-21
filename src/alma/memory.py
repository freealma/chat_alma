"""
---
version: 0.0.1
changelog: "Primera versión del paquete Alma"
path: src/alma/memory.py
description: "Módulo de gestión de memorias para Alma"
functions: [MemoryManager]
---
"""
import sqlite3
import os
import re

class MemoryManager:
    def __init__(self, db_path="/alma/db/alma.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inicializa la DB con el schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Leer schema.sql
        with open("/alma/schema.sql", "r") as f:
            schema = f.read()
        
        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema)
        conn.close()
    
    def search_memories(self, query, limit=5):
        """Búsqueda SIMPLE de memorias relevantes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Keywords básicas
        words = [word for word in query.lower().split() if len(word) > 2]
        
        if not words:
            # Si no hay palabras, devolver memorias más usadas
            cursor.execute('''
                SELECT * FROM memories 
                ORDER BY use_count DESC, importance DESC 
                LIMIT ?
            ''', (limit,))
        else:
            # Búsqueda por palabras
            conditions = []
            params = []
            for word in words:
                conditions.append("(content LIKE ? OR tags LIKE ?)")
                params.extend([f'%{word}%', f'%{word}%'])
            
            where_clause = " OR ".join(conditions)
            sql = f'''
                SELECT * FROM memories 
                WHERE {where_clause}
                ORDER BY importance DESC, use_count DESC
                LIMIT ?
            '''
            params.append(limit)
            cursor.execute(sql, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        
        # Actualizar contadores de uso
        if results:
            uuids = [row['uuid'] for row in results]
            placeholders = ','.join(['?'] * len(uuids))
            cursor.execute(f'''
                UPDATE memories 
                SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE uuid IN ({placeholders})
            ''', uuids)
            conn.commit()
        
        conn.close()
        return results
    
    def add_memory(self, content, tags=None, memory_type="context"):
        """Agregar una memoria simple"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memories (content, tags, memory_type)
            VALUES (?, ?, ?)
        ''', (content, str(tags) if tags else None, memory_type))
        
        conn.commit()
        conn.close()
        return True