# Data Service Template for AI Code Generation
# Template variables are marked with {{variable_name}} format

"""
{{data_service_name}} - {{database_type}} Data Access Service

This service provides HTTP API access to {{database_type}} database
following the Improved Hybrid Approach architecture pattern.

Generated for business domain: {{business_domain}}
Database entities: {{database_entities}}
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

# Database imports based on type
{{database_imports}}

# Configuration
from .config import DataServiceSettings
from .models import {{data_model_imports}}
from .database import {{database_connection_imports}}

# Initialize structured logging
logger = logging.getLogger(__name__)

# Settings
settings = DataServiceSettings()

# Database connection
{{database_connection_setup}}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("starting_{{data_service_name}}")
    await setup_database_connection()
    await initialize_database_schema()

    yield

    # Shutdown
    logger.info("shutting_down_{{data_service_name}}")
    await cleanup_database_connection()

# FastAPI app
app = FastAPI(
    title="{{data_service_title}}",
    description="{{data_service_description}}",
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
async def log_requests(request, call_next):
    """Log all database requests"""
    start_time = asyncio.get_event_loop().time()

    request_id = request.headers.get("X-Request-ID") or generate_request_id("data")

    logger.info(
        "data_request_started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        service="{{data_service_name}}"
    )

    response = await call_next(request)

    duration = asyncio.get_event_loop().time() - start_time
    logger.info(
        "data_request_completed",
        request_id=request_id,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
        service="{{data_service_name}}"
    )

    response.headers["X-Request-ID"] = request_id
    return response

# Database operation utilities
{{database_utilities}}

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await test_database_connection()
        return {
            "status": "healthy",
            "service": "{{data_service_name}}",
            "database": "{{database_type}}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # More thorough readiness check
        await test_database_operations()
        return {
            "status": "ready",
            "service": "{{data_service_name}}",
            "database": "{{database_type}}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")

# Generic CRUD endpoints
{{crud_endpoints}}

# Entity-specific endpoints for {{business_domain}}
{{entity_endpoints}}

# Bulk operation endpoints
@app.post("/bulk_insert/{table_name}")
async def bulk_insert(
    table_name: str = Path(..., description="Table/collection name"),
    items: List[Dict[str, Any]] = Body(..., description="List of items to insert")
):
    """Bulk insert operation"""
    try:
        result = await perform_bulk_insert(table_name, items)
        logger.info("bulk_insert_completed", table=table_name, count=len(items))
        return result
    except Exception as e:
        logger.error("bulk_insert_failed", table=table_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/bulk_update/{table_name}")
async def bulk_update(
    table_name: str = Path(..., description="Table/collection name"),
    updates: List[Dict[str, Any]] = Body(..., description="List of update operations")
):
    """Bulk update operation"""
    try:
        result = await perform_bulk_update(table_name, updates)
        logger.info("bulk_update_completed", table=table_name, count=len(updates))
        return result
    except Exception as e:
        logger.error("bulk_update_failed", table=table_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Advanced query endpoints
{{advanced_query_endpoints}}

# Transaction endpoints (for PostgreSQL)
{{transaction_endpoints}}

# Aggregation endpoints (for MongoDB)
{{aggregation_endpoints}}

# Example entity endpoints - Replace with actual business entities
{{example_entity_endpoints}}

# Database-specific error handling
{{error_handling}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port={{service_port}},
        reload=settings.debug,
        log_config=None  # Use logging configuration from lifespan
    )