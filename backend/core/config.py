from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import re


class Settings(BaseSettings):
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    FRONTEND_PORT: int = 8501
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_HOST: str = "http://localhost:11434"
    LLM_MODEL: str = "qwen2.5:7b"
    DEFAULT_MODEL: str = "qwen2.5:7b"
    CHROMA_DB_PATH: str = "./data/chroma"
    MAX_SEARCH_RESULTS: int = 5
    LOG_LEVEL: str = "INFO"
    REQUEST_TIMEOUT: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

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
