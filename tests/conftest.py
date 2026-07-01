from unittest.mock import MagicMock, patch

import pytest

# 1. Mock OllamaClient methods globally at import time to prevent real network calls
check_conn_patcher = patch("backend.models.ollama_client.OllamaClient.check_connection", return_value=True)
list_models_patcher = patch("backend.models.ollama_client.OllamaClient.list_models", return_value=[{"name": "qwen2.5:7b"}])
has_model_patcher = patch("backend.models.ollama_client.OllamaClient.has_model", return_value=True)
request_patcher = patch("backend.models.ollama_client.OllamaClient._request", return_value=MagicMock())

# Start the client patchers
check_conn_patcher.start()
list_models_patcher.start()
has_model_patcher.start()
request_patcher.start()

# 2. Mock AIService methods globally
ai_generate_patcher = patch("backend.services.ai_service.AIService.generate_response", return_value={"response": "{}"})
ai_stream_patcher = patch("backend.services.ai_service.AIService.stream_response", return_value=[{"response": "{}"}])
ai_health_patcher = patch("backend.services.ai_service.AIService.health_check", return_value={
    "status": "healthy",
    "connection": "connected",
    "base_url": "http://localhost:11434",
    "default_model": "qwen2.5:7b",
    "model_available": True
})

# Start the AI service patchers
ai_generate_patcher.start()
ai_stream_patcher.start()
ai_health_patcher.start()

# 3. Patch requests globally to prevent any outgoing socket requests
requests_get_patcher = patch("requests.get")
requests_post_patcher = patch("requests.post")
requests_request_patcher = patch("requests.request")

requests_get_patcher.start()
requests_post_patcher.start()
requests_request_patcher.start()

@pytest.fixture(autouse=True)
def reset_startup_checks_flag():
    try:
        import backend.core.startup_validation
        backend.core.startup_validation._startup_checks_run = False
    except ImportError:
        pass

# Cleanup patchers after session
def pytest_sessionfinish(session, exitstatus):
    check_conn_patcher.stop()
    list_models_patcher.stop()
    has_model_patcher.stop()
    request_patcher.stop()

    ai_generate_patcher.stop()
    ai_stream_patcher.stop()
    ai_health_patcher.stop()

    requests_get_patcher.stop()
    requests_post_patcher.stop()
    requests_request_patcher.stop()
