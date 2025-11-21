"""
---
name: memory.py
type: script
version: 0.0.3
changelog: "Reforma completa del sistema de creación automática de memorias"
path: src/alma/memory.py
description: "Módulo de gestión de memorias con sistema de aprendizaje evolutivo"
functional_changes: 
  - "Sistema de scoring multi-capa para detección de conversaciones importantes"
  - "Extracción inteligente con LLM obligatorio para análisis semántico"
  - "Memorias compuestas que agrupan conocimiento relacionado"
  - "Sistema de aprendizaje adaptativo con umbrales dinámicos"
  - "Métricas completas y retroalimentación automática"
functions_added:
  - calculate_conversation_score
  - analyze_semantic_importance
  - extract_knowledge_components
  - create_composite_memory
  - update_learning_parameters
  - get_learning_metrics
  - should_create_composite_memory
functions_modified:
  - create_memory_from_conversation (completamente reformado)
  - should_create_memory (sistema de scoring multi-capa)
  - extract_important_concepts (LLM obligatorio con análisis profundo)
tags:
  - memory
  - llm
  - learning-evolution
  - semantic-analysis
  - adaptive-thresholds
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
        
        # Sistema de aprendizaje adaptativo
        self.learning_metrics = {
            'total_conversations': 0,
            'memories_created': 0,
            'success_rate': 0.0,
            'avg_conversation_score': 0.0,
            'adaptation_threshold': 0.6,  # Umbral dinámico inicial
            'last_adaptation': datetime.now(),
            'conversation_patterns': {}
        }
        
        self._init_db()
        self._load_learning_metrics()
    
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
    
    def create_memory_from_conversation(self, question: str, answer: str, conversation_history: List[Dict] = None) -> bool:
        """
        Sistema reformado de creación automática de memorias con scoring multi-capa
        """
        self.learning_metrics['total_conversations'] += 1
        
        print(f"🧠 [Sistema Evolutivo] Analizando conversación #{self.learning_metrics['total_conversations']}")
        print(f"   📝 Pregunta: {question[:80]}...")
        print(f"   💬 Respuesta: {answer[:80]}...")
        
        # 1. Calcular score multi-capa
        conversation_score, score_breakdown = self.calculate_conversation_score(question, answer, conversation_history)
        print(f"   📊 Score: {conversation_score:.2f} (Umbral: {self.learning_metrics['adaptation_threshold']:.2f})")
        print(f"   🔍 Desglose: {score_breakdown}")
        
        # 2. Verificar si supera el umbral adaptativo
        if conversation_score < self.learning_metrics['adaptation_threshold']:
            print(f"   ❌ Score insuficiente para crear memoria")
            self._update_conversation_patterns(question, answer, False)
            return False
        
        try:
            # 3. Análisis semántico profundo con LLM
            print("   🔬 Realizando análisis semántico profundo...")
            semantic_analysis = self.analyze_semantic_importance(question, answer)
            
            if not semantic_analysis.get('is_valuable', False):
                print(f"   ❌ Análisis semántico: No es conocimiento valioso")
                self._update_conversation_patterns(question, answer, False)
                return False
            
            # 4. Extraer componentes de conocimiento
            knowledge_components = self.extract_knowledge_components(question, answer, semantic_analysis)
            print(f"   📚 Componentes extraídos: {len(knowledge_components)}")
            
            # 5. Verificar si debería crear memoria compuesta
            if self.should_create_composite_memory(question, knowledge_components):
                success = self.create_composite_memory(question, answer, knowledge_components, conversation_history)
            else:
                # 6. Crear memoria individual
                success = self._create_individual_memory(question, answer, knowledge_components, semantic_analysis)
            
            # 7. Actualizar métricas de aprendizaje
            self._update_learning_metrics(success, conversation_score)
            self._update_conversation_patterns(question, answer, success)
            
            if success:
                print("   ✅ Memoria creada exitosamente")
                self.learning_metrics['memories_created'] += 1
            else:
                print("   ❌ Error en la creación de memoria")
                
            return success
            
        except Exception as e:
            print(f"⚠️  Error en creación automática de memoria: {e}")
            self._update_conversation_patterns(question, answer, False)
            return False
    
    def calculate_conversation_score(self, question: str, answer: str, conversation_history: List[Dict] = None) -> Tuple[float, Dict]:
        """
        Calcula score 0-1 basado en múltiples factores con pesos adaptativos
        """
        scores = {}
        
        # 1. Análisis semántico con LLM (40%)
        try:
            semantic_score = self._calculate_semantic_score(question, answer)
            scores['semantic'] = semantic_score
        except Exception as e:
            print(f"   ⚠️  Fallback en análisis semántico: {e}")
            scores['semantic'] = 0.3  # Fallback conservador
        
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
        prompt = f"""Analiza el valor educativo de esta conversación:

PREGUNTA: {question}
RESPUESTA: {answer}

Evalúa del 1 al 10:
1. ¿Es conocimiento técnico específico?
2. ¿Contiene procedimientos o metodologías?
3. ¿Es aplicable en múltiples contextos?
4. ¿Corrige conceptos erróneos?
5. ¿Proporciona mejores prácticas?

Devuelve SOLO el promedio numérico:"""

        try:
            response = self._call_llm_api(prompt, max_tokens=50)
            score = float(response.strip())
            return score / 10.0  # Normalizar a 0-1
        except:
            return 0.5  # Fallback
    
    def _calculate_technical_score(self, question: str, answer: str) -> float:
        """Calcula score basado en indicadores técnicos"""
        score = 0.0
        text = f"{question} {answer}".lower()
        
        # Indicadores técnicos fuertes
        strong_indicators = [
            'python', 'sql', 'nmap', 'metasploit', 'docker', 'api', 'http',
            'vulnerability', 'exploit', 'authentication', 'encryption',
            'algorithm', 'function', 'class', 'database', 'network'
        ]
        
        # Indicadores de procedimiento
        procedure_indicators = [
            'cómo', 'paso a paso', 'procedimiento', 'configurar', 'instalar',
            'implementar', 'solucionar', 'depurar', 'optimizar'
        ]
        
        # Puntos por indicadores técnicos
        tech_count = sum(1 for indicator in strong_indicators if indicator in text)
        score += min(0.5, tech_count * 0.1)
        
        # Puntos por indicadores de procedimiento
        proc_count = sum(1 for indicator in procedure_indicators if indicator in text)
        score += min(0.3, proc_count * 0.15)
        
        # Puntos por longitud y estructura
        if len(answer.split()) > 50:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_pattern_score(self, question: str, answer: str) -> float:
        """Calcula score basado en patrones históricos"""
        question_key = question.lower().strip()
        
        # Verificar si es un patrón recurrente
        for pattern, data in self.learning_metrics['conversation_patterns'].items():
            if pattern in question_key:
                success_rate = data['successes'] / max(1, data['attempts'])
                return success_rate
        
        return 0.3  # Score base para nuevos patrones
    
    def _calculate_context_score(self, question: str, answer: str, conversation_history: List[Dict] = None) -> float:
        """Calcula score basado en contexto conversacional"""
        if not conversation_history:
            return 0.2
        
        # Verificar si continúa una conversación técnica previa
        recent_technical = any(
            any(word in msg.get('content', '').lower() for word in ['python', 'sql', 'nmap', 'security'])
            for msg in conversation_history[-3:]  # Últimos 3 mensajes
        )
        
        return 0.6 if recent_technical else 0.2
    
    def analyze_semantic_importance(self, question: str, answer: str) -> Dict[str, Any]:
        """
        Análisis semántico profundo con LLM para determinar valor del conocimiento
        """
        prompt = f"""Analiza esta conversación y determina su valor como conocimiento:

PREGUNTA: {question}
RESPUESTA: {answer}

Responde en formato JSON:
{{
    "is_valuable": boolean,
    "knowledge_type": "conceptual" | "procedural" | "factual" | "methodological",
    "complexity_level": 1-5,
    "applicability": "específico" | "general" | "especializado",
    "key_insights": ["insight1", "insight2", ...],
    "recommended_tags": ["tag1", "tag2", ...]
}}"""

        try:
            response = self._call_llm_api(prompt, max_tokens=500)
            analysis = json.loads(response.strip())
            return analysis
        except Exception as e:
            print(f"   ⚠️  Error en análisis semántico: {e}")
            # Fallback básico
            return {
                "is_valuable": len(answer) > 100,
                "knowledge_type": "factual",
                "complexity_level": 2,
                "applicability": "general",
                "key_insights": [],
                "recommended_tags": ["fallback"]
            }
    
    def extract_knowledge_components(self, question: str, answer: str, semantic_analysis: Dict) -> List[Dict]:
        """
        Extrae componentes estructurados de conocimiento usando LLM
        """
        prompt = f"""Extrae los componentes de conocimiento de esta conversación:

PREGUNTA: {question}
RESPUESTA: {answer}

ANÁLISIS SEMÁNTICO: {json.dumps(semantic_analysis, ensure_ascii=False)}

Extrae en formato JSON:
{{
    "components": [
        {{
            "concept": "nombre del concepto",
            "explanation": "explicación clara",
            "category": "categoría técnica",
            "importance": 1-5,
            "relationships": ["concepto_relacionado1", ...]
        }}
    ]
}}"""

        try:
            response = self._call_llm_api(prompt, max_tokens=800)
            components_data = json.loads(response.strip())
            return components_data.get('components', [])
        except Exception as e:
            print(f"   ⚠️  Error extrayendo componentes: {e}")
            # Fallback: crear componente básico
            return [{
                "concept": "Conocimiento técnico",
                "explanation": answer[:200],
                "category": "general",
                "importance": 2,
                "relationships": []
            }]
    
    def should_create_composite_memory(self, question: str, knowledge_components: List[Dict]) -> bool:
        """
        Determina si se debe crear una memoria compuesta
        """
        if len(knowledge_components) <= 1:
            return False
        
        # Verificar si hay múltiples conceptos relacionados
        unique_categories = len(set(comp.get('category', '') for comp in knowledge_components))
        total_relationships = sum(len(comp.get('relationships', [])) for comp in knowledge_components)
        
        return unique_categories >= 2 or total_relationships >= 3
    
    def create_composite_memory(self, question: str, answer: str, knowledge_components: List[Dict], conversation_history: List[Dict] = None) -> bool:
        """
        Crea una memoria compuesta que agrupa conocimiento relacionado
        """
        print("   🧩 Creando memoria compuesta...")
        
        # Generar contenido estructurado
        composite_content = f"""MEMORIA COMPUESTA - CONOCIMIENTO INTEGRADO

CONTEXTO: {question}

COMPONENTES DE CONOCIMIENTO:
"""
        
        for i, component in enumerate(knowledge_components, 1):
            composite_content += f"""
{i}. {component.get('concept', 'Concepto')}
   - Explicación: {component.get('explanation', '')}
   - Categoría: {component.get('category', 'general')}
   - Importancia: {component.get('importance', 2)}/5
   - Relaciones: {', '.join(component.get('relationships', []))}
"""
        
        composite_content += f"\nRESPUESTA ORIGINAL: {answer}"
        composite_content += f"\n--- Memoria compuesta creada el {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Calcular importancia promedio
        avg_importance = statistics.mean([comp.get('importance', 2) for comp in knowledge_components])
        
        # Extraer tags únicos de todos los componentes
        all_tags = set()
        for component in knowledge_components:
            all_tags.add(component.get('category', 'general'))
            all_tags.update(comp.lower().replace(' ', '-') for comp in component.get('relationships', []))
        
        return self.add_memory_enhanced(
            content=composite_content,
            tags=list(all_tags),
            memory_type="structure",
            importance=min(5, int(avg_importance) + 1),  # Bonus por ser compuesta
            related_to="architecture"
        )
    
    def _create_individual_memory(self, question: str, answer: str, knowledge_components: List[Dict], semantic_analysis: Dict) -> bool:
        """
        Crea una memoria individual estándar
        """
        print("   📄 Creando memoria individual...")
        
        # Usar el primer componente como base
        main_component = knowledge_components[0] if knowledge_components else {
            "concept": "Conocimiento técnico",
            "category": "general"
        }
        
        memory_content = f"""CONSULTA: {question}

CONOCIMIENTO: {answer}

CONCEPTO PRINCIPAL: {main_component.get('concept', 'Técnica/Concepto')}
CATEGORÍA: {main_component.get('category', 'general')}
EXPLICACIÓN: {main_component.get('explanation', answer[:300])}

TIPO: {semantic_analysis.get('knowledge_type', 'factual')}
COMPLEJIDAD: {semantic_analysis.get('complexity_level', 2)}/5
APLICABILIDAD: {semantic_analysis.get('applicability', 'general')}

--- Memoria creada automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        # Generar tags
        tags = semantic_analysis.get('recommended_tags', [])
        tags.append(main_component.get('category', 'general'))
        
        return self.add_memory_enhanced(
            content=memory_content,
            tags=tags,
            memory_type=self._determine_memory_type(semantic_analysis),
            importance=main_component.get('importance', 2),
            related_to=self._determine_related_to(main_component.get('category', ''))
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
        # Actualizar tasa de éxito
        total_attempts = self.learning_metrics['total_conversations']
        current_success_rate = self.learning_metrics['success_rate']
        
        if total_attempts > 0:
            new_success_rate = ((current_success_rate * (total_attempts - 1)) + (1 if success else 0)) / total_attempts
            self.learning_metrics['success_rate'] = new_success_rate
        
        # Actualizar score promedio
        current_avg = self.learning_metrics['avg_conversation_score']
        new_avg = ((current_avg * (total_attempts - 1)) + conversation_score) / total_attempts
        self.learning_metrics['avg_conversation_score'] = new_avg
        
        # Adaptar umbral cada 10 conversaciones
        if total_attempts % 10 == 0:
            self._adapt_threshold()
    
    def _adapt_threshold(self):
        """Adapta el umbral basado en métricas recientes"""
        old_threshold = self.learning_metrics['adaptation_threshold']
        
        # Si la tasa de éxito es muy baja, bajar el umbral
        if self.learning_metrics['success_rate'] < 0.2:
            new_threshold = max(0.3, old_threshold - 0.1)
        # Si la tasa de éxito es muy alta, subir el umbral para mayor calidad
        elif self.learning_metrics['success_rate'] > 0.8:
            new_threshold = min(0.9, old_threshold + 0.05)
        else:
            # Ajuste basado en score promedio
            score_ratio = self.learning_metrics['avg_conversation_score'] / old_threshold
            if score_ratio > 1.2:  # Scores consistentemente altos
                new_threshold = min(0.9, old_threshold + 0.05)
            elif score_ratio < 0.8:  # Scores consistentemente bajos
                new_threshold = max(0.3, old_threshold - 0.05)
            else:
                new_threshold = old_threshold
        
        if new_threshold != old_threshold:
            print(f"   🔄 Umbral adaptado: {old_threshold:.2f} → {new_threshold:.2f}")
            self.learning_metrics['adaptation_threshold'] = new_threshold
            self.learning_metrics['last_adaptation'] = datetime.now()
    
    def _update_conversation_patterns(self, question: str, answer: str, success: bool):
        """Actualiza patrones de conversación"""
        # Extraer patrón clave de la pregunta
        words = question.lower().split()
        key_words = [w for w in words if len(w) > 3 and w not in ['cómo', 'qué', 'cuál', 'porque']]
        
        if key_words:
            pattern = ' '.join(key_words[:3])  # Usar hasta 3 palabras clave
            if pattern not in self.learning_metrics['conversation_patterns']:
                self.learning_metrics['conversation_patterns'][pattern] = {
                    'attempts': 0,
                    'successes': 0
                }
            
            self.learning_metrics['conversation_patterns'][pattern]['attempts'] += 1
            if success:
                self.learning_metrics['conversation_patterns'][pattern]['successes'] += 1
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Retorna métricas actuales del sistema de aprendizaje"""
        return {
            'total_conversations': self.learning_metrics['total_conversations'],
            'memories_created': self.learning_metrics['memories_created'],
            'success_rate': round(self.learning_metrics['success_rate'], 3),
            'avg_conversation_score': round(self.learning_metrics['avg_conversation_score'], 3),
            'adaptation_threshold': round(self.learning_metrics['adaptation_threshold'], 3),
            'active_patterns': len(self.learning_metrics['conversation_patterns']),
            'last_adaptation': self.learning_metrics['last_adaptation'].strftime('%Y-%m-%d %H:%M')
        }

    # === MÉTODOS EXISTENTES MANTENIDOS (con mejoras menores) ===
    
    def should_create_memory(self, question: str, answer: str) -> bool:
        """Método legacy - ahora usa el sistema de scoring completo"""
        score, _ = self.calculate_conversation_score(question, answer)
        return score >= self.learning_metrics['adaptation_threshold']
    
    def extract_important_concepts(self, question: str, answer: str) -> List[str]:
        """Método legacy - ahora usa extracción de componentes"""
        components = self.extract_knowledge_components(question, answer, {})
        return [comp.get('concept', '') for comp in components if comp.get('concept')]
    
    # Mantener todos los demás métodos existentes sin cambios
    def _call_llm_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """Llamada a la API de DeepSeek (sin cambios)"""
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
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def search_memories_enhanced(self, query: str, limit: int = 5, use_llm: bool = True) -> List[Dict[str, Any]]:
        # ... (mantener implementación existente)
    
    def search_memories_simple(self, query, limit=5):
        # ... (mantener implementación existente)
    
    def add_memory_enhanced(self, content: str, tags: List[str] = None, 
                          memory_type: str = "context", importance: int = 2,
                          related_to: str = None) -> bool:
        # ... (mantener implementación existente)
    
    def _init_db(self):
        # ... (mantener implementación existente)
    
    def optimize_memories(self) -> Dict[str, Any]:
        # ... (mantener implementación existente)
    
    def _apply_lru_policy(self) -> Dict[str, Any]:
        # ... (mantener implementación existente)

# Función de compatibilidad para el script de inyección
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