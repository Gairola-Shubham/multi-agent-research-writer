import pytest
import json
from unittest.mock import MagicMock, patch, ANY
from backend.agents.research_agent import ResearchAgent
from backend.services.ai_service import AIService
from backend.search.search_service import SearchService
from backend.memory.memory_service import MemoryService

@pytest.fixture(autouse=True)
def mock_memory_service_class():
    """Automatically mock the MemoryService class globally in all tests in this file."""
    with patch("backend.agents.research_agent.MemoryService") as mock:
        mock_instance = MagicMock(spec=MemoryService)
        mock.return_value = mock_instance
        yield mock_instance

def test_research_agent_import():
    """Verify ResearchAgent can be imported."""
    agent = ResearchAgent()
    assert agent is not None

def test_research_agent_conduct_research_success(mock_memory_service_class):
    """Verify conduct_research works with valid JSON responses from AI, search, and memory."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "This is a summary of Quantum Computing.",\n  "key_points": ["Qubits exist", "Superposition is key"],\n  "suggested_subtopics": ["Entanglement", "Quantum Gates"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = [
        {"title": "Quantum Computing Source", "url": "http://quantum.com", "snippet": "A guide to qubits."}
    ]
    
    mock_memory_service_class.search.return_value = [
        {"id": "doc123", "text": "Historical context on superposition", "metadata": {"topic": "Quantum Computing", "section": "Intro"}, "distance": 0.1}
    ]
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
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
    assert section_data["sources"] == [{"title": "Quantum Computing Source", "url": "http://quantum.com"}]
    
    # Assert search was called
    mock_search_service.search.assert_called_once_with(query="Quantum Computing Intro", max_results=3)
    # Assert memory was searched
    mock_memory_service_class.search.assert_called_once_with(query="Quantum Computing Intro", top_k=3)
    # Assert output was saved to memory
    mock_memory_service_class.add_document.assert_called_once()
    
    # Verify AI generate_response prompt separates search and memory
    prompt = mock_ai_service.generate_response.call_args[1]["prompt"]
    assert "Web Search Results:" in prompt
    assert "Memory Results:" in prompt
    assert "Title: Quantum Computing Source" in prompt
    assert "Memory Text: Historical context on superposition" in prompt

def test_research_agent_search_failure_fallback(mock_memory_service_class):
    """Verify ResearchAgent fallback works when SearchService fails but memory succeeds."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "Summary.",\n  "key_points": ["Point 1"],\n  "suggested_subtopics": ["Sub 1"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.side_effect = Exception("Search connection timed out")
    
    mock_memory_service_class.search.return_value = [
        {"id": "doc1", "text": "Cached superposition data", "metadata": {}, "distance": 0.2}
    ]
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    results = agent.conduct_research(plan)
    
    # Completed successfully despite search failure
    assert results["topic"] == "Quantum Computing"
    assert len(results["research"]) == 1
    assert results["research"][0]["sources"] == []
    
    # AIService was still called with the memory results
    prompt = mock_ai_service.generate_response.call_args[1]["prompt"]
    assert "No web search results available." in prompt
    assert "Cached superposition data" in prompt

def test_research_agent_memory_failure_fallback(mock_memory_service_class):
    """Verify ResearchAgent fallback works when MemoryService search fails but search succeeds."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "Summary.",\n  "key_points": ["Point 1"],\n  "suggested_subtopics": ["Sub 1"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = [{"title": "Web Source", "url": "http://web.com", "snippet": "Web context"}]
    
    mock_memory_service_class.search.side_effect = Exception("ChromaDB read error")
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    results = agent.conduct_research(plan)
    
    assert results["topic"] == "Quantum Computing"
    assert len(results["research"]) == 1
    
    # AIService was called with search results but empty memory results
    prompt = mock_ai_service.generate_response.call_args[1]["prompt"]
    assert "Web context" in prompt
    assert "No memory results available." in prompt

def test_research_agent_both_fail_fallback(mock_memory_service_class):
    """Verify ResearchAgent fallback works when both search and memory fail."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "Summary.",\n  "key_points": ["Point 1"],\n  "suggested_subtopics": ["Sub 1"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.side_effect = Exception("Network down")
    mock_memory_service_class.search.side_effect = Exception("ChromaDB locked")
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    results = agent.conduct_research(plan)
    
    assert results["topic"] == "Quantum Computing"
    assert len(results["research"]) == 1
    
    prompt = mock_ai_service.generate_response.call_args[1]["prompt"]
    assert "No web search results available." in prompt
    assert "No memory results available." in prompt

def test_research_agent_successful_memory_storage(mock_memory_service_class):
    """Verify research results are correctly formatted and saved into memory."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "Synthesis summary.",\n  "key_points": ["Insight 1"],\n  "suggested_subtopics": ["Subtopic 1"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = []
    mock_memory_service_class.search.return_value = []
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    
    agent.conduct_research(plan)
    
    # Verify add_document is called once
    mock_memory_service_class.add_document.assert_called_once()
    args, kwargs = mock_memory_service_class.add_document.call_args
    
    doc_id = kwargs.get("document_id") or args[0]
    doc_text = kwargs.get("text") or args[1]
    doc_meta = kwargs.get("metadata") or args[2]
    
    assert doc_id.startswith("research_")
    assert "Quantum Computing" in doc_text
    assert "Synthesis summary." in doc_text
    assert "Insight 1" in doc_text
    
    assert doc_meta["topic"] == "Quantum Computing"
    assert doc_meta["section"] == "Intro"
    assert doc_meta["summary"] == "Synthesis summary."
    # Lists must be stored as JSON strings
    assert json.loads(doc_meta["key_points"]) == ["Insight 1"]
    assert json.loads(doc_meta["suggested_subtopics"]) == ["Subtopic 1"]
    assert json.loads(doc_meta["sources"]) == []

def test_research_agent_duplicate_document_handling(mock_memory_service_class):
    """Verify that if saving to memory fails (e.g. duplicate ID or database error), the agent does not crash."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "Summary.",\n  "key_points": ["Point 1"],\n  "suggested_subtopics": ["Sub 1"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = []
    mock_memory_service_class.search.return_value = []
    
    # Simulate ValueError for duplicate ID or other ChromaDB storage errors
    mock_memory_service_class.add_document.side_effect = ValueError("Document with ID already exists.")
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    
    # The call must succeed and not raise ValueError
    results = agent.conduct_research(plan)
    assert len(results["research"]) == 1

def test_research_agent_malformed_memory_results(mock_memory_service_class):
    """Verify that if memory results are malformed (e.g., metadata is None/missing), the agent handles it safely."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "summary": "Summary.",\n  "key_points": ["Point 1"],\n  "suggested_subtopics": ["Sub 1"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = []
    
    # Return a search result with None or string instead of dict for metadata
    mock_memory_service_class.search.return_value = [
        {"id": "doc1", "text": "Malformed metadata", "metadata": None, "distance": 0.3}
    ]
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    
    # Must not crash
    results = agent.conduct_research(plan)
    assert len(results["research"]) == 1
    
    prompt = mock_ai_service.generate_response.call_args[1]["prompt"]
    assert "Malformed metadata" in prompt

def test_research_agent_clean_markdown_code_blocks(mock_memory_service_class):
    """Verify ResearchAgent cleans markdown code blocks before parsing."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": '```json\n{\n  "section": "Intro",\n  "summary": "This is a summary.",\n  "key_points": ["Key 1"],\n  "suggested_subtopics": ["Sub 1"]\n}\n```'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = []
    mock_memory_service_class.search.return_value = []
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    results = agent.conduct_research(plan)
    
    assert results["research"][0]["section"] == "Intro"
    assert results["research"][0]["summary"] == "This is a summary."
    assert results["research"][0]["sources"] == []

def test_research_agent_invalid_json_retries_and_raises(mock_memory_service_class):
    """Verify research_section retries 3 times and raises error on persistent invalid JSON."""
    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate_response.return_value = {
        "response": "Plain text that is not JSON"
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = []
    mock_memory_service_class.search.return_value = []
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
    plan = {
        "topic": "Quantum Computing",
        "sections": ["Intro"]
    }
    
    with pytest.raises(ValueError, match="Failed to generate valid research JSON for section 'Intro'"):
        agent.conduct_research(plan)
        
    assert mock_ai_service.generate_response.call_count == 3

def test_research_agent_missing_required_key(mock_memory_service_class):
    """Verify verification raises ValueError when key 'summary' is missing."""
    mock_ai_service = MagicMock(spec=AIService)
    # Missing 'summary'
    mock_ai_service.generate_response.return_value = {
        "response": '{\n  "section": "Intro",\n  "key_points": ["Key 1"],\n  "suggested_subtopics": ["Sub 1"]\n}'
    }
    mock_search_service = MagicMock(spec=SearchService)
    mock_search_service.search.return_value = []
    mock_memory_service_class.search.return_value = []
    
    agent = ResearchAgent(
        ai_service_instance=mock_ai_service,
        search_service_instance=mock_search_service,
        memory_service_instance=mock_memory_service_class
    )
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
