# Changelog - Alma CLI

Todos los cambios notables en Alma CLI serán documentados en este archivo.

## [0.0.2] - 2025-11-21

### ✨ Nuevas Características
- **Búsqueda inteligente con LLM**: Nuevo modo `smart` que usa DeepSeek para re-rankear resultados
- **Comando `/searchmode`**: Permite cambiar entre búsqueda simple (rápida) e inteligente (con LLM)
- **Script de inicialización**: `inject_memories.sh` para cargar 30 memorias base automáticamente
- **Mejor feedback**: Indicadores visuales del modo de búsqueda activo

### 🔧 Mejoras Técnicas
- **MemoryManager mejorado**: Soporte para búsqueda híbrida (keywords + re-ranking LLM)
- **Arquitectura modular**: Separación clara entre búsqueda simple e inteligente
- **Manejo de errores**: Fallback automático a búsqueda simple si LLM falla
- **Integración API**: MemoryManager ahora recibe API key para llamadas a DeepSeek

### 📝 Documentación
- README actualizado con nuevos comandos y características
- Documentación técnica expandida en `alma.md`
- Guía de instalación mejorada

### 🐛 Correcciones
- Problemas de importación de módulos resueltos
- Mejor manejo de contenedores Docker
- Paths de base de datos corregidos

## [0.0.1] - 2025-11-20

### 🚀 Lanzamiento Inicial
- Chat CLI básico con DeepSeek AI
- Sistema de memoria persistente en SQLite
- Comandos `/add`, `/memories`, `/exit`
- Búsqueda por keywords simples
- Containerización con Docker
- Estructura de proyecto modular

---

## Format

Este changelog sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y el proyecto usa [Versionado Semántico](https://semver.org/spec/v2.0.0.html).