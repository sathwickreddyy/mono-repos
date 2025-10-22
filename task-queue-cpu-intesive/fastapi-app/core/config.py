"""
Configuration Management Module

This module provides type-safe configuration management using Pydantic Settings.

Architectural Decisions:
1. **Why Pydantic Settings over os.getenv()?**
   - Type validation at startup (fail fast)
   - Default values with documentation
   - Environment variable precedence
   - Auto-generates config documentation

2. **Why separate settings classes?**
   - Single Responsibility Principle
   - Easy to test individual components
   - Clear namespace (settings.redis.host vs REDIS_HOST)

3. **Why computed properties?**
   - Derived values calculated once
   - No hardcoded connection strings
   - DRY principle (Don't Repeat Yourself)

Design Pattern: Configuration Object Pattern
"""

import os
import secrets
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    """
    Redis connection configuration.
    
    Supports both standalone and authenticated Redis instances.
    Automatically constructs connection URLs from components.
    """
    
    host: str = Field(
        default="redis",
        env="REDIS_HOST",
        description="Redis server hostname"
    )
    port: int = Field(
        default=6379,
        env="REDIS_PORT",
        ge=1,
        le=65535,
        description="Redis server port"
    )
    db: int = Field(
        default=0,
        env="REDIS_DB",
        ge=0,
        le=15,
        description="Redis database number (0-15)"
    )
    password: Optional[str] = Field(
        default=None,
        env="REDIS_PASSWORD",
        description="Redis password for authentication"
    )
    max_connections: int = Field(
        default=50,
        env="REDIS_MAX_CONNECTIONS",
        ge=10,
        le=1000,
        description="Maximum number of connections in the pool"
    )
    
    @property
    def url(self) -> str:
        """
        Construct Redis URL for connections.
        
        Returns:
            Redis connection URL with optional authentication
            
        Examples:
            - No auth: redis://redis:6379/0
            - With auth: redis://:password@redis:6379/0
        """
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


class CelerySettings(BaseSettings):
    """
    Celery task queue configuration.
    
    Auto-generates broker and result backend URLs from Redis settings
    if not explicitly provided via environment variables.
    
    Design Pattern: Convention over Configuration
    - Uses Redis DB 0 for broker by default
    - Uses Redis DB 1 for results by default
    """
    
    broker_url: Optional[str] = Field(
        default=None,
        env="CELERY_BROKER_URL",
        description="Celery broker URL (auto-generated if not set)"
    )
    result_backend: Optional[str] = Field(
        default=None,
        env="CELERY_RESULT_BACKEND",
        description="Celery result backend URL (auto-generated if not set)"
    )
    task_serializer: str = Field(
        default="json",
        env="CELERY_TASK_SERIALIZER",
        description="Serializer for task messages"
    )
    result_serializer: str = Field(
        default="json",
        env="CELERY_RESULT_SERIALIZER",
        description="Serializer for task results"
    )
    accept_content: List[str] = Field(
        default=["json"],
        env="CELERY_ACCEPT_CONTENT",
        description="Accepted content types"
    )
    timezone: str = Field(
        default="UTC",
        env="CELERY_TIMEZONE",
        description="Timezone for Celery beat scheduling"
    )
    task_track_started: bool = Field(
        default=True,
        env="CELERY_TASK_TRACK_STARTED",
        description="Track task started events"
    )
    task_time_limit: int = Field(
        default=600,
        env="CELERY_TASK_TIME_LIMIT",
        ge=60,
        le=3600,
        description="Hard time limit for task execution (seconds)"
    )
    task_soft_time_limit: int = Field(
        default=540,
        env="CELERY_TASK_SOFT_TIME_LIMIT",
        ge=30,
        le=3600,
        description="Soft time limit for task execution (seconds)"
    )
    result_expires: int = Field(
        default=604800,  # 7 days
        env="CELERY_RESULT_EXPIRES",
        ge=3600,
        description="Task result expiration time (seconds)"
    )
    
    @field_validator("broker_url", mode="before")
    @classmethod
    def set_broker_url(cls, v: Optional[str]) -> str:
        """
        Auto-generate broker URL from Redis settings if not provided.
        
        Why validator? Allows override via environment variable while
        providing sensible default based on Redis configuration.
        """
        if v is None or v == '':
            redis = RedisSettings()
            return redis.url
        return v
    
    @field_validator("result_backend", mode="before")
    @classmethod
    def set_result_backend(cls, v: Optional[str]) -> str:
        """
        Auto-generate result backend URL from Redis settings if not provided.
        Uses Redis DB 1 to separate broker and results.
        
        Why separate DBs? Prevents broker queue operations from interfering
        with result lookups. Better performance isolation.
        """
        if v is None or v == '':
            redis = RedisSettings()
            # Use next DB for results (DB 0 for broker, DB 1 for results)
            return redis.url.replace(f"/{redis.db}", f"/{redis.db + 1}")
        return v
    
    # Note: Removed validator for task_soft_time_limit as it requires access to other fields
    # This should be validated in __init__ if needed
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


class APISettings(BaseSettings):
    """
    FastAPI application configuration.
    
    Includes server settings, security, performance tuning, and feature flags.
    """
    
    # Application metadata
    title: str = Field(
        default="Distributed Task Processing System",
        env="API_TITLE",
        description="API title for documentation"
    )
    version: str = Field(
        default="1.0.0",
        env="API_VERSION",
        description="API version"
    )
    description: str = Field(
        default="Horizontally scalable task queue for CPU-intensive financial calculations",
        env="API_DESCRIPTION",
        description="API description for documentation"
    )
    
    # Server configuration
    host: str = Field(
        default="0.0.0.0",
        env="API_HOST",
        description="Server bind address"
    )
    port: int = Field(
        default=8000,
        env="API_PORT",
        ge=1024,
        le=65535,
        description="Server port"
    )
    workers: int = Field(
        default=1,
        env="FASTAPI_WORKERS",
        ge=1,
        le=8,
        description="Number of Uvicorn workers"
    )
    
    # Security
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="API_SECRET_KEY",
        description="Secret key for signing tokens"
    )
    allowed_origins: List[str] = Field(
        default=["*"],
        env="API_ALLOWED_ORIGINS",
        description="CORS allowed origins"
    )
    
    # Performance & Circuit Breaker
    max_queue_size: int = Field(
        default=500,
        env="MAX_QUEUE_SIZE",
        ge=1,
        le=10000,
        description="Maximum tasks in queue before backpressure triggers"
    )
    request_timeout: int = Field(
        default=300,
        env="API_REQUEST_TIMEOUT",
        ge=30,
        le=600,
        description="Request timeout in seconds"
    )
    
    # Feature flags
    enable_docs: bool = Field(
        default=True,
        env="API_ENABLE_DOCS",
        description="Enable OpenAPI documentation endpoints"
    )
    enable_cors: bool = Field(
        default=True,
        env="API_ENABLE_CORS",
        description="Enable CORS middleware"
    )
    enable_metrics: bool = Field(
        default=True,
        env="API_ENABLE_METRICS",
        description="Enable Prometheus metrics endpoint"
    )
    
    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8"
    )


class LoggingSettings(BaseSettings):
    """
    Logging configuration.
    
    Supports both structured (JSON) and human-readable (pretty) formats.
    Use JSON in production for log aggregation tools (ELK, Splunk).
    """
    
    level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    format: str = Field(
        default="json",
        env="LOG_FORMAT",
        pattern="^(json|pretty)$",
        description="Log format: json for production, pretty for development"
    )
    
    @property
    def use_json_format(self) -> bool:
        """Whether to use JSON formatting for logs."""
        return self.format.lower() == "json"
    
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8"
    )


class Settings:
    """
    Main settings container (Composition Pattern).
    
    Aggregates all configuration modules into a single object.
    Provides convenience methods for accessing computed values.
    
    Design Pattern: Facade Pattern
    - Simple interface to complex subsystems
    - Single import point for all configuration
    
    Usage:
        from core.config import settings
        
        print(settings.redis.url)
        print(settings.api.max_queue_size)
    """
    
    def __init__(self):
        """Initialize all configuration modules."""
        self.redis = RedisSettings()
        self.celery = CelerySettings()
        self.api = APISettings()
        self.logging = LoggingSettings()
    
    @property
    def server_id(self) -> str:
        """
        Get server identifier from environment.
        
        Used for logging and debugging in multi-server deployments.
        Set via docker-compose.yml environment variable SERVER_ID.
        
        Returns:
            Server identifier (e.g., "fastapi-1", "fastapi-2")
        """
        return os.getenv("SERVER_ID", "unknown")
    
    @property
    def is_production(self) -> bool:
        """
        Check if running in production environment.
        
        Returns:
            True if ENVIRONMENT=production, False otherwise
        """
        env = os.getenv("ENVIRONMENT", "development").lower()
        return env in ("production", "prod")
    
    def get_celery_config(self) -> dict:
        """
        Get Celery configuration as dictionary.
        
        Used by Celery worker initialization.
        
        Returns:
            Dictionary of Celery configuration parameters
        """
        return {
            "broker_url": self.celery.broker_url,
            "result_backend": self.celery.result_backend,
            "task_serializer": self.celery.task_serializer,
            "result_serializer": self.celery.result_serializer,
            "accept_content": self.celery.accept_content,
            "timezone": self.celery.timezone,
            "task_track_started": self.celery.task_track_started,
            "task_time_limit": self.celery.task_time_limit,
            "task_soft_time_limit": self.celery.task_soft_time_limit,
            "result_expires": self.celery.result_expires,
        }


# Singleton instance
# Why singleton? Configuration should be loaded once at startup
# and shared across the application (avoid re-reading env vars)
settings = Settings()
