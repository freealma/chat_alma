-- schema.sql
-- version: 0.0.1
-- description: "Esquema de base de datos para la gestión de memorias en Alma CLI"

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

CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories(tags);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_use_count ON memories(use_count);
CREATE INDEX IF NOT EXISTS idx_memories_related_to ON memories(related_to);
CREATE INDEX IF NOT EXISTS idx_memories_memory_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_last_used ON memories(last_used);
CREATE INDEX IF NOT EXISTS idx_memories_uuid ON memories(uuid);

CREATE INDEX IF NOT EXISTS idx_relations_source ON memory_relations(source_uuid);
CREATE INDEX IF NOT EXISTS idx_relations_target ON memory_relations(target_uuid);
CREATE INDEX IF NOT EXISTS idx_relations_type ON memory_relations(relation_type);