from fastapi import APIRouter, HTTPException, status

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
from backend.workflows.research_workflow import ResearchWorkflow

router = APIRouter()
workflow = ResearchWorkflow()

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
    logger.info(f"Workflow started for topic: '{payload.topic}'")

    try:
        try:
            workflow_state = workflow.run(
                topic=payload.topic,
                style=payload.style,
                depth=payload.depth
            )
            logger.info(f"Workflow completed successfully for topic: '{payload.topic}'")
        except ValueError as e:
            logger.error(f"Workflow execution validation error for topic '{payload.topic}': {e}")
            raise ValueError(f"Failed to generate structured research: {e}")
        except Exception as e:
            logger.error(f"Workflow failed for topic '{payload.topic}': {e}")
            raise

        editor_result = workflow_state.get("final", {})
        review_result = workflow_state.get("review", {})

        if not editor_result or not review_result:
            raise ValueError("Workflow state is missing required 'final' or 'review' fields.")

        final_result = {
            "topic": editor_result["topic"],
            "title": editor_result["title"],
            "final_markdown": editor_result["final_markdown"],
            "review": review_result,
            "changes_applied": editor_result["changes_applied"]
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

