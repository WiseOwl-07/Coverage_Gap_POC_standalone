"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "Coverage Gap Detection POC"
    groq_api_key: str
    log_level: str = "INFO"
    
    # LLM Configuration
    llm_model: str = "llama-3.3-70b-versatile"  # Groq's latest model
    llm_temperature: float = 0.3  # Lower for more consistent insurance analysis
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Supports both .env files (local) and Streamlit secrets (cloud deployment).
    """
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            return Settings(
                groq_api_key=st.secrets.get("GROQ_API_KEY", ""),
                app_name=st.secrets.get("APP_NAME", "Coverage Gap Detection POC"),
                log_level=st.secrets.get("LOG_LEVEL", "INFO")
            )
    except (ImportError, FileNotFoundError):
        pass
    
    # Fall back to .env file (for local development)
    return Settings()

