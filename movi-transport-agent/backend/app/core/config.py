from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import json

# Compute database path at module level
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "database" / "transport.db"
DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = DEFAULT_DATABASE_URL

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Movi Transport Agent API"

    # OpenRouter API (for Gemini multimodal processing)
    OPENROUTER_API_KEY: str

    # OpenAI API (for TTS)
    OPENAI_API_KEY: str

    # CORS (can be JSON array or comma-separated string)
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:7860"

    # LangSmith Observability (TICKET #5)
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "movi-transport-agent"

    # Claude Configuration (TICKET #5 - via OpenRouter)
    CLAUDE_MODEL: str = "anthropic/claude-sonnet-4.5"
    CLAUDE_TEMPERATURE: float = 0.3
    CLAUDE_MAX_TOKENS: int = 4000

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins as list."""
        if self.BACKEND_CORS_ORIGINS.startswith('['):
            # JSON array format
            return json.loads(self.BACKEND_CORS_ORIGINS)
        else:
            # Comma-separated format
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(',')]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
