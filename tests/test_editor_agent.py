from unittest.mock import MagicMock

import pytest

from backend.agents.editor_agent import EditorAgent
from backend.services.ai_service import AIService


def test_editor_agent_import():
    """Verify EditorAgent can be imported."""
    agent = EditorAgent()
    assert agent is not None


def test_editor_agent_edit_bypassed():
    """Verify edit_report bypasses LLM call and returns original markdown."""
    mock_ai_service = MagicMock(spec=AIService)
    agent = EditorAgent(ai_service_instance=mock_ai_service)

    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview\n\nThis is a report.",
    }
    review_output = {
        "score": 80,
        "strengths": ["Clear intro"],
        "issues": ["Typo in title"],
        "suggestions": ["Make title compelling"],
        "ready_for_editing": True,
    }

    results = agent.edit_report(report_output, review_output)

    assert results["topic"] == "Quantum Computing"
    assert results["title"] == "Quantum Computing Overview"
    assert (
        results["final_markdown"] == "# Quantum Computing Overview\n\nThis is a report."
    )
    assert results["changes_applied"] == [
        "Editor bypassed for performance optimization."
    ]
    mock_ai_service.generate_response.assert_not_called()


def test_editor_agent_invalid_inputs():
    """Verify edit_report validates its input structures."""
    agent = EditorAgent()

    # Non-dictionary report_output
    with pytest.raises(ValueError, match="Input report_output must be a dictionary"):
        agent.edit_report("not a dict", {})

    # Non-dictionary review_output
    with pytest.raises(ValueError, match="Input review_output must be a dictionary"):
        agent.edit_report({}, "not a dict")

    # Missing topic
    with pytest.raises(ValueError, match="Input report_output is missing 'topic'"):
        agent.edit_report({"title": "Title", "markdown": "md"}, {})

    # Missing title
    with pytest.raises(ValueError, match="Input report_output is missing 'title'"):
        agent.edit_report({"topic": "Topic", "markdown": "md"}, {})

    # Missing markdown
    with pytest.raises(ValueError, match="Input report_output is missing 'markdown'"):
        agent.edit_report({"topic": "Topic", "title": "Title"}, {})
