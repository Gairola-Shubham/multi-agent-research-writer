"""
Backward compatibility layer for the Ollama client.
All exports are redirected to the new backend.llm module.
"""

from backend.llm.ollama_provider import (
    OllamaConnectionError,
    OllamaError,
    OllamaModelNotFoundError,
    OllamaProvider as OllamaClient,
    OllamaTimeoutError,
)

__all__ = [
    "OllamaClient",
    "OllamaError",
    "OllamaConnectionError",
    "OllamaTimeoutError",
    "OllamaModelNotFoundError",
]
