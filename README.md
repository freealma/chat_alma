---
date: 2025-04-06
version: 0.0.2
path: README.md
description: "Alma chat cli con memoria persistente qe mejora."
changelog: "Se agrega manejo de memorias con LLM en `memory.py` y `alma.py`"
tags: 
 - "alma"
 - "cli"
 - "doc"
---

# 🤖 Alma CLI

**Chat terminal inteligente con memoria persistente especializado en hacking y programación**

Alma es una CLI que combina el poder de DeepSeek AI con un sistema de memorias que aprende de tus conversaciones, ideal para pentesting, desarrollo y consultas técnicas.

## 🚀 Características

- 💬 **Chat interactivo** con DeepSeek AI
- 🧠 **Memoria persistente** en SQLite con búsqueda inteligente
- 🔍 **Búsqueda contextual** automática en conversaciones pasadas
- 🧩 **Dos modos de búsqueda**: simple (rápido) y smart (con LLM)
- 📝 **Comandos integrados** para gestionar memorias
- 🐳 **Containerizado** con Docker para fácil despliegue
- 🎯 **Especializado** en seguridad informática y programación

## 🛠️ Instalación Rápida

### Prerrequisitos
- Docker
- API Key de [DeepSeek](https://platform.deepseek.com/)

### Configuración en 30 segundos

1. **Clona y configura:**
```bash
git clone <tu-repo>
cd alma
echo "DEEPSEEK_API_KEY=tu_api_key_aqui" > .env
```

2. **Construir y ejecutar:**
```bash
docker build -t alma-cli .
docker run -it --env-file .env -v $(pwd)/db:/alma/db alma-cli
```

## 🎮 Uso

```bash
# Iniciar chat
docker run -it --env-file .env -v $(pwd)/db:/alma/db alma-cli

# Comandos disponibles:
🤖 Alma CLI v0.1.0
💬 Chat con memoria persistente
📝 Comandos: /add, /memories, /exit, /searchmode
🔍 Modos de búsqueda: simple (rápido) | smart (con LLM)

🧑 Tú: /searchmode
🔍 Modo de búsqueda cambiado a: smart (con LLM)

🧑 Tú: /add Los ataques XSS requieren validación de entrada
✅ Memoria guardada

🧑 Tú: cómo prevenir xss?
🔍 Buscando memorias relevantes...
   Modo: smart
   ✅ Memorias encontradas (re-rankeadas por relevancia)
🤖 Generando respuesta...
🤖 Alma: Basándome en memorias previas, para prevenir XSS...
```

### Comandos del Sistema

- `/add <texto>` - Guardar nueva memoria
- `/memories` - Listar memorias recientes  
- `/searchmode` - Cambiar entre búsqueda simple/smart
- `/exit` - Salir del programa

## 🧠 Cargar Memorias Iniciales

Después de ejecutar Alma por primera vez, carga las memorias base:

```bash
# Desde la raíz del proyecto
./src/alma/utils/inject_memories.sh
```

Esto cargará 30 memorias sobre:
- Estructura y funcionamiento de Alma
- Comandos disponibles
- Arquitectura técnica  
- Visión futura como agente pentester

## 🏗️ Estructura del Proyecto

```
alma/
├── db/                 # Base de datos SQLite (volumen persistente)
├── doc/
│   ├── alma.md        # Documentación técnica completa
│   └── changelog.md   # Historial de cambios
├── src/alma/
│   ├── alma.py        # CLI principal con búsqueda mejorada
│   ├── memory.py      # Gestor de memorias con soporte LLM
│   ├── __init__.py
│   ├── __main__.py
│   └── utils/
│       └── inject_memories.sh  # Script de inicialización
├── meta/
│   └── schema.sql     # Esquema de la base de datos
├── Dockerfile
├── .env              # Configuración (API keys)
└── pyproject.toml    # Dependencias Python
```

## 🔧 Desarrollo

```bash
# Instalación para desarrollo
pip install -e .

# Ejecutar directamente
python -m alma

# O via script
python src/alma/alma.py
```

## 🐛 Troubleshooting

**Problema**: El contenedor no muestra input  
**Solución**: Usar `docker run` directo en lugar de docker-compose

**Problema**: Error de API key  
**Solución**: Verificar que el archivo `.env` tenga `DEEPSEEK_API_KEY=tu_key`

**Problema**: Módulo no encontrado  
**Solución**: Reconstruir la imagen con `docker build --no-cache`

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo MIT License.

## 🆘 Soporte

Si encuentras issues:
1. Revisa la documentación en `doc/alma.md`
2. Consulta el changelog en `doc/changelog.md`
3. Abre un issue en el repositorio

---

**Alma CLI v0.0.2** - Tu compañero inteligente para hacking y desarrollo 💻