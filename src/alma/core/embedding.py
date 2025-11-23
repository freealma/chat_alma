#!/usr/bin/env python3
# src/alma/core/embedding.py
"""
Módulo para gestión de embeddings con Hugging Face LOCAL
"""
import json
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

from .config import AlmaConfig

class HuggingFaceEmbedder:
    """Manejador de embeddings con Hugging Face models LOCAL"""
    
    def __init__(self, config: AlmaConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"  # 🎯 MODELO LIVIANO
        self._load_model()
    
    def _load_model(self):
        """Cargar modelo local - OPTIMIZADO"""
        try:
            from transformers import AutoModel, AutoTokenizer
            import torch
            
            print(f"🔄 Cargando modelo LOCAL: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            # SOLO CPU
            self.model = self.model.to('cpu')
            self.model.eval()
            
            print("✅ Modelo cargado en CPU")
                
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            raise
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Crear embedding para texto"""
        try:
            import torch
            
            if not text or len(text.strip()) < 10:
                return None
            
            inputs = self.tokenizer(
                text, 
                padding=True, 
                truncation=True, 
                return_tensors="pt",
                max_length=256
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
            
            return embeddings[0].tolist()
            
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
            
            if not content or len(content) < 50:
                return None
            
            processed_content = self._preprocess_content(content)
            content_hash = self.calculate_content_hash(processed_content)
            embedding = self.create_embedding(processed_content)
            
            return {
                'chunk_id': file_path.stem,
                'file_path': str(file_path),
                'content': processed_content,
                'content_hash': content_hash,
                'embedding': embedding,
                'token_count': len(processed_content.split())
            }
            
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
            return None
    
    def _preprocess_content(self, content: str, max_length: int = 1000) -> str:
        """Preprocesar contenido para embeddings"""
        import re
        
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
                self.model_name if chunk_data['embedding'] else None
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
        
        print(f"📁 Procesando {len(chunk_files)} chunks con modelo LOCAL...")
        
        processed = 0
        for chunk_file in sorted(chunk_files):
            print(f"🔍 Procesando: {chunk_file.name}")
            
            chunk_data = self.process_chunk_file(chunk_file)
            if chunk_data and chunk_data['embedding'] and self.save_chunk_to_db(chunk_data):
                processed += 1
                print(f"  ✅ Embedding generado")
            else:
                print(f"  ❌ Falló embedding")
        
        print(f"🎉 Embeddings completados: {processed}/{len(chunk_files)}")

# Alias para compatibilidad
DeepSeekEmbedder = HuggingFaceEmbedder