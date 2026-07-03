from unittest.mock import MagicMock

import pytest

from backend.agents.writer_agent import WriterAgent
from backend.services.ai_service import AIService


def test_writer_agent_import():
    """Verify WriterAgent can be imported."""
    agent = WriterAgent()
    assert agent is not None


def test_writer_agent_write_report_success():
    """Verify write_report works with a valid JSON response from AI."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": (
            '{\n  "title": "Quantum Computing Future",\n'
            '  "markdown": "# Quantum Computing Future\\n\\n## Introduction\\n'
            '\\nThis is a report."\n}'
        )
    }

    agent = WriterAgent(ai_service_instance=mock_ai_service)
    research_output = {
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
    results = agent.write_report(research_output)

    assert results["topic"] == "Quantum Computing"
    assert results["title"] == "Quantum Computing Future"
    assert (
        results["markdown"]
        == "# Quantum Computing Future\n\n## Introduction\n\nThis is a report."
    )
    mock_ai_service.generate_response.assert_called_once()


def test_writer_agent_clean_markdown_code_blocks():
    """Verify WriterAgent cleans markdown code blocks before parsing JSON."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": (
            '```json\n{\n  "title": "Quantum Computing Future",\n'
            '  "markdown": "# Markdown"\n}\n```'
        )
    }

    agent = WriterAgent(ai_service_instance=mock_ai_service)
    research_output = {
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
    results = agent.write_report(research_output)

    assert results["title"] == "Quantum Computing Future"
    assert results["markdown"] == "# Markdown"


def test_writer_agent_invalid_json_retries_and_raises():
    """Verify write_report retries 3 times and raises error on
    persistent invalid JSON.
    """
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": "Plain text that is not JSON"
    }

    agent = WriterAgent(ai_service_instance=mock_ai_service)
    research_output = {
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

    with pytest.raises(ValueError, match="Failed to generate a valid report JSON"):
        agent.write_report(research_output)

    assert mock_ai_service.generate_response.call_count == 3


def test_writer_agent_missing_required_key():
    """Verify verification raises ValueError when key 'markdown' is missing."""
    mock_ai_service = MagicMock(spec=AIService)
    # Missing 'markdown'
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "title": "Quantum Computing Future"\n}'
    }

    agent = WriterAgent(ai_service_instance=mock_ai_service)
    research_output = {
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

    with pytest.raises(ValueError, match="Key 'markdown' is missing or not a string"):
        agent.write_report(research_output)


def test_writer_agent_invalid_research_inputs():
    """Verify write_report validates its input dictionary."""
    agent = WriterAgent()

    # Non-dictionary input
    with pytest.raises(ValueError, match="Input research_output must be a dictionary"):
        agent.write_report("not a dict")

    # Missing topic
    with pytest.raises(ValueError, match="Input research_output is missing 'topic'"):
        agent.write_report({"research": [{"section": "Intro"}]})

    # Missing research
    with pytest.raises(
        ValueError,
        match="Input research_output must contain a non-empty list of 'research'",
    ):
        agent.write_report({"topic": "Quantum Computing"})

    # Empty research list
    with pytest.raises(
        ValueError,
        match="Input research_output must contain a non-empty list of 'research'",
    ):
        agent.write_report({"topic": "Quantum Computing", "research": []})
