"""
---
name: memory_optimizer.py
title: "Optimizador de Memorias con LLM y argparse"
version: 1.1.0
path: src/alma/memory_optimizer.py
description: "Script de optimización avanzada con interfaz CLI"
functions: [main, optimize_tags, optimize_relationships, version_memories, full_optimization]
tags: [optimization, llm, cli, relationships]
---
"""
import sqlite3
import json
import requests
import argparse
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

class MemoryOptimizer:
    def __init__(self, db_path: str, api_key: str):
        self.db_path = db_path
        self.api_key = api_key
        self.stats = {
            'tags_improved': 0,
            'relations_created': 0,
            'memories_versioned': 0,
            'errors': 0
        }
    
    def optimize_tags(self, batch_size: int = 10) -> Dict[str, Any]:
        """Optimiza tags de memorias"""
        print(f"🏷️  Optimizando tags ({batch_size} memorias)...")
        
        memories = self._get_memories_with_basic_tags(limit=batch_size)
        improved_count = 0
        
        for memory in memories:
            try:
                improved_tags = self._generate_improved_tags_llm(memory)
                if improved_tags and improved_tags != json.loads(memory.get('tags', '[]')):
                    self._update_memory_tags(memory['uuid'], improved_tags)
                    improved_count += 1
                    print(f"  ✅ {memory['uuid'][:8]}: {improved_tags}")
            except Exception as e:
                print(f"  ❌ Error en {memory['uuid'][:8]}: {e}")
                self.stats['errors'] += 1
        
        self.stats['tags_improved'] = improved_count
        return {'improved': improved_count, 'total': len(memories)}
    
    def optimize_relationships(self, batch_size: int = 5) -> Dict[str, Any]:
        """Crea relaciones entre memorias"""
        print(f"🔗 Creando relaciones ({batch_size} memorias)...")
        
        memories = self._get_memories_without_relations(limit=batch_size)
        relations_created = 0
        
        for memory in memories:
            try:
                relations = self._find_related_memories_llm(memory)
                for target_uuid, relation_type, strength in relations:
                    if self._create_relation(memory['uuid'], target_uuid, relation_type, strength):
                        relations_created += 1
                
                if relations:
                    print(f"  ✅ {memory['uuid'][:8]}: {len(relations)} relaciones")
                    
            except Exception as e:
                print(f"  ❌ Error en {memory['uuid'][:8]}: {e}")
                self.stats['errors'] += 1
        
        self.stats['relations_created'] = relations_created
        return {'relations_created': relations_created, 'memories_processed': len(memories)}
    
    def version_memories(self, batch_size: int = 15) -> Dict[str, Any]:
        """Actualiza versionado de memorias"""
        print(f"📝 Versionando memorias ({batch_size})...")
        
        memories = self._get_memories_for_versioning(limit=batch_size)
        versioned_count = 0
        
        for memory in memories:
            try:
                version_info = self._analyze_memory_version_llm(memory)
                if self._update_memory_version(memory['uuid'], version_info):
                    versioned_count += 1
                    status = "obsoleta" if version_info.get('is_obsolete') else "actualizada"
                    print(f"  ✅ {memory['uuid'][:8]}: v{version_info.get('recommended_version', '1.0.0')} ({status})")
            except Exception as e:
                print(f"  ❌ Error versionando {memory['uuid'][:8]}: {e}")
                self.stats['errors'] += 1
        
        self.stats['memories_versioned'] = versioned_count
        return {'versioned': versioned_count, 'total': len(memories)}
    
    def full_optimization(self, batch_size: int = 10):
        """Ejecuta optimización completa"""
        print("🚀 Ejecutando optimización completa...")
        
        results = {}
        results['tags'] = self.optimize_tags(batch_size)
        results['relationships'] = self.optimize_relationships(batch_size // 2)
        results['versioning'] = self.version_memories(batch_size)
        
        print("\n📊 Resumen de optimización:")
        print(f"  🏷️  Tags mejorados: {self.stats['tags_improved']}")
        print(f"  🔗 Relaciones creadas: {self.stats['relations_created']}")
        print(f"  📝 Memorias versionadas: {self.stats['memories_versioned']}")
        print(f"  ❌ Errores: {self.stats['errors']}")
        
        return results

    # Métodos LLM (se mantienen iguales al anterior)
    def _generate_improved_tags_llm(self, memory: Dict) -> List[str]:
        prompt = f"""Mejora los tags para esta memoria técnica:

CONTENIDO:
{memory['content'][:400]}

TAGS ACTUALES: {json.loads(memory.get('tags', '[]'))}

Genera 3-5 tags específicos para hacking/programación.
Responde SOLO con JSON: {{"tags": ["tag1", "tag2", "tag3"]}}"""

        try:
            response = self._call_llm_api(prompt)
            data = json.loads(response)
            return data.get('tags', [])
        except:
            return json.loads(memory.get('tags', '[]'))
    
    def _find_related_memories_llm(self, memory: Dict) -> List[tuple]:
        prompt = f"""Encuentra relaciones para esta memoria:

MEMORIA: {memory['content'][:300]}

OTRAS MEMORIAS:
{self._get_other_memories_preview(memory['uuid'])}

Responde con JSON: {{"relations": [{{"target_uuid": "uuid", "relation_type": "tipo", "strength": 0.8}}]}}"""

        try:
            response = self._call_llm_api(prompt)
            data = json.loads(response)
            return [
                (rel['target_uuid'], rel['relation_type'], rel['strength'])
                for rel in data.get('relations', [])
            ]
        except:
            return []
    
    def _analyze_memory_version_llm(self, memory: Dict) -> Dict[str, Any]:
        prompt = f"""Analiza esta memoria técnica:

CONTENIDO: {memory['content'][:300]}
FECHA: {memory.get('created_at', 'N/A')}

Responde con JSON: {{
    "is_up_to_date": boolean,
    "recommended_version": "1.0.0", 
    "is_obsolete": boolean,
    "update_reason": "razón"
}}"""

        try:
            response = self._call_llm_api(prompt)
            return json.loads(response)
        except:
            return {
                "is_up_to_date": True,
                "recommended_version": "1.0.0",
                "is_obsolete": False,
                "update_reason": "Análisis falló"
            }
    
    def _call_llm_api(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=data, 
            headers=headers, 
            timeout=45
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    # Métodos de base de datos (se mantienen iguales)
    def _get_memories_with_basic_tags(self, limit: int):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM memories 
            WHERE tags IS NULL OR tags = '[]' OR json_array_length(tags) < 2
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def _get_memories_without_relations(self, limit: int):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.* FROM memories m
            LEFT JOIN memory_relations mr ON m.uuid = mr.source_uuid
            WHERE mr.id IS NULL AND m.use_count > 0
            ORDER BY m.importance DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def _get_memories_for_versioning(self, limit: int):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM memories 
            WHERE version = '1.0.0' OR is_obsolete = FALSE
            ORDER BY use_count DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def _get_other_memories_preview(self, exclude_uuid: str) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT uuid, content FROM memories 
            WHERE uuid != ? 
            ORDER BY importance DESC 
            LIMIT 15
        ''', (exclude_uuid,))
        
        preview = ""
        for uuid, content in cursor.fetchall():
            preview += f"UUID: {uuid}\nContenido: {content[:80]}...\n\n"
        
        conn.close()
        return preview
    
    def _update_memory_tags(self, uuid: str, tags: List[str]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE memories SET tags = ? WHERE uuid = ?', 
                      (json.dumps(tags), uuid))
        conn.commit()
        conn.close()
        return True
    
    def _create_relation(self, source_uuid: str, target_uuid: str, relation_type: str, strength: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar que la memoria objetivo existe
            cursor.execute('SELECT 1 FROM memories WHERE uuid = ?', (target_uuid,))
            if not cursor.fetchone():
                return False
            
            cursor.execute('''
                INSERT OR IGNORE INTO memory_relations 
                (source_uuid, target_uuid, relation_type, strength)
                VALUES (?, ?, ?, ?)
            ''', (source_uuid, target_uuid, relation_type, strength))
            
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _update_memory_version(self, uuid: str, version_info: Dict) -> bool:
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
            return cursor.rowcount > 0
        except:
            conn.rollback()
            return False
        finally:
            conn.close()

def main():
    """Función principal con argparse"""
    parser = argparse.ArgumentParser(
        description='Memory Optimizer - Mejora automática de memorias con LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  python memory_optimizer.py --full                    # Optimización completa
  python memory_optimizer.py --tags --batch 15         # Solo tags, 15 memorias
  python memory_optimizer.py --relations --batch 8     # Solo relaciones
  python memory_optimizer.py --version --batch 20      # Solo versionado
        '''
    )
    
    parser.add_argument('--full', action='store_true', help='Optimización completa')
    parser.add_argument('--tags', action='store_true', help='Optimizar tags')
    parser.add_argument('--relations', action='store_true', help='Crear relaciones')
    parser.add_argument('--version', action='store_true', help='Actualizar versionado')
    parser.add_argument('--batch', type=int, default=10, help='Tamaño del lote (default: 10)')
    parser.add_argument('--db-path', default='/alma/db/alma.db', help='Ruta de la base de datos')
    
    args = parser.parse_args()
    
    # Verificar API key
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY no encontrada")
        sys.exit(1)
    
    # Verificar base de datos
    if not os.path.exists(args.db_path):
        print(f"❌ Base de datos no encontrada: {args.db_path}")
        sys.exit(1)
    
    optimizer = MemoryOptimizer(args.db_path, api_key)
    
    if args.full or (not args.tags and not args.relations and not args.version):
        # Por defecto hacer optimización completa
        optimizer.full_optimization(batch_size=args.batch)
    else:
        if args.tags:
            optimizer.optimize_tags(batch_size=args.batch)
        if args.relations:
            optimizer.optimize_relationships(batch_size=args.batch // 2)
        if args.version:
            optimizer.version_memories(batch_size=args.batch)

if __name__ == "__main__":
    main()