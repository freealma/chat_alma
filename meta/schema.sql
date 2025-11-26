-- Schema mejorado para memoria y logs
CREATE SCHEMA alma;

CREATE TABLE alma.memories (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    importance INTEGER DEFAULT 1,
    usage_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding_vector VECTOR(1536), -- Para búsqueda semántica
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE alma.agent_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_type VARCHAR(50) NOT NULL,
    action_details JSONB NOT NULL,
    input_context TEXT,
    output_result TEXT,
    success BOOLEAN DEFAULT true,
    learning_insights TEXT,
    memory_refs INTEGER[] -- Referencias a memorias usadas
);

CREATE TABLE alma.conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    context_summary TEXT,
    memory_used INTEGER[],
    new_memories_created INTEGER[]
);

-- Índices para búsqueda eficiente
CREATE INDEX idx_memories_type ON alma.memories(memory_type);
CREATE INDEX idx_memories_importance ON alma.memories(importance);
CREATE INDEX idx_memories_usage ON alma.memories(usage_count);
CREATE INDEX idx_logs_timestamp ON alma.agent_logs(timestamp);
CREATE INDEX idx_conversations_session ON alma.conversations(session_id);