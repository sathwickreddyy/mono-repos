from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "url_shortener"
    kgs_database_name: str = "key_generation"

    # KGS Configuration
    kgs_service_url: str = "http://localhost:8001"
    key_length: int = 6
    batch_size: int = 1000
    min_cache_threshold: int = 100

    # URL Shortener Configuration
    base_url: str = "http://localhost:8000"
    default_expiry_days: int = 365

    # Redis Configuration (optional for caching)
    redis_url: Optional[str] = "redis://localhost:6379"

    # API Configuration
    api_title: str = "URL Shortener Service"
    api_version: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
