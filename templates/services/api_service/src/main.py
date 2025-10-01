"""
FastAPI Application Factory

This module creates and configures the FastAPI application instance.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.api.v1 import health_router
from src.core.config import get_settings
from src.core.logging_config import configure_logging
from src.core.middleware import RequestIDMiddleware, LoggingMiddleware

# Configure logging before anything else
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    settings = get_settings()
    logger.info(
        "Starting API service",
        extra={
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "version": "1.0.0",
        },
    )

    # TODO: Initialize connections (Redis, RabbitMQ) here
    # Example:
    # await redis_client.connect()
    # await rabbitmq_client.connect()

    yield

    # TODO: Cleanup connections here
    # Example:
    # await redis_client.disconnect()
    # await rabbitmq_client.disconnect()

    logger.info("API service stopped")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="FastAPI service for microservices architecture",
        version="1.0.0",
        docs_url="/api/docs" if settings.ENABLE_SWAGGER else None,
        redoc_url="/api/redoc" if settings.ENABLE_REDOC else None,
        openapi_url="/api/openapi.json" if settings.ENABLE_SWAGGER else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # CORS Configuration
    # ═══════════════════════════════════════════════════════════════════════════
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_CREDENTIALS,
            allow_methods=settings.CORS_METHODS,
            allow_headers=settings.CORS_HEADERS,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Custom Middleware
    # ═══════════════════════════════════════════════════════════════════════════
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    # ═══════════════════════════════════════════════════════════════════════════
    # Include Routers
    # ═══════════════════════════════════════════════════════════════════════════
    app.include_router(health_router.router, prefix="/api/v1", tags=["health"])

    # TODO: Add your business routers here
    # Example:
    # from src.api.v1 import users_router
    # app.include_router(users_router.router, prefix="/api/v1", tags=["users"])

    logger.info("FastAPI application created successfully")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_config=None,  # We use custom logging
    )
