import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Aura - Intelligent Document Query System"
    app_version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    
    # Security
    bearer_token: str = Field(..., env="BEARER_TOKEN")
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    
    # Google Gemini API
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    
    # Pinecone Configuration
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(default="gcp-starter", env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="aura-documents", env="PINECONE_INDEX_NAME")
    
    # PostgreSQL Configuration
    postgres_server: str = Field(default="localhost", env="POSTGRES_SERVER")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="aura_db", env="POSTGRES_DB")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Document Processing
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()