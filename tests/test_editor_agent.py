import pytest
from unittest.mock import MagicMock
from backend.agents.editor_agent import EditorAgent
from backend.services.ai_service import AIService

def test_editor_agent_import():
    """Verify EditorAgent can be imported."""
    agent = EditorAgent()
    assert agent is not None

def test_editor_agent_edit_success():
    """Verify edit_report works with valid JSON from AI."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "title": "Quantum Computing Future",\n  "final_markdown": "# Quantum Computing Future\\n\\nThis is refined.",\n  "changes_applied": ["Fixed grammar in section 1", "Addressed review suggestions"]\n}'
    }

    agent = EditorAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview\n\nThis is a report."
    }
    review_output = {
        "score": 80,
        "strengths": ["Clear intro"],
        "issues": ["Typo in title"],
        "suggestions": ["Make title compelling"],
        "ready_for_editing": True
    }

    results = agent.edit_report(report_output, review_output)

    assert results["topic"] == "Quantum Computing"
    assert results["title"] == "Quantum Computing Future"
    assert results["final_markdown"] == "# Quantum Computing Future\n\nThis is refined."
    assert results["changes_applied"] == ["Fixed grammar in section 1", "Addressed review suggestions"]
    mock_ai_service.generate_response.assert_called_once()

def test_editor_agent_clean_markdown_code_blocks():
    """Verify EditorAgent cleans markdown code blocks before parsing JSON."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '```json\n{\n  "title": "Quantum Computing",\n  "final_markdown": "# Preserved Markdown",\n  "changes_applied": ["Change 1"]\n}\n```'
    }

    agent = EditorAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview"
    }
    review_output = {
        "score": 80,
        "strengths": [],
        "issues": [],
        "suggestions": [],
        "ready_for_editing": True
    }

    results = agent.edit_report(report_output, review_output)
    assert results["final_markdown"] == "# Preserved Markdown"
    assert results["changes_applied"] == ["Change 1"]

def test_editor_agent_invalid_json_retries_and_raises():
    """Verify edit_report retries 3 times and raises error on persistent invalid JSON."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": "Plain text that is not JSON at all"
    }

    agent = EditorAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview"
    }
    review_output = {
        "score": 80,
        "strengths": [],
        "issues": [],
        "suggestions": [],
        "ready_for_editing": True
    }

    with pytest.raises(ValueError, match="Failed to generate a valid editor JSON"):
        agent.edit_report(report_output, review_output)

    assert mock_ai_service.generate_response.call_count == 3

def test_editor_agent_missing_required_key():
    """Verify validation raises ValueError when key 'final_markdown' is missing."""
    mock_ai_service = MagicMock(spec=AIService)
    # Missing 'final_markdown'
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "title": "Quantum Computing Future",\n  "changes_applied": ["Change 1"]\n}'
    }

    agent = EditorAgent(ai_service_instance=mock_ai_service)
    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview"
    }
    review_output = {
        "score": 80,
        "strengths": [],
        "issues": [],
        "suggestions": [],
        "ready_for_editing": True
    }

    with pytest.raises(ValueError, match="Key 'final_markdown' is missing or not a string"):
        agent.edit_report(report_output, review_output)

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
