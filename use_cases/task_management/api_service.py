"""
Task Management API Service - FastAPI Implementation.

This service provides REST API endpoints for task management with full CRUD operations,
user authentication, caching, and event publishing. It follows the Improved Hybrid
Approach by accessing data only via HTTP calls to data services.

Key Features:
- Task CRUD operations with validation
- User authentication and authorization
- Redis caching for performance
- RabbitMQ event publishing
- Due date tracking and notifications
- Attachment support
- Productivity analytics
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any, Optional, List
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as redis
import aio_pika
import httpx
import orjson
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from shared_dtos import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskStatsResponse,
    TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent, TaskActivity,
    ActionType, AttachmentInfo, AttachmentUploadedEvent, ReminderRequest
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """API service configuration."""

    # Service settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # External services
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://admin:admin123@rabbitmq:5672/"

    # Data services
    DB_POSTGRES_SERVICE_URL: str = "http://db_postgres_service:8000"
    DB_MONGO_SERVICE_URL: str = "http://db_mongo_service:8000"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API settings
    ALLOWED_HOSTS: List[str] = ["*"]
    MAX_TASKS_PER_PAGE: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
security = HTTPBearer()


# Dependency injection
async def get_redis() -> redis.Redis:
    """Get Redis client from app state."""
    return app.state.redis


async def get_rabbitmq_channel() -> aio_pika.Channel:
    """Get RabbitMQ channel from app state."""
    return app.state.rabbitmq_channel


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client: redis.Redis = Depends(get_redis)
) -> Dict[str, Any]:
    """Get current authenticated user."""
    token = credentials.credentials

    # Check token in Redis cache first
    user_data = await redis_client.get(f"auth_token:{token}")
    if user_data:
        return orjson.loads(user_data)

    # Validate token via postgres data service
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.DB_POSTGRES_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            user = response.json()

            # Cache user data for 30 minutes
            await redis_client.setex(
                f"auth_token:{token}",
                1800,  # 30 minutes
                orjson.dumps(user)
            )

            return user
        except httpx.HTTPError as e:
            logger.error(f"Auth verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )


class TaskService:
    """Service layer for task operations."""

    def __init__(
        self,
        redis_client: redis.Redis,
        rabbitmq_channel: aio_pika.Channel,
        postgres_url: str,
        mongo_url: str
    ):
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel
        self.postgres_url = postgres_url
        self.mongo_url = mongo_url

    async def create_task(self, task_data: TaskCreate, user_id: int) -> TaskResponse:
        """Create a new task."""
        request_id = str(uuid4())

        # Create task via postgres data service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.postgres_url}/tasks",
                    json={
                        **task_data.model_dump(),
                        "user_id": user_id
                    },
                    headers={"X-Request-ID": request_id}
                )
                response.raise_for_status()
                task = TaskResponse(**response.json())

                # Cache task
                await self._cache_task(task)

                # Update user task counters
                await self._update_user_counters(user_id)

                # Log activity
                await self._log_activity(
                    task.id, user_id, ActionType.CREATED,
                    {"source": "api"}, request_id
                )

                # Publish task created event
                await self._publish_task_created_event(task, request_id)

                logger.info(f"Task created: {task.id} for user {user_id}")
                return task

            except httpx.HTTPError as e:
                logger.error(f"Failed to create task: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create task"
                )

    async def get_task(self, task_id: int, user_id: int) -> Optional[TaskResponse]:
        """Get task by ID with ownership check."""
        # Try cache first
        cached_task = await self.redis_client.get(f"task:{task_id}")
        if cached_task:
            task = TaskResponse(**orjson.loads(cached_task))
            if task.user_id == user_id:
                return task

        # Get from postgres data service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.postgres_url}/tasks/{task_id}",
                    params={"user_id": user_id}
                )
                if response.status_code == 404:
                    return None

                response.raise_for_status()
                task = TaskResponse(**response.json())

                # Cache task
                await self._cache_task(task)

                return task

            except httpx.HTTPError as e:
                logger.error(f"Failed to get task {task_id}: {e}")
                return None

    async def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
        user_id: int
    ) -> Optional[TaskResponse]:
        """Update task with ownership check."""
        request_id = str(uuid4())

        # Get current task data for change tracking
        current_task = await self.get_task(task_id, user_id)
        if not current_task:
            return None

        # Update via postgres data service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{self.postgres_url}/tasks/{task_id}",
                    json=task_data.model_dump(exclude_unset=True),
                    params={"user_id": user_id},
                    headers={"X-Request-ID": request_id}
                )
                response.raise_for_status()
                updated_task = TaskResponse(**response.json())

                # Update cache
                await self._cache_task(updated_task)

                # Track what changed
                changes = self._get_task_changes(current_task, updated_task)

                # Log activity
                action = ActionType.COMPLETED if updated_task.status == "completed" else ActionType.UPDATED
                await self._log_activity(
                    task_id, user_id, action,
                    {"changes": changes, "source": "api"}, request_id
                )

                # Publish appropriate events
                if updated_task.status == "completed" and current_task.status != "completed":
                    await self._publish_task_completed_event(updated_task, request_id)
                else:
                    await self._publish_task_updated_event(
                        current_task, updated_task, changes, request_id
                    )

                # Update counters if status changed
                if current_task.status != updated_task.status:
                    await self._update_user_counters(user_id)

                logger.info(f"Task updated: {task_id} by user {user_id}")
                return updated_task

            except httpx.HTTPError as e:
                logger.error(f"Failed to update task {task_id}: {e}")
                return None

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete task with ownership check."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.postgres_url}/tasks/{task_id}",
                    params={"user_id": user_id}
                )
                if response.status_code == 404:
                    return False

                response.raise_for_status()

                # Remove from cache
                await self.redis_client.delete(f"task:{task_id}")

                # Update counters
                await self._update_user_counters(user_id)

                logger.info(f"Task deleted: {task_id} by user {user_id}")
                return True

            except httpx.HTTPError as e:
                logger.error(f"Failed to delete task {task_id}: {e}")
                return False

    async def list_tasks(
        self,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> TaskListResponse:
        """List tasks with filtering and pagination."""
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    "user_id": user_id,
                    "page": page,
                    "per_page": min(per_page, settings.MAX_TASKS_PER_PAGE)
                }

                if status:
                    params["status"] = status
                if priority:
                    params["priority"] = priority

                response = await client.get(
                    f"{self.postgres_url}/tasks",
                    params=params
                )
                response.raise_for_status()

                return TaskListResponse(**response.json())

            except httpx.HTTPError as e:
                logger.error(f"Failed to list tasks for user {user_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve tasks"
                )

    async def get_task_stats(self, user_id: int) -> TaskStatsResponse:
        """Get user task statistics."""
        # Check cache first
        cached_stats = await self.redis_client.get(f"user_stats:{user_id}")
        if cached_stats:
            return TaskStatsResponse(**orjson.loads(cached_stats))

        # Get from postgres data service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.postgres_url}/tasks/stats",
                    params={"user_id": user_id}
                )
                response.raise_for_status()
                stats = TaskStatsResponse(**response.json())

                # Cache for 5 minutes
                await self.redis_client.setex(
                    f"user_stats:{user_id}",
                    300,
                    orjson.dumps(stats.model_dump())
                )

                return stats

            except httpx.HTTPError as e:
                logger.error(f"Failed to get stats for user {user_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve statistics"
                )

    async def create_reminder(self, task_id: int, user_id: int, remind_at: datetime) -> bool:
        """Create a reminder for a task."""
        # Verify task ownership
        task = await self.get_task(task_id, user_id)
        if not task:
            return False

        reminder = ReminderRequest(
            task_id=task_id,
            user_id=user_id,
            remind_at=remind_at
        )

        # Store reminder in Redis with expiration
        reminder_key = f"reminder:{task_id}:{remind_at.isoformat()}"
        await self.redis_client.setex(
            reminder_key,
            int((remind_at - datetime.utcnow()).total_seconds()) + 3600,  # 1 hour buffer
            orjson.dumps(reminder.model_dump())
        )

        logger.info(f"Reminder created for task {task_id} at {remind_at}")
        return True

    # Helper methods
    async def _cache_task(self, task: TaskResponse) -> None:
        """Cache task data in Redis."""
        await self.redis_client.setex(
            f"task:{task.id}",
            3600,  # 1 hour
            orjson.dumps(task.model_dump())
        )

    async def _update_user_counters(self, user_id: int) -> None:
        """Update user task counters in Redis."""
        # This could be optimized by calculating deltas, but for simplicity
        # we invalidate the cache and let it be recalculated
        await self.redis_client.delete(f"user_stats:{user_id}")

    async def _log_activity(
        self,
        task_id: int,
        user_id: int,
        action: ActionType,
        metadata: Dict[str, Any],
        request_id: str
    ) -> None:
        """Log task activity to MongoDB via data service."""
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action=action,
            metadata=metadata,
            source="api"
        )

        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{self.mongo_url}/activities",
                    json=activity.model_dump(),
                    headers={"X-Request-ID": request_id}
                )
            except httpx.HTTPError as e:
                logger.error(f"Failed to log activity: {e}")
                # Don't fail the main operation for logging issues

    def _get_task_changes(self, old_task: TaskResponse, new_task: TaskResponse) -> Dict[str, Any]:
        """Get changes between task versions."""
        changes = {}
        for field in ["title", "description", "status", "priority", "due_date"]:
            old_value = getattr(old_task, field)
            new_value = getattr(new_task, field)
            if old_value != new_value:
                changes[field] = {"from": old_value, "to": new_value}
        return changes

    async def _publish_task_created_event(self, task: TaskResponse, request_id: str) -> None:
        """Publish task created event."""
        event = TaskCreatedEvent(
            task_id=task.id,
            user_id=task.user_id,
            task_data=task,
            request_id=request_id
        )
        await self._publish_event("task.created", event.model_dump())

    async def _publish_task_updated_event(
        self,
        old_task: TaskResponse,
        new_task: TaskResponse,
        changes: Dict[str, Any],
        request_id: str
    ) -> None:
        """Publish task updated event."""
        event = TaskUpdatedEvent(
            task_id=new_task.id,
            user_id=new_task.user_id,
            previous_data=old_task.model_dump(),
            new_data=new_task.model_dump(),
            changes=changes,
            request_id=request_id
        )
        await self._publish_event("task.updated", event.model_dump())

    async def _publish_task_completed_event(self, task: TaskResponse, request_id: str) -> None:
        """Publish task completed event."""
        event = TaskCompletedEvent(
            task_id=task.id,
            user_id=task.user_id,
            task_data=task,
            completion_time=task.completed_at or datetime.utcnow(),
            request_id=request_id
        )
        await self._publish_event("task.completed", event.model_dump())

    async def _publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish event to RabbitMQ."""
        try:
            message = aio_pika.Message(
                orjson.dumps(event_data),
                headers={"event_type": event_type}
            )

            exchange = await self.rabbitmq_channel.declare_exchange(
                "task_events",
                aio_pika.ExchangeType.TOPIC
            )

            await exchange.publish(message, routing_key=event_type)
            logger.info(f"Published event: {event_type}")

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")


# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting Task Management API Service")

    # Initialize Redis
    app.state.redis = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
    )

    # Initialize RabbitMQ
    app.state.rabbitmq_connection = await aio_pika.connect_robust(
        settings.RABBITMQ_URL,
        client_properties={"connection_name": "task_api_service"}
    )
    app.state.rabbitmq_channel = await app.state.rabbitmq_connection.channel()

    # Test connections
    await app.state.redis.ping()
    logger.info("Redis connection established")
    logger.info("RabbitMQ connection established")

    yield

    # Cleanup
    logger.info("Shutting down Task Management API Service")
    await app.state.redis.close()
    await app.state.rabbitmq_channel.close()
    await app.state.rabbitmq_connection.close()


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Task Management API",
        description="REST API for personal task management system",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


# Dependency to get task service
async def get_task_service(
    redis_client: redis.Redis = Depends(get_redis),
    rabbitmq_channel: aio_pika.Channel = Depends(get_rabbitmq_channel)
) -> TaskService:
    """Get task service instance."""
    return TaskService(
        redis_client,
        rabbitmq_channel,
        settings.DB_POSTGRES_SERVICE_URL,
        settings.DB_MONGO_SERVICE_URL
    )


# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "task_management_api"}


@app.post("/api/v1/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Create a new task."""
    return await task_service.create_task(task_data, current_user["id"])


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Get task by ID."""
    task = await task_service.get_task(task_id, current_user["id"])
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@app.put("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Update task."""
    task = await task_service.update_task(task_id, task_data, current_user["id"])
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@app.delete("/api/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Delete task."""
    success = await task_service.delete_task(task_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@app.get("/api/v1/tasks", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_user: Dict[str, Any] = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """List tasks with filtering and pagination."""
    return await task_service.list_tasks(
        current_user["id"], status_filter, priority_filter, page, per_page
    )


@app.get("/api/v1/tasks/stats", response_model=TaskStatsResponse)
async def get_task_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Get user task statistics."""
    return await task_service.get_task_stats(current_user["id"])


@app.post("/api/v1/tasks/{task_id}/reminders")
async def create_reminder(
    task_id: int,
    remind_at: datetime,
    current_user: Dict[str, Any] = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Create a reminder for a task."""
    success = await task_service.create_reminder(task_id, current_user["id"], remind_at)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"message": "Reminder created successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_service:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )