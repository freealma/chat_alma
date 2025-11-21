---
date: 2025-04-06
version: 0.0.1
path: README.md
description: "Alma chat cli con memoria persistente qe mejora."
---

# 🤖 Alma CLI

**Chat terminal inteligente con memoria persistente especializado en hacking y programación**

Alma es una CLI que combina el poder de DeepSeek AI con un sistema de memorias que aprende de tus conversaciones, ideal para pentesting, desarrollo y consultas técnicas.

## 🚀 Características

- 💬 **Chat interactivo** con DeepSeek AI
- 🧠 **Memoria persistente** en SQLite con búsqueda inteligente
- 🔍 **Búsqueda contextual** automática en conversaciones pasadas
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

2. **Ejecuta:**
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
📝 Comandos: /add, /memories, /exit

🧑 Tú: /add Los ataques XSS requieren validación de entrada
✅ Memoria guardada

🧑 Tú: cómo prevenir xss?
🔍 Buscando memorias relevantes...
🤖 Generando respuesta...
🤖 Alma: Basándome en memorias previas, para prevenir XSS...
```

### Comandos del Sistema

- `/add <texto>` - Guardar nueva memoria
- `/memories` - Listar memorias recientes  
- `/exit` - Salir del programa

## 🏗️ Estructura del Proyecto

```
alma/
├── db/                 # Base de datos SQLite (volumen persistente)
├── doc/
│   └── alma.md        # Documentación técnica completa
├── meta/
│   └── schema.sql     # Esquema de la base de datos
├── src/alma/
│   ├── alma.py        # CLI principal
│   ├── memory.py      # Gestor de memorias
│   └── __main__.py    # Entry point alternativo
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

## 📊 Schema de Base de Datos

La base de datos utiliza un schema optimizado con:
- **UUIDs únicos** para cada memoria
- **Sistema de importancia** (1-5 estrellas)
- **Contadores de uso** para relevancia
- **Tipos de memoria** categorizados
- **Búsqueda full-text** con tags

Ver `meta/schema.sql` para detalles completos.

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

Distribuido bajo MIT License. Ver `LICENSE` para más información.

## 🆘 Soporte

Si encuentras issues:
1. Revisa la documentación en `doc/alma.md`
2. Abre un issue en el repositorio
3. Contacta al mantenedor

---