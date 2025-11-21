"""
---
version: 0.0.1
changelog: "Primera versión del paquete Alma"
path: src/alma/__init__.py
description: "Inicializador del paquete Alma"
functions: []
---
"""
# src/alma/__init__.py
from .alma import main
from .memory import MemoryManager

__version__ = "0.0.2"
__all__ = ['main', 'MemoryManager']