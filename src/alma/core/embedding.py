#!/usr/bin/env python3
"""
Módulo para gestión de embeddings con DeepSeek
"""
import json
import hashlib
import requests
from typing import List, Dict, Optional
from pathlib import Path

from .config import AlmaConfig

class DeepSeekEmbedder:
    """Manejador de embeddings con DeepSeek API"""
    
    def __init__(self, config: AlmaConfig):
        self.config = config
        self.base_url = "https://api.deepseek.com/v1"
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Crear embedding para texto"""
        headers = {
            "Authorization": f"Bearer {self.config.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "input": text,
            "model": self.config.embedding_model
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                json=data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result['data'][0]['embedding']
        except Exception as e:
            print(f"❌ Error creando embedding: {e}")
            return None
    
    def calculate_content_hash(self, content: str) -> str:
        """Calcular hash único del contenido"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def process_chunk_file(self, file_path: Path) -> Optional[Dict]:
        """Procesar archivo chunk y generar embedding"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content or len(content) < 100:
                return None
            
            # Preprocesar contenido
            processed_content = self._preprocess_content(content)
            content_hash = self.calculate_content_hash(processed_content)
            
            # Generar embedding
            embedding = self.create_embedding(processed_content)
            
            return {
                'chunk_id': file_path.stem,
                'file_path': str(file_path),
                'content': processed_content,
                'content_hash': content_hash,
                'embedding': embedding,
                'token_count': len(processed_content) // 4  # Aproximación
            }
            
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
            return None
    
    def _preprocess_content(self, content: str, max_length: int = 4000) -> str:
        """Preprocesar contenido para embeddings"""
        import re
        
        # Limpieza básica de markdown
        cleaned = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        cleaned = re.sub(r'#+\s*', '', cleaned)
        cleaned = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', cleaned)
        cleaned = re.sub(r'\n{2,}', '\n', cleaned)
        cleaned = cleaned.strip()
        
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def save_chunk_to_db(self, chunk_data: Dict) -> bool:
        """Guardar chunk en base de datos"""
        conn = self.config.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO chunks (
                    chunk_id, file_path, content, content_hash, token_count, 
                    embedding, embedding_model
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk_data['chunk_id'],
                chunk_data['file_path'],
                chunk_data['content'],
                chunk_data['content_hash'],
                chunk_data['token_count'],
                json.dumps(chunk_data['embedding']) if chunk_data['embedding'] else None,
                self.config.embedding_model if chunk_data['embedding'] else None
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando chunk: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def generate_all_embeddings(self):
        """Generar embeddings para todos los chunks"""
        if not self.config.chunks_dir.exists():
            print(f"❌ Directorio no encontrado: {self.config.chunks_dir}")
            return
        
        chunk_files = list(self.config.chunks_dir.glob("chunk_*.md"))
        if not chunk_files:
            print("❌ No se encontraron archivos chunk_*.md")
            return
        
        print(f"📁 Procesando {len(chunk_files)} chunks...")
        
        processed = 0
        for chunk_file in sorted(chunk_files):
            print(f"🔍 Procesando: {chunk_file.name}")
            
            chunk_data = self.process_chunk_file(chunk_file)
            if chunk_data and self.save_chunk_to_db(chunk_data):
                processed += 1
        
        print(f"✅ Embeddings generados: {processed}/{len(chunk_files)}")