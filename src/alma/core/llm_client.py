import os
import httpx
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

class AlmaLLMClient:
    """
    Cliente para DeepSeek API vía OpenAI-compatible endpoint
    Patrón Singleton para mantener el estado
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlmaLLMClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evitar re-inicialización si ya está inicializado
        if not hasattr(self, 'api_key'):
            self.api_key = os.getenv('DEEPSEEK_API_KEY')
            self.base_url = "https://api.deepseek.com/v1"
            self.model = "deepseek-chat"
            self._initialized = False
    
    def initialize(self) -> bool:
        """Inicializa el cliente LLM con DeepSeek - retorna éxito"""
        if self._initialized:
            return True
            
        try:
            console.print(f"[dim]🔍 Inicializando DeepSeek LLM...[/dim]")
            
            if not self.api_key:
                console.print("[yellow]⚠️  DEEPSEEK_API_KEY no encontrada en variables de entorno[/yellow]")
                return False
            
            # Verificar que la API key tenga formato válido
            if not (self.api_key.startswith('sk-') and len(self.api_key) > 10):
                console.print("[red]❌ DEEPSEEK_API_KEY tiene formato inválido[/red]")
                return False
            
            # Probar la conexión con una consulta simple
            console.print("[dim]🔄 Probando conexión con DeepSeek API...[/dim]")
            test_response = self._make_api_call("Responde solo con 'OK' si estás funcionando.")
            
            if test_response and "OK" in test_response.upper():
                console.print("✅ [green]Cliente DeepSeek inicializado correctamente[/green]")
                console.print(f"[dim]🤖 Modelo: {self.model}[/dim]")
                self._initialized = True
                return True
            else:
                console.print("[red]❌ No se pudo conectar a DeepSeek API[/red]")
                if test_response:
                    console.print(f"[dim]Respuesta de prueba: {test_response}[/dim]")
                return False
            
        except Exception as e:
            console.print(f"❌ [red]Error inicializando DeepSeek: {e}[/red]")
            return False
    
    def is_initialized(self) -> bool:
        """Verifica si el cliente está inicializado"""
        return self._initialized
    
    def ensure_initialized(self) -> bool:
        """Asegura que el cliente esté inicializado antes de usar"""
        if not self._initialized:
            return self.initialize()
        return True

    def _make_api_call(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """Hace una llamada real a la API de DeepSeek"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres Alma, un asistente especializado en seguridad informática y pentesting. Responde de manera concisa y técnica."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    console.print(f"[red]❌ Error API ({response.status_code}): {response.text}[/red]")
                    return None
                    
        except httpx.TimeoutException:
            console.print("[red]❌ Timeout conectando a DeepSeek API[/red]")
            return None
        except Exception as e:
            console.print(f"[red]❌ Error en llamada API: {e}[/red]")
            return None
    
    def query(self, prompt: str, context: Optional[str] = None) -> str:
        """Consulta al modelo DeepSeek"""
        # ⬇️⬇️⬇️ IMPORTANTE: Verificar inicialización antes de cada consulta
        if not self.ensure_initialized():
            return "[Modo sin LLM] No se pudo inicializar el cliente DeepSeek. Verifica DEEPSEEK_API_KEY."
        
        console.print(f"[dim]🔄 Consultando DeepSeek...[/dim]")
        
        # Construir el prompt con contexto si está disponible
        full_prompt = prompt
        if context:
            full_prompt = f"Contexto: {context}\n\nPregunta: {prompt}"
        
        response = self._make_api_call(full_prompt)
        
        if response:
            return response
        else:
            return "[Error] No se pudo obtener respuesta de DeepSeek"
    
def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
    """Analiza código para mejoras de autonomía del agente"""
    if not self.ensure_initialized():
        return {"error": "LLM no configurado"}
    
    prompt = f"""
Como experto en arquitectura de agentes AI, analiza este código {language} para Alma Agent.

ENFOQUE: Mejoras técnicas para AUTONOMÍA y CRECIMIENTO del agente

Código:
```{language}
{code}
```

Responde SOLO en JSON con:
- "autonomy_improvements": [mejoras para autonomía]
- "next_features": [features sugeridas]  
- "architecture_issues": [problemas arquitectónicos]
- "learning_opportunities": [oportunidades de aprendizaje]
- "priority": "alta|media|baja"

ENFÓCATE EN:
• Cómo hacer el agente más autónomo
• Capacidades de reasoning que faltan
• Sistema de memoria mejorado
• Toma de decisiones automática
• Procesamiento de contexto
"""
    
    response = self._make_api_call(prompt, max_tokens=2000)
    
    if response:
        try:
            # Parsear simple
            cleaned = response.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned)
        except:
            return {"analysis": response}
    return {"error": "Sin respuesta"}


# Instancia global - SINGLETON
llm_client = AlmaLLMClient()
