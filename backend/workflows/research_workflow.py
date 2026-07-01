import logging
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.writer_agent import WriterAgent
from backend.agents.reviewer_agent import ReviewerAgent
from backend.agents.editor_agent import EditorAgent
from backend.core.logger import logger

class ResearchWorkflowState(TypedDict):
    topic: str
    style: str
    depth: str
    plan: Dict[str, Any]
    research: Dict[str, Any]
    draft: Dict[str, Any]
    review: Dict[str, Any]
    final: Dict[str, Any]

class ResearchWorkflow:
    def __init__(
        self,
        planner: Any = None,
        research_agent: Any = None,
        writer: Any = None,
        reviewer: Any = None,
        editor: Any = None
    ):
        self.planner = planner or PlannerAgent()
        self.research_agent = research_agent or ResearchAgent()
        self.writer = writer or WriterAgent()
        self.reviewer = reviewer or ReviewerAgent()
        self.editor = editor or EditorAgent()
        self.graph = self._build_graph()

    def PlannerNode(self, state: ResearchWorkflowState) -> Dict[str, Any]:
        logger.info("Node entered: PlannerNode")
        try:
            plan = self.planner.create_plan(
                topic=state["topic"],
                style=state["style"],
                depth=state["depth"]
            )
            logger.info("Node completed: PlannerNode")
            return {"plan": plan}
        except Exception as e:
            logger.error(f"Node PlannerNode failed: {e}")
            raise

    def ResearchNode(self, state: ResearchWorkflowState) -> Dict[str, Any]:
        logger.info("Node entered: ResearchNode")
        try:
            research = self.research_agent.conduct_research(state["plan"])
            logger.info("Node completed: ResearchNode")
            return {"research": research}
        except Exception as e:
            logger.error(f"Node ResearchNode failed: {e}")
            raise

    def WriterNode(self, state: ResearchWorkflowState) -> Dict[str, Any]:
        logger.info("Node entered: WriterNode")
        try:
            draft = self.writer.write_report(state["research"])
            logger.info("Node completed: WriterNode")
            return {"draft": draft}
        except Exception as e:
            logger.error(f"Node WriterNode failed: {e}")
            raise

    def ReviewerNode(self, state: ResearchWorkflowState) -> Dict[str, Any]:
        logger.info("Node entered: ReviewerNode")
        try:
            review = self.reviewer.review_report(state["draft"])
            logger.info("Node completed: ReviewerNode")
            return {"review": review}
        except Exception as e:
            logger.error(f"Node ReviewerNode failed: {e}")
            raise

    def EditorNode(self, state: ResearchWorkflowState) -> Dict[str, Any]:
        logger.info("Node entered: EditorNode")
        try:
            final = self.editor.edit_report(state["draft"], state["review"])
            logger.info("Node completed: EditorNode")
            return {"final": final}
        except Exception as e:
            logger.error(f"Node EditorNode failed: {e}")
            raise

    def _build_graph(self):
        builder = StateGraph(ResearchWorkflowState)
        
        # Add nodes
        builder.add_node("PlannerNode", self.PlannerNode)
        builder.add_node("ResearchNode", self.ResearchNode)
        builder.add_node("WriterNode", self.WriterNode)
        builder.add_node("ReviewerNode", self.ReviewerNode)
        builder.add_node("EditorNode", self.EditorNode)
        
        # Connect nodes in order: START -> Planner -> Research -> Writer -> Reviewer -> Editor -> END
        builder.add_edge(START, "PlannerNode")
        builder.add_edge("PlannerNode", "ResearchNode")
        builder.add_edge("ResearchNode", "WriterNode")
        builder.add_edge("WriterNode", "ReviewerNode")
        builder.add_edge("ReviewerNode", "EditorNode")
        builder.add_edge("EditorNode", END)
        
        return builder.compile()

    def run(self, topic: str, style: str, depth: str) -> Dict[str, Any]:
        logger.info(f"Workflow started for topic='{topic}', style='{style}', depth='{depth}'")
        initial_state: ResearchWorkflowState = {
            "topic": topic,
            "style": style,
            "depth": depth,
            "plan": {},
            "research": {},
            "draft": {},
            "review": {},
            "final": {}
        }
        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("Workflow completed successfully")
            return final_state
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise

def run(topic: str, style: str, depth: str) -> Dict[str, Any]:
    """
    Public module-level run function that executes the LangGraph research workflow.
    """
    workflow = ResearchWorkflow()
    return workflow.run(topic, style, depth)
