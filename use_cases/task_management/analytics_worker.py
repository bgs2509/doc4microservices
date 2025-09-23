"""
Task Management Analytics Worker Service - AsyncIO Implementation.

This worker service processes task activity data, generates productivity
analytics, creates reports, and maintains historical data. It consumes
events from RabbitMQ and stores analytics in MongoDB via the data service.

Key Features:
- Real-time activity processing
- Productivity analytics generation
- User behavior tracking
- Performance metrics calculation
- Historical data aggregation
- Automated report generation
"""

from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict
import statistics

import redis.asyncio as redis
import aio_pika
import httpx
import orjson
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from shared_dtos import (
    TaskActivity, ProductivityStats, ActionType,
    TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent,
    GenerateAnalyticsCommand, CleanupTasksCommand
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Analytics worker configuration."""

    # External services
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://admin:admin123@rabbitmq:5672/"
    TASK_API_URL: str = "http://task_api_service:8000"
    DB_MONGO_SERVICE_URL: str = "http://db_mongo_service:8000"

    # Analytics settings
    BATCH_SIZE: int = 100
    ANALYTICS_INTERVAL_SECONDS: int = 3600  # 1 hour
    CLEANUP_INTERVAL_SECONDS: int = 86400  # 24 hours
    RETENTION_DAYS: int = 365  # 1 year
    MIN_TASKS_FOR_ANALYSIS: int = 5

    # Performance settings
    MAX_CONCURRENT_PROCESSING: int = 10
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


class AnalyticsWorkerService:
    """Service for processing task analytics and generating insights."""

    def __init__(
        self,
        redis_client: redis.Redis,
        rabbitmq_channel: aio_pika.Channel
    ):
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel
        self.running = False
        self.processing_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_PROCESSING)

    async def start(self) -> None:
        """Start the analytics worker."""
        self.running = True
        logger.info("Starting analytics worker service")

        # Setup exchanges and queues
        await self._setup_messaging()

        # Start background tasks
        tasks = [
            asyncio.create_task(self._process_task_events(), name="task-events"),
            asyncio.create_task(self._process_analytics_commands(), name="analytics-commands"),
            asyncio.create_task(self._periodic_analytics_generation(), name="periodic-analytics"),
            asyncio.create_task(self._periodic_cleanup(), name="cleanup")
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Analytics worker tasks cancelled")
        except Exception as e:
            logger.error(f"Analytics worker error: {e}")
            raise

    async def stop(self) -> None:
        """Stop the analytics worker."""
        self.running = False
        logger.info("Stopping analytics worker service")

    async def _setup_messaging(self) -> None:
        """Setup RabbitMQ exchanges and queues."""
        # Task events exchange
        self.task_events_exchange = await self.rabbitmq_channel.declare_exchange(
            "task_events",
            aio_pika.ExchangeType.TOPIC
        )

        # Analytics exchange
        self.analytics_exchange = await self.rabbitmq_channel.declare_exchange(
            "analytics",
            aio_pika.ExchangeType.DIRECT
        )

        # Task events queue for analytics
        self.task_events_queue = await self.rabbitmq_channel.declare_queue(
            "analytics.task_events",
            durable=True
        )

        # Bind to all task events
        await self.task_events_queue.bind(self.task_events_exchange, routing_key="task.#")

        # Analytics commands queue
        self.analytics_commands_queue = await self.rabbitmq_channel.declare_queue(
            "analytics.commands",
            durable=True
        )
        await self.analytics_commands_queue.bind(self.analytics_exchange, routing_key="analytics.command")

        logger.info("Analytics messaging setup complete")

    async def _process_task_events(self) -> None:
        """Process task events for analytics."""
        async with self.task_events_queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self.running:
                    break

                await self._handle_task_event(message)

    async def _handle_task_event(self, message: aio_pika.IncomingMessage) -> None:
        """Handle a single task event message."""
        async with message.process():
            try:
                event_data = orjson.loads(message.body)
                event_type = message.headers.get("event_type")

                if event_type == "task.created":
                    await self._process_task_created_event(TaskCreatedEvent(**event_data))
                elif event_type == "task.updated":
                    await self._process_task_updated_event(TaskUpdatedEvent(**event_data))
                elif event_type == "task.completed":
                    await self._process_task_completed_event(TaskCompletedEvent(**event_data))
                else:
                    logger.debug(f"Unhandled event type: {event_type}")

            except Exception as e:
                logger.error(f"Error handling task event: {e}")

    async def _process_task_created_event(self, event: TaskCreatedEvent) -> None:
        """Process task created event."""
        async with self.processing_semaphore:
            try:
                # Record activity
                activity = TaskActivity(
                    task_id=event.task_id,
                    user_id=event.user_id,
                    action=ActionType.CREATED,
                    timestamp=event.timestamp,
                    metadata={
                        "priority": event.task_data.priority.value,
                        "has_due_date": event.task_data.due_date is not None,
                        "title_length": len(event.task_data.title),
                        "has_description": bool(event.task_data.description)
                    },
                    source="api"
                )

                await self._store_activity(activity)

                # Update user metrics cache
                await self._invalidate_user_stats_cache(event.user_id)

                # Track creation patterns
                await self._track_creation_patterns(event)

                logger.debug(f"Processed task created event: {event.task_id}")

            except Exception as e:
                logger.error(f"Error processing task created event: {e}")

    async def _process_task_updated_event(self, event: TaskUpdatedEvent) -> None:
        """Process task updated event."""
        async with self.processing_semaphore:
            try:
                # Determine the primary action type
                action = ActionType.UPDATED
                if "status" in event.changes:
                    if event.changes["status"]["to"] == "completed":
                        action = ActionType.COMPLETED
                    elif event.changes["status"]["to"] == "cancelled":
                        action = ActionType.CANCELLED
                    else:
                        action = ActionType.STATUS_CHANGED

                # Record activity
                activity = TaskActivity(
                    task_id=event.task_id,
                    user_id=event.user_id,
                    action=action,
                    timestamp=event.timestamp,
                    metadata={
                        "changes": event.changes,
                        "fields_changed": list(event.changes.keys())
                    },
                    source="api"
                )

                await self._store_activity(activity)

                # Update user metrics cache
                await self._invalidate_user_stats_cache(event.user_id)

                logger.debug(f"Processed task updated event: {event.task_id}")

            except Exception as e:
                logger.error(f"Error processing task updated event: {e}")

    async def _process_task_completed_event(self, event: TaskCompletedEvent) -> None:
        """Process task completed event."""
        async with self.processing_semaphore:
            try:
                # Calculate completion time
                created_at = event.task_data.created_at
                completed_at = event.completion_time
                completion_time_hours = (completed_at - created_at).total_seconds() / 3600

                # Record activity
                activity = TaskActivity(
                    task_id=event.task_id,
                    user_id=event.user_id,
                    action=ActionType.COMPLETED,
                    timestamp=event.timestamp,
                    metadata={
                        "completion_time_hours": completion_time_hours,
                        "priority": event.task_data.priority.value,
                        "was_overdue": event.task_data.due_date and completed_at > event.task_data.due_date,
                        "completion_hour": completed_at.hour,
                        "completion_day_of_week": completed_at.weekday()
                    },
                    source="api"
                )

                await self._store_activity(activity)

                # Update user metrics and completion patterns
                await self._update_completion_metrics(event.user_id, activity)
                await self._invalidate_user_stats_cache(event.user_id)

                logger.debug(f"Processed task completed event: {event.task_id}")

            except Exception as e:
                logger.error(f"Error processing task completed event: {e}")

    async def _process_analytics_commands(self) -> None:
        """Process analytics commands."""
        async with self.analytics_commands_queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self.running:
                    break

                await self._handle_analytics_command(message)

    async def _handle_analytics_command(self, message: aio_pika.IncomingMessage) -> None:
        """Handle analytics command message."""
        async with message.process():
            try:
                command_data = orjson.loads(message.body)
                command_type = command_data.get("command_type")

                if command_type == "generate_analytics":
                    command = GenerateAnalyticsCommand(**command_data)
                    await self._generate_user_analytics(command)
                elif command_type == "cleanup_tasks":
                    command = CleanupTasksCommand(**command_data)
                    await self._cleanup_old_data(command)
                else:
                    logger.warning(f"Unknown analytics command type: {command_type}")

            except Exception as e:
                logger.error(f"Error handling analytics command: {e}")

    async def _store_activity(self, activity: TaskActivity) -> None:
        """Store activity data in MongoDB."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.DB_MONGO_SERVICE_URL}/activities",
                    json=activity.model_dump(),
                    timeout=30.0
                )

                if response.status_code != 201:
                    logger.error(f"Failed to store activity: {response.status_code}")

        except Exception as e:
            logger.error(f"Error storing activity: {e}")

    async def _track_creation_patterns(self, event: TaskCreatedEvent) -> None:
        """Track task creation patterns."""
        try:
            # Track hourly creation patterns
            hour = event.timestamp.hour
            creation_key = f"creation_pattern:{event.user_id}:hour:{hour}"
            await self.redis_client.incr(creation_key)
            await self.redis_client.expire(creation_key, 86400 * 30)  # 30 days

            # Track daily creation patterns
            day_of_week = event.timestamp.weekday()
            daily_key = f"creation_pattern:{event.user_id}:day:{day_of_week}"
            await self.redis_client.incr(daily_key)
            await self.redis_client.expire(daily_key, 86400 * 30)  # 30 days

            # Track priority distribution
            priority_key = f"priority_pattern:{event.user_id}:{event.task_data.priority.value}"
            await self.redis_client.incr(priority_key)
            await self.redis_client.expire(priority_key, 86400 * 30)  # 30 days

        except Exception as e:
            logger.error(f"Error tracking creation patterns: {e}")

    async def _update_completion_metrics(self, user_id: int, activity: TaskActivity) -> None:
        """Update completion metrics."""
        try:
            completion_time = activity.metadata.get("completion_time_hours", 0)
            completion_hour = activity.metadata.get("completion_hour", 0)

            # Track completion times
            completion_times_key = f"completion_times:{user_id}"
            await self.redis_client.lpush(completion_times_key, str(completion_time))
            await self.redis_client.ltrim(completion_times_key, 0, 99)  # Keep last 100
            await self.redis_client.expire(completion_times_key, 86400 * 30)  # 30 days

            # Track most productive hours
            productive_hour_key = f"productive_hour:{user_id}:{completion_hour}"
            await self.redis_client.incr(productive_hour_key)
            await self.redis_client.expire(productive_hour_key, 86400 * 30)  # 30 days

        except Exception as e:
            logger.error(f"Error updating completion metrics: {e}")

    async def _generate_user_analytics(self, command: GenerateAnalyticsCommand) -> None:
        """Generate analytics for specific user or all users."""
        try:
            if command.user_id:
                await self._generate_analytics_for_user(command.user_id, command.period_days)
            else:
                # Generate for all active users
                await self._generate_analytics_for_all_users(command.period_days)

        except Exception as e:
            logger.error(f"Error generating analytics: {e}")

    async def _generate_analytics_for_user(self, user_id: int, period_days: int) -> None:
        """Generate analytics for a specific user."""
        try:
            # Calculate period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)

            # Get user activities from MongoDB
            activities = await self._get_user_activities(user_id, start_date, end_date)

            if len(activities) < settings.MIN_TASKS_FOR_ANALYSIS:
                logger.info(f"Insufficient data for user {user_id} analytics")
                return

            # Calculate statistics
            stats = await self._calculate_productivity_stats(user_id, activities, start_date, end_date)

            # Store statistics
            await self._store_productivity_stats(stats)

            # Cache for quick access
            await self._cache_user_stats(stats)

            logger.info(f"Generated analytics for user {user_id}: {stats.completion_rate:.1%} completion rate")

        except Exception as e:
            logger.error(f"Error generating analytics for user {user_id}: {e}")

    async def _generate_analytics_for_all_users(self, period_days: int) -> None:
        """Generate analytics for all users."""
        try:
            # Get list of active users from Redis patterns
            user_ids = set()

            # Scan for user activity patterns
            async for key in self.redis_client.scan_iter(match="creation_pattern:*"):
                parts = key.split(":")
                if len(parts) >= 2:
                    try:
                        user_id = int(parts[1])
                        user_ids.add(user_id)
                    except ValueError:
                        continue

            logger.info(f"Generating analytics for {len(user_ids)} users")

            # Generate analytics for each user
            for user_id in user_ids:
                await self._generate_analytics_for_user(user_id, period_days)
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Error generating analytics for all users: {e}")

    async def _get_user_activities(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get user activities from MongoDB."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.DB_MONGO_SERVICE_URL}/activities",
                    params={
                        "user_id": user_id,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "limit": 1000
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    return response.json().get("activities", [])
                else:
                    logger.error(f"Failed to get activities: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Error getting user activities: {e}")
            return []

    async def _calculate_productivity_stats(
        self,
        user_id: int,
        activities: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> ProductivityStats:
        """Calculate productivity statistics from activities."""
        try:
            # Group activities by task and action
            task_activities = defaultdict(list)
            for activity in activities:
                task_activities[activity["task_id"]].append(activity)

            # Calculate metrics
            total_tasks = 0
            completed_tasks = 0
            cancelled_tasks = 0
            overdue_tasks = 0
            completion_times = []
            completion_hours = []
            priority_counts = defaultdict(int)
            status_counts = defaultdict(int)

            for task_id, task_activities_list in task_activities.items():
                total_tasks += 1

                # Find creation and completion
                created = None
                completed = None
                final_priority = "medium"

                for activity in task_activities_list:
                    if activity["action"] == "created":
                        created = datetime.fromisoformat(activity["timestamp"])
                        final_priority = activity["metadata"].get("priority", "medium")
                    elif activity["action"] == "completed":
                        completed = datetime.fromisoformat(activity["timestamp"])
                        completed_tasks += 1
                        completion_hours.append(completed.hour)

                        if created:
                            completion_time = (completed - created).total_seconds() / 3600
                            completion_times.append(completion_time)

                        if activity["metadata"].get("was_overdue"):
                            overdue_tasks += 1
                    elif activity["action"] == "cancelled":
                        cancelled_tasks += 1

                priority_counts[final_priority] += 1

            # Calculate final statistics
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
            avg_completion_time = statistics.mean(completion_times) if completion_times else None

            # Find most productive hour
            most_productive_hour = None
            if completion_hours:
                hour_counts = defaultdict(int)
                for hour in completion_hours:
                    hour_counts[hour] += 1
                most_productive_hour = max(hour_counts, key=hour_counts.get)

            # Current status distribution (simplified - would need current task data)
            status_counts = {
                "todo": total_tasks - completed_tasks - cancelled_tasks,
                "completed": completed_tasks,
                "cancelled": cancelled_tasks,
                "in_progress": 0  # Would need current data
            }

            return ProductivityStats(
                user_id=user_id,
                period_start=start_date,
                period_end=end_date,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                cancelled_tasks=cancelled_tasks,
                overdue_tasks=overdue_tasks,
                completion_rate=completion_rate,
                average_completion_time_hours=avg_completion_time,
                most_productive_hour=most_productive_hour,
                tasks_by_priority=dict(priority_counts),
                tasks_by_status=status_counts
            )

        except Exception as e:
            logger.error(f"Error calculating productivity stats: {e}")
            raise

    async def _store_productivity_stats(self, stats: ProductivityStats) -> None:
        """Store productivity statistics in MongoDB."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.DB_MONGO_SERVICE_URL}/analytics/productivity",
                    json=stats.model_dump(),
                    timeout=30.0
                )

                if response.status_code != 201:
                    logger.error(f"Failed to store productivity stats: {response.status_code}")

        except Exception as e:
            logger.error(f"Error storing productivity stats: {e}")

    async def _cache_user_stats(self, stats: ProductivityStats) -> None:
        """Cache user statistics in Redis."""
        try:
            cache_key = f"user_analytics:{stats.user_id}"
            cache_data = {
                "completion_rate": stats.completion_rate,
                "total_tasks": stats.total_tasks,
                "completed_tasks": stats.completed_tasks,
                "average_completion_time": stats.average_completion_time_hours,
                "most_productive_hour": stats.most_productive_hour,
                "generated_at": datetime.utcnow().isoformat()
            }

            await self.redis_client.setex(
                cache_key,
                settings.REDIS_CACHE_TTL,
                orjson.dumps(cache_data)
            )

        except Exception as e:
            logger.error(f"Error caching user stats: {e}")

    async def _invalidate_user_stats_cache(self, user_id: int) -> None:
        """Invalidate user statistics cache."""
        try:
            await self.redis_client.delete(f"user_analytics:{user_id}")
        except Exception as e:
            logger.error(f"Error invalidating user stats cache: {e}")

    async def _periodic_analytics_generation(self) -> None:
        """Periodically generate analytics for all users."""
        while self.running:
            try:
                await asyncio.sleep(settings.ANALYTICS_INTERVAL_SECONDS)

                # Generate analytics for the last 7 days
                command = GenerateAnalyticsCommand(
                    user_id=None,  # All users
                    period_days=7
                )

                await self._generate_user_analytics(command)
                logger.info("Completed periodic analytics generation")

            except Exception as e:
                logger.error(f"Error in periodic analytics generation: {e}")

    async def _periodic_cleanup(self) -> None:
        """Periodically cleanup old data."""
        while self.running:
            try:
                await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)

                # Cleanup data older than retention period
                cleanup_date = datetime.utcnow() - timedelta(days=settings.RETENTION_DAYS)
                command = CleanupTasksCommand(
                    completed_before=cleanup_date,
                    batch_size=settings.BATCH_SIZE
                )

                await self._cleanup_old_data(command)
                logger.info("Completed periodic data cleanup")

            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

    async def _cleanup_old_data(self, command: CleanupTasksCommand) -> None:
        """Cleanup old analytics data."""
        try:
            # Cleanup MongoDB activities
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{settings.DB_MONGO_SERVICE_URL}/activities/cleanup",
                    json={
                        "completed_before": command.completed_before.isoformat(),
                        "batch_size": command.batch_size
                    },
                    timeout=120.0
                )

                if response.status_code == 200:
                    deleted_count = response.json().get("deleted_count", 0)
                    logger.info(f"Cleaned up {deleted_count} old activity records")

            # Cleanup Redis patterns older than 30 days
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            cleanup_patterns = [
                "creation_pattern:*",
                "completion_times:*",
                "productive_hour:*",
                "priority_pattern:*"
            ]

            for pattern in cleanup_patterns:
                expired_keys = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    ttl = await self.redis_client.ttl(key)
                    if ttl == -1:  # No expiration set, delete old keys
                        expired_keys.append(key)

                if expired_keys:
                    await self.redis_client.delete(*expired_keys[:100])  # Batch delete
                    logger.info(f"Cleaned up {len(expired_keys)} Redis keys for pattern {pattern}")

        except Exception as e:
            logger.error(f"Error in data cleanup: {e}")


async def main() -> None:
    """Main function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup external services
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
    )
    await redis_client.ping()
    logger.info("Redis connection established")

    rabbitmq_connection = await aio_pika.connect_robust(
        settings.RABBITMQ_URL,
        client_properties={"connection_name": "analytics_worker"}
    )
    rabbitmq_channel = await rabbitmq_connection.channel()
    await rabbitmq_channel.set_qos(prefetch_count=settings.BATCH_SIZE)
    logger.info("RabbitMQ connection established")

    # Create service
    analytics_service = AnalyticsWorkerService(redis_client, rabbitmq_channel)

    # Setup graceful shutdown
    def shutdown_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(analytics_service.stop())

    signal.signal(signal.SIGINT, lambda s, f: shutdown_handler())
    signal.signal(signal.SIGTERM, lambda s, f: shutdown_handler())

    try:
        logger.info("Starting analytics worker service...")
        await analytics_service.start()
    except Exception as e:
        logger.error(f"Analytics worker error: {e}")
        raise
    finally:
        # Cleanup
        await redis_client.close()
        await rabbitmq_channel.close()
        await rabbitmq_connection.close()
        logger.info("Analytics worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())