# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-11-24

### 🚀 Agregado
- **Sistema de Memoria Contextual**: 
  - Comando `memory create` para crear memorias
  - Comando `memory list` para listar memorias almacenadas
  - Comando `memory search` para buscar en memorias
  - Persistencia en PostgreSQL con tablas `alma_memories` y `pentest_sessions`

- **Integración DeepSeek LLM**:
  - Cliente API para DeepSeek con patrón Singleton
  - Comando `test-llm` para probar conexiones
  - Manejo robusto de errores y timeouts

- **Sistema de Diagnóstico**:
  - Comando `debug-env` para verificar variables de entorno
  - Comando `status` para estado del sistema
  - Verificación automática de conexiones

- **Infraestructura**:
  - Docker Compose con red externa
  - Configuración via variables de entorno
  - Estructura modular de comandos con Typer

### 🔧 Cambiado
- **Arquitectura**: Migración a estructura modular con `core/` y `commands/`
- **Base de Datos**: Esquema mejorado con soporte para JSONB y metadatos
- **Manejo de Estado**: Patrón Singleton para cliente LLM

### 🐛 Corregido
- **Inicialización**: Problema de estado en cliente LLM entre comandos
- **Variables de Entorno**: Carga correcta desde archivo `.env`
- **Conexión DB**: Valores por defecto corregidos para base de datos `hood`

### 📊 Estructura de Datos
```sql
-- Tabla de memorias
alma_memories (id, created_at, memory_type, content, metadata, context, importance)

-- Tabla de sesiones  
pentest_sessions (id, session_name, target, started_at, status, findings)
```

### 🎯 Compatibilidad
- **Python**: 3.11+
- **PostgreSQL**: 13+
- **Docker**: 20+
- **DeepSeek API**: v1

## [0.1.0] - 2024-11-20

### 🚀 Agregado
- Estructura inicial del proyecto con Typer
- Configuración básica de Docker
- Esqueleto de comandos principales

---

**Nota**: Versiones anteriores a 0.1.0 fueron de desarrollo interno.