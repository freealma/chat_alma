# src/alma/core/__init__.py
# Este archivo puede estar vacío o contener solo esto:
from .database import db_manager
from .llm_client import llm_client

__all__ = ['db_manager', 'llm_client']