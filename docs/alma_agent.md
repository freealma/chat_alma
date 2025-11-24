# Alma Agent - Documentación Técnica

## 🎯 Visión General

Alma Agent es un copiloto pentester inteligente construido en Python que combina:
- **🧠 Memoria contextual** con PostgreSQL
- **🤖 Capacidades LLM** con DeepSeek API
- **🔍 Herramientas de análisis** de seguridad
- **💾 Sistema de memorias** persistente

## 🏗️ Arquitectura

### Estructura de Proyecto
```
alma/
├── src/alma/
│   ├── core/
│   │   ├── database.py      # Gestión de conexión PostgreSQL
│   │   └── llm_client.py    # Cliente DeepSeek API
│   ├── commands/
│   │   ├── memory_ops.py    # Operaciones con memorias
│   │   └── code_review.py   # Análisis de código (próximo)
│   ├── alma_agent.py        # CLI principal con Typer
│   └── __main__.py          # Punto de entrada
```

### Flujo de Datos
```
Usuario → Typer CLI → Alma Agent → PostgreSQL + DeepSeek API
                ↓
        Resultados formateados con Rich
```

## 🔧 Comandos Implementados

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
**Salida esperada**:
```
╭───────────────────────────────────────────────────────── Alma Agent Status ─────────────────────────────────────────────────────────╮
│ 🧠 Memorias almacenadas: 0                                                                                                          │
│ 🔍 Sesiones activas: 0                                                                                                              │
│ 🤖 Estado LLM: ✅ Conectado                                                                                                         │
│ 📊 Base de datos: Conectada                                                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### `alma test-llm`
**Propósito**: Prueba la conexión con DeepSeek API
```bash
docker compose exec alma-agent alma test-llm "Tu pregunta aquí"
```
**Parámetros**:
- `prompt`: Texto de la pregunta (opcional, default: "Hola Alma")

#### `alma debug-env`
**Propósito**: Diagnóstico de variables de entorno
```bash
docker compose exec alma-agent alma debug-env
```
**Salida esperada**:
```
🔍 Variables de entorno:
  ✅ DB_HOST: psql
  ✅ DB_PORT: 5432
  ✅ DB_NAME: hood
  ✅ DB_USER: alma
  ✅ DB_PASSWORD: ***
  ✅ DEEPSEEK_API_KEY: ***
```

### Comandos de Memoria

#### `alma memory create`
**Propósito**: Crea una nueva memoria en la base de datos
```bash
docker compose exec alma-agent alma memory create "Contenido de la memoria" --memory-type observation --importance 3
```
**Opciones**:
- `--memory-type`: Tipo de memoria (default: "observation")
- `--importance`: Importancia 1-5 (default: 1)
- `--context`: Contexto adicional (opcional)

#### `alma memory list`
**Propósito**: Lista memorias almacenadas
```bash
docker compose exec alma-agent alma memory list --limit 10 --memory-type observation
```
**Opciones**:
- `--limit`: Límite de resultados (default: 10)
- `--memory-type`: Filtrar por tipo

#### `alma memory search`
**Propósito**: Busca en las memorias por contenido
```bash
docker compose exec alma-agent alma memory search "término de búsqueda"
```

## 🔌 Configuración

### Variables de Entorno
Archivo `alma.env`:
```env
DEEPSEEK_API_KEY=sk-tu_api_key_aqui
DB_HOST=psql
DB_PORT=5432
DB_NAME=hood
DB_USER=alma
DB_PASSWORD=umamia
```

### Esquema de Base de Datos

#### Tabla `alma_memories`
```sql
CREATE TABLE alma_memories (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    context TEXT,
    importance INTEGER DEFAULT 1
);
```

#### Tabla `pentest_sessions`
```sql
CREATE TABLE pentest_sessions (
    id SERIAL PRIMARY KEY,
    session_name VARCHAR(255) NOT NULL,
    target TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    findings JSONB
);
```

## 🛠️ Desarrollo

### Agregar Nuevos Comandos

1. **Crear archivo en `src/alma/commands/`**
```python
import typer
from rich.console import Console

console = Console()
nuevo_app = typer.Typer(help="Descripción del comando")

@nuevo_app.command("accion")
def comando_accion(parametro: str = typer.Argument(...)):
    """Descripción de la acción"""
    console.print("Ejecutando acción...")

# Registrar en app principal
from alma.alma_agent import app
app.add_typer(nuevo_app, name="nuevo", help="Comandos nuevos")
```

2. **El comando estará disponible como**:
```bash
alma nuevo accion "valor"
```

### Estructura del Cliente LLM

El cliente DeepSeek usa el patrón Singleton:
```python
llm_client = AlmaLLMClient()  # Instancia única
llm_client.ensure_initialized()  # Inicialización bajo demanda
response = llm_client.query("prompt")  # Consulta
```

## 🚨 Solución de Problemas

### Error: "Modo sin LLM"
**Causa**: DEEPSEEK_API_KEY no configurada o inválida
**Solución**:
```bash
# Verificar variables
docker compose exec alma-agent alma debug-env

# Verificar formato de API Key
echo $DEEPSEEK_API_KEY  # Debe empezar con "sk-" y tener >10 caracteres
```

### Error: "service alma-agent is not running"
**Causa**: Contenedor no iniciado
**Solución**:
```bash
docker compose up -d alma-agent
docker compose ps  # Verificar estado
```

### Error de conexión a base de datos
**Solución**:
```bash
# Verificar que la red docker esté disponible
docker network ls | grep srv_srv-network

# Verificar conexión manual
docker compose exec alma-agent python -c "
import psycopg2
conn = psycopg2.connect(host='psql', database='hood', user='alma', password='umamia')
print('✅ Conexión exitosa')
"
```

## 📈 Métricas de Performance

- **Tiempo de respuesta LLM**: < 5 segundos
- **Conexión DB**: < 1 segundo
- **Memoria utilizada**: ~100MB por contenedor
- **Almacenamiento**: ~1MB por 1000 memorias

## 🔮 Roadmap

### Versión 0.1.1 (Actual)
- [x] Sistema de memoria básico
- [x] Integración DeepSeek API
- [x] Comandos de diagnóstico

### Versión 0.2.0 (Próxima)
- [ ] Análisis automático de código
- [ ] Comandos de escaneo de red
- [ ] Sistema de plugins

### Versión 1.0.0 (Futuro)
- [ ] Modo agente autónomo
- [ ] Interfaz web complementaria
- [ ] Sistema de reporting