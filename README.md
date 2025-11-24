# 🤖 Alma Agent - Copiloto Pentester Inteligente

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Compatible-blue.svg)](https://www.postgresql.org/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-green.svg)](https://deepseek.com/)

Alma Agent es tu compañero inteligente para tareas de pentesting y seguridad, combinando la potencia de LLMs con herramientas prácticas de análisis.

## ✨ Características

- **🧠 Memoria Contextual**: Almacena y recupera información de sesiones anteriores
- **🤖 Asistente LLM**: Integración nativa con DeepSeek API para análisis inteligente
- **🔍 Herramientas de Seguridad**: Comandos especializados para pentesting
- **💾 Persistencia**: Base de datos PostgreSQL para almacenamiento durable
- **🐳 Contenedorizado**: Ejecución consistente con Docker

## 🚀 Comenzando

### Prerrequisitos
- Docker y Docker Compose
- Acceso a una base de datos PostgreSQL
- API Key de [DeepSeek](https://platform.deepseek.com/)

### Instalación Rápida

1. **Clonar y configurar**:
```bash
git clone <repositorio>
cd alma

# Configurar variables de entorno
cp alma.env.example alma.env
# Editar alma.env con tus credenciales
```

2. **Inicializar**:
```bash
docker compose up -d alma-agent
docker compose exec alma-agent alma init
```

3. **¡Listo!**:
```bash
docker compose exec alma-agent alma --help
```

## 📋 Uso Básico

### Gestión del Sistema
```bash
# Ver estado
docker compose exec alma-agent alma status

# Probar LLM
docker compose exec alma-agent alma test-llm "Analiza esta vulnerabilidad XSS"

# Diagnóstico
docker compose exec alma-agent alma debug-env
```

### Sistema de Memoria
```bash
# Crear memoria
docker compose exec alma-agent alma memory create "El servidor usa Apache 2.4.49 vulnerable" --importance 4

# Listar memorias
docker compose exec alma-agent alma memory list

# Buscar memorias
docker compose exec alma-agent alma memory search "Apache"
```

## 🏗️ Estructura del Proyecto

```
alma/
├── src/alma/                 # Código fuente
│   ├── core/                # Núcleo del sistema
│   ├── commands/            # Comandos Typer
│   └── alma_agent.py        # CLI principal
├── docs/                    # Documentación
│   └── alma_agent.md        # Guía técnica
├── docker-compose.yaml      # Orquestación
├── Dockerfile              # Contenedor
└── alma.env               # Configuración
```

## 🔧 Comandos Disponibles

### Sistema
- `init` - Inicializa base de datos y LLM
- `status` - Estado del sistema
- `test-llm` - Prueba conexión DeepSeek
- `debug-env` - Diagnóstico variables

### Memoria
- `memory create` - Crear nueva memoria
- `memory list` - Listar memorias
- `memory search` - Buscar en memorias

## ⚙️ Configuración

### Variables de Entorno (`alma.env`)
```env
DEEPSEEK_API_KEY=sk-tu_clave_aqui
DB_HOST=psql
DB_PORT=5432
DB_NAME=hood
DB_USER=alma
DB_PASSWORD=tu_password
```

### Base de Datos
Alma Agent crea automáticamente:
- Tabla `alma_memories` para almacenamiento contextual
- Tabla `pentest_sessions` para sesiones de testing

## 🐛 Solución de Problemas

### LLM No Responde
```bash
# Verificar API Key
docker compose exec alma-agent alma debug-env

# Probar conexión manual
docker compose exec alma-agent alma test-llm "Hola"
```

### Error de Base de Datos
```bash
# Reinicializar
docker compose exec alma-agent alma init

# Verificar conexión
docker compose exec alma-agent python -c "import psycopg2; conn = psycopg2.connect(host='psql', database='hood', user='alma', password='umamia'); print('✅ OK')"
```

## 📖 Documentación

- [**Guía Técnica**](docs/alma_agent.md) - Arquitectura y desarrollo
- [**Changelog**](CHANGELOG.md) - Historial de versiones

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## 🙏 Agradecimientos

- [DeepSeek](https://deepseek.com/) por el acceso a modelos LLM
- [Typer](https://typer.tiangolo.com/) para la CLI
- [Rich](https://rich.readthedocs.io/) para interfaces en terminal