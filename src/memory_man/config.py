"""Configuration settings for Memory-Man."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MEMORY_MAN_",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Database settings
    # Use absolute path for centralized database storage
    # The actual database is in the repository, with a symlink from .claude
    database_url: str = "sqlite+aiosqlite:////home/beano/.claude/memory_man.db"

    # Storage paths
    data_dir: Path = Path("/home/beano/.claude/memory_man_data")
    
    # Memory settings
    max_memory_size: int = 10000  # Max characters per memory
    default_project: str = "default"
    
    # Search settings
    search_limit: int = 20
    
    # Development settings
    debug: bool = False
    log_level: str = "INFO"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()