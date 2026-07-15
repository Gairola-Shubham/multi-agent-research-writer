from typing import Dict, Type

from backend.llm.base import BaseLLMProvider
from backend.llm.ollama_provider import OllamaProvider


class LLMProviderFactory:
    """Factory class to manage registration and creation of LLM providers."""

    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "ollama": OllamaProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_cls: Type[BaseLLMProvider]) -> None:
        """Register a new LLM provider class."""
        cls._providers[name.lower()] = provider_cls

    @classmethod
    def get_provider(cls, name: str, **kwargs) -> BaseLLMProvider:
        """Get an instance of the requested LLM provider."""
        provider_name = name.lower()
        if provider_name not in cls._providers:
            raise ValueError(
                f"Unknown LLM provider: '{name}'. "
                f"Available providers: {list(cls._providers.keys())}"
            )
        return cls._providers[provider_name](**kwargs)
