from typing import Any, Dict, Iterator, Optional

from backend.core.logger import logger
from backend.models.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)


class AIService:
    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()

    def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a text response synchronously from Ollama.
        """
        model_name = model or self.client.default_model
        logger.info(f"AIService generate response requested for model '{model_name}'")
        try:
            # First check if Ollama is online
            if not self.client.check_connection():
                raise OllamaConnectionError(f"Ollama server at {self.client.base_url} is unreachable.")

            response = self.client.generate(
                model=model_name,
                prompt=prompt,
                system=system,
                options=options,
                timeout=timeout
            )
            return response
        except (OllamaConnectionError, OllamaTimeoutError, OllamaModelNotFoundError) as e:
            logger.error(f"AIService generate response error: {e}")
            raise
        except Exception as e:
            logger.error(f"AIService generate response unexpected error: {e}")
            raise OllamaError(f"Unexpected AI Service error: {e}") from e

    def stream_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Yield streaming text generation chunks from Ollama.
        """
        model_name = model or self.client.default_model
        logger.info(f"AIService stream response requested for model '{model_name}'")
        try:
            if not self.client.check_connection():
                raise OllamaConnectionError(f"Ollama server at {self.client.base_url} is unreachable.")

            yield from self.client.generate_stream(
                model=model_name,
                prompt=prompt,
                system=system,
                options=options,
                timeout=timeout
            )
        except (OllamaConnectionError, OllamaTimeoutError, OllamaModelNotFoundError) as e:
            logger.error(f"AIService stream response error: {e}")
            raise
        except Exception as e:
            logger.error(f"AIService stream response unexpected error: {e}")
            raise OllamaError(f"Unexpected AI Service error: {e}") from e

    def health_check(self) -> Dict[str, Any]:
        """
        Check connectivity and default model availability.
        """
        is_connected = self.client.check_connection()
        status = {
            "status": "healthy" if is_connected else "unhealthy",
            "connection": "connected" if is_connected else "disconnected",
            "base_url": self.client.base_url,
            "default_model": self.client.default_model,
            "model_available": False
        }

        if is_connected:
            try:
                status["model_available"] = self.client.has_model(self.client.default_model)
            except Exception as e:
                logger.warning(f"AIService health_check could not verify model availability: {e}")

        return status

# Singleton instance of AIService
ai_service = AIService()
