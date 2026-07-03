from unittest.mock import MagicMock

import pytest

from backend.agents.planner_agent import PlannerAgent
from backend.services.ai_service import AIService


def test_planner_agent_import():
    """Verify PlannerAgent can be imported."""
    agent = PlannerAgent()
    assert agent is not None


def test_planner_agent_create_plan_success():
    """Verify create_plan works with a valid JSON response from AI."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": (
            "{\n"
            '  "topic": "Quantum Computing",\n'
            '  "difficulty": "Hard",\n'
            '  "estimated_sources": 8,\n'
            '  "sections": ["Intro", "Qubits", "Algorithms", "Future"],\n'
            '  "execution_order": ["Intro", "Qubits", "Algorithms", '
            '"Future"]\n'
            "}"
        )
    }

    agent = PlannerAgent(ai_service_instance=mock_ai_service)
    plan = agent.create_plan(
        topic="Quantum Computing", style="Technical", depth="Standard"
    )

    assert plan["topic"] == "Quantum Computing"
    assert plan["difficulty"] == "Hard"
    assert plan["estimated_sources"] == 8
    assert plan["sections"] == ["Intro", "Qubits", "Algorithms", "Future"]
    assert plan["execution_order"] == ["Intro", "Qubits", "Algorithms", "Future"]

    # Verify mock was called
    mock_ai_service.generate_response.assert_called_once()


def test_planner_agent_clean_markdown_code_blocks():
    """Verify create_plan can parse a response wrapped in markdown code blocks."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": (
            "```json\n"
            "{\n"
            '  "topic": "Quantum Computing",\n'
            '  "difficulty": "Hard",\n'
            '  "estimated_sources": 8,\n'
            '  "sections": ["Intro"],\n'
            '  "execution_order": ["Intro"]\n'
            "}\n"
            "```"
        )
    }

    agent = PlannerAgent(ai_service_instance=mock_ai_service)
    plan = agent.create_plan(
        topic="Quantum Computing", style="Technical", depth="Standard"
    )
    assert plan["topic"] == "Quantum Computing"
    assert plan["sections"] == ["Intro"]


def test_planner_agent_invalid_json_retries_and_raises():
    """Verify create_plan retries and raises error on persistent invalid JSON."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": "This is not JSON text at all"
    }

    agent = PlannerAgent(ai_service_instance=mock_ai_service)
    with pytest.raises(
        ValueError, match="Failed to generate a valid research plan JSON"
    ):
        agent.create_plan(
            topic="Quantum Computing", style="Technical", depth="Standard"
        )

    # Should have retried 3 times
    assert mock_ai_service.generate_response.call_count == 3


def test_planner_agent_missing_keys_fallback_or_raises():
    """Verify validation handles missing required keys properly."""
    mock_ai_service = MagicMock(spec=AIService)
    # Missing execution_order
    mock_ai_service.generate_response.return_value = {
        "response": (
            "{\n"
            '  "topic": "Quantum Computing",\n'
            '  "difficulty": "Hard",\n'
            '  "estimated_sources": 8,\n'
            '  "sections": ["Intro"]\n'
            "}"
        )
    }

    agent = PlannerAgent(ai_service_instance=mock_ai_service)
    with pytest.raises(ValueError, match="Missing required key 'execution_order'"):
        agent.create_plan(
            topic="Quantum Computing", style="Technical", depth="Standard"
        )
