#!/usr/bin/env python3
"""
Embedding Generator para Alma RAG usando DeepSeek
Genera embeddings para chunks markdown usando DeepSeek API
"""
import os
import sys
import sqlite3
import json
import argparse
import hashlib
import requests
from pathlib import Path
from typing import List, Dict, Optional

class DeepSeekEmbedder:
    """Generador de embeddings usando DeepSeek API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Verificar si la API está disponible"""
        if not self.api_key:
            print("❌ DEEPSEEK_API_KEY no configurada")
            return False
        return True
    
    def is_available(self) -> bool:
        return self.available
    
    def create_embedding(self, text: str, model: str = "deepseek-embedding") -> Optional[List[float]]:
        """Crear embedding usando DeepSeek API"""
        if not self.is_available():
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "input": text,
            "model": model
        }
        
        try:
            print(f"   📡 Enviando a DeepSeek... ({len(text)} caracteres)")
            response = requests.post(
                f"{self.base_url}/embeddings",
                json=data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            embedding = result['data'][0]['embedding']
            print(f"   ✅ Embedding generado ({len(embedding)} dimensiones)")
            return embedding
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión con DeepSeek: {e}")
            return None
        except Exception as e:
            print(f"❌ Error creando embedding: {e}")
            return None

class EmbeddingGenerator:
    """Generador de embeddings con DeepSeek"""
    
    def __init__(self, db_path: str, chunks_dir: str, deepseek_key: str = None):
        self.db_path = db_path
        self.chunks_dir = Path(chunks_dir)
        self.embedder = DeepSeekEmbedder(deepseek_key)
        self._init_database()
    
    def _init_database(self):
        """Inicializar base de datos con schema RAG"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        schema = """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id TEXT UNIQUE NOT NULL,
            file_path TEXT NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT UNIQUE NOT NULL,
            token_count INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en',
            category TEXT,
            tags TEXT,
            metadata TEXT,
            embedding BLOB,
            embedding_model TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chunk_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_chunk_id TEXT NOT NULL,
            target_chunk_id TEXT NOT NULL,
            relation_type TEXT,
            similarity_score REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_chunk_id) REFERENCES chunks(chunk_id),
            FOREIGN KEY (target_chunk_id) REFERENCES chunks(chunk_id)
        );

        CREATE INDEX IF NOT EXISTS idx_chunks_content_hash ON chunks(content_hash);
        CREATE INDEX IF NOT EXISTS idx_chunks_category ON chunks(category);
        CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks(embedding_model);
        """
        
        cursor.executescript(schema)
        conn.close()
        print("✅ Base de datos RAG inicializada")
    
    def calculate_hash(self, content: str) -> str:
        """Calcular hash del contenido para evitar duplicados"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def count_tokens_approximate(self, text: str) -> int:
        """Contar tokens de forma aproximada"""
        # Aproximación para texto en inglés: 1 token ≈ 4 caracteres
        return max(1, len(text) // 4)
    
    def preprocess_markdown(self, content: str, max_length: int = 4000) -> str:
        """Preprocesar contenido markdown para embeddings"""
        import re
        
        # Limpiar markdown pero mantener contenido semántico
        cleaned = content
        
        # Remover bloques de código muy largos pero mantener descripciones
        cleaned = re.sub(r'```.*?```', '[code block]', cleaned, flags=re.DOTALL)
        
        # Remover URLs y enlaces
        cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[url]', cleaned)
        
        # Simplificar formato pero mantener estructura
        cleaned = re.sub(r'#+\s*', '', cleaned)  # Headers
        cleaned = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', cleaned)  # Bold/italic
        cleaned = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', cleaned)  # Underline
        
        # Limpiar espacios
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r' {2,}', ' ', cleaned)
        cleaned = cleaned.strip()
        
        # Limitar longitud para evitar costos excesivos
        if len(cleaned) > max_length:
            # Truncar pero manteniendo oraciones completas
            sentences = re.split(r'[.!?]+', cleaned)
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence) <= max_length:
                    truncated += sentence + "."
                else:
                    break
            cleaned = truncated.strip()
            if len(cleaned) > max_length:
                cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def extract_metadata(self, content: str, filename: str) -> Dict:
        """Extraer metadatos del contenido"""
        metadata = {
            "filename": filename,
            "language": "en",
            "has_code": "```" in content,
            "has_headers": "# " in content,
            "has_lists": "- " in content or "* " in content or "1." in content,
            "word_count": len(content.split()),
            "char_count": len(content)
        }
        
        # Detectar categoría basada en contenido
        content_lower = content.lower()
        security_keywords = ['hack', 'pentest', 'security', 'vulnerability', 'exploit', 'malware', 'firewall']
        programming_keywords = ['code', 'programming', 'function', 'class', 'variable', 'algorithm', 'database']
        architecture_keywords = ['system', 'architecture', 'design', 'microservices', 'api', 'backend', 'frontend']
        
        if any(word in content_lower for word in security_keywords):
            metadata["category"] = "security"
        elif any(word in content_lower for word in programming_keywords):
            metadata["category"] = "programming"  
        elif any(word in content_lower for word in architecture_keywords):
            metadata["category"] = "architecture"
        else:
            metadata["category"] = "general"
        
        return metadata
    
    def process_chunk_file(self, file_path: Path) -> Optional[Dict]:
        """Procesar un archivo chunk individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content or len(content) < 100:
                print(f"⚠️  Archivo muy corto o vacío: {file_path}")
                return None
            
            print(f"   📖 Leyendo {file_path.name}...")
            
            # Preprocesar contenido
            processed_content = self.preprocess_markdown(content)
            content_hash = self.calculate_hash(processed_content)
            token_count = self.count_tokens_approximate(processed_content)
            
            # Extraer metadatos
            metadata = self.extract_metadata(content, file_path.name)
            
            # Crear embedding con DeepSeek
            embedding = None
            if self.embedder.is_available():
                embedding = self.embedder.create_embedding(processed_content)
            else:
                print("   ⚠️  DeepSeek no disponible, omitiendo embedding")
            
            chunk_data = {
                'chunk_id': file_path.stem,
                'file_path': str(file_path),
                'content': processed_content,
                'content_hash': content_hash,
                'token_count': token_count,
                'language': metadata.get('language', 'en'),
                'category': metadata.get('category', 'general'),
                'tags': json.dumps([metadata['category']]),
                'metadata': json.dumps(metadata),
                'embedding': json.dumps(embedding) if embedding else None,
                'embedding_model': 'deepseek-embedding' if embedding else 'none'
            }
            
            return chunk_data
            
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
            return None
    
    def save_chunk_to_db(self, chunk_data: Dict) -> bool:
        """Guardar chunk en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar si ya existe por hash
            cursor.execute(
                "SELECT chunk_id FROM chunks WHERE content_hash = ?",
                (chunk_data['content_hash'],)
            )
            existing = cursor.fetchone()
            
            if existing:
                print(f"   ⚠️  Chunk duplicado: {chunk_data['chunk_id']} (ya existe como {existing[0]})")
                
                # Actualizar si no tenía embedding pero ahora sí
                if not chunk_data['embedding']:
                    return False
                
                # Verificar si el existente tiene embedding
                cursor.execute(
                    "SELECT embedding FROM chunks WHERE chunk_id = ?",
                    (existing[0],)
                )
                existing_embedding = cursor.fetchone()[0]
                
                if not existing_embedding and chunk_data['embedding']:
                    # Actualizar con nuevo embedding
                    cursor.execute('''
                        UPDATE chunks SET embedding = ?, embedding_model = ? 
                        WHERE chunk_id = ?
                    ''', (
                        chunk_data['embedding'],
                        chunk_data['embedding_model'],
                        existing[0]
                    ))
                    conn.commit()
                    print(f"   ✅ Embedding actualizado para: {existing[0]}")
                    return True
                
                return False
            
            # Insertar nuevo chunk
            cursor.execute('''
                INSERT INTO chunks (
                    chunk_id, file_path, content, content_hash, token_count,
                    language, category, tags, metadata, embedding, embedding_model
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk_data['chunk_id'],
                chunk_data['file_path'],
                chunk_data['content'],
                chunk_data['content_hash'],
                chunk_data['token_count'],
                chunk_data['language'],
                chunk_data['category'],
                chunk_data['tags'],
                chunk_data['metadata'],
                chunk_data['embedding'],
                chunk_data['embedding_model']
            ))
            
            conn.commit()
            has_embedding = "✅" if chunk_data['embedding'] else "⚠️ "
            print(f"   {has_embedding} Chunk guardado: {chunk_data['chunk_id']} ({chunk_data['token_count']} tokens)")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando chunk {chunk_data['chunk_id']}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_existing_chunks(self) -> set:
        """Obtener set de chunks ya existentes en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT chunk_id FROM chunks")
        existing = set(row[0] for row in cursor.fetchall())
        conn.close()
        return existing
    
    def generate_embeddings(self, force_update: bool = False):
        """Generar embeddings para todos los chunks"""
        if not self.chunks_dir.exists():
            print(f"❌ Directorio no encontrado: {self.chunks_dir}")
            return
        
        chunk_files = list(self.chunks_dir.glob("chunk_*.md"))
        if not chunk_files:
            print("❌ No se encontraron archivos chunk_*.md")
            return
        
        print(f"📁 Encontrados {len(chunk_files)} chunks en {self.chunks_dir}")
        
        if not self.embedder.is_available():
            print("❌ DeepSeek no disponible. No se generarán embeddings.")
            print("   Configura DEEPSEEK_API_KEY o usa --deepseek-key")
            return
        
        existing_chunks = self.get_existing_chunks()
        processed = skipped = errors = 0
        
        for chunk_file in sorted(chunk_files):
            chunk_id = chunk_file.stem
            
            if not force_update and chunk_id in existing_chunks:
                print(f"⏭️  Saltando (ya existe): {chunk_file.name}")
                skipped += 1
                continue
            
            print(f"🔍 Procesando: {chunk_file.name}")
            chunk_data = self.process_chunk_file(chunk_file)
            
            if chunk_data:
                if self.save_chunk_to_db(chunk_data):
                    processed += 1
                else:
                    skipped += 1
            else:
                errors += 1
            
            # Pequeña pausa para no saturar la API
            import time
            time.sleep(0.5)
        
        print(f"\n🎉 Proceso completado:")
        print(f"  ✅ Nuevos/procesados: {processed}")
        print(f"  ⏭️  Saltados: {skipped}") 
        print(f"  ❌ Errores: {errors}")
        print(f"  📊 Total en base de datos: {len(existing_chunks) + processed}")

def main():
    parser = argparse.ArgumentParser(description='Generar embeddings para chunks markdown usando DeepSeek')
    parser.add_argument('--db-path', default='/alma/db/alma.db', help='Ruta a la base de datos')
    parser.add_argument('--chunks-dir', default='/alma/data/chunks', help='Directorio con chunks markdown')
    parser.add_argument('--deepseek-key', help='DeepSeek API Key (o usar DEEPSEEK_API_KEY env)')
    parser.add_argument('--force', action='store_true', help='Forzar reprocesamiento de todos los chunks')
    
    args = parser.parse_args()
    
    # Verificar que el directorio existe
    if not os.path.exists(args.chunks_dir):
        print(f"❌ Directorio de chunks no existe: {args.chunks_dir}")
        sys.exit(1)
    
    generator = EmbeddingGenerator(
        db_path=args.db_path,
        chunks_dir=args.chunks_dir,
        deepseek_key=args.deepseek_key
    )
    
    generator.generate_embeddings(force_update=args.force)

if __name__ == "__main__":
    main()