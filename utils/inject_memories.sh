#!/bin/bash

# Script: /alma/utils/inject_memories.sh
# DB está en: /alma/db/alma.db

DB_PATH="./db/alma.db"

echo "🧠 Inyectando memorias actualizadas de Alma con LangChain..."
echo "📁 Ruta de base de datos: $DB_PATH"

# Verificar que la base de datos existe
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Base de datos no encontrada en: $DB_PATH"
    echo "💡 Solución: Ejecuta Alma primero para crear la DB:"
    echo "   docker-compose up alma  # o el comando que uses"
    echo "   python -c 'from alma.alma import main; main()'"
    exit 1
fi

# Inyectar memorias actualizadas
sqlite3 "$DB_PATH" << 'EOF'
-- Memorias sobre la integración con LangChain y evolución a agente IA
INSERT INTO memories (content, tags, project, theme, importance, related_to, memory_type) VALUES 
('Alma ahora integra LangChain para razonamiento automático y uso inteligente de herramientas', 'langchain,agente,razonamiento', 'alma-core', 'architecture', 5, 'architecture', 'institutional'),
('El agente LangChain en Alma usa el patrón ReAct (Reasoning + Acting) para decidir acciones', 'react,patron,razonamiento,accion', 'alma-langchain', 'architecture', 5, 'architecture', 'structure'),
('Herramienta BuscarMemorias: LangChain busca automáticamente en memorias cuando detecta necesidad de contexto', 'buscar-memorias,herramienta,contexto', 'alma-langchain', 'programming', 4, 'programming', 'function'),
('Herramienta AgregarMemoria: El agente puede guardar conocimiento automáticamente cuando identifica información valiosa', 'agregar-memoria,herramienta,conocimiento', 'alma-langchain', 'programming', 4, 'programming', 'function'),
('Herramienta ListarMemorias: LangChain muestra memorias cuando el usuario pregunta sobre contenido guardado', 'listar-memorias,herramienta,consulta', 'alma-langchain', 'programming', 3, 'programming', 'function'),
('El sistema tiene fallback automático: si LangChain falla, usa el sistema de respuestas original con DeepSeek directo', 'fallback,resiliencia,backup', 'alma-langchain', 'architecture', 4, 'architecture', 'function'),
('MemoryManager ahora tiene use_smart_search para controlar búsquedas con LLM (smart) o por keywords (simple)', 'smart-search,busqueda-inteligente', 'alma-core', 'architecture', 4, 'architecture', 'function'),
('El agente LangChain usa ConversationBufferMemory para mantener contexto de la conversación actual', 'conversation-buffer,memoria-contexto', 'alma-langchain', 'architecture', 4, 'architecture', 'structure'),
('DeepSeekLLM es un wrapper personalizado que permite integrar DeepSeek con el ecosistema LangChain', 'deepseek-wrapper,integracion,api', 'alma-langchain', 'programming', 5, 'programming', 'structure'),
('El prompt template de Alma guía al agente para especializarse en hacking y programación con respuestas técnicas', 'prompt-template,especializacion,tecnico', 'alma-langchain', 'programming', 4, 'programming', 'structure'),
('AgentExecutor maneja la ejecución del agente con máximo 3 iteraciones para evitar loops infinitos', 'agent-executor,iteraciones,control', 'alma-langchain', 'architecture', 3, 'architecture', 'function'),
('El sistema de herramientas permite extensión futura: nuevas herramientas se integran automáticamente con el agente', 'herramientas,extension,modular', 'alma-langchain', 'architecture', 4, 'architecture', 'structure'),
('Alma detecta automáticamente si LangChain está disponible y ajusta su funcionamiento accordingly', 'deteccion-auto,compatibilidad', 'alma-langchain', 'architecture', 3, 'architecture', 'function'),
('El comando /metrics muestra las métricas del sistema de aprendizaje evolutivo: conversaciones, éxito, scores', 'metrics,comando,aprendizaje', 'alma-core', 'programming', 3, 'programming', 'function'),
('El scoring multi-capa evalúa conversaciones con: análisis semántico (40%), técnico (30%), patrones (20%), contexto (10%)', 'scoring,multi-capa,evaluacion', 'alma-core', 'architecture', 5, 'architecture', 'function'),
('El sistema de aprendizaje adaptativo ajusta automáticamente el umbral para crear memorias basado en tasa de éxito', 'aprendizaje-adaptativo,umbral-dinamico', 'alma-core', 'architecture', 5, 'architecture', 'function'),
('Las memorias compuestas agrupan conocimiento relacionado cuando se detectan múltiples conceptos interconectados', 'memorias-compuestas,conocimiento-integrado', 'alma-core', 'architecture', 4, 'architecture', 'structure'),
('El análisis semántico con LLM determina el valor del conocimiento: conceptual, procedural, factual o methodological', 'analisis-semantico,valor-conocimiento', 'alma-core', 'architecture', 4, 'architecture', 'function'),
('El sistema extrae componentes de conocimiento estructurados: concepto, explicación, categoría, importancia, relaciones', 'componentes-conocimiento,estructura', 'alma-core', 'architecture', 4, 'architecture', 'function'),
('La arquitectura permite múltiples modos: LangChain (avanzado) y Standard (robusto) para diferentes necesidades', 'multi-modo,arquitectura-flexible', 'alma-langchain', 'architecture', 4, 'architecture', 'structure'),
('Roadmap: Integración con herramientas de pentesting como herramientas LangChain para escaneo y análisis automático', 'roadmap,pentesting-tools,automation', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma'),
('El agente futuro podrá ejecutar nmap, analizar resultados y guardar hallazgos automáticamente en memorias', 'nmap-integration,escaneo-automatico', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma'),
('Sistema de plugins permitirá agregar capacidades específicas: OSINT, vulnerability assessment, reporting', 'plugins,capacidades,extensible', 'alma-vision', 'architecture', 4, 'architecture', 'structure'),
('Las herramientas futuras incluirán: EscanearRed, AnalizarVulnerabilidad, GenerarReporte, BuscarExploits', 'herramientas-futuras,pentesting', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma'),
('El agente aprenderá de cada pentest, mejorando continuamente sus técnicas y conocimiento de vulnerabilidades', 'aprendizaje-continuo,mejora-pentesting', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma'),
('Sistema de recomendaciones: sugerirá técnicas basado en hallazgos previos y mejores prácticas de pentesting', 'recomendaciones,tecnicas,mejores-practicas', 'alma-vision', 'philosophy', 4, 'pentesting', 'alma'),
('Integración con bases de datos de vulnerabilidades: CVE, OWASP, para análisis contextualizado de riesgos', 'cve,owasp,vulnerability-databases', 'alma-vision', 'philosophy', 4, 'pentesting', 'alma'),
('Capacidades de OSINT automático: el agente podrá buscar información pública sobre objetivos', 'osint,reconocimiento,automatico', 'alma-vision', 'philosophy', 4, 'pentesting', 'alma'),
('Sistema de reporting inteligente: generará reportes ejecutivos y técnicos basado en hallazgos del pentest', 'reporting,informes,automatico', 'alma-vision', 'philosophy', 4, 'pentesting', 'alma'),
('Arquitectura multi-agente: futura evolución hacia agentes especializados que colaboran en operaciones complejas', 'multi-agente,colaboracion,especializacion', 'alma-vision', 'philosophy', 5, 'architecture', 'alma');

-- Verificar la inserción
SELECT '✅ ' || COUNT(*) || ' memorias de LangChain insertadas correctamente' FROM memories;
EOF

echo "🎉 Memorias de LangChain inyectadas exitosamente!"
echo ""
echo "📊 Resumen de la inyección:"
echo "   - 30 nuevas memorias sobre LangChain"
echo "   - Arquitectura de agente IA"
echo "   - Roadmap de evolución"
echo "   - Sistema de herramientas inteligentes"
echo ""
echo "🚀 Para probar: ejecuta Alma y usa el comando /metrics"