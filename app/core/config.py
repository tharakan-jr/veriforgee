from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "VeriForge"
    VERSION: str = "0.1.0"
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "mock", "openai", etc.
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    
    # Artefact settings
    MAX_ARTEFACT_LENGTH: int = 100_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
