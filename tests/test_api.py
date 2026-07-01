import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.models.ollama_client import OllamaConnectionError, OllamaError

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "running",
        "application": "AI Multi-Agent Research Writer"
    }

def test_health_endpoint():
    with patch("backend.services.ai_service.ai_service.health_check") as mock_health:
        mock_health.return_value = {
            "status": "healthy",
            "connection": "connected",
            "base_url": "http://localhost:11434",
            "default_model": "qwen2.5:7b",
            "model_available": True
        }
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_research_endpoint_success():
    mock_plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    mock_research = {
        "topic": "Quantum Computing",
        "research": [
            {
                "section": "Intro",
                "summary": "This is a summary.",
                "key_points": ["Key 1"],
                "suggested_subtopics": ["Sub 1"]
            }
        ]
    }
    mock_report = {
        "topic": "Quantum Computing",
        "title": "Future of Quantum Computing",
        "markdown": "# Future of Quantum Computing\n\nThis is the markdown content."
    }
    mock_review = {
        "score": 90,
        "strengths": ["Clear intro"],
        "issues": ["Typo"],
        "suggestions": ["Fix typo"],
        "ready_for_editing": True
    }
    with patch("backend.api.routes.planner.create_plan") as mock_create_plan, \
         patch("backend.api.routes.research_agent.conduct_research") as mock_conduct_research, \
         patch("backend.api.routes.writer_agent.write_report") as mock_write_report, \
         patch("backend.api.routes.reviewer_agent.review_report") as mock_review_report:
        
        mock_create_plan.return_value = mock_plan
        mock_conduct_research.return_value = mock_research
        mock_write_report.return_value = mock_report
        mock_review_report.return_value = mock_review
        
        response = client.post(
            "/research",
            json={"topic": "Quantum Computing", "style": "Technical", "depth": "Standard"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Quantum Computing"
        assert data["title"] == "Future of Quantum Computing"
        assert data["markdown"] == "# Future of Quantum Computing\n\nThis is the markdown content."
        assert data["review"] == mock_review

def test_research_endpoint_writer_failure():
    mock_plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    mock_research = {
        "topic": "Quantum Computing",
        "research": [
            {
                "section": "Intro",
                "summary": "Summary text",
                "key_points": [],
                "suggested_subtopics": []
            }
        ]
    }
    with patch("backend.api.routes.planner.create_plan") as mock_create_plan, \
         patch("backend.api.routes.research_agent.conduct_research") as mock_conduct_research, \
         patch("backend.api.routes.writer_agent.write_report") as mock_write_report, \
         patch("backend.api.routes.reviewer_agent.review_report") as mock_review_report:
        
        mock_create_plan.return_value = mock_plan
        mock_conduct_research.return_value = mock_research
        mock_write_report.side_effect = ValueError("Writer failed to generate JSON")
        
        response = client.post(
            "/research",
            json={"topic": "Quantum Computing", "style": "Technical", "depth": "Standard"}
        )
        assert response.status_code == 422
        assert "Failed to generate structured research" in response.json()["detail"]
        mock_review_report.assert_not_called()

def test_research_endpoint_malformed_research_output():
    mock_plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    with patch("backend.api.routes.planner.create_plan") as mock_create_plan, \
         patch("backend.api.routes.research_agent.conduct_research") as mock_conduct_research, \
         patch("backend.api.routes.writer_agent.write_report") as mock_write_report, \
         patch("backend.api.routes.reviewer_agent.review_report") as mock_review_report:
        
        mock_create_plan.return_value = mock_plan
        mock_conduct_research.side_effect = ValueError("Research agent malformed output")
        
        response = client.post(
            "/research",
            json={"topic": "Quantum Computing", "style": "Technical", "depth": "Standard"}
        )
        assert response.status_code == 422
        assert "Failed to generate structured research" in response.json()["detail"]
        mock_write_report.assert_not_called()
        mock_review_report.assert_not_called()

def test_research_endpoint_ollama_offline():
    with patch("backend.api.routes.planner.create_plan") as mock_create_plan, \
         patch("backend.api.routes.research_agent.conduct_research") as mock_conduct_research, \
         patch("backend.api.routes.writer_agent.write_report") as mock_write_report, \
         patch("backend.api.routes.reviewer_agent.review_report") as mock_review_report:
        
        mock_create_plan.side_effect = OllamaConnectionError("Ollama host offline")
        response = client.post(
            "/research",
            json={"topic": "Quantum Computing", "style": "Technical", "depth": "Standard"}
        )
        assert response.status_code == 503
        assert "Ollama offline" in response.json()["detail"]
        mock_conduct_research.assert_not_called()
        mock_write_report.assert_not_called()
        mock_review_report.assert_not_called()
