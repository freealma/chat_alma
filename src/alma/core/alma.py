#!/usr/bin/env python3
"""
Alma Unified - Chat con RAG y Memoria Integrada
Versión con LangChain + LlamaIndex pero sin embeddings pesados
"""
import os
import sys
import sqlite3
import json
import argparse
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

class AlmaMemoryManager:
    """Gestor unificado de memorias con RAG"""
    
    def __init__(self, db_path: str = "/alma/db/alma.db", api_key: str = None):
        self.db_path = db_path
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self._init_db()
        
        # Inicializar LlamaIndex si está disponible
        self.vector_index = None
        self._init_llama_index()
    
    def _init_db(self):
        """Inicializar base de datos"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
        if not cursor.fetchone():
            schema = """
            CREATE TABLE memories (
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
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
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
            """
            cursor.executescript(schema)
            print("✅ Base de datos inicializada")
        
        conn.close()
    
    def _init_llama_index(self):
        """Inicializar LlamaIndex sin embeddings pesados"""
        try:
            from llama_index import VectorStoreIndex, Document
            from llama_index.embeddings import OpenAIEmbedding
            
            # Usar embeddings simples que no requieren modelos pesados
            embed_model = OpenAIEmbedding()
            
            documents = self._load_memories_as_documents()
            
            if documents:
                self.vector_index = VectorStoreIndex.from_documents(
                    documents, 
                    embed_model=embed_model
                )
                print(f"✅ LlamaIndex inicializado con {len(documents)} memorias")
            else:
                print("ℹ️  No hay memorias para indexar aún")
                
        except ImportError:
            print("⚠️  LlamaIndex no disponible, usando búsqueda por keywords")
        except Exception as e:
            print(f"⚠️  Error inicializando LlamaIndex: {e}")
            print("🔄 Usando búsqueda por keywords como fallback")
    
    def _load_memories_as_documents(self):
        """Cargar memorias como documentos de LlamaIndex"""
        try:
            from llama_index import Document
        except ImportError:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT uuid, content, tags, memory_type, importance 
            FROM memories 
            WHERE content IS NOT NULL AND LENGTH(content) > 10
        ''')
        
        documents = []
        for row in cursor.fetchall():
            uuid, content, tags, memory_type, importance = row
            
            doc = Document(
                text=content,
                metadata={
                    "uuid": uuid,
                    "tags": tags or "",
                    "memory_type": memory_type or "context",
                    "importance": importance or 2,
                    "source": "alma_memory"
                }
            )
            documents.append(doc)
        
        conn.close()
        return documents
    
    def add_memory(self, content: str, tags: List[str] = None, 
                   memory_type: str = "context", importance: int = 2,
                   related_to: str = None) -> bool:
        """Agregar nueva memoria"""
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
            
            conn.commit()
            
            if self.vector_index is not None:
                self._update_llama_index()
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando memoria: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _update_llama_index(self):
        """Actualizar índice de LlamaIndex"""
        try:
            from llama_index import VectorStoreIndex
            from llama_index.embeddings import OpenAIEmbedding
            
            documents = self._load_memories_as_documents()
            if documents:
                embed_model = OpenAIEmbedding()
                self.vector_index = VectorStoreIndex.from_documents(
                    documents, 
                    embed_model=embed_model
                )
        except Exception as e:
            print(f"⚠️  Error actualizando LlamaIndex: {e}")
    
    def search_memories_rag(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Búsqueda usando RAG con LlamaIndex"""
        if self.vector_index is None:
            return self.search_memories_keywords(query, limit)
        
        try:
            from llama_index import VectorStoreIndex
            
            query_engine = self.vector_index.as_query_engine()
            response = query_engine.query(query)
            
            relevant_memories = []
            if response.source_nodes:
                for node in response.source_nodes[:limit]:
                    memory_data = {
                        'content': node.node.text,
                        'metadata': node.node.metadata,
                        'score': node.score
                    }
                    relevant_memories.append(memory_data)
            
            return relevant_memories
            
        except Exception as e:
            print(f"⚠️  Error en búsqueda RAG: {e}")
            return self.search_memories_keywords(query, limit)
    
    def search_memories_keywords(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Búsqueda tradicional por keywords"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        words = [word for word in query.lower().split() if len(word) > 2]
        
        if not words:
            cursor.execute('''
                SELECT * FROM memories 
                ORDER BY use_count DESC, importance DESC 
                LIMIT ?
            ''', (limit,))
        else:
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
    
    def get_context_summary(self, query: str) -> str:
        """Obtener resumen de contexto para el chat"""
        # Intentar RAG primero, luego keywords como fallback
        memories = self.search_memories_rag(query, limit=3)
        
        if not memories:
            return ""
        
        topics = set()
        for memory in memories:
            content = memory.get('content', '')
            sentences = re.split(r'[.!?]', content)
            for sentence in sentences[:2]:
                words = sentence.strip().split()[:5]
                if len(words) >= 3:
                    topic = ' '.join(words)
                    if len(topic) > 10:
                        topics.add(topic)
        
        topics_list = list(topics)[:3]
        if topics_list:
            return f"Context: I know about - {', '.join(topics_list)}"
        else:
            return ""
    
    def list_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Listar memorias recientes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT uuid, content, tags, memory_type, importance, use_count, created_at
            FROM memories 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM memories')
        total_memories = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM memory_relations')
        total_relations = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(importance) FROM memories')
        avg_importance = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(use_count) FROM memories')
        total_uses = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Verificar disponibilidad de dependencias
        try:
            from llama_index import VectorStoreIndex
            rag_enabled = self.vector_index is not None
        except ImportError:
            rag_enabled = False
            
        try:
            from langchain.agents import AgentExecutor
            langchain_enabled = True
        except ImportError:
            langchain_enabled = False
        
        return {
            'total_memories': total_memories,
            'total_relations': total_relations,
            'average_importance': round(avg_importance, 2),
            'total_uses': total_uses,
            'rag_enabled': rag_enabled,
            'langchain_enabled': langchain_enabled
        }
    
    def optimize_memories(self):
        """Optimizar base de memorias"""
        print("🔧 Optimizando memorias...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM memories 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM memories 
                    GROUP BY content
                )
            ''')
            duplicates_removed = cursor.rowcount
            
            cursor.execute('''
                UPDATE memories 
                SET importance = MIN(5, importance + 1)
                WHERE use_count > 5 AND importance < 5
            ''')
            promoted = cursor.rowcount
            
            conn.commit()
            
            if self.vector_index is not None:
                self._update_llama_index()
            
            return {
                'duplicates_removed': duplicates_removed,
                'memories_promoted': promoted
            }
            
        except Exception as e:
            print(f"❌ Error optimizando: {e}")
            conn.rollback()
            return {'error': str(e)}
        finally:
            conn.close()

def call_deepseek_api(api_key: str, message: str, context: str = "") -> str:
    """Llamar a la API de DeepSeek"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_msg = f"""You are Alma, a technical assistant specialized in hacking and programming.

{context}

Instructions:
- Respond in English only
- Be technical and concise
- Integrate context naturally without listing sources
- Focus on practical solutions
- If you don't know something, admit it"""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 800,
        "stream": False
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=data, 
            headers=headers, 
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ API Error: {e}"

def setup_langchain_agent(api_key: str, memory_manager: AlmaMemoryManager):
    """Configurar agente de LangChain"""
    try:
        from langchain.agents import AgentExecutor, create_react_agent
        from langchain.tools import Tool
        from langchain.memory import ConversationBufferMemory
        from langchain.prompts import PromptTemplate
    except ImportError:
        print("❌ LangChain no disponible")
        return None
    
    try:
        class DeepSeekLLM:
            def __init__(self, api_key):
                self.api_key = api_key
            
            def __call__(self, prompt):
                return call_deepseek_api(self.api_key, prompt)
        
        llm = DeepSeekLLM(api_key)
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        def search_tool(query: str) -> str:
            context = memory_manager.get_context_summary(query)
            return context if context else "No relevant context found."
        
        def add_memory_tool(content: str) -> str:
            success = memory_manager.add_memory(content)
            return "Memory saved" if success else "Error saving memory"
        
        tools = [
            Tool(
                name="SearchMemories",
                func=search_tool,
                description="Search relevant memories for context"
            ),
            Tool(
                name="SaveMemory",
                func=add_memory_tool,
                description="Save important information to memory"
            )
        ]
        
        prompt_template = """You are Alma, a technical assistant. Use tools when needed.

Tools:
{tools}

Conversation:
{history}

Human: {input}
Thought:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "history", "tools"]
        )
        
        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
        
    except Exception as e:
        print(f"❌ LangChain setup failed: {e}")
        return None

def chat_mode(memory_manager: AlmaMemoryManager, use_langchain: bool = True):
    """Modo chat interactivo"""
    api_key = memory_manager.api_key
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    langchain_available = False
    if use_langchain:
        try:
            from langchain.agents import AgentExecutor
            langchain_available = True
        except ImportError:
            langchain_available = False
    
    agent = None
    if use_langchain and langchain_available:
        agent = setup_langchain_agent(api_key, memory_manager)
        mode = "LangChain"
    else:
        mode = "Standard"
    
    print(f"🤖 Alma Unified v1.0.0 ({mode} + RAG)")
    print("💬 Chat mode - Type your message or /help")
    print()
    
    while True:
        try:
            user_input = input("🧑 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("👋 Goodbye!")
                break
            
            if user_input == '/help':
                print("\n📝 Commands:")
                print("  /add <text>     - Save memory")
                print("  /memories       - List memories") 
                print("  /metrics        - Show metrics")
                print("  /optimize       - Optimize memories")
                print("  /exit           - Exit")
                print()
                continue
            
            if user_input.startswith('/add '):
                content = user_input[5:].strip()
                if content:
                    memory_manager.add_memory(content)
                    print("✅ Memory saved")
                continue
            
            if user_input == '/memories':
                memories = memory_manager.list_memories(8)
                print("\n📚 Recent memories:")
                for i, mem in enumerate(memories, 1):
                    preview = mem['content'][:70].replace('\n', ' ')
                    print(f"  {i}. {preview}...")
                print()
                continue
            
            if user_input == '/metrics':
                metrics = memory_manager.get_metrics()
                print("\n📊 System metrics:")
                for key, value in metrics.items():
                    print(f"  {key}: {value}")
                print()
                continue
            
            if user_input == '/optimize':
                result = memory_manager.optimize_memories()
                print(f"✅ Optimization result: {result}")
                continue
            
            if not user_input:
                continue
            
            print("💭 Processing...")
            
            context = memory_manager.get_context_summary(user_input)
            if context:
                print(f"   📚 {context}")
            
            try:
                if agent:
                    response = agent.invoke({"input": user_input})
                    final_response = response['output']
                else:
                    final_response = call_deepseek_api(api_key, user_input, context)
                
                print(f"🤖 Alma: {final_response}\n")
                
                if "error" not in final_response.lower():
                    memory_manager.add_memory(
                        f"Q: {user_input}\nA: {final_response}",
                        memory_type="context"
                    )
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal con argparse"""
    parser = argparse.ArgumentParser(
        description='Alma Unified - Chat with RAG Memory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  alma                    # Interactive chat
  alma --add "Memory text" # Add memory
  alma --memories         # List memories  
  alma --metrics          # Show metrics
  alma --optimize         # Optimize database
        '''
    )
    
    parser.add_argument('--add', type=str, help='Add a new memory')
    parser.add_argument('--memories', action='store_true', help='List memories')
    parser.add_argument('--metrics', action='store_true', help='Show metrics')
    parser.add_argument('--optimize', action='store_true', help='Optimize memories')
    parser.add_argument('--no-langchain', action='store_true', help='Disable LangChain')
    parser.add_argument('--db-path', default='/alma/db/alma.db', help='Database path')
    
    args = parser.parse_args()
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ Please set DEEPSEEK_API_KEY environment variable")
        sys.exit(1)
    
    memory_manager = AlmaMemoryManager(db_path=args.db_path, api_key=api_key)
    
    if args.add:
        success = memory_manager.add_memory(args.add)
        print("✅ Memory saved" if success else "❌ Failed to save memory")
    elif args.memories:
        memories = memory_manager.list_memories(10)
        print("\n📚 Memories:")
        for i, mem in enumerate(memories, 1):
            print(f"{i}. {mem['content'][:100]}...")
    elif args.metrics:
        metrics = memory_manager.get_metrics()
        print("📊 Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
    elif args.optimize:
        result = memory_manager.optimize_memories()
        print(f"✅ Optimization completed: {result}")
    else:
        chat_mode(memory_manager, use_langchain=not args.no_langchain)

if __name__ == "__main__":
    main()