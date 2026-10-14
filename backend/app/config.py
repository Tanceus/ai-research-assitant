"""Configuration settings for the application."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/research_assistant"
    )
    
    # Embedding Model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Vector Store
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    
    # API Settings
    API_TITLE: str = "AI Research Assistant API"
    API_VERSION: str = "1.0.0"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # PDF Processing
    MAX_PDF_SIZE_MB: int = int(os.getenv("MAX_PDF_SIZE_MB", "50"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

