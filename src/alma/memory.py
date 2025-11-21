"""
---
name: memory.py
type: script
version: 0.0.5
changelog: "Sistema de contexto inteligente, respuestas naturales, optimización de búsquedas"
path: src/alma/memory.py
description: "Módulo de gestión de memorias con contexto inteligente"
functional_changes: 
  - "Nuevo método get_context_summary para resúmenes naturales"
  - "Búsquedas optimizadas con mejor extracción de temas"
  - "Sistema de scoring ajustado para mejor calidad"
  - "Reducción de verbosidad en logs"
functions_added:
  - get_context_summary
  - _extract_main_topics
  - _calculate_relevance_score
functions_improved:
  - search_memories_enhanced (más eficiente)
  - create_memory_from_conversation (menos verboso)
  - _call_llm_api (mejor manejo de errores)
tags:
  - memory
  - context
  - natural-language
  - optimization
---
"""
import sqlite3
import os
import re
import requests
import json
import time
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import statistics

class MemoryManager:
    def __init__(self, db_path="/alma/db/alma.db", api_key=None):
        self.db_path = db_path
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.use_smart_search = True 

        # Sistema de aprendizaje adaptativo
        self.learning_metrics = {
            'total_conversations': 0,
            'memories_created': 0,
            'success_rate': 0.0,
            'avg_conversation_score': 0.0,
            'adaptation_threshold': 0.6,
            'last_adaptation': datetime.now(),
            'conversation_patterns': {}
        }
        
        self._init_db()
        self._load_learning_metrics()
    
    def get_context_summary(self, query: str, limit: int = 3) -> str:
        """
        Devuelve un resumen natural del contexto relevante
        En lugar de listar memorias, extrae temas principales
        """
        memories = self.search_memories_enhanced(query, limit=limit)
        
        if not memories:
            return ""
        
        # Extraer temas principales de las memorias
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
    
    def _load_learning_metrics(self):
        """Carga métricas de aprendizaje desde la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM memories WHERE memory_type != "institutional"')
            memory_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM memories')
            total_memories = cursor.fetchone()[0]
            
            if total_memories > 0:
                self.learning_metrics['memories_created'] = memory_count
                self.learning_metrics['success_rate'] = min(1.0, memory_count / max(1, self.learning_metrics['total_conversations']))
            
            conn.close()
        except Exception as e:
            print(f"⚠️  Error cargando métricas: {e}")
    
    def create_memory_from_conversation(self, question: str, answer: str, conversation_history: List[Dict] = None) -> bool:
        """
        Sistema de creación automática de memorias - versión optimizada
        """
        self.learning_metrics['total_conversations'] += 1
        
        # Calcular score multi-capa
        conversation_score, score_breakdown = self.calculate_conversation_score(question, answer, conversation_history)
        
        # Verificar si supera el umbral adaptativo
        if conversation_score < self.learning_metrics['adaptation_threshold']:
            self._update_conversation_patterns(question, answer, False)
            return False
        
        try:
            # Análisis semántico profundo con LLM
            semantic_analysis = self.analyze_semantic_importance(question, answer)
            
            if not semantic_analysis.get('is_valuable', False):
                self._update_conversation_patterns(question, answer, False)
                return False
            
            # Extraer componentes de conocimiento
            knowledge_components = self.extract_knowledge_components(question, answer, semantic_analysis)
            
            # Crear memoria apropiada
            if self.should_create_composite_memory(question, knowledge_components):
                success = self.create_composite_memory(question, answer, knowledge_components, conversation_history)
            else:
                success = self._create_individual_memory(question, answer, knowledge_components, semantic_analysis)
            
            # Actualizar métricas
            self._update_learning_metrics(success, conversation_score)
            self._update_conversation_patterns(question, answer, success)
            
            if success:
                self.learning_metrics['memories_created'] += 1
                
            return success
            
        except Exception as e:
            print(f"⚠️  Error creando memoria: {e}")
            self._update_conversation_patterns(question, answer, False)
            return False
    
    def calculate_conversation_score(self, question: str, answer: str, conversation_history: List[Dict] = None) -> Tuple[float, Dict]:
        """
        Calcula score 0-1 basado en múltiples factores - versión optimizada
        """
        scores = {}
        
        # 1. Análisis semántico con LLM (40%)
        try:
            semantic_score = self._calculate_semantic_score(question, answer)
            scores['semantic'] = semantic_score
        except Exception:
            scores['semantic'] = 0.3
        
        # 2. Indicadores técnicos (30%)
        technical_score = self._calculate_technical_score(question, answer)
        scores['technical'] = technical_score
        
        # 3. Patrones históricos (20%)
        pattern_score = self._calculate_pattern_score(question, answer)
        scores['patterns'] = pattern_score
        
        # 4. Contexto conversacional (10%)
        context_score = self._calculate_context_score(question, answer, conversation_history)
        scores['context'] = context_score
        
        # Score final ponderado
        final_score = (
            scores['semantic'] * 0.4 +
            scores['technical'] * 0.3 +
            scores['patterns'] * 0.2 +
            scores['context'] * 0.1
        )
        
        return min(1.0, final_score), scores
    
    def _calculate_semantic_score(self, question: str, answer: str) -> float:
        """Calcula score basado en análisis semántico con LLM"""
        prompt = f"""Evalúa el valor educativo de esta conversación (1-10):

P: {question}
R: {answer}

Considera: especificidad técnica, utilidad práctica, aplicabilidad.
Devuelve solo el número:"""

        try:
            response = self._call_llm_api(prompt, max_tokens=20)
            score = float(response.strip())
            return score / 10.0
        except:
            return 0.5
    
    def _calculate_technical_score(self, question: str, answer: str) -> float:
        """Calcula score basado en indicadores técnicos - optimizado"""
        score = 0.0
        text = f"{question} {answer}".lower()
        
        # Indicadores técnicos
        tech_indicators = [
            'python', 'sql', 'nmap', 'metasploit', 'docker', 'api', 'http',
            'vulnerability', 'exploit', 'authentication', 'encryption',
            'algorithm', 'function', 'database', 'network', 'security'
        ]
        
        # Puntos por indicadores técnicos
        tech_count = sum(1 for indicator in tech_indicators if indicator in text)
        score += min(0.5, tech_count * 0.08)
        
        # Puntos por estructura de respuesta
        if len(answer.split()) > 30:  # Menos estricto
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_pattern_score(self, question: str, answer: str) -> float:
        """Calcula score basado en patrones históricos"""
        question_key = question.lower().strip()
        
        for pattern, data in self.learning_metrics['conversation_patterns'].items():
            if pattern in question_key:
                success_rate = data['successes'] / max(1, data['attempts'])
                return success_rate
        
        return 0.3
    
    def _calculate_context_score(self, question: str, answer: str, conversation_history: List[Dict] = None) -> float:
        """Calcula score basado en contexto conversacional"""
        if not conversation_history:
            return 0.2
        
        recent_technical = any(
            any(word in msg.get('content', '').lower() for word in ['python', 'sql', 'nmap', 'security', 'hack'])
            for msg in conversation_history[-3:]
        )
        
        return 0.6 if recent_technical else 0.2
    
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
    
    def extract_knowledge_components(self, question: str, answer: str, semantic_analysis: Dict) -> List[Dict]:
        """
        Extrae componentes de conocimiento - versión optimizada
        """
        prompt = f"""Extrae componentes clave:

P: {question}
R: {answer}

JSON:
{{
    "components": [
        {{
            "concept": "concepto principal",
            "category": "categoría",
            "importance": 1-3
        }}
    ]
}}"""

        try:
            response = self._call_llm_api(prompt, max_tokens=400)
            components_data = json.loads(response.strip())
            return components_data.get('components', [])
        except Exception:
            return [{
                "concept": "Conocimiento técnico",
                "category": "general",
                "importance": 2
            }]
    
    def should_create_composite_memory(self, question: str, knowledge_components: List[Dict]) -> bool:
        """Determina si crear memoria compuesta"""
        return len(knowledge_components) > 2
    
    def create_composite_memory(self, question: str, answer: str, knowledge_components: List[Dict], conversation_history: List[Dict] = None) -> bool:
        """Crea memoria compuesta - versión optimizada"""
        composite_content = f"""CONOCIMIENTO INTEGRADO

CONTEXTO: {question}

COMPONENTES:
"""
        
        for i, component in enumerate(knowledge_components, 1):
            composite_content += f"{i}. {component.get('concept', 'Concepto')} - {component.get('category', 'general')}\n"
        
        composite_content += f"\nRESPUESTA: {answer}"
        
        # Calcular importancia promedio
        avg_importance = statistics.mean([comp.get('importance', 2) for comp in knowledge_components])
        
        return self.add_memory_enhanced(
            content=composite_content,
            tags=[comp.get('category', 'general') for comp in knowledge_components],
            memory_type="structure",
            importance=min(5, int(avg_importance)),
            related_to="architecture"
        )
    
    def _create_individual_memory(self, question: str, answer: str, knowledge_components: List[Dict], semantic_analysis: Dict) -> bool:
        """Crea memoria individual - versión optimizada"""
        main_component = knowledge_components[0] if knowledge_components else {
            "concept": "Técnica/Concepto",
            "category": "general"
        }
        
        memory_content = f"""CONSULTA: {question}

CONOCIMIENTO: {answer}

CONCEPTO: {main_component.get('concept', 'Técnica')}
CATEGORÍA: {main_component.get('category', 'general')}"""
        
        return self.add_memory_enhanced(
            content=memory_content,
            tags=[main_component.get('category', 'general')],
            memory_type="context",
            importance=main_component.get('importance', 2),
            related_to="programming"
        )
    
    def _determine_memory_type(self, semantic_analysis: Dict) -> str:
        """Determina el tipo de memoria basado en análisis semántico"""
        knowledge_type = semantic_analysis.get('knowledge_type', 'factual')
        type_mapping = {
            'conceptual': 'alma',
            'procedural': 'function',
            'methodological': 'structure',
            'factual': 'context'
        }
        return type_mapping.get(knowledge_type, 'context')
    
    def _determine_related_to(self, category: str) -> str:
        """Determina la categoría related_to"""
        category_mapping = {
            'security': 'pentesting',
            'programming': 'programming',
            'infrastructure': 'architecture',
            'methodology': 'philosophy'
        }
        return category_mapping.get(category.lower(), 'programming')
    
    def _update_learning_metrics(self, success: bool, conversation_score: float):
        """Actualiza métricas de aprendizaje"""
        total_attempts = self.learning_metrics['total_conversations']
        current_success_rate = self.learning_metrics['success_rate']
        
        if total_attempts > 0:
            new_success_rate = ((current_success_rate * (total_attempts - 1)) + (1 if success else 0)) / total_attempts
            self.learning_metrics['success_rate'] = new_success_rate
        
        current_avg = self.learning_metrics['avg_conversation_score']
        new_avg = ((current_avg * (total_attempts - 1)) + conversation_score) / total_attempts
        self.learning_metrics['avg_conversation_score'] = new_avg
        
        if total_attempts % 10 == 0:
            self._adapt_threshold()
    
    def _adapt_threshold(self):
        """Adapta el umbral basado en métricas"""
        old_threshold = self.learning_metrics['adaptation_threshold']
        
        if self.learning_metrics['success_rate'] < 0.2:
            new_threshold = max(0.3, old_threshold - 0.1)
        elif self.learning_metrics['success_rate'] > 0.8:
            new_threshold = min(0.9, old_threshold + 0.05)
        else:
            score_ratio = self.learning_metrics['avg_conversation_score'] / old_threshold
            if score_ratio > 1.2:
                new_threshold = min(0.9, old_threshold + 0.05)
            elif score_ratio < 0.8:
                new_threshold = max(0.3, old_threshold - 0.05)
            else:
                new_threshold = old_threshold
        
        if new_threshold != old_threshold:
            self.learning_metrics['adaptation_threshold'] = new_threshold
            self.learning_metrics['last_adaptation'] = datetime.now()
    
    def _update_conversation_patterns(self, question: str, answer: str, success: bool):
        """Actualiza patrones de conversación"""
        words = question.lower().split()
        key_words = [w for w in words if len(w) > 3 and w not in ['cómo', 'qué', 'cuál', 'porque']]
        
        if key_words:
            pattern = ' '.join(key_words[:2])  # Menos palabras clave
            if pattern not in self.learning_metrics['conversation_patterns']:
                self.learning_metrics['conversation_patterns'][pattern] = {
                    'attempts': 0,
                    'successes': 0
                }
            
            self.learning_metrics['conversation_patterns'][pattern]['attempts'] += 1
            if success:
                self.learning_metrics['conversation_patterns'][pattern]['successes'] += 1
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Retorna métricas actuales"""
        return {
            'total_conversations': self.learning_metrics['total_conversations'],
            'memories_created': self.learning_metrics['memories_created'],
            'success_rate': round(self.learning_metrics['success_rate'], 3),
            'avg_conversation_score': round(self.learning_metrics['avg_conversation_score'], 3),
            'adaptation_threshold': round(self.learning_metrics['adaptation_threshold'], 3),
            'active_patterns': len(self.learning_metrics['conversation_patterns']),
            'last_adaptation': self.learning_metrics['last_adaptation'].strftime('%Y-%m-%d %H:%M')
        }

    # === MÉTODOS EXISTENTES MANTENIDOS ===
    
    def should_create_memory(self, question: str, answer: str) -> bool:
        """Método legacy - ahora usa el sistema de scoring completo"""
        score, _ = self.calculate_conversation_score(question, answer)
        return score >= self.learning_metrics['adaptation_threshold']
    
    def extract_important_concepts(self, question: str, answer: str) -> List[str]:
        """Método legacy - ahora usa extracción de componentes"""
        components = self.extract_knowledge_components(question, answer, {})
        return [comp.get('concept', '') for comp in components if comp.get('concept')]
    
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
            timeout=20  # Timeout más corto
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def search_memories_enhanced(self, query: str, limit: int = 5, use_llm: bool = True) -> List[Dict[str, Any]]:
        """Búsqueda mejorada - versión optimizada"""
        if use_llm and self.api_key and len(query.split()) > 2:
            return self._search_with_llm_reranking(query, limit)
        else:
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
    
    def search_memories_simple(self, query, limit=5):
        """Búsqueda simple por keywords - optimizada"""
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
        
        with open("/alma/schema.sql", "r") as f:
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
        """Versión mejorada de add_memory"""
        is_duplicate = self._is_duplicate_memory(content)
        
        if is_duplicate:
            return self._increase_existing_memory_importance(content)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO memories (content, tags, memory_type, importance, related_to)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                content,
                json.dumps(tags) if tags else '[]',
                memory_type,
                importance,
                related_to
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

    def _is_duplicate_memory(self, content: str) -> bool:
        """
        Verifica si ya existe una memoria similar - MENOS ESTRICTO
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extraer palabras clave del contenido
        words = self._extract_keywords(content)
        
        if not words:
            return False
            
        # Buscar coincidencias EXACTAS de contenido, no similares
        cursor.execute('SELECT COUNT(*) FROM memories WHERE content = ?', (content,))
        exact_match = cursor.fetchone()[0] > 0
        
        conn.close()
        
        if exact_match:
            return True
        
        # Solo considerar duplicado si hay al menos 5 palabras clave en común
        if len(words) >= 5:
            conditions = []
            params = []
            for word in words[:5]:  # Usar solo las 5 palabras más importantes
                conditions.append("content LIKE ?")
                params.append(f'%{word}%')
            
            where_clause = " AND ".join(conditions)
            sql = f'SELECT COUNT(*) FROM memories WHERE {where_clause}'
            
            cursor.execute(sql, params)
            count = cursor.fetchone()[0]
            
            if count > 0:
                return True
        
        return False
    
    def _increase_existing_memory_importance(self, content: str) -> bool:
        """Aumenta la importancia de una memoria existente similar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        words = self._extract_keywords(content)
        
        if not words:
            return False
            
        conditions = []
        params = []
        for word in words[:3]:
            conditions.append("content LIKE ?")
            params.append(f'%{word}%')
        
        where_clause = " OR ".join(conditions)
        sql = f'UPDATE memories SET importance = MIN(5, importance + 1) WHERE {where_clause}'
        
        try:
            cursor.execute(sql, params)
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave de un texto"""
        stop_words = {
            'el', 'la', 'los', 'las', 'de', 'en', 'y', 'o', 'pero', 'para', 
            'con', 'sin', 'por', 'que', 'como', 'cuando', 'donde', 'porque'
        }
        
        words = re.findall(r'\b[a-záéíóúñ]{3,20}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]
        
        # Contar frecuencia
        word_count = {}
        for word in filtered_words:
            word_count[word] = word_count.get(word, 0) + 1
        
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10]]
    
    def optimize_memories(self) -> Dict[str, Any]:
        """Optimiza la base de memorias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            optimization_results = {}
            
            # 1. Eliminar duplicados SEMÁNTICOS
            cursor.execute('''
                WITH duplicates AS (
                    SELECT uuid, content,
                        LENGTH(content) as content_length,
                        ROW_NUMBER() OVER (
                            PARTITION BY SUBSTR(content, 1, 100) 
                            ORDER BY use_count DESC, importance DESC, content_length DESC
                        ) as rn
                    FROM memories
                )
                DELETE FROM memories 
                WHERE uuid IN (SELECT uuid FROM duplicates WHERE rn > 1)
            ''')
            optimization_results['semantic_duplicates_removed'] = cursor.rowcount
            
            # 2. Eliminar duplicados EXACTOS
            cursor.execute('''
                DELETE FROM memories 
                WHERE uuid NOT IN (
                    SELECT MIN(uuid) 
                    FROM memories 
                    GROUP BY content
                )
            ''')
            optimization_results['exact_duplicates_removed'] = cursor.rowcount
            
            # 3. Promocionar memorias muy usadas
            cursor.execute('''
                UPDATE memories 
                SET importance = MIN(5, importance + 1)
                WHERE use_count > 8 AND importance < 5
            ''')
            optimization_results['importance_increased'] = cursor.rowcount
            
            # 4. Degradar memorias nunca usadas
            cursor.execute('''
                UPDATE memories 
                SET importance = GREATEST(1, importance - 1)
                WHERE use_count = 0 AND importance > 1
                AND last_used < datetime('now', '-30 days')
            ''')
            optimization_results['importance_decreased'] = cursor.rowcount
            
            # 5. Limpiar relaciones huérfanas
            try:
                cursor.execute('''
                    DELETE FROM memory_relations 
                    WHERE source_uuid NOT IN (SELECT uuid FROM memories)
                    OR target_uuid NOT IN (SELECT uuid FROM memories)
                ''')
                optimization_results['orphaned_relations_removed'] = cursor.rowcount
            except sqlite3.OperationalError:
                optimization_results['orphaned_relations_removed'] = 0
            
            # 6. Reconstruir índices
            cursor.execute('REINDEX idx_memories_content')
            cursor.execute('REINDEX idx_memories_importance')
            
            # 7. Aplicar política LRU
            lru_result = self._apply_lru_policy()
            optimization_results.update(lru_result)
            
            conn.commit()
            
            total_optimizations = sum(optimization_results.values())
            optimization_results['message'] = f'✅ Optimización completada: {total_optimizations} mejoras'
            
            return optimization_results
            
        except Exception as e:
            print(f"❌ Error optimizando: {e}")
            conn.rollback()
            return {'error': str(e)}
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

# Función de compatibilidad
def inject_sample_memories(memory_manager: MemoryManager):
    """Inyecta memorias de muestra para testing"""
    sample_memories = [
        {
            "content": "CONSULTA: ¿Cómo escanear puertos con nmap?\n\nCONOCIMIENTO: Usa 'nmap -sS -p- target_ip' para escaneo SYN de todos los puertos...",
            "tags": ["nmap", "port-scanning", "network-security"],
            "memory_type": "function",
            "importance": 4,
            "related_to": "pentesting"
        }
    ]
    
    for memory in sample_memories:
        memory_manager.add_memory_enhanced(**memory)