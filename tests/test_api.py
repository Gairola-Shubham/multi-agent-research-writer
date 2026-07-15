from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.ollama_client import OllamaConnectionError

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "running",
        "application": "AI Multi-Agent Research Writer",
    }


def test_health_endpoint():
    with patch("backend.services.ai_service.ai_service.health_check") as mock_health:
        mock_health.return_value = {
            "status": "healthy",
            "connection": "connected",
            "base_url": "http://localhost:11434",
            "default_model": "phi3:latest",
            "model_available": True,
        }
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_research_endpoint_success():
    mock_plan = {"topic": "Quantum Computing", "sections": ["Intro"]}
    mock_research = {
        "topic": "Quantum Computing",
        "research": [
            {
                "section": "Intro",
                "summary": "This is a summary.",
                "key_points": ["Key 1"],
                "suggested_subtopics": ["Sub 1"],
            }
        ],
    }
    mock_report = {
        "topic": "Quantum Computing",
        "title": "Future of Quantum Computing",
        "markdown": "# Future of Quantum Computing\n\nThis is the markdown content.",
    }
    mock_review = {
        "score": 90,
        "strengths": ["Clear intro"],
        "issues": ["Typo"],
        "suggestions": ["Fix typo"],
        "ready_for_editing": True,
    }
    mock_editor = {
        "topic": "Quantum Computing",
        "title": "Future of Quantum Computing Refined",
        "final_markdown": (
            "# Future of Quantum Computing Refined\n\n"
            "This is the refined markdown content."
        ),
        "changes_applied": ["Fixed grammar", "Polished title"],
    }

    with patch("backend.api.routes.workflow.run") as mock_run:
        mock_run.return_value = {
            "topic": "Quantum Computing",
            "style": "Technical",
            "depth": "Standard",
            "plan": mock_plan,
            "research": mock_research,
            "draft": mock_report,
            "review": mock_review,
            "final": mock_editor,
        }

        response = client.post(
            "/research",
            json={
                "topic": "Quantum Computing",
                "style": "Technical",
                "depth": "Standard",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Quantum Computing"
        assert data["title"] == "Future of Quantum Computing Refined"
        assert data["final_markdown"] == (
            "# Future of Quantum Computing Refined\n\n"
            "This is the refined markdown content."
        )
        assert data["review"] == mock_review
        assert data["changes_applied"] == ["Fixed grammar", "Polished title"]
        mock_run.assert_called_once_with(
            topic="Quantum Computing", style="Technical", depth="Standard"
        )


def test_research_endpoint_writer_failure():
    with patch("backend.api.routes.workflow.run") as mock_run:
        mock_run.side_effect = ValueError(
            "Failed to generate report JSON: Writer failed"
        )

        response = client.post(
            "/research",
            json={
                "topic": "Quantum Computing",
                "style": "Technical",
                "depth": "Standard",
            },
        )
        assert response.status_code == 422
        assert "Failed to generate structured research" in response.json()["detail"]


def test_research_endpoint_malformed_research_output():
    with patch("backend.api.routes.workflow.run") as mock_run:
        mock_run.side_effect = ValueError(
            "Failed to generate research JSON: Research agent malformed output"
        )

        response = client.post(
            "/research",
            json={
                "topic": "Quantum Computing",
                "style": "Technical",
                "depth": "Standard",
            },
        )
        assert response.status_code == 422
        assert "Failed to generate structured research" in response.json()["detail"]


def test_research_endpoint_malformed_reviewer_output():
    with patch("backend.api.routes.workflow.run") as mock_run:
        mock_run.side_effect = ValueError(
            "Failed to generate review JSON: Reviewer failed"
        )

        response = client.post(
            "/research",
            json={
                "topic": "Quantum Computing",
                "style": "Technical",
                "depth": "Standard",
            },
        )
        assert response.status_code == 422
        assert "Failed to generate structured research" in response.json()["detail"]


def test_research_endpoint_editor_failure():
    with patch("backend.api.routes.workflow.run") as mock_run:
        mock_run.side_effect = ValueError(
            "Failed to generate editor JSON: Editor failed"
        )

        response = client.post(
            "/research",
            json={
                "topic": "Quantum Computing",
                "style": "Technical",
                "depth": "Standard",
            },
        )
        assert response.status_code == 422
        assert "Failed to generate structured research" in response.json()["detail"]


def test_research_endpoint_ollama_offline():
    with patch("backend.api.routes.workflow.run") as mock_run:
        mock_run.side_effect = OllamaConnectionError("Ollama host offline")

        response = client.post(
            "/research",
            json={
                "topic": "Quantum Computing",
                "style": "Technical",
                "depth": "Standard",
            },
        )
        assert response.status_code == 503
        assert "Ollama offline" in response.json()["detail"]
