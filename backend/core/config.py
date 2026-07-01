import re
from typing import Any, Dict
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Centralized default constants
DEFAULT_BACKEND_HOST = "0.0.0.0"
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 8501
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_LLM_MODEL = "qwen2.5:7b"
DEFAULT_CHROMA_DB_PATH = "./data/chroma"
DEFAULT_MAX_SEARCH_RESULTS = 5
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_REQUEST_TIMEOUT = 60
API_V1_PATH = "/api/v1"


class Settings(BaseSettings):
    BACKEND_HOST: str = DEFAULT_BACKEND_HOST
    BACKEND_PORT: int = DEFAULT_BACKEND_PORT
    API_V1_STR: str = API_V1_PATH
    FRONTEND_PORT: int = DEFAULT_FRONTEND_PORT
    
    # Ollama / LLM configuration
    OLLAMA_BASE_URL: str = DEFAULT_OLLAMA_URL
    OLLAMA_HOST: str = DEFAULT_OLLAMA_URL
    LLM_MODEL: str = DEFAULT_LLM_MODEL
    DEFAULT_MODEL: str = DEFAULT_LLM_MODEL
    
    CHROMA_DB_PATH: str = DEFAULT_CHROMA_DB_PATH
    MAX_SEARCH_RESULTS: int = DEFAULT_MAX_SEARCH_RESULTS
    LOG_LEVEL: str = DEFAULT_LOG_LEVEL
    REQUEST_TIMEOUT: int = DEFAULT_REQUEST_TIMEOUT

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="before")
    @classmethod
    def populate_fallbacks(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Fallback OLLAMA_HOST to OLLAMA_BASE_URL
            base_url = data.get("OLLAMA_BASE_URL") or DEFAULT_OLLAMA_URL
            if not data.get("OLLAMA_HOST"):
                data["OLLAMA_HOST"] = base_url
            # Fallback DEFAULT_MODEL to LLM_MODEL
            llm_model = data.get("LLM_MODEL") or DEFAULT_LLM_MODEL
            if not data.get("DEFAULT_MODEL"):
                data["DEFAULT_MODEL"] = llm_model
        return data

    @field_validator("BACKEND_PORT", "FRONTEND_PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535. Got: {v}")
        return v

    @field_validator("OLLAMA_BASE_URL", "OLLAMA_HOST")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v or not re.match(r"^https?://[a-zA-Z0-9\.\-_]+(:\d+)?(/.*)?$", v):
            raise ValueError(f"Invalid URL format. Got: {v}")
        return v

    @field_validator("LLM_MODEL", "DEFAULT_MODEL", "CHROMA_DB_PATH")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or blank.")
        return v


settings = Settings()
