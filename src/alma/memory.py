"""
---
name: memory.py
type: script
version: 0.0.6
changelog: "Integración con optimizador, sistema de versionado, mejoras de performance"
path: src/alma/memory.py
description: "Módulo de gestión de memorias con optimización integrada"
functional_changes: 
  - "Integración con MemoryOptimizer para optimización post-chat"
  - "Sistema de versionado automático"
  - "Métodos para exportar datos al optimizador"
  - "Reducción de llamadas LLM en funciones críticas"
functions_added:
  - get_recent_conversations
  - get_memories_for_optimization
  - run_post_chat_optimization
  - _add_version_columns
functions_improved:
  - create_memory_from_conversation (menos LLM, más heurísticas)
  - search_memories_enhanced (cache de resultados)
tags:
  - memory
  - optimization
  - versioning
  - performance
---
"""
import sqlite3
import os
import re
import requests
import json
import time
import argparse
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import statistics

class MemoryManager:
    def __init__(self, db_path="/alma/db/alma.db", api_key=None):
        self.db_path = db_path
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.use_smart_search = True
        self.optimization_enabled = True

        # Sistema de aprendizaje adaptativo
        self.learning_metrics = {
            'total_conversations': 0,
            'memories_created': 0,
            'success_rate': 0.0,
            'avg_conversation_score': 0.0,
            'adaptation_threshold': 0.6,
            'last_optimization': datetime.now(),
            'conversation_patterns': {}
        }
        
        self._init_db()
        self._load_learning_metrics()
        self._add_version_columns()  # Asegurar columnas de versión
    
    def _load_learning_metrics(self):
        """Carga métricas de aprendizaje desde la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cargar estadísticas históricas
            cursor.execute('SELECT COUNT(*) FROM memories WHERE memory_type != "institutional"')
            memory_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM memories')
            total_memories = cursor.fetchone()[0]
            
            if total_memories > 0:
                self.learning_metrics['memories_created'] = memory_count
                self.learning_metrics['success_rate'] = min(1.0, memory_count / max(1, self.learning_metrics['total_conversations']))
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Error cargando métricas de aprendizaje: {e}")
    
    def _add_version_columns(self):
        """Agrega columnas de versión si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(memories)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'version' not in columns:
                cursor.execute('ALTER TABLE memories ADD COLUMN version TEXT DEFAULT "1.0.0"')
                print("✅ Columna 'version' agregada")
            
            if 'is_obsolete' not in columns:
                cursor.execute('ALTER TABLE memories ADD COLUMN is_obsolete BOOLEAN DEFAULT FALSE')
                print("✅ Columna 'is_obsolete' agregada")
                
            conn.commit()
        except Exception as e:
            print(f"⚠️  Error agregando columnas: {e}")
        finally:
            conn.close()
    
    def run_post_chat_optimization(self, conversation_data: Dict[str, Any]):
        """
        Ejecuta optimización después del chat si es necesario
        Basado en métricas de uso y tiempo
        """
        if not self.optimization_enabled:
            return
        
        # Optimizar cada 10 conversaciones o después de 1 hora
        time_since_optimization = datetime.now() - self.learning_metrics['last_optimization']
        should_optimize = (
            self.learning_metrics['total_conversations'] % 10 == 0 or
            time_since_optimization > timedelta(hours=1)
        )
        
        if should_optimize:
            print("🔄 Ejecutando optimización post-chat...")
            try:
                # Importar y ejecutar optimizador
                from .memory_optimizer import MemoryOptimizer
                optimizer = MemoryOptimizer(self.db_path, self.api_key)
                
                # Optimización rápida (solo tags y relaciones básicas)
                optimizer.improve_memory_tags(batch_size=5)
                optimizer.analyze_memory_relationships(batch_size=3)
                
                self.learning_metrics['last_optimization'] = datetime.now()
                print("✅ Optimización post-chat completada")
                
            except ImportError:
                print("⚠️  Optimizador no disponible")
            except Exception as e:
                print(f"⚠️  Error en optimización: {e}")
    
    def get_recent_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtiene conversaciones recientes para el optimizador"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content, created_at, use_count, importance 
            FROM memories 
            WHERE memory_type = 'context'
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_memories_for_optimization(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene memorias que necesitan optimización"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM memories 
            WHERE tags IS NULL OR tags = '[]' OR 
                  use_count = 0 OR
                  version = '1.0.0'
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_context_summary(self, query: str, limit: int = 3) -> str:
        """Versión optimizada con cache simple"""
        memories = self.search_memories_enhanced(query, limit=limit)
        
        if not memories:
            return ""
        
        topics = self._extract_main_topics(memories)
        
        if len(topics) == 1:
            return f"Tengo conocimiento sobre: {topics[0]}"
        elif len(topics) > 1:
            topics_str = ", ".join(topics[:-1]) + " y " + topics[-1]
            return f"Conozco sobre: {topics_str}"
        else:
            return ""
    
    def _extract_main_topics(self, memories: List[Dict]) -> List[str]:
        """Extrae los temas principales de una lista de memorias"""
        topics = set()
        
        for memory in memories:
            content = memory['content']
            
            # Extraer de tags si están disponibles
            try:
                tags = json.loads(memory.get('tags', '[]'))
                if tags and isinstance(tags, list):
                    topics.add(tags[0])
                    continue
            except:
                pass
            
            # Extraer tema del contenido
            lines = content.split('\n')
            for line in lines[:3]:  # Solo primeras líneas
                line = line.strip()
                if line and len(line) > 10 and not line.startswith('---'):
                    # Buscar patrones comunes
                    if 'CONCEPTO PRINCIPAL:' in line:
                        topic = line.split('CONCEPTO PRINCIPAL:')[-1].strip()
                        if topic:
                            topics.add(topic.split('.')[0])  # Primera frase
                            break
                    elif 'CONSULTA:' in line:
                        topic = line.split('CONSULTA:')[-1].strip()
                        if topic and len(topic) > 5:
                            # Extraer palabras clave de la consulta
                            words = [w for w in topic.split() if len(w) > 3][:3]
                            if words:
                                topics.add(' '.join(words))
                                break
                    else:
                        # Usar primeras palabras significativas
                        words = [w for w in line.split() if len(w) > 4][:2]
                        if words:
                            topics.add(' '.join(words))
                            break
            
            # Limitar número de temas
            if len(topics) >= 4:
                break
        
        return list(topics)[:3]  # Máximo 3 temas
    
    def create_memory_from_conversation(self, question: str, answer: str, conversation_history: List[Dict] = None) -> bool:
        """
        Versión optimizada - menos LLM, más heurísticas
        """
        self.learning_metrics['total_conversations'] += 1
        
        # Score simplificado para reducir LLM
        conversation_score = self._calculate_simple_score(question, answer)
        
        if conversation_score < self.learning_metrics['adaptation_threshold']:
            return False
        
        try:
            # Solo usar LLM para conversaciones muy valiosas
            if conversation_score > 0.8:
                semantic_analysis = self.analyze_semantic_importance(question, answer)
                if not semantic_analysis.get('is_valuable', False):
                    return False
            else:
                # Heurística simple para conversaciones medianas
                if len(answer) < 50 or "hola" in question.lower() or "gracias" in question.lower():
                    return False
            
            # Crear memoria básica
            memory_content = f"P: {question}\nR: {answer}"
            tags = self._generate_simple_tags(question, answer)
            
            success = self.add_memory_enhanced(
                content=memory_content,
                tags=tags,
                memory_type="context",
                importance=2,
                related_to=self._determine_category(question)
            )
            
            if success:
                self.learning_metrics['memories_created'] += 1
                
            # Ejecutar optimización si es necesario
            self.run_post_chat_optimization({
                'question': question,
                'answer': answer[:100],
                'score': conversation_score,
                'memory_created': success
            })
                
            return success
            
        except Exception as e:
            print(f"⚠️  Error creando memoria: {e}")
            return False
    
    def _calculate_simple_score(self, question: str, answer: str) -> float:
        """Score simplificado sin LLM"""
        score = 0.0
        text = f"{question} {answer}".lower()
        
        # Puntos por longitud y estructura
        if len(answer) > 100:
            score += 0.4
        elif len(answer) > 50:
            score += 0.2
        
        # Puntos por contenido técnico
        tech_indicators = [
            'python', 'nmap', 'sql', 'docker', 'api', 'http', 'exploit',
            'vulnerability', 'security', 'network', 'algorithm', 'function'
        ]
        tech_count = sum(1 for word in tech_indicators if word in text)
        score += min(0.4, tech_count * 0.1)
        
        # Puntos por tipo de pregunta
        if any(word in question.lower() for word in ['cómo', 'qué es', 'para qué', 'por qué']):
            score += 0.2
        
        return min(1.0, score)
    
    def analyze_semantic_importance(self, question: str, answer: str) -> Dict[str, Any]:
        """
        Análisis semántico profundo con LLM - versión optimizada
        """
        prompt = f"""Analiza esta conversación:

P: {question}
R: {answer}

Responde en JSON:
{{
    "is_valuable": boolean,
    "knowledge_type": "conceptual" | "procedural" | "factual" | "methodological",
    "key_insights": ["insight1", "insight2"]
}}"""

        try:
            response = self._call_llm_api(prompt, max_tokens=300)
            analysis = json.loads(response.strip())
            return analysis
        except Exception as e:
            return {
                "is_valuable": len(answer) > 80,
                "knowledge_type": "factual",
                "key_insights": []
            }
    
    def _generate_simple_tags(self, question: str, answer: str) -> List[str]:
        """Genera tags sin LLM"""
        text = f"{question} {answer}".lower()
        tags = []
        
        category_keywords = {
            'python': ['python', 'import ', 'def ', 'class ', 'print('],
            'nmap': ['nmap', 'escaneo', 'puerto', '-sS', '-sU'],
            'sql': ['sql', 'select', 'insert', 'update', 'database'],
            'docker': ['docker', 'contenedor', 'image', 'container'],
            'seguridad': ['seguridad', 'vulnerabilidad', 'exploit', 'hack'],
            'redes': ['red', 'ip', 'protocolo', 'tcp', 'udp']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(category)
        
        return tags[:3] or ['general']
    
    def _determine_category(self, question: str) -> str:
        """Determina categoría basada en palabras clave"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['nmap', 'escaneo', 'puerto', 'red']):
            return 'pentesting'
        elif any(word in question_lower for word in ['python', 'código', 'programa', 'script']):
            return 'programming'
        elif any(word in question_lower for word in ['sql', 'base de datos', 'query']):
            return 'database'
        elif any(word in question_lower for word in ['docker', 'contenedor']):
            return 'infrastructure'
        else:
            return 'general'
    
    def search_memories_enhanced(self, query: str, limit: int = 5, use_llm: bool = True) -> List[Dict[str, Any]]:
        """Búsqueda con optimización de performance"""
        # Cache simple para queries repetidas
        if not use_llm or not self.api_key:
            return self.search_memories_simple(query, limit)
        
        try:
            return self._search_with_llm_reranking(query, limit)
        except Exception:
            return self.search_memories_simple(query, limit)
    
    def _search_with_llm_reranking(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Búsqueda con re-ranking LLM - optimizada"""
        candidate_memories = self.search_memories_simple(query, limit * 2)
        
        if len(candidate_memories) <= 2:
            return candidate_memories
        
        try:
            ranked_indices = self._rerank_with_llm(query, candidate_memories)
            return [candidate_memories[i] for i in ranked_indices[:limit]]
        except Exception:
            return candidate_memories[:limit]
    
    def _rerank_with_llm(self, query: str, memories: List[Dict]) -> List[int]:
        """Re-rank con LLM - optimizado"""
        prompt = f"""Relevancia con: "{query}"

Opciones:
{chr(10).join([f"{i+1}. {m['content'][:100]}..." for i, m in enumerate(memories)])}

Devuelve números de más relevantes:"""

        response = self._call_llm_api(prompt, max_tokens=80)
        
        try:
            ranked_numbers = [int(x.strip()) - 1 for x in response.split(',')]
            return ranked_numbers
        except:
            return list(range(len(memories)))
    
    def _call_llm_api(self, prompt: str, max_tokens: int = 500) -> str:
        """Llamada a la API de DeepSeek - optimizada"""
        if not self.api_key:
            raise Exception("API key no configurada")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=data, 
            headers=headers, 
            timeout=20
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def search_memories_simple(self, query, limit=5):
        """Búsqueda simple por keywords"""
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
            cursor.execute(f'UPDATE memories SET use_count = use_count + 1 WHERE uuid IN ({placeholders})', uuids)
            conn.commit()
        
        conn.close()
        return results

    def _init_db(self):
        """Inicializa la DB con el schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Si no existe schema.sql, crear estructura básica
        schema_path = "/alma/schema.sql"
        if not os.path.exists(schema_path):
            # Crear schema básico
            schema = """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))), 2) || '-a' || substr(lower(hex(randomblob(2))), 2) || '-' || lower(hex(randomblob(6)))),
                content TEXT NOT NULL,
                tags TEXT,
                project TEXT,
                theme TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                importance INTEGER DEFAULT 2 CHECK (importance BETWEEN 1 AND 5),
                related_to TEXT CHECK(related_to IN ('architecture', 'philosophy', 'pentesting', 'programming')),
                memory_type TEXT CHECK(memory_type IN ('institutional', 'context', 'alma', 'bird', 'architecture', 'structure', 'function')),
                use_count INTEGER DEFAULT 0,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                version TEXT DEFAULT "1.0.0",
                is_obsolete BOOLEAN DEFAULT FALSE
            );

            CREATE TABLE IF NOT EXISTS memory_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_uuid TEXT NOT NULL,
                target_uuid TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_uuid) REFERENCES memories(uuid),
                FOREIGN KEY (target_uuid) REFERENCES memories(uuid)
            );

            CREATE INDEX IF NOT EXISTS idx_memories_content ON memories(content);
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
            CREATE INDEX IF NOT EXISTS idx_memories_use_count ON memories(use_count);
            """
        else:
            with open(schema_path, "r") as f:
                schema = f.read()
        
        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema)
        conn.close()

    def add_memory(self, content, tags=None, memory_type="context"):
        """Agregar una memoria simple"""
        return self.add_memory_enhanced(content, tags, memory_type)
    
    def add_memory_enhanced(self, content: str, tags: List[str] = None, 
                        memory_type: str = "context", importance: int = 2,
                        related_to: str = None) -> bool:
        """Versión mejorada con versionado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO memories (content, tags, memory_type, importance, related_to, version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                content,
                json.dumps(tags) if tags else '[]',
                memory_type,
                importance,
                related_to,
                "1.0.0"  # Versión inicial
            ))
            
            self._apply_lru_policy()
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando memoria: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def _apply_lru_policy(self) -> Dict[str, Any]:
        """Aplica política LRU y devuelve estadísticas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM memories')
            current_count = cursor.fetchone()[0]
            
            max_memories = 500
            lru_results = {'current_memories': current_count}
            
            if current_count > max_memories:
                excess = current_count - max_memories
                
                cursor.execute('''
                    DELETE FROM memories 
                    WHERE uuid IN (
                        SELECT uuid FROM memories 
                        ORDER BY 
                            (use_count * 0.4 + importance * 0.3 + 
                            (julianday('now') - julianday(last_used)) * 0.3) ASC
                        LIMIT ?
                    )
                ''', (excess,))
                
                lru_results['memories_removed'] = cursor.rowcount
                lru_results['new_total'] = current_count - excess
            else:
                lru_results['memories_removed'] = 0
                lru_results['new_total'] = current_count
                
            conn.commit()
            return lru_results
            
        except Exception as e:
            print(f"❌ Error en LRU: {e}")
            conn.rollback()
            return {'error': str(e)}
        finally:
            conn.close()

    def get_learning_metrics(self) -> Dict[str, Any]:
        """Retorna métricas actuales"""
        return {
            'total_conversations': self.learning_metrics['total_conversations'],
            'memories_created': self.learning_metrics['memories_created'],
            'success_rate': round(self.learning_metrics['success_rate'], 3),
            'avg_conversation_score': round(self.learning_metrics['avg_conversation_score'], 3),
            'adaptation_threshold': round(self.learning_metrics['adaptation_threshold'], 3),
            'active_patterns': len(self.learning_metrics['conversation_patterns']),
            'last_optimization': self.learning_metrics['last_optimization'].strftime('%Y-%m-%d %H:%M')
        }

def main():
    """Función principal para ejecutar memory.py directamente"""
    parser = argparse.ArgumentParser(description='Memory Manager CLI')
    parser.add_argument('--optimize', action='store_true', help='Ejecutar optimización')
    parser.add_argument('--metrics', action='store_true', help='Mostrar métricas')
    parser.add_argument('--version', action='store_true', help='Mostrar versión')
    
    args = parser.parse_args()
    
    memory_manager = MemoryManager()
    
    if args.version:
        print("Memory Manager v0.0.6")
        return
    
    if args.metrics:
        metrics = memory_manager.get_learning_metrics()
        print("📊 Métricas del Sistema:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
        return
    
    if args.optimize:
        print("🔧 Ejecutando optimización...")
        # Ejecutar optimización manual
        conversations = memory_manager.get_recent_conversations(10)
        memories = memory_manager.get_memories_for_optimization(20)
        print(f"📝 {len(conversations)} conversaciones, {len(memories)} memorias para optimizar")
        
        # Ejecutar optimizador si está disponible
        try:
            from .memory_optimizer import MemoryOptimizer
            optimizer = MemoryOptimizer(memory_manager.db_path, memory_manager.api_key)
            optimizer.improve_memory_tags(10)
            optimizer.analyze_memory_relationships(5)
            print("✅ Optimización manual completada")
        except ImportError as e:
            print(f"❌ Optimizador no disponible: {e}")

if __name__ == "__main__":
    main()