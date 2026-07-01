import json
import time
from typing import Any, Dict, Iterator, List, Optional

import requests

from backend.core.config import settings
from backend.core.logger import logger


class OllamaError(Exception):
    """Base exception for Ollama client errors."""
    pass

class OllamaConnectionError(OllamaError):
    """Raised when the Ollama server is unreachable."""
    pass

class OllamaTimeoutError(OllamaError):
    """Raised when a request to Ollama times out."""
    pass

class OllamaModelNotFoundError(OllamaError):
    """Raised when the requested model is not found on the Ollama server."""
    pass

class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        self.base_url = base_url or settings.OLLAMA_HOST or settings.OLLAMA_BASE_URL
        # Clean trailing slash if present
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        self.default_model = default_model or settings.DEFAULT_MODEL or settings.LLM_MODEL
        self.timeout = timeout if timeout is not None else settings.REQUEST_TIMEOUT

        # Connection check is deferred until check_connection is explicitly called or property is accessed
        self._is_online: Optional[bool] = None

    @property
    def is_online(self) -> bool:
        if self._is_online is None:
            self._is_online = self.check_connection()
        return self._is_online

    @is_online.setter
    def is_online(self, value: bool) -> None:
        self._is_online = value

    def _request(
        self,
        method: str,
        path: str,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        **kwargs
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        timeout = kwargs.pop("timeout", self.timeout)

        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"Ollama API {method} {path} (attempt {attempt}/{max_retries})")
                response = requests.request(method, url, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.Timeout as e:
                logger.warning(f"Ollama request timeout on {method} {path} (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise OllamaTimeoutError(f"Request to Ollama timed out after {max_retries} attempts.") from e
            except requests.ConnectionError as e:
                logger.warning(f"Ollama request connection error on {method} {path} (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise OllamaConnectionError(f"Cannot connect to Ollama server at {self.base_url}.") from e
            except requests.RequestException as e:
                logger.warning(f"Ollama request HTTP error on {method} {path} (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    status_code = getattr(e.response, 'status_code', None)
                    raise OllamaError(f"Ollama API returned error: {e}. Status code: {status_code}") from e

            # Wait with exponential backoff
            time.sleep(backoff_factor * (2 ** (attempt - 1)))

        raise OllamaError("Ollama request failed after maximum retries.")

    def check_connection(self) -> bool:
        """
        Check if Ollama service is running and reachable.
        Returns True if connected, False otherwise.
        """
        try:
            # Short timeout for connection ping
            response = requests.get(f"{self.base_url}/", timeout=3)
            if response.status_code == 200:
                logger.info(f"Ollama connection check successful at {self.base_url}")
                self._is_online = True
                return True
            else:
                logger.warning(f"Ollama connection check returned status {response.status_code} at {self.base_url}")
                self._is_online = False
                return False
        except Exception as e:
            logger.warning(f"Ollama connection check failed at {self.base_url}: {e}")
            self._is_online = False
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Retrieve available models from Ollama.
        """
        try:
            response = self._request("GET", "/api/tags")
            models = response.json().get("models", [])
            logger.info(f"Retrieved {len(models)} models from Ollama.")
            return models
        except Exception as e:
            logger.error(f"Failed to list models from Ollama: {e}")
            raise

    def has_model(self, model_name: str) -> bool:
        """
        Check if a specific model is installed on the Ollama server.
        """
        try:
            models = self.list_models()
            target = model_name
            target_no_tag = model_name.split(':')[0] if ':' in model_name else model_name

            for m in models:
                m_name = m.get("name", "")
                if m_name == target:
                    return True

                # Compare without tag if tag wasn't specified in target
                m_name_no_tag = m_name.split(':')[0] if ':' in m_name else m_name
                if m_name_no_tag == target_no_tag:
                    if ':' not in target:
                        return True
                    # Compare specific tags
                    target_tag = target.split(':')[1]
                    m_tag = m_name.split(':')[1] if ':' in m_name else ""
                    if target_tag == m_tag:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking model existence for '{model_name}': {e}")
            return False

    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from the Ollama library.
        Blocks until the model is pulled completely, yielding progress logs.
        """
        payload = {"name": model_name}
        url = f"{self.base_url}/api/pull"

        try:
            logger.info(f"Starting pull request for Ollama model '{model_name}'...")
            # We use stream=True to monitor download progress
            response = requests.post(url, json=payload, timeout=600, stream=True)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    status = data.get("status", "")
                    completed = data.get("completed", 0)
                    total = data.get("total", 0)
                    if total > 0:
                        pct = (completed / total) * 100
                        logger.info(f"Pulling '{model_name}': {status} ({pct:.2f}%)")
                    else:
                        logger.info(f"Pulling '{model_name}': {status}")

            logger.info(f"Successfully pulled model '{model_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model '{model_name}': {e}")
            return False

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a synchronous text response.
        """
        # Verify model existence
        if not self.has_model(model):
            raise OllamaModelNotFoundError(f"Model '{model}' is not installed on Ollama server.")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options

        response = self._request("POST", "/api/generate", json=payload, timeout=timeout)
        return response.json()

    def generate_stream(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Yield streaming text generation chunks.
        """
        # Verify model existence
        if not self.has_model(model):
            raise OllamaModelNotFoundError(f"Model '{model}' is not installed on Ollama server.")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options

        url = f"{self.base_url}/api/generate"
        t = timeout if timeout is not None else self.timeout

        try:
            logger.info(f"Ollama stream triggered for model: '{model}'")
            response = requests.post(url, json=payload, timeout=t, stream=True)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    yield json.loads(line.decode('utf-8'))
        except requests.Timeout as e:
            logger.error(f"Ollama stream timeout error: {e}")
            raise OllamaTimeoutError("Streaming request to Ollama timed out.") from e
        except requests.ConnectionError as e:
            logger.error(f"Ollama stream connection error: {e}")
            raise OllamaConnectionError("Connection error during streaming.") from e
        except requests.RequestException as e:
            logger.error(f"Ollama stream error: {e}")
            raise OllamaError(f"Error during streaming: {e}") from e
