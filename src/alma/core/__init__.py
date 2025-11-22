"""
---
version: "1.0.0"
changelog: "Versión inicial del paquete Alma Core"
path: src/alma/core/__init__.py
description: "Inicializador del paquete Alma Core"
functions: []
---
"""
# src/alma/core/__init__.py
from .alma import main, AlmaMemoryManager, chat_mode

__all__ = ['main', 'AlmaMemoryManager', 'chat_mode']