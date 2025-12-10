from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://seouser:seopass@postgres:5432/seochecker"
    
    # Gemini API
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.2
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192
    
    # Application
    UPLOAD_DIR: str = "/app/workspace"
    MAX_UPLOAD_SIZE: int = 524288000  # 500MB (upload limit)
    MAX_EXTRACTED_SIZE: int = 524288000  # 500MB (extracted limit)
    CHUNK_SIZE: int = 180
    CHUNK_OVERLAP: int = 20
    
    # Gemini Rate Limiting
    GEMINI_MAX_CONCURRENT: int = 3
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

