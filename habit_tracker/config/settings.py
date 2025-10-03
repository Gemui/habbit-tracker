"""Application settings and configuration."""

import os
from typing import Optional


class Settings:
    """Application settings and configuration management."""
    
    # Database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    
    # Application settings
    APP_NAME: str = "Habit Tracker"
    APP_VERSION: str = "1.0.0"
    
    # CLI settings
    DEFAULT_TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # Analytics settings
    DEFAULT_SUMMARY_DAYS: int = 7
    MAX_HABIT_NAME_LENGTH: int = 100
    
    # Data directory
    DATA_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "data"
    )
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Get the database URL, with fallback to default SQLite.
        
        Returns:
            The database URL string
        """
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        # Ensure data directory exists
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        db_path = os.path.join(cls.DATA_DIR, "habits.db")
        return f"sqlite:///{db_path}"
    
    @classmethod
    def is_development(cls) -> bool:
        """
        Check if the application is running in development mode.
        
        Returns:
            True if in development mode
        """
        return os.getenv("ENVIRONMENT", "production").lower() == "development"
    
    @classmethod
    def is_testing(cls) -> bool:
        """
        Check if the application is running in testing mode.
        
        Returns:
            True if in testing mode
        """
        return os.getenv("ENVIRONMENT", "production").lower() == "testing"






