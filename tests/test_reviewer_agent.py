from unittest.mock import MagicMock

import pytest

from backend.agents.reviewer_agent import ReviewerAgent
from backend.services.ai_service import AIService


def test_reviewer_agent_import():
    """Verify ReviewerAgent can be imported."""
    agent = ReviewerAgent()
    assert agent is not None


def test_reviewer_agent_review_success():
    """Verify review_report works with a valid JSON response from AI."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": (
            '{\n  "score": 90,\n'
            '  "strengths": ["Strong intro"],\n'
            '  "issues": ["Minor typo"],\n'
            '  "suggestions": ["Fix typo"],\n'
            '  "ready_for_editing": true\n}'
        )
    }

    agent = ReviewerAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview\n\nThis is a report.",
    }
    results = agent.review_report(report_output)

    assert results["score"] == 90
    assert results["strengths"] == ["Strong intro"]
    assert results["issues"] == ["Minor typo"]
    assert results["suggestions"] == ["Fix typo"]
    assert results["ready_for_editing"] is True
    mock_ai_service.generate_response.assert_called_once()


def test_reviewer_agent_clean_markdown_code_blocks():
    """Verify ReviewerAgent cleans markdown code blocks before parsing JSON."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": (
            '```json\n{\n  "score": 90,\n'
            '  "strengths": [],\n'
            '  "issues": [],\n'
            '  "suggestions": [],\n'
            '  "ready_for_editing": true\n}\n```'
        )
    }

    agent = ReviewerAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview\n\nThis is a report.",
    }
    results = agent.review_report(report_output)
    assert results["score"] == 90


def test_reviewer_agent_invalid_json_retries_and_raises():
    """Verify review_report retries 3 times and raises error on
    persistent invalid JSON.
    """
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": "Plain text that is not JSON"
    }

    agent = ReviewerAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview",
    }

    with pytest.raises(ValueError, match="Failed to generate a valid review JSON"):
        agent.review_report(report_output)

    assert mock_ai_service.generate_response.call_count == 3


def test_reviewer_agent_score_out_of_bounds():
    """Verify validation raises ValueError when score is out of bounds (0-100)."""
    mock_ai_service = MagicMock(spec=AIService)

    # Score 105 (out of bounds)
    mock_ai_service.generate_response.return_value = {
        "response": (
            '{\n  "score": 105,\n'
            '  "strengths": [],\n'
            '  "issues": [],\n'
            '  "suggestions": [],\n'
            '  "ready_for_editing": true\n}'
        )
    }
    agent = ReviewerAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview",
    }
    with pytest.raises(ValueError, match="Key 'score' must be between 0 and 100"):
        agent.review_report(report_output)

    # Score -5 (out of bounds)
    mock_ai_service.generate_response.return_value = {
        "response": (
            '{\n  "score": -5,\n'
            '  "strengths": [],\n'
            '  "issues": [],\n'
            '  "suggestions": [],\n'
            '  "ready_for_editing": true\n}'
        )
    }
    with pytest.raises(ValueError, match="Key 'score' must be between 0 and 100"):
        agent.review_report(report_output)


def test_reviewer_agent_missing_key():
    """Verify validation raises ValueError when a key is missing."""
    mock_ai_service = MagicMock(spec=AIService)

    # Missing strengths
    mock_ai_service.generate_response.return_value = {
        "response": (
            '{\n  "score": 80,\n'
            '  "issues": [],\n'
            '  "suggestions": [],\n'
            '  "ready_for_editing": true\n}'
        )
    }
    agent = ReviewerAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview",
    }
    with pytest.raises(ValueError, match="Missing required key 'strengths'"):
        agent.review_report(report_output)


def test_reviewer_agent_invalid_report_inputs():
    """Verify review_report validates its input dictionary."""
    agent = ReviewerAgent()

    # Non-dictionary input
    with pytest.raises(ValueError, match="Input report_output must be a dictionary"):
        agent.review_report("not a dict")

    # Missing topic
    with pytest.raises(ValueError, match="Input report_output is missing 'topic'"):
        agent.review_report({"title": "A Title", "markdown": "Some md"})

    # Missing title
    with pytest.raises(ValueError, match="Input report_output is missing 'title'"):
        agent.review_report({"topic": "Quantum Computing", "markdown": "Some md"})

    # Missing markdown
    with pytest.raises(ValueError, match="Input report_output is missing 'markdown'"):
        agent.review_report({"topic": "Quantum Computing", "title": "A Title"})
