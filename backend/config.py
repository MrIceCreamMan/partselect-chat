from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "PartSelect Chat Assistant"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Deepseek
    DEEPSEEK_API_KEY: str
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # Database
    DATABASE_URL: str

    # Chroma
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3000"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Agent Settings
    MAX_TOOL_ITERATIONS: int = 5
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
