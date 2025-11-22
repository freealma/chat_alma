"""
---
version: 0.0.1
changelog: "Primera versión del paquete Alma"
path: src/alma/__main__.py
description: "Punto de entrada principal para el paquete Alma"
functions: []
---
"""
# src/alma/__main__.py
from .core.alma import main

if __name__ == "__main__":
    main()