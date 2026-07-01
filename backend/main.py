from dotenv import load_dotenv

# Explicitly load .env file prior to other imports
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.core.config import settings
from backend.core.logger import logger

# Initialize production-ready FastAPI application
app = FastAPI(
    title="AI Multi-Agent Research Writer Backend",
    description="Backend API for conducting comprehensive, multi-agent automated research.",
    version="0.1.0"
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

# Register the API router under the configured API version prefix (e.g. /api/v1) for versioning consistency
if settings.API_V1_STR:
    app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info("FastAPI Backend application successfully initialized.")
