-- Schema optimizado para RAG con chunks y embeddings
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT UNIQUE NOT NULL,           -- chunk_001_en.md
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,       -- Para evitar duplicados
    token_count INTEGER DEFAULT 0,
    language TEXT DEFAULT 'en',
    category TEXT,
    tags TEXT,                               -- JSON array
    metadata TEXT,                           -- JSON con metadatos adicionales
    embedding BLOB,                          -- Embedding vector serializado
    embedding_model TEXT,                    -- Modelo usado para el embedding
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunk_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_chunk_id TEXT NOT NULL,
    target_chunk_id TEXT NOT NULL,
    relation_type TEXT,                      -- similarity, reference, etc.
    similarity_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_chunk_id) REFERENCES chunks(chunk_id),
    FOREIGN KEY (target_chunk_id) REFERENCES chunks(chunk_id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_input TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    used_chunks TEXT,                        -- JSON array de chunk_ids usados
    context_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_chunks_content_hash ON chunks(content_hash);
CREATE INDEX IF NOT EXISTS idx_chunks_category ON chunks(category);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at);
CREATE INDEX IF NOT EXISTS idx_chunk_relations_source ON chunk_relations(source_chunk_id);
CREATE INDEX IF NOT EXISTS idx_chunk_relations_target ON chunk_relations(target_chunk_id);