import os
import pytest
from unittest.mock import patch, MagicMock
from backend.core.config import Settings
from backend.core.startup_validation import run_startup_checks
from backend.models.ollama_client import OllamaClient
from backend.services.ai_service import AIService, ai_service


def test_configuration_reuse_and_defaults():
    """Verify configuration reuse and fallbacks function correctly."""
    s = Settings(
        OLLAMA_BASE_URL="http://test-ollama-url:11434",
        OLLAMA_HOST="",
        LLM_MODEL="test-model",
        DEFAULT_MODEL=""
    )
    assert s.OLLAMA_HOST == "http://test-ollama-url:11434"
    assert s.DEFAULT_MODEL == "test-model"


@patch("backend.models.ollama_client.OllamaClient.check_connection")
def test_lazy_initialization_ollama_client(mock_check_connection):
    """Verify that OllamaClient does not perform network connection checks on creation."""
    client = OllamaClient(
        base_url="http://test-url",
        default_model="test-model",
        timeout=10
    )
    mock_check_connection.assert_not_called()
    assert client._is_online is None
    
    # Accessing is_online property should invoke check_connection lazily
    mock_check_connection.return_value = True
    
    online_status = client.is_online
    mock_check_connection.assert_called_once()
    assert online_status is True


@patch("os.makedirs")
@patch("builtins.open")
@patch("os.remove")
@patch("backend.services.ai_service.ai_service.client")
def test_avoid_duplicate_startup_checks(mock_client, mock_remove, mock_open, mock_makedirs):
    """Verify that run_startup_checks runs validation logic exactly once and caches result."""
    import backend.core.startup_validation
    backend.core.startup_validation._startup_checks_run = False
    
    mock_client.check_connection.return_value = True
    mock_client.has_model.return_value = True
    
    # First execution should execute logic
    run_startup_checks()
    mock_makedirs.assert_called_once()
    
    # Second execution should skip executing logic
    mock_makedirs.reset_mock()
    run_startup_checks()
    mock_makedirs.assert_not_called()


@patch("backend.services.ai_service.ai_service.client")
@patch("chromadb.PersistentClient")
def test_health_endpoint_graceful_degradation(mock_chroma, mock_client):
    """Verify health endpoint logs warnings and returns unhealthy status without failing on exception."""
    mock_client.check_connection.side_effect = Exception("Ollama connection failed exception")
    mock_chroma.side_effect = Exception("ChromaDB persistent client error exception")
    
    from fastapi.testclient import TestClient
    from backend.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["ollama"] == "unhealthy"
    assert data["chromadb"] == "unhealthy"


def test_service_singletons():
    """Verify that AIService instances are reused globally."""
    assert isinstance(ai_service, AIService)
    from backend.services.ai_service import ai_service as imported_service
    assert ai_service is imported_service


@patch("backend.api.routes.workflow")
def test_health_endpoint_reuses_workflow_services(mock_workflow):
    """Verify that health check endpoint attempts to reuse existing service instances from workflow."""
    mock_search_service = MagicMock()
    mock_memory_service = MagicMock()
    mock_memory_service.collection = MagicMock()
    
    mock_workflow.research_agent = MagicMock()
    mock_workflow.research_agent.search_service = mock_search_service
    mock_workflow.research_agent.memory_service = mock_memory_service
    
    from fastapi.testclient import TestClient
    from backend.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["search"] == "healthy"
    assert data["memory"] == "healthy"
