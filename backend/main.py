from dotenv import load_dotenv

# Explicitly load .env file prior to other imports
load_dotenv()

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from backend.api.routes import router as api_router  # noqa: E402
from backend.core.config import settings  # noqa: E402
from backend.core.logger import logger  # noqa: E402
from backend.core.startup_validation import run_startup_checks  # noqa: E402

logger.info("LangGraph initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run startup checks
    run_startup_checks()
    logger.info("FastAPI started")
    yield


# Initialize production-ready FastAPI application
app = FastAPI(
    title="AI Multi-Agent Research Writer Backend",
    description=(
        "Backend API for conducting comprehensive, multi-agent automated research."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

# Enable CORS for frontend and development purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust allowed origins in production as necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the API router on the root to support GET / and GET /health directly
app.include_router(api_router)

# Register the API router under the configured API version prefix
# (e.g. /api/v1) for versioning consistency
if settings.API_V1_STR:
    app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info("FastAPI Backend application successfully initialized.")
