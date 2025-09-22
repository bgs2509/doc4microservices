# FastAPI Service Template for AI Code Generation
# Template variables are marked with {{variable_name}} format

"""
{{service_name}} - FastAPI Business Logic Service

This service implements the {{business_domain}} business logic
following the Improved Hybrid Approach architecture pattern.

Generated from business requirements:
{{business_requirements}}
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import structlog

# Configuration
from .config import Settings
from .models import {{model_imports}}
from .dependencies import {{dependency_imports}}

# Initialize structured logging
logger = structlog.get_logger(__name__)

# Settings
settings = Settings()

# HTTP client for data service communication
http_client: Optional[httpx.AsyncClient] = None

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global http_client

    # Startup
    logger.info("Starting {{service_name}}")
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )

    # Verify data service connections
    await verify_data_services()

    yield

    # Shutdown
    logger.info("Shutting down {{service_name}}")
    if http_client:
        await http_client.aclose()

# FastAPI app
app = FastAPI(
    title="{{service_title}}",
    description="{{service_description}}",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with structured logging"""
    start_time = asyncio.get_event_loop().time()

    # Generate request ID
    request_id = request.headers.get("X-Request-ID", f"req-{id(request)}")

    # Log request
    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        user_agent=request.headers.get("user-agent"),
    )

    # Process request
    response = await call_next(request)

    # Log response
    duration = asyncio.get_event_loop().time() - start_time
    logger.info(
        "request_completed",
        request_id=request_id,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )

    response.headers["X-Request-ID"] = request_id
    return response

# Data service clients
class DataServiceClient:
    """Client for communicating with data services"""

    def __init__(self):
        self.postgres_url = settings.postgres_service_url
        self.mongo_url = settings.mongo_service_url

    async def postgres_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make request to PostgreSQL data service"""
        url = f"{self.postgres_url}{endpoint}"

        try:
            response = await http_client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error("postgres_service_error", error=str(e), endpoint=endpoint)
            raise HTTPException(status_code=503, detail="PostgreSQL service unavailable")
        except httpx.HTTPStatusError as e:
            logger.error("postgres_service_http_error", status_code=e.response.status_code, endpoint=endpoint)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    async def mongo_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make request to MongoDB data service"""
        url = f"{self.mongo_url}{endpoint}"

        try:
            response = await http_client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error("mongo_service_error", error=str(e), endpoint=endpoint)
            raise HTTPException(status_code=503, detail="MongoDB service unavailable")
        except httpx.HTTPStatusError as e:
            logger.error("mongo_service_http_error", status_code=e.response.status_code, endpoint=endpoint)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

# Dependency injection
async def get_data_client() -> DataServiceClient:
    """Get data service client dependency"""
    return DataServiceClient()

async def verify_data_services():
    """Verify that data services are available"""
    client = DataServiceClient()

    try:
        # Check PostgreSQL service
        await client.postgres_request("GET", "/health")
        logger.info("postgres_service_connected")

        # Check MongoDB service
        await client.mongo_request("GET", "/health")
        logger.info("mongo_service_connected")

    except Exception as e:
        logger.error("data_service_connection_failed", error=str(e))
        raise

# Pydantic models for {{business_domain}}
{{pydantic_models}}

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    data_client: DataServiceClient = Depends(get_data_client)
) -> Dict[str, Any]:
    """Authenticate user from JWT token"""
    try:
        # Validate token with PostgreSQL service
        user_data = await data_client.postgres_request(
            "POST",
            "/auth/validate",
            json={"token": credentials.credentials}
        )
        return user_data
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "{{service_name}}"}

@app.get("/ready")
async def readiness_check(data_client: DataServiceClient = Depends(get_data_client)):
    """Readiness check endpoint"""
    try:
        await data_client.postgres_request("GET", "/health")
        await data_client.mongo_request("GET", "/health")
        return {"status": "ready", "service": "{{service_name}}"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")

# Business logic endpoints for {{business_domain}}
{{api_endpoints}}

# Example endpoint structure - Replace with actual business logic
{{example_endpoints}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_config=None  # Use structlog configuration
    )