import os
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel

console = Console()

class AlmaLLMClient:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.initialized = False
        self.llm = None
        
    def initialize(self):
        """Inicializa el cliente LLM"""
        try:
            console.print(f"[dim]🔍 Buscando DEEPSEEK_API_KEY...[/dim]")
            
            if not self.api_key:
                console.print("[yellow]⚠️  DEEPSEEK_API_KEY no encontrada en variables de entorno[/yellow]")
                console.print("[dim]Variables de entorno disponibles:[/dim]")
                for key, value in os.environ.items():
                    if 'key' in key.lower() or 'api' in key.lower():
                        console.print(f"[dim]  {key}: {'*' * len(value) if value else 'None'}[/dim]")
                
                self.initialized = False
                return
            
            # Verificar que la API key tenga formato válido
            if self.api_key.startswith('sk-') and len(self.api_key) > 10:
                console.print("✅ [green]Cliente LLM inicializado con DeepSeek[/green]")
                console.print(f"[dim]📋 API Key: {self.api_key[:10]}...[/dim]")
                self.initialized = True
            else:
                console.print("[red]❌ DEEPSEEK_API_KEY tiene formato inválido[/red]")
                self.initialized = False
            
        except Exception as e:
            console.print(f"❌ [red]Error inicializando LLM: {e}[/red]")
            self.initialized = False
    
    def query(self, prompt: str, context: Optional[str] = None) -> str:
        """Consulta al modelo LLM"""
        if not self.initialized:
            return "[Modo sin LLM] Esta funcionalidad requiere configurar DEEPSEEK_API_KEY"
        
        # Aquí irá la integración real con DeepSeek
        return f"[DeepSeek] Procesando: {prompt} (API Key: {self.api_key[:10]}...)"

# ⬇️⬇️⬇️ IMPORTANTE: Crear la instancia aquí ⬇️⬇️⬇️
llm_client = AlmaLLMClient()