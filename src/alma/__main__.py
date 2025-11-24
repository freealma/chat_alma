from alma.alma_agent import app
import alma.commands 
from alma.alma_agent import app

# ⬇️⬇️⬇️ IMPORTANTE: Importar todos los módulos de comandos para que se registren
try:
    # Comandos de memoria
    from alma.commands import memory_ops
    print("✅ Comandos de memoria registrados")
except ImportError as e:
    print(f"⚠️  No se pudieron cargar comandos de memoria: {e}")

try:
    # Comandos de análisis de código
    from alma.commands import code_review  
    print("✅ Comandos de análisis de código registrados")
except ImportError as e:
    print(f"⚠️  No se pudieron cargar comandos de código: {e}")

if __name__ == "__main__":
    app()