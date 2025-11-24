# Alma Agent - Documentación Técnica v0.1.3

## 🎯 Visión General

Alma Agent v0.1.3 es un **agente pentester inteligente con auto-ajuste de conocimiento** que combina:
- **🧠 Memoria contextual** con PostgreSQL y reasoning automático
- **🤖 Capacidades LLM** con DeepSeek API y rate limiting
- **🔍 Análisis de código** inteligente con enfoque en crecimiento
- **🚀 Sistema de crecimiento** automático basado en experiencia
- **💾 Auto-diagnóstico** y planificación de roadmap

## 🏗️ Arquitectura Mejorada

### Estructura de Proyecto v0.1.3
```
alma/
├── src/alma/
│   ├── core/
│   │   ├── database.py          # Gestión de conexión PostgreSQL
│   │   ├── llm_client.py        # Cliente DeepSeek API con seguridad
│   │   └── memory.py            # Sistema de memoria contextual
│   ├── commands/
│   │   ├── memory_ops.py        # 🧠 Memoria + plan-roadmap
│   │   ├── code_review.py       # 🔍 Análisis de código seguro
│   │   ├── agent_growth.py      # 🚀 Crecimiento y autonomía (NUEVO)
│   │   └── __init__.py
│   ├── alma_agent.py            # CLI principal con Typer
│   └── __main__.py              # Punto de entrada
```

### Flujo de Datos Inteligente
```
Usuario → Typer CLI → Alma Agent → PostgreSQL + DeepSeek API
                ↓                       ↓
        Resultados formateados   🧠 Auto-análisis
                ↓                       ↓
        🚀 Sugerencias crecimiento  📈 Planificación roadmap
```

## 🔧 Comandos Implementados v0.1.3

### Comandos del Sistema

#### `alma init`
**Propósito**: Inicializa la base de datos y configura el cliente LLM
```bash
docker compose exec alma-agent alma init
```
**Salida esperada**:
```
🔧 Parámetros DB: psql:5432/hood
📊 Conectado a: hood como alma
📁 Usando schema: alma
✅ Tablas creadas en schema: alma
✅ Tablas verificadas: ['alma_memories', 'pentest_sessions']
🔍 Inicializando DeepSeek LLM...
✅ Cliente DeepSeek inicializado correctamente
🤖 Modelo: deepseek-chat
✅ Base de datos inicializada correctamente
✅ Cliente DeepSeek LLM configurado y conectado
```

#### `alma status`
**Propósito**: Muestra el estado actual del sistema
```bash
docker compose exec alma-agent alma status
```
**Nueva salida**:
```
╭───────────────────────────────────────────────────────── Alma Agent Status ─────────────────────────────────────────────────────────╮
│ 🧠 Memorias almacenadas: 12                                                                                                         │
│ 🔍 Sesiones activas: 2                                                                                                              │
│ 🤖 Estado LLM: ✅ Conectado (15 llamadas)                                                                                           │
│ 🚀 Análisis crecimiento: 3 planes generados                                                                                        │
│ 📊 Base de datos: Conectada                                                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### `alma test-llm`
**Propósito**: Prueba la conexión con DeepSeek API con rate limiting
```bash
docker compose exec alma-agent alma test-llm "Tu pregunta aquí"
```

#### `alma debug-env`
**Propósito**: Diagnóstico seguro de variables de entorno
```bash
docker compose exec alma-agent alma debug-env
```

### 🧠 Comandos de Memoria Mejorados

#### `alma memory create`
**Propósito**: Crea una nueva memoria con contexto enriquecido
```bash
docker compose exec alma-agent alma memory create "El servidor expone API sin autenticación" --memory-type vulnerability --importance 4 --context "Endpoint: /api/users"
```

#### `alma memory list`
**Propósito**: Lista memorias con filtros inteligentes
```bash
docker compose exec alma-agent alma memory list --limit 15 --memory-type vulnerability
```

#### `alma memory search`
**Propósito**: Búsqueda semántica en memorias
```bash
docker compose exec alma-agent alma memory search "autenticación"
```

#### `alma memory plan-roadmap` 🆕
**Propósito**: Genera roadmap de crecimiento basado en experiencias pasadas
```bash
docker compose exec alma-agent alma memory plan-roadmap
```
**Salida esperada**:
```
🧠 Planificando con memorias importantes...
╭───────────────────────────────────────────────────────── 📈 Roadmap Basado en Experiencia ─────────────────────────────────────────────────────────╮
│ Basado en 8 memorias importantes, sugiero:                                                                            │
│ 1. SISTEMA DE DETECCIÓN AUTOMÁTICA de APIs no autenticadas                                                            │
│ 2. SCANNER DE CONFIGURACIONES inseguras en servicios web                                                              │
│ 3. INTEGRACIÓN con herramientas de escaneo existentes                                                                 │
│ 4. APRENDIZAJE de patrones de vulnerabilidades recurrentes                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✅ Plan guardado en memorias
```

### 🔍 Comandos de Análisis de Código Seguro

#### `alma code analyze`
**Propósito**: Analiza código con enfoque en seguridad y mejores prácticas
```bash
docker compose exec alma-agent alma code analyze "import subprocess; subprocess.call(user_input)" --language python
```

#### `alma code review-file`
**Propósito**: Analiza archivos completos con validación de seguridad
```bash
docker compose exec alma-agent alma code review-file /app/src/alma/alma_agent.py
```

#### `alma code review-dir` 🆕
**Propósito**: Analiza directorios completos de forma segura
```bash
docker compose exec alma-agent alma code review-dir /app/src --file-pattern "*.py"
```

### 🚀 Comandos de Crecimiento y Autonomía 🆕

#### `alma growth suggest-features`
**Propósito**: Sugiere features para aumentar autonomía del agente
```bash
docker compose exec alma-agent alma growth suggest-features --component memory
docker compose exec alma-agent alma growth suggest-features --component reasoning
docker compose exec alma-agent alma growth suggest-features --component all
```

#### `alma growth analyze-usage`
**Propósito**: Analiza patrones de uso real para sugerir mejoras
```bash
docker compose exec alma-agent alma growth analyze-usage
```
**Salida esperada**:
```
📊 Analizando patrones de uso real...
╭───────────────────────────────────────────────────────── 📈 Mejoras Basadas en Uso Real ─────────────────────────────────────────────────────────╮
│ ESTADÍSTICAS DE USO:                                                                                                  │
│ - vulnerability: 8 memorias (importancia avg: 4.2)                                                                    │
│ - observation: 4 memorias (importancia avg: 2.5)                                                                      │
│                                                                                                                       │
│ PATRONES DETECTADOS:                                                                                                  │
│ 1. 70% de uso en detección de vulnerabilidades → Priorizar escáner automático                                         │
│ 2. Alta importancia en memorias de seguridad → Desarrollar sistema de alertas                                         │
│ 3. Foco en APIs web → Integrar OWASP Top 10 detection                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### `alma growth tech-debt`
**Propósito**: Identifica technical debt que bloquea el crecimiento
```bash
docker compose exec alma-agent alma growth tech-debt
```

## 🔧 Mejoras de Seguridad Implementadas

### Rate Limiting Inteligente
```python
# En llm_client.py - Previene abuso de API
def _make_api_call(self, prompt: str, max_tokens: int = 3000):
    time.sleep(1)  # 1 segundo entre llamadas
    # Lógica de llamada segura...
```

### Validación de Rutas Seguras
```python
# En code_review.py - Previene path traversal
def is_safe_path(path: str) -> bool:
    abs_path = os.path.abspath(path)
    return abs_path.startswith('/app')  # Solo dentro de /app
```

### Sanitización de Inputs
```python
# En llm_client.py - Previene inyecciones
def _sanitize_input(self, text: str, max_length: int = 10000) -> str:
    text = text[:max_length]  # Limitar longitud
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Remover control chars
    return text.strip()
```

## 🔌 Configuración v0.1.3

### Variables de Entorno Mejoradas
Archivo `alma.env`:
```env
# Configuración esencial
DEEPSEEK_API_KEY=sk-tu_api_key_aqui
DB_HOST=psql
DB_PORT=5432
DB_NAME=hood
DB_USER=alma
DB_PASSWORD=umamia

# Límites de seguridad (opcionales)
MAX_FILE_SIZE=50000
RATE_LIMIT_DELAY=1
```

### Esquema de Base de Datos Extendido

#### Tabla `alma_memories` (mejorada)
```sql
CREATE TABLE alma_memories (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    context TEXT,
    importance INTEGER DEFAULT 1,
    -- Campos para auto-aprendizaje
    usage_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    related_memories INTEGER[] -- Para conectar memorias relacionadas
);
```

## 🛠️ Desarrollo v0.1.3

### Agregar Nuevos Comandos de Crecimiento

1. **Crear archivo en `src/alma/commands/`**:
```python
import typer
from rich.console import Console
from alma.core.llm_client import llm_client
from alma.core.database import db_manager

console = Console()
growth_app = typer.Typer(help="Crecimiento del agente")

@growth_app.command("mi-feature")
def mi_feature():
    """Descripción de la feature de crecimiento"""
    # Usar llm_client para reasoning
    # Usar db_manager para acceder a memorias
    # Implementar lógica de auto-mejora
```

2. **Registrar en `alma_agent.py`**:
```python
try:
    from alma.commands.agent_growth import growth_app
    app.add_typer(growth_app, name="growth", help="Crecimiento y autonomía del agente")
except ImportError as e:
    console.print(f"[yellow]⚠️  No se pudieron cargar comandos de crecimiento: {e}[/yellow]")
```

### Estructura del Cliente LLM Mejorado

```python
llm_client = AlmaLLMClient()           # Instancia única con rate limiting
llm_client.ensure_initialized()        # Inicialización bajo demanda
llm_client.analyze_code(code, lang)    # Análisis seguro
llm_client.query(prompt, context)      # Consulta con sanitización
```

## 🚨 Solución de Problemas v0.1.3

### Error: "Rate limit exceeded"
**Causa**: Llamadas muy frecuentes a DeepSeek API
**Solución**:
```bash
# El sistema implementa rate limiting automático
# Espera 1-2 segundos entre comandos que usen LLM
```

### Error: "Ruta no permitida"
**Causa**: Intento de acceder a archivos fuera de `/app`
**Solución**:
```bash
# Mover archivos a /app/src o /app/tests
docker compose exec alma-agent alma code review-file /app/src/tu_archivo.py
```

### Error: "Archivo muy grande"
**Causa**: Archivo mayor a 50KB
**Solución**:
```bash
# Dividir archivos grandes o usar análisis por partes
docker compose exec alma-agent alma code review-dir /app/src --file-pattern "*.py"
```

## 📈 Métricas de Performance v0.1.3

- **Tiempo de respuesta LLM**: < 3 segundos (con rate limiting)
- **Análisis de código**: 2-5 segundos por archivo
- **Planificación roadmap**: 5-10 segundos
- **Memoria utilizada**: ~120MB por contenedor
- **Almacenamiento**: ~2MB por 1000 memorias con metadata

## 🔮 Roadmap v0.1.3 → v0.2.0

### ✅ Completado en v0.1.3
- [x] **Sistema de crecimiento automático** con `agent_growth`
- [x] **Rate limiting** inteligente para DeepSeek API
- [x] **Validación de seguridad** en análisis de archivos
- [x] **Planificación de roadmap** basada en experiencia
- [x] **Auto-diagnóstico** de technical debt
- [x] **Análisis de patrones** de uso real

### 🚀 Próximo en v0.2.0
- [ ] **Modo conversacional** interactivo
- [ ] **Tool calling automático** para ejecución de comandos
- [ ] **Sistema de plugins** extensible
- [ ] **Escaneo de red** integrado
- [ ] **Dashboard web** complementario

### 🔮 Futuro v1.0.0
- [ ] **Agente totalmente autónomo** con reasoning avanzado
- [ ] **Aprendizaje por refuerzo** de técnicas de pentesting
- [ ] **Integración con herramientas** de seguridad (nmap, metasploit)
- [ ] **Sistema de reporting** automático
- [ ] **Comunidad de plugins** de la comunidad

---

**v0.1.3**: ¡Alma Agent ahora piensa en su propio crecimiento! 🧠🚀