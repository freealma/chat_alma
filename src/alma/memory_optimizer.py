"""
---
name: memory_optimizer.py
title: "Optimizador de Memorias con LLM"
version: 1.0.0
path: src/alma/optimization/memory_optimizer.py
description: "Script separado para optimización avanzada de memorias usando LLM"
functions: [analyze_memory_relationships, improve_memory_tags, consolidate_knowledge, version_memories]
tags: [optimization, llm, relationships, versioning]
---
"""
import sqlite3
import json
import requests
from typing import List, Dict, Any
from datetime import datetime

class MemoryOptimizer:
    def __init__(self, db_path: str, api_key: str):
        self.db_path = db_path
        self.api_key = api_key
    
    def analyze_memory_relationships(self, batch_size: int = 10):
        """Analiza y crea relaciones entre memorias usando LLM"""
        memories = self._get_memories_without_relations(limit=batch_size)
        
        for memory in memories:
            try:
                # Encontrar memorias relacionadas
                related_memories = self._find_related_memories_llm(memory)
                
                # Crear relaciones en la base de datos
                for related_memory, relation_type, strength in related_memories:
                    self._create_relation(
                        memory['uuid'], 
                        related_memory, 
                        relation_type, 
                        strength
                    )
                
                print(f"✅ Memoria {memory['uuid'][:8]} - {len(related_memories)} relaciones creadas")
                
            except Exception as e:
                print(f"❌ Error analizando memoria {memory['uuid'][:8]}: {e}")
    
    def _find_related_memories_llm(self, memory: Dict) -> List[tuple]:
        """Usa LLM para encontrar memorias relacionadas"""
        prompt = f"""Analiza esta memoria y encuentra relaciones con otras:

MEMORIA ACTUAL:
{memory['content'][:500]}

MEMORIAS EXISTENTES:
{self._get_other_memories_preview(memory['uuid'])}

Para cada memoria relacionada, identifica:
1. UUID de la memoria relacionada
2. Tipo de relación: "similar", "complementaria", "opuesta", "jerarquica", "secuencial"
3. Fuerza de relación (0.1 a 1.0)

Responde en JSON:
{{
    "relations": [
        {{
            "target_uuid": "uuid",
            "relation_type": "tipo",
            "strength": 0.8
        }}
    ]
}}"""

        response = self._call_llm_api(prompt)
        
        try:
            data = json.loads(response)
            return [
                (rel['target_uuid'], rel['relation_type'], rel['strength'])
                for rel in data.get('relations', [])
            ]
        except:
            return []
    
    def improve_memory_tags(self, batch_size: int = 15):
        """Mejora los tags de las memorias usando LLM"""
        memories = self._get_memories_with_basic_tags(limit=batch_size)
        
        for memory in memories:
            try:
                improved_tags = self._generate_improved_tags_llm(memory)
                self._update_memory_tags(memory['uuid'], improved_tags)
                print(f"✅ Tags mejorados para {memory['uuid'][:8]}: {improved_tags}")
            except Exception as e:
                print(f"❌ Error mejorando tags: {e}")
    
    def _generate_improved_tags_llm(self, memory: Dict) -> List[str]:
        """Genera tags mejorados usando LLM"""
        prompt = f"""Mejora los tags para esta memoria técnica:

CONTENIDO:
{memory['content']}

TAGS ACTUALES: {json.loads(memory.get('tags', '[]'))}

Genera 3-5 tags específicos y relevantes para hacking/programación.
Considera: tecnologías, técnicas, conceptos, herramientas.

Responde en JSON:
{{
    "improved_tags": ["tag1", "tag2", "tag3"]
}}"""

        response = self._call_llm_api(prompt)
        
        try:
            data = json.loads(response)
            return data.get('improved_tags', [])
        except:
            return json.loads(memory.get('tags', '[]'))
    
    def consolidate_knowledge(self):
        """Consolida conocimiento similar en memorias compuestas"""
        similar_groups = self._find_similar_memories_llm()
        
        for group in similar_groups:
            if len(group) > 1:
                self._create_composite_memory(group)
                print(f"🧩 Consolidadas {len(group)} memorias similares")
    
    def version_memories(self):
        """Agrega versión a las memorias y marca memorias obsoletas"""
        # Primero agregar columna de versión si no existe
        self._add_version_column()
        
        # Analizar memorias para versionado
        memories_to_version = self._get_memories_for_versioning()
        
        for memory in memories_to_version:
            version_info = self._analyze_memory_version_llm(memory)
            self._update_memory_version(memory['uuid'], version_info)
    
    def _add_version_column(self):
        """Agrega columna de versión a la tabla memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(memories)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'version' not in columns:
                cursor.execute('ALTER TABLE memories ADD COLUMN version TEXT DEFAULT "1.0.0"')
                cursor.execute('ALTER TABLE memories ADD COLUMN is_obsolete BOOLEAN DEFAULT FALSE')
                conn.commit()
                print("✅ Columna de versión agregada")
        except Exception as e:
            print(f"❌ Error agregando columna: {e}")
        finally:
            conn.close()
    
    def _analyze_memory_version_llm(self, memory: Dict) -> Dict[str, Any]:
        """Analiza si una memoria necesita actualización de versión"""
        prompt = f"""Analiza esta memoria técnica:

CONTENIDO:
{memory['content']}

FECHA CREACIÓN: {memory['created_at']}

Determina:
1. ¿Está actualizada? (tecnologías/conceptos vigentes)
2. Versión recomendada (semver)
3. ¿Está obsoleta?

Responde en JSON:
{{
    "is_up_to_date": boolean,
    "recommended_version": "1.0.0",
    "is_obsolete": boolean,
    "update_reason": "razón"
}}"""

        response = self._call_llm_api(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                "is_up_to_date": True,
                "recommended_version": "1.0.0",
                "is_obsolete": False,
                "update_reason": "Análisis falló"
            }
    
    def _call_llm_api(self, prompt: str) -> str:
        """Llamada a la API de DeepSeek"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000,
            "stream": False
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=data, 
            headers=headers, 
            timeout=60
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    # Métodos de base de datos auxiliares
    def _get_memories_without_relations(self, limit: int = 10):
        """Obtiene memorias sin relaciones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.* FROM memories m
            LEFT JOIN memory_relations mr ON m.uuid = mr.source_uuid
            WHERE mr.id IS NULL
            ORDER BY m.importance DESC, m.use_count DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def _get_other_memories_preview(self, exclude_uuid: str) -> str:
        """Obtiene preview de otras memorias para el LLM"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT uuid, content FROM memories 
            WHERE uuid != ? 
            ORDER BY importance DESC 
            LIMIT 20
        ''', (exclude_uuid,))
        
        preview = ""
        for uuid, content in cursor.fetchall():
            preview += f"UUID: {uuid}\nContenido: {content[:100]}...\n\n"
        
        conn.close()
        return preview
    
    def _create_relation(self, source_uuid: str, target_uuid: str, relation_type: str, strength: float):
        """Crea una relación entre memorias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO memory_relations (source_uuid, target_uuid, relation_type, strength)
                VALUES (?, ?, ?, ?)
            ''', (source_uuid, target_uuid, relation_type, strength))
            
            conn.commit()
        except Exception as e:
            print(f"❌ Error creando relación: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _get_memories_with_basic_tags(self, limit: int = 15):
        """Obtiene memorias con tags básicos para mejorar"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM memories 
            WHERE tags IS NULL OR tags = '[]' OR tags LIKE '%general%'
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def _update_memory_tags(self, uuid: str, tags: List[str]):
        """Actualiza los tags de una memoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE memories SET tags = ? WHERE uuid = ?
            ''', (json.dumps(tags), uuid))
            
            conn.commit()
        finally:
            conn.close()
    
    def _update_memory_version(self, uuid: str, version_info: Dict):
        """Actualiza la versión de una memoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE memories 
                SET version = ?, is_obsolete = ?
                WHERE uuid = ?
            ''', (
                version_info.get('recommended_version', '1.0.0'),
                version_info.get('is_obsolete', False),
                uuid
            ))
            
            conn.commit()
        finally:
            conn.close()

# Script de ejecución
def main():
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    db_path = "/alma/db/alma.db"
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY no encontrada")
        return
    
    optimizer = MemoryOptimizer(db_path, api_key)
    
    print("🚀 Iniciando optimización de memorias...")
    
    # 1. Agregar versión
    print("📝 Agregando sistema de versionado...")
    optimizer.version_memories()
    
    # 2. Mejorar tags
    print("🏷️  Mejorando tags...")
    optimizer.improve_memory_tags()
    
    # 3. Crear relaciones
    print("🔗 Creando relaciones...")
    optimizer.analyze_memory_relationships()
    
    # 4. Consolidar conocimiento
    print("🧩 Consolidando conocimiento...")
    optimizer.consolidate_knowledge()
    
    print("🎉 Optimización completada!")

if __name__ == "__main__":
    main()