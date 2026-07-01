import os
import re
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from backend.core.config import Settings
from backend.core.startup_validation import run_startup_checks


def test_configuration_validation_success():
    """Verify that settings load successfully with valid configuration."""
    valid_settings = Settings(
        BACKEND_HOST="127.0.0.1",
        BACKEND_PORT=9000,
        FRONTEND_PORT=9001,
        OLLAMA_BASE_URL="http://localhost:11434",
        OLLAMA_HOST="http://localhost:11434",
        LLM_MODEL="llama3",
        DEFAULT_MODEL="llama3",
        CHROMA_DB_PATH="/tmp/chromadb"
    )
    assert valid_settings.BACKEND_PORT == 9000
    assert valid_settings.FRONTEND_PORT == 9001
    assert valid_settings.LLM_MODEL == "llama3"


def test_configuration_validation_invalid_port():
    """Verify that settings validation catches out-of-range ports."""
    with pytest.raises(ValidationError) as excinfo:
        Settings(BACKEND_PORT=70000)
    assert "Port must be between 1 and 65535" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        Settings(BACKEND_PORT=-1)
    assert "Port must be between 1 and 65535" in str(excinfo.value)


def test_configuration_validation_invalid_url():
    """Verify that settings validation catches malformed URLs."""
    with pytest.raises(ValidationError) as excinfo:
        Settings(OLLAMA_BASE_URL="not-a-url")
    assert "Invalid URL format" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        Settings(OLLAMA_HOST="ftp://localhost:11434")
    assert "Invalid URL format" in str(excinfo.value)


def test_configuration_validation_empty_fields():
    """Verify that settings validation catches empty/blank strings in required fields."""
    with pytest.raises(ValidationError) as excinfo:
        Settings(LLM_MODEL=" ")
    assert "Field cannot be empty or blank" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        Settings(CHROMA_DB_PATH="")
    assert "Field cannot be empty or blank" in str(excinfo.value)


@patch("backend.services.ai_service.ai_service.client")
@patch("chromadb.PersistentClient")
@patch("backend.search.search_service.SearchService")
@patch("backend.memory.memory_service.MemoryService")
def test_health_endpoint(mock_memory, mock_search, mock_chroma, mock_ollama_client):
    """Verify that health endpoint queries and returns all required component statuses."""
    # Setup mocks
    mock_ollama_client.check_connection.return_value = True
    mock_ollama_client.has_model.return_value = True
    
    mock_chroma_instance = MagicMock()
    mock_chroma.return_value = mock_chroma_instance
    mock_chroma_instance.heartbeat.return_value = 123456
    
    mock_memory_instance = MagicMock()
    mock_memory.return_value = mock_memory_instance
    mock_memory_instance.collection = MagicMock()
    
    from fastapi.testclient import TestClient
    from backend.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ollama"] == "healthy"
    assert data["chromadb"] == "healthy"
    assert data["search"] == "healthy"
    assert data["memory"] == "healthy"
    assert data["workflow"] == "healthy"
    assert "version" in data


@patch("backend.services.ai_service.ai_service.client")
@patch("os.makedirs")
@patch("builtins.open")
@patch("os.remove")
def test_startup_checks_success(mock_remove, mock_open, mock_makedirs, mock_ollama_client):
    """Verify that startup checks pass and log success status without raising errors."""
    from unittest.mock import ANY
    mock_ollama_client.check_connection.return_value = True
    mock_ollama_client.has_model.return_value = True
    
    # Executing startup checks should not raise any exceptions
    run_startup_checks()
    
    mock_makedirs.assert_called_with(ANY, exist_ok=True)
    mock_open.assert_called()


@patch("backend.services.ai_service.ai_service.client")
@patch("os.makedirs")
def test_startup_checks_critical_chromadb_failure(mock_makedirs, mock_ollama_client):
    """Verify that startup checks raise RuntimeError when ChromaDB directory is not writable."""
    mock_makedirs.side_effect = PermissionError("Permission denied")
    
    with pytest.raises(RuntimeError, match="Critical ChromaDB path is not writable"):
        run_startup_checks()


def test_docker_compatibility_compose_file():
    """Verify that docker-compose.yml configuration has valid syntax and structures."""
    compose_path = "docker-compose.yml"
    assert os.path.exists(compose_path)
    
    with open(compose_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for basic docker-compose structures
    assert "services:" in content
    assert "backend:" in content
    assert "frontend:" in content
    assert "healthcheck:" in content
    assert "chroma_data:" in content
