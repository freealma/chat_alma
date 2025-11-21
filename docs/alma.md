# Contexto chat alma cli

Vamos a replantear con la siguiente estrctura , qe no cargue logs de la conversacion pero qe si pueda cargar memorias dentro del chat

Deberia correr el terminal clihecha contenedor y con las dependencias en pyrpoject.toml


## Estructura Fisica :

```txt
/alma/
.
├── alma.env
├── config
│   ├── alma.dockerfile                 # Contenedor docker de Alma.
│   ├── alma.env                        # API KEY deepseek
│   └── alma.yaml                       # Configuracion de rutas
├── db
│   └── alma.db                         # Base de datos de memorias.
├── docs
│   └── alma.md                         # Documentacion de alma
├── meta
│   └── alma.sql                        # Schema de memorias
├── pyproject.toml                      # Dependencias
├── README .MD
└── src
    └── alma
        ├── alma.py                     # Terminal cli (corre cuando empieza el docker)
        ├── core
        │   ├── __init__.py
        │   └── memory_manager.py       # Gestor de busqueda de memorias
        ├── __init__.py
        └── utils
            ├── config_loader.py        # Carga de configuracion
            ├── init_db.py              # Iniciador de db con carga de muchas memorias
            └── __init__.py
```

---

## Configuracion

Utiliza la clave de deepseek para tomar la configuracion 

```
DEEPSEEK_API_KEY=sk-5ef64334e5b24321b0c08858310c2fbd
```

---

## Contenerizacion :

Vamos a crear un dockerfile y un docker compose qe monte el volumen de la base de datos.

---

### alma.dockerfile

No utilizemos docker-compose solo docker tiene todos los scripts aca

Ubicacion: `config/alma.dockerfile`

El contenedor deberia hacer todo el manejo bajo `WORKDIR alma`

---

## Scripts alma

Los script deberian ser tratados como paquete y poder correr comandos dentro del terminal cli. y poder correrse en un terminal aparte tambien

Deberia tener solo algunso scripts en principio 

---

### alma.py

Script principal terminal CLI persistente. con funciones internas a modo agente.

 - Funcion para agregar memoria dentro del chat

 - Funcion para actualizar lso usos de las memorias cada vez qe llama a una memoria

---

### memory_manager.py

Coneccion a db y manejo de memorias y busqueda con los campos de la db

 - Manejo de memorias por tag temas contexto 

 - Usar clave llm para busqueda lmas inteligente entre las memorias

 - Creacion de memorias 

 - Calcular importancia de las memorias y revisar memorias iguales cuando vea mas de 5 memorias iguales reforzar la importancia de la memoria

---

### config_loader.py

Hacerlo como class para que pueda ser importado

Funciones :

 - Carga la config de `config/alma.yaml`

 - Conectar a la base de datos en `db/alma.db`

 - Mantener la configuracion persistente para todos los scripts

 - Agregado de memorias inteligentes durante el chat

 - Funcion para agregar memorias dentro del chat

---

### init_db.py

Script para cargar 20 memorias la primera vez.

---

## Base de datos :

Capacidad para 500 memorias maximos

Base de datos en sqlite3 en `db/alma.db`

---

### Tablas :

Configuraremos las ditintas tablas de manera tal qe se pueda ver el stack y la configuracion interna

---

#### memories 

tabla principal de memorias deberia tener varias filas para poder filtrar bien

id:
uuid:
content:
tags:
project:
them:
created_at:
importance: (1,2,3,4,5)
related_to: (architecture,philosophy,pentesting,programming)
memorie_type: (institutional,context,alma,bird,architecture,structure,function)
user_count:

---

#### relations:

Tabla de relaciones para los tags y los tipos , cuantas memorias estan relacionadas a cada tag , relacionar con uuid y project, y demas relaciones qe se nos puedan ocurrir

---

Respuesta esperada 