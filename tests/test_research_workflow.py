import pytest
from unittest.mock import MagicMock, patch
from backend.workflows.research_workflow import ResearchWorkflow, run

def test_research_workflow_success():
    """Verify that the workflow executes successfully in the correct order with proper state updates."""
    mock_planner = MagicMock()
    mock_planner.create_plan.return_value = {"topic": "Test Topic", "sections": ["Intro"], "execution_order": ["Intro"]}
    
    mock_research = MagicMock()
    mock_research.conduct_research.return_value = {"topic": "Test Topic", "research": [{"section": "Intro", "summary": "Info"}]}
    
    mock_writer = MagicMock()
    mock_writer.write_report.return_value = {"topic": "Test Topic", "title": "Test Title", "markdown": "# Test Title"}
    
    mock_reviewer = MagicMock()
    mock_reviewer.review_report.return_value = {"score": 90, "strengths": ["Clear"], "issues": [], "suggestions": [], "ready_for_editing": True}
    
    mock_editor = MagicMock()
    mock_editor.edit_report.return_value = {
        "topic": "Test Topic",
        "title": "Test Title",
        "final_markdown": "# Test Title (Edited)",
        "changes_applied": ["Polished draft"]
    }
    
    # Trace the order of calls
    call_order = []
    
    def planner_side_effect(*args, **kwargs):
        call_order.append("PlannerAgent")
        return mock_planner.create_plan.return_value
        
    def research_side_effect(*args, **kwargs):
        call_order.append("ResearchAgent")
        return mock_research.conduct_research.return_value
        
    def writer_side_effect(*args, **kwargs):
        call_order.append("WriterAgent")
        return mock_writer.write_report.return_value
        
    def reviewer_side_effect(*args, **kwargs):
        call_order.append("ReviewerAgent")
        return mock_reviewer.review_report.return_value
        
    def editor_side_effect(*args, **kwargs):
        call_order.append("EditorAgent")
        return mock_editor.edit_report.return_value

    mock_planner.create_plan.side_effect = planner_side_effect
    mock_research.conduct_research.side_effect = research_side_effect
    mock_writer.write_report.side_effect = writer_side_effect
    mock_reviewer.review_report.side_effect = reviewer_side_effect
    mock_editor.edit_report.side_effect = editor_side_effect

    # Inject mock agents into workflow
    workflow = ResearchWorkflow(
        planner=mock_planner,
        research_agent=mock_research,
        writer=mock_writer,
        reviewer=mock_reviewer,
        editor=mock_editor
    )
    
    # Run workflow
    final_state = workflow.run(topic="Test Topic", style="Academic", depth="Brief")
    
    # Verify execution order
    assert call_order == ["PlannerAgent", "ResearchAgent", "WriterAgent", "ReviewerAgent", "EditorAgent"]
    
    # Verify state updates
    assert final_state["topic"] == "Test Topic"
    assert final_state["style"] == "Academic"
    assert final_state["depth"] == "Brief"
    assert final_state["plan"] == mock_planner.create_plan.return_value
    assert final_state["research"] == mock_research.conduct_research.return_value
    assert final_state["draft"] == mock_writer.write_report.return_value
    assert final_state["review"] == mock_reviewer.review_report.return_value
    assert final_state["final"] == mock_editor.edit_report.return_value

def test_research_workflow_node_failure():
    """Verify that if a node raises an exception, the workflow fails and aborts."""
    mock_planner = MagicMock()
    mock_planner.create_plan.side_effect = ValueError("Failed to create plan")
    
    mock_research = MagicMock()
    
    workflow = ResearchWorkflow(
        planner=mock_planner,
        research_agent=mock_research
    )
    
    with pytest.raises(ValueError, match="Failed to create plan"):
        workflow.run(topic="Test Topic", style="Academic", depth="Brief")
        
    # Verify research agent was never called
    mock_research.conduct_research.assert_not_called()

def test_research_workflow_public_run():
    """Verify that the public run module-level method runs the workflow."""
    with patch("backend.workflows.research_workflow.ResearchWorkflow") as mock_workflow_class:
        mock_instance = MagicMock()
        mock_workflow_class.return_value = mock_instance
        mock_instance.run.return_value = {"final": {"data": "yes"}}
        
        result = run(topic="Test Topic", style="Academic", depth="Brief")
        
        mock_workflow_class.assert_called_once()
        mock_instance.run.assert_called_once_with("Test Topic", "Academic", "Brief")
        assert result == {"final": {"data": "yes"}}

@patch("backend.services.ai_service.ai_service.generate_response")
def test_workflow_agent_retry_success(mock_ai_generate):
    """Verify that the agent's internal retry mechanism works within workflow execution."""
    # First two generate_response calls fail, third succeeds
    mock_ai_generate.side_effect = [
        ValueError("Connection lost"),
        ValueError("Timeout"),
        {"response": '{"topic": "Quantum", "difficulty": "Easy", "estimated_sources": 5, "sections": ["Intro"], "execution_order": ["Intro"]}'}
    ]
    
    # Mock remaining pipeline agents
    mock_research = MagicMock()
    mock_research.conduct_research.return_value = {"topic": "Quantum", "research": []}
    mock_writer = MagicMock()
    mock_writer.write_report.return_value = {"topic": "Quantum", "title": "Title", "markdown": "# Title"}
    mock_reviewer = MagicMock()
    mock_reviewer.review_report.return_value = {"score": 90, "strengths": [], "issues": [], "suggestions": [], "ready_for_editing": True}
    mock_editor = MagicMock()
    mock_editor.edit_report.return_value = {"topic": "Quantum", "title": "Title", "final_markdown": "# Title", "changes_applied": []}

    workflow = ResearchWorkflow(
        research_agent=mock_research,
        writer=mock_writer,
        reviewer=mock_reviewer,
        editor=mock_editor
    )
    
    # Run the workflow
    final_state = workflow.run(topic="Quantum", style="Academic", depth="Brief")
    
    # Verify generate_response was called 3 times due to 2 retries
    assert mock_ai_generate.call_count == 3
    assert final_state["plan"]["topic"] == "Quantum"
