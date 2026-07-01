import pytest
from unittest.mock import MagicMock
from backend.agents.research_agent import ResearchAgent
from backend.services.ai_service import AIService

def test_research_agent_import():
    """Verify ResearchAgent can be imported."""
    agent = ResearchAgent()
    assert agent is not None

def test_research_agent_conduct_research_success():
    """Verify conduct_research works with a valid JSON response from AI."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "This is a summary of Quantum Computing.",\n  "key_points": ["Qubits exist", "Superposition is key"],\n  "suggested_subtopics": ["Entanglement", "Quantum Gates"]\n}'
    }
    
    agent = ResearchAgent(ai_service_instance=mock_ai_service)
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    results = agent.conduct_research(plan)
    
    assert results["topic"] == "Quantum Computing"
    assert len(results["research"]) == 1
    
    section_data = results["research"][0]
    assert section_data["section"] == "Intro"
    assert section_data["summary"] == "This is a summary of Quantum Computing."
    assert section_data["key_points"] == ["Qubits exist", "Superposition is key"]
    assert section_data["suggested_subtopics"] == ["Entanglement", "Quantum Gates"]
    
    mock_ai_service.generate_response.assert_called_once()

def test_research_agent_clean_markdown_code_blocks():
    """Verify ResearchAgent cleans markdown code blocks before parsing."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '```json\n{\n  "section": "Intro",\n  "summary": "This is a summary.",\n  "key_points": ["Key 1"],\n  "suggested_subtopics": ["Sub 1"]\n}\n```'
    }
    
    agent = ResearchAgent(ai_service_instance=mock_ai_service)
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    results = agent.conduct_research(plan)
    
    assert results["research"][0]["section"] == "Intro"
    assert results["research"][0]["summary"] == "This is a summary."

def test_research_agent_invalid_json_retries_and_raises():
    """Verify research_section retries 3 times and raises error on persistent invalid JSON."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": "Plain text that is not JSON"
    }
    
    agent = ResearchAgent(ai_service_instance=mock_ai_service)
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    
    with pytest.raises(ValueError, match="Failed to generate valid research JSON for section 'Intro'"):
        agent.conduct_research(plan)
        
    assert mock_ai_service.generate_response.call_count == 3

def test_research_agent_missing_required_key():
    """Verify verification raises ValueError when key 'summary' is missing."""
    mock_ai_service = MagicMock(spec=AIService)
    # Missing 'summary'
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "key_points": ["Key 1"],\n  "suggested_subtopics": ["Sub 1"]\n}'
    }
    
    agent = ResearchAgent(ai_service_instance=mock_ai_service)
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    
    with pytest.raises(ValueError, match="Key 'summary' is missing or not a string"):
        agent.conduct_research(plan)

def test_research_agent_invalid_plan_inputs():
    """Verify conduct_research validates its input plan."""
    agent = ResearchAgent()
    
    # Non-dictionary plan
    with pytest.raises(ValueError, match="Input plan must be a dictionary"):
        agent.conduct_research("not a dict")
        
    # Missing topic
    with pytest.raises(ValueError, match="Input plan is missing 'topic'"):
        agent.conduct_research({"sections": ["Intro"]})
        
    # Missing sections
    with pytest.raises(ValueError, match="Input plan must contain a non-empty list of 'sections'"):
        agent.conduct_research({"topic": "Quantum Computing"})
        
    # Empty sections list
    with pytest.raises(ValueError, match="Input plan must contain a non-empty list of 'sections'"):
        agent.conduct_research({"topic": "Quantum Computing", "sections": []})
