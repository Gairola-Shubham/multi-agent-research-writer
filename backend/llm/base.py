from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional


class LLMError(Exception):
    """Base exception for LLM provider errors."""

    pass


class LLMConnectionError(LLMError):
    """Raised when the LLM server is unreachable."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when a request to the LLM server times out."""

    pass


class LLMModelNotFoundError(LLMError):
    """Raised when the requested model is not found on the LLM server."""

    pass


class BaseLLMProvider(ABC):
    """Abstract base class representing an LLM Provider."""

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Get the base URL of the LLM provider."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Get the default model name for the LLM provider."""
        pass

    @property
    @abstractmethod
    def is_online(self) -> bool:
        """Check if the LLM provider is online (cached check)."""
        pass

    @is_online.setter
    @abstractmethod
    def is_online(self, value: bool) -> None:
        """Set the online status cache of the LLM provider."""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """Verify connection to the LLM provider.

        Returns True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models from the LLM provider."""
        pass

    @abstractmethod
    def has_model(self, model_name: str) -> bool:
        """Check if a specific model is installed/available."""
        pass

    @abstractmethod
    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model.

        Blocks until the model is pulled completely, yielding progress logs.
        """
        pass

    @abstractmethod
    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate a synchronous text response."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Yield streaming text generation chunks."""
        pass
