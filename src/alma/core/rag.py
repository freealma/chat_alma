#!/usr/bin/env python3
# src/alma/core/rag.py
"""
Módulo para Retrieval Augmented Generation
"""
import json
import sqlite3
from typing import List, Dict, Optional
import numpy as np

from .config import AlmaConfig
from .embedding import DeepSeekEmbedder

class RAGSystem:
    """Sistema RAG para búsqueda semántica"""
    
    def __init__(self, config: AlmaConfig):
        self.config = config
        self.embedder = DeepSeekEmbedder(config)
    
    def search_similar_chunks(self, query: str, limit: int = 5) -> List[Dict]:
        """Buscar chunks similares usando embeddings"""
        conn = self.config.get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener todos los chunks con embeddings
        cursor.execute('''
            SELECT chunk_id, content, embedding FROM chunks 
            WHERE embedding IS NOT NULL
        ''')
        chunks_with_embeddings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not chunks_with_embeddings:
            return self._search_keywords(query, limit)
        
        # Generar embedding para la query
        query_embedding = self.embedder.create_embedding(query)
        if not query_embedding:
            return self._search_keywords(query, limit)
        
        # Calcular similitudes
        scored_chunks = []
        for chunk in chunks_with_embeddings:
            chunk_embedding = json.loads(chunk['embedding'])
            similarity = self._cosine_similarity(query_embedding, chunk_embedding)
            scored_chunks.append((similarity, chunk))
        
        # Ordenar por similitud
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for score, chunk in scored_chunks[:limit]]
    
    def _search_keywords(self, query: str, limit: int = 5) -> List[Dict]:
        """Búsqueda por keywords (fallback)"""
        conn = self.config.get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        words = [word for word in query.lower().split() if len(word) > 2]
        
        if not words:
            cursor.execute('''
                SELECT chunk_id, content FROM chunks 
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        else:
            conditions = []
            params = []
            for word in words:
                conditions.append("content LIKE ?")
                params.append(f'%{word}%')
            
            where_clause = " OR ".join(conditions)
            cursor.execute(f'''
                SELECT chunk_id, content FROM chunks 
                WHERE {where_clause} 
                ORDER BY created_at DESC LIMIT ?
            ''', params + [limit])
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcular similitud coseno"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0
    
    def get_context(self, query: str) -> str:
        """Obtener contexto relevante para la query"""
        chunks = self.search_similar_chunks(query, limit=3)
        
        if not chunks:
            return ""
        
        context_parts = []
        for chunk in chunks:
            content = chunk['content']
            if len(content) > 150:
                content = content[:147] + "..."
            context_parts.append(content)
        
        return " | ".join(context_parts)