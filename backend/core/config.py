from pydantic_settings import BaseSettings, SettingsConfigDict


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

settings = Settings()
