#!/bin/bash

# Ruta relativa desde el proyecto root
DB_PATH="./db/alma.db"

echo "🧠 Inyectando memorias iniciales en Alma..."

# Verificar que la base de datos existe
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Base de datos no encontrada en: $DB_PATH"
    echo "   Ejecuta Alma al menos una vez para crear la DB"
    exit 1
fi

# Verificar que sqlite3 está instalado
if ! command -v sqlite3 &> /dev/null; then
    echo "❌ sqlite3 no encontrado. Instala con: sudo apt install sqlite3"
    exit 1
fi

# Inyectar memorias (sin especificar ID para que use AUTOINCREMENT)
sqlite3 "$DB_PATH" << 'EOF'
-- Memorias sobre la estructura y funcionamiento de Alma
INSERT INTO memories (content, tags, project, theme, importance, related_to, memory_type) VALUES 
('Alma es un CLI chat especializado en pentesting y programación que combina DeepSeek AI con memoria persistente', 'alma,cli,chat,pentesting', 'alma-core', 'architecture', 5, 'architecture', 'institutional'),
('El sistema de Alma usa SQLite con UUIDs para gestionar memorias con importancia del 1 al 5 y contadores de uso', 'sqlite,uuid,database,memories', 'alma-core', 'architecture', 4, 'architecture', 'structure'),
('Comando /add: Guarda nuevas memorias en la base de datos para consultas futuras', 'add,command,memoria', 'alma-core', 'programming', 4, 'programming', 'function'),
('Comando /memories: Lista las 10 memorias más recientes con sus contadores de uso', 'memories,command,listar', 'alma-core', 'programming', 3, 'programming', 'function'),
('Comando /exit: Cierra la sesión del chat Alma', 'exit,command,salir', 'alma-core', 'programming', 2, 'programming', 'function'),
('Alma busca automáticamente memorias relevantes antes de cada respuesta usando keywords del input del usuario', 'busqueda,keywords,relevancia', 'alma-core', 'architecture', 4, 'architecture', 'function'),
('La importancia de las memorias va de 1 a 5 estrellas y afecta su prioridad en búsquedas', 'importancia,estrellas,prioridad', 'alma-core', 'architecture', 3, 'architecture', 'structure'),
('Las memorias se categorizan en: institutional, context, alma, bird, architecture, structure, function', 'categorias,tipos,memoria', 'alma-core', 'architecture', 3, 'architecture', 'structure'),
('El contador use_count incrementa cada vez que una memoria es usada en una respuesta', 'use_count,contador,uso', 'alma-core', 'architecture', 3, 'architecture', 'structure'),
('Alma está diseñado para evolucionar hacia un agente pentester de compañía con múltiples funciones especializadas', 'agente,pentester,evolucion', 'alma-vision', 'philosophy', 5, 'philosophy', 'alma'),
('El sistema de relaciones entre memorias permite conectar conceptos relacionados para mejores respuestas', 'relaciones,conexiones,conceptos', 'alma-core', 'architecture', 4, 'architecture', 'structure'),
('Docker permite ejecutar Alma de forma consistente en cualquier entorno', 'docker,container,deployment', 'alma-core', 'architecture', 3, 'architecture', 'structure'),
('El archivo .env contiene DEEPSEEK_API_KEY para la conexión con la API de DeepSeek', 'env,api_key,configuracion', 'alma-core', 'architecture', 4, 'architecture', 'structure'),
('Las búsquedas usan LIKE con wildcards para encontrar coincidencias parciales en contenido y tags', 'busqueda,like,wildcards', 'alma-core', 'programming', 3, 'programming', 'function'),
('El algoritmo de búsqueda prioriza importancia, luego use_count y finalmente last_used', 'algoritmo,busqueda,prioridad', 'alma-core', 'architecture', 4, 'architecture', 'function'),
('Las memorias institutional contienen conocimiento fundamental sobre Alma y su operación', 'institutional,fundamental,conocimiento', 'alma-core', 'architecture', 3, 'architecture', 'structure'),
('El tipo context se usa para memorias de conversación específicas del usuario', 'context,usuario,conversacion', 'alma-core', 'architecture', 3, 'architecture', 'structure'),
('La visión a futuro incluye integración con herramientas de pentesting como nmap, metasploit y burp suite', 'pentesting,herramientas,integracion', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma'),
('El sistema LRU automáticamente elimina memorias poco usadas cuando se excede el límite de 500', 'lru,limite,optimizacion', 'alma-core', 'architecture', 3, 'architecture', 'function'),
('Alma.py es el script principal que maneja la interfaz CLI y el loop de conversación', 'alma.py,main,cli', 'alma-core', 'programming', 4, 'programming', 'structure'),
('Memory.py contiene la clase MemoryManager para todas las operaciones de base de datos', 'memory.py,MemoryManager,database', 'alma-core', 'programming', 4, 'programming', 'structure'),
('El schema.sql define la estructura de la base de datos con constraints de validación', 'schema.sql,database,estructura', 'alma-core', 'architecture', 3, 'architecture', 'structure'),
('Las memorias con related_to=pentesting serán el foco para el agente especializado', 'pentesting,agente,especializacion', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma'),
('El sistema de tags permite búsquedas más precisas por categorías técnicas', 'tags,categorias,busqueda', 'alma-core', 'architecture', 3, 'architecture', 'function'),
('La respuesta de Alma combina el contexto de memorias con la inteligencia de DeepSeek', 'respuesta,contexto,deepseek', 'alma-core', 'architecture', 4, 'architecture', 'function'),
('El proyecto busca crear un compañero de pentesting que recuerde técnicas y hallazgos previos', 'companero,pentesting,memoria', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma'),
('Las relaciones entre memorias permiten navegación contextual entre conceptos relacionados', 'navegacion,contextual,relaciones', 'alma-core', 'architecture', 3, 'architecture', 'function'),
('El comando /optimize limpiará duplicados y mejorará la estructura de la base de datos', 'optimize,comando,limpieza', 'alma-core', 'programming', 3, 'programming', 'function'),
('La arquitectura modular permite agregar nuevos comandos y funciones fácilmente', 'modular,arquitectura,extension', 'alma-core', 'architecture', 4, 'architecture', 'structure'),
('El roadmap incluye comandos para escaneo de redes, análisis de vulnerabilidades y reportes automáticos', 'roadmap,comandos,pentesting', 'alma-vision', 'philosophy', 5, 'pentesting', 'alma');

-- Verificar la inserción
SELECT '✅ ' || COUNT(*) || ' memorias insertadas correctamente' FROM memories;
EOF

echo "🎉 Memorias inyectadas exitosamente!"