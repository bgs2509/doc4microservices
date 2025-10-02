"""
Application Configuration

Centralized configuration using Pydantic Settings.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # Project Configuration
    # ═══════════════════════════════════════════════════════════════════════════
    PROJECT_NAME: str = Field(default="MyApp", description="Project name")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment",
    )
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info",
        description="Logging level",
    )
    LOG_FORMAT: Literal["json", "text"] = Field(
        default="json",
        description="Log format",
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # API Configuration
    # ═══════════════════════════════════════════════════════════════════════════
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_WORKERS: int = Field(default=4, description="Number of workers")
    API_RELOAD: bool = Field(default=False, description="Auto-reload on code changes")

    # ═══════════════════════════════════════════════════════════════════════════
    # CORS Configuration
    # ═══════════════════════════════════════════════════════════════════════════
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="CORS allowed origins",
    )
    CORS_CREDENTIALS: bool = Field(default=True, description="Allow credentials")
    CORS_METHODS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed HTTP methods",
    )
    CORS_HEADERS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed headers",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ═══════════════════════════════════════════════════════════════════════════
    # Data Service URLs (HTTP-only access)
    # ═══════════════════════════════════════════════════════════════════════════
    POSTGRES_SERVICE_URL: str = Field(
        default="http://template_data_postgres_api:8000",
        description="PostgreSQL service URL",
    )
    MONGO_SERVICE_URL: str = Field(
        default="http://template_data_mongo_api:8000",
        description="MongoDB service URL",
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # Redis Configuration
    # ═══════════════════════════════════════════════════════════════════════════
    REDIS_URL: str = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL",
    )
    REDIS_MAX_CONNECTIONS: int = Field(
        default=50,
        description="Redis connection pool size",
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # RabbitMQ Configuration
    # ═══════════════════════════════════════════════════════════════════════════
    RABBITMQ_URL: str = Field(
        default="amqp://admin:admin@rabbitmq:5672/",
        description="RabbitMQ connection URL",
    )
    RABBITMQ_EXCHANGE: str = Field(
        default="myapp_events",
        description="RabbitMQ exchange name",
    )
    RABBITMQ_QUEUE_PREFIX: str = Field(
        default="myapp",
        description="Queue name prefix",
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # Security
    # ═══════════════════════════════════════════════════════════════════════════
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for signing tokens",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration (minutes)",
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # Observability
    # ═══════════════════════════════════════════════════════════════════════════
    SENTRY_DSN: str | None = Field(default=None, description="Sentry DSN")
    SENTRY_ENVIRONMENT: str | None = Field(default=None, description="Sentry environment")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=1.0,
        description="Sentry traces sample rate",
    )

    JAEGER_ENABLED: bool = Field(default=False, description="Enable Jaeger tracing")
    JAEGER_HOST: str = Field(default="jaeger", description="Jaeger host")
    JAEGER_PORT: int = Field(default=6831, description="Jaeger port")

    # ═══════════════════════════════════════════════════════════════════════════
    # Feature Flags
    # ═══════════════════════════════════════════════════════════════════════════
    ENABLE_SWAGGER: bool = Field(default=True, description="Enable Swagger UI")
    ENABLE_REDOC: bool = Field(default=True, description="Enable ReDoc")
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings
    """
    return Settings()
