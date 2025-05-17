import os
from typing import List, Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/lexic_db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://lexic.cl",
        "https://lawyers.lexic.cl",
        "https://lexic-lawyers.pages.dev",
        "https://staging-lexic.pages.dev"
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    API_KEY: str = os.getenv("API_KEY")

    # AWS S3
    USE_S3_STORAGE: bool = bool(os.getenv("USE_S3_STORAGE", "false").lower() == "true")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: Optional[str] = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")

    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "storage")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()