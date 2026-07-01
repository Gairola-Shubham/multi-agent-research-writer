from fastapi import APIRouter, HTTPException, status

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.reviewer_agent import ReviewerAgent
from backend.agents.writer_agent import WriterAgent
from backend.core.logger import logger
from backend.models.ollama_client import (
    OllamaConnectionError,
    OllamaError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)
from backend.schemas.request_models import ResearchRequest
from backend.schemas.response_models import ResearchResponse
from backend.services.ai_service import ai_service

router = APIRouter()
planner = PlannerAgent()
research_agent = ResearchAgent()
writer_agent = WriterAgent()
reviewer_agent = ReviewerAgent()

@router.get("/")
async def root():
    logger.info("Root endpoint called.")
    return {
        "status": "running",
        "application": "AI Multi-Agent Research Writer"
    }

@router.get("/health")
async def health():
    logger.info("Health endpoint called.")
    return ai_service.health_check()

@router.post("/research", response_model=ResearchResponse)
async def research(payload: ResearchRequest):
    logger.info(f"Research request received for topic: '{payload.topic}' (style: '{payload.style}', depth: '{payload.depth}')")
    logger.info(f"Planner execution started for topic: '{payload.topic}'")

    try:
        try:
            plan = planner.create_plan(
                topic=payload.topic,
                style=payload.style,
                depth=payload.depth
            )
            logger.info(f"Planner execution completed successfully for topic: '{payload.topic}'")
        except ValueError as e:
            logger.error(f"Planner validation error for topic '{payload.topic}': {e}")
            raise ValueError(f"Failed to generate plan: {e}")

        logger.info(f"Research execution started for topic: '{payload.topic}'")
        try:
            research_result = research_agent.conduct_research(plan)
            logger.info(f"Research execution completed successfully for topic: '{payload.topic}'")
        except ValueError as e:
            logger.error(f"Research validation error for topic '{payload.topic}': {e}")
            raise ValueError(f"Failed to generate research: {e}")

        logger.info(f"Writer execution started for topic: '{payload.topic}'")
        try:
            report_result = writer_agent.write_report(research_result)
            logger.info(f"Writer execution completed successfully for topic: '{payload.topic}'")
            logger.info(f"Markdown report generated successfully for topic: '{payload.topic}'")
        except ValueError as e:
            logger.error(f"Writer validation error for topic '{payload.topic}': {e}")
            raise ValueError(f"Failed to generate report: {e}")

        logger.info(f"Reviewer execution started for topic: '{payload.topic}'")
        try:
            review_result = reviewer_agent.review_report(report_result)
            logger.info(f"Reviewer execution completed successfully for topic: '{payload.topic}'")
            logger.info(f"Review score: {review_result.get('score')} for topic: '{payload.topic}'")
        except ValueError as e:
            logger.error(f"Review execution failed for topic '{payload.topic}': {e}")
            raise ValueError(f"Failed to review report: {e}")

        final_result = {
            **report_result,
            "review": review_result
        }
        return ResearchResponse(**final_result)
    except ValueError as e:
        logger.error(f"Validation error for topic '{payload.topic}': {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to generate structured research: {str(e)}"
        )
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error for topic '{payload.topic}': {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama offline: {str(e)}"
        )
    except OllamaModelNotFoundError as e:
        logger.error(f"Ollama model not found error for topic '{payload.topic}': {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model not found: {str(e)}"
        )
    except OllamaTimeoutError as e:
        logger.error(f"Ollama request timeout for topic '{payload.topic}': {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Request timeout: {str(e)}"
        )
    except OllamaError as e:
        logger.error(f"Ollama error for topic '{payload.topic}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ollama service error: {str(e)}"
        )
    except Exception as e:
        logger.critical(f"Unhandled error in research endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
