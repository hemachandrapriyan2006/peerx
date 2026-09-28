"""
PeerX Backend Configuration
Loads settings from environment variables.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Explicitly locate and load backend/.env or root .env
_base_dir = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_base_dir, ".env")
if os.path.exists(_env_path):
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Difficulty thresholds (configurable)
    DIFFICULTY_DECREASE_THRESHOLD: float = 40.0   # Score < 40% → reduce difficulty
    DIFFICULTY_MAINTAIN_LOW: float = 40.0          # 40-70% → keep or guided practice
    DIFFICULTY_MAINTAIN_HIGH: float = 70.0
    DIFFICULTY_MODERATE_INCREASE: float = 70.0     # 70-85% → moderate increase
    DIFFICULTY_HARD_INCREASE: float = 85.0         # > 85% → increase difficulty

    # Mastery score weights
    MASTERY_WEIGHT_ACCURACY: float = 0.40
    MASTERY_WEIGHT_REASONING: float = 0.25
    MASTERY_WEIGHT_RECENT: float = 0.25
    MASTERY_WEIGHT_COVERAGE: float = 0.10

    # Context limits
    MAX_CONVERSATION_HISTORY: int = 10  # Max messages to include in context
    MAX_RECENT_ATTEMPTS: int = 5        # Recent attempts for performance calc

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
