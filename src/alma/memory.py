"""
---
name: memory.py
type: script
version: 0.0.2
changelog: "Se agrega consulta mejorada de memorias con re-ranking LLM"
path: src/alma/memory.py
description: "modulo de gestión de memorias con búsqueda mejorada con LLM"
functional_changes: "Se agrega método search_memories_enhanced que usa LLM para re-ranking"
functions_added:
  - search_memories_enhanced
functions_modified:
  - search_memories_simple
tags:
  - memory
  - llm
  - database

---
"""
import sqlite3
import os
import re
import requests
import json
import numpy as np
from typing import List, Dict, Any

class MemoryManager:
    def __init__(self, db_path="/alma/db/alma.db", api_key=None):
        self.db_path = db_path
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self._init_db()
    
    def search_memories_enhanced(self, query: str, limit: int = 5, use_llm: bool = True) -> List[Dict[str, Any]]:
        """Búsqueda mejorada que puede usar LLM para relevancia"""
        if use_llm and self.api_key:
            return self._search_with_llm_reranking(query, limit)
        else:
            return self.search_memories_simple(query, limit)
    
    def _search_with_llm_reranking(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Búsqueda híbrida: keyword + re-ranking con LLM"""
        # 1. Búsqueda inicial por keywords (rápida)
        candidate_memories = self.search_memories_simple(query, limit * 2)
        
        if len(candidate_memories) <= 1:
            return candidate_memories
        
        # 2. Re-ranking con LLM para los top candidatos
        try:
            ranked_indices = self._rerank_with_llm(query, candidate_memories)
            reranked_memories = [candidate_memories[i] for i in ranked_indices[:limit]]
            return reranked_memories
        except Exception as e:
            print(f"⚠️  Fallback a búsqueda simple: {e}")
            return candidate_memories[:limit]
    
    def _rerank_with_llm(self, query: str, memories: List[Dict]) -> List[int]:
        """Usa LLM para re-rankear memorias por relevancia"""
        prompt = f"""Evalúa la relevancia de estas memorias con la consulta: "{query}"

Memorias:
{chr(10).join([f"{i+1}. {m['content'][:150]}..." for i, m in enumerate(memories)])}

Devuelve SOLO los números de las 5 memorias más relevantes en orden descendente, separados por comas:"""

        response = self._call_llm_api(prompt, max_tokens=100)
        
        # Parsear respuesta: "3, 1, 5, 2"
        try:
            ranked_numbers = [int(x.strip()) - 1 for x in response.split(',')]
            return ranked_numbers
        except:
            # Fallback: devolver orden original
            return list(range(len(memories)))
    
    def _call_llm_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """Llamada simple a la API de DeepSeek"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Baja temperatura para consistencia
            "max_tokens": max_tokens,
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
    
    def search_memories_simple(self, query, limit=5):
        """Búsqueda original por keywords (renombrada)"""
        # Tu implementación actual aquí
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        words = [word for word in query.lower().split() if len(word) > 2]
        
        if not words:
            cursor.execute('SELECT * FROM memories ORDER BY use_count DESC, importance DESC LIMIT ?', (limit,))
        else:
            conditions = []
            params = []
            for word in words:
                conditions.append("(content LIKE ? OR tags LIKE ?)")
                params.extend([f'%{word}%', f'%{word}%'])
            
            where_clause = " OR ".join(conditions)
            sql = f'SELECT * FROM memories WHERE {where_clause} ORDER BY importance DESC, use_count DESC LIMIT ?'
            params.append(limit)
            cursor.execute(sql, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        
        if results:
            uuids = [row['uuid'] for row in results]
            placeholders = ','.join(['?'] * len(uuids))
            cursor.execute(f'UPDATE memories SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP WHERE uuid IN ({placeholders})', uuids)
            conn.commit()
        
        conn.close()
        return results
    
    # Mantener los métodos existentes
    def _init_db(self):
        """Inicializa la DB con el schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with open("/alma/schema.sql", "r") as f:
            schema = f.read()
        
        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema)
        conn.close()
    
    def add_memory(self, content, tags=None, memory_type="context"):
        """Agregar una memoria simple"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO memories (content, tags, memory_type) VALUES (?, ?, ?)', 
                     (content, str(tags) if tags else None, memory_type))
        
        conn.commit()
        conn.close()
        return True