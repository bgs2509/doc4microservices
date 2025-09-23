"""
Task Management Reminder Worker Service - AsyncIO Implementation.

This worker service handles task reminders and notifications by monitoring
due dates, sending notifications via Telegram bot, and managing reminder
schedules. It processes events from RabbitMQ and sends notifications.

Key Features:
- Due date monitoring with configurable look-ahead
- Telegram notifications via bot API
- Overdue task detection
- Reminder scheduling and management
- Event-driven notification processing
- Graceful shutdown handling
"""

from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json

import redis.asyncio as redis
import aio_pika
import httpx
import orjson
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from shared_dtos import (
    TaskResponse, TaskDueSoonEvent, TaskOverdueEvent, ReminderEvent,
    ProcessRemindersCommand, TaskStatus
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Reminder worker configuration."""

    # External services
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://admin:admin123@rabbitmq:5672/"
    TASK_API_URL: str = "http://task_api_service:8000"
    BOT_API_URL: str = "http://task_bot_service:8000"

    # Reminder settings
    CHECK_INTERVAL_SECONDS: int = 300  # 5 minutes
    DUE_SOON_MINUTES: int = 60  # 1 hour
    OVERDUE_CHECK_MINUTES: int = 1440  # 24 hours
    REMINDER_RETRY_ATTEMPTS: int = 3
    REMINDER_RETRY_DELAY: int = 60  # 1 minute

    # Notification settings
    BATCH_SIZE: int = 50
    MAX_CONCURRENT_NOTIFICATIONS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


class ReminderWorkerService:
    """Service for handling task reminders and notifications."""

    def __init__(
        self,
        redis_client: redis.Redis,
        rabbitmq_channel: aio_pika.Channel
    ):
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel
        self.running = False
        self.notification_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_NOTIFICATIONS)

    async def start(self) -> None:
        """Start the reminder worker."""
        self.running = True
        logger.info("Starting reminder worker service")

        # Setup exchanges and queues
        await self._setup_messaging()

        # Start background tasks
        tasks = [
            asyncio.create_task(self._periodic_reminder_check(), name="reminder-check"),
            asyncio.create_task(self._process_reminder_events(), name="reminder-events"),
            asyncio.create_task(self._cleanup_old_reminders(), name="reminder-cleanup")
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Reminder worker tasks cancelled")
        except Exception as e:
            logger.error(f"Reminder worker error: {e}")
            raise

    async def stop(self) -> None:
        """Stop the reminder worker."""
        self.running = False
        logger.info("Stopping reminder worker service")

    async def _setup_messaging(self) -> None:
        """Setup RabbitMQ exchanges and queues."""
        # Task events exchange
        self.task_events_exchange = await self.rabbitmq_channel.declare_exchange(
            "task_events",
            aio_pika.ExchangeType.TOPIC
        )

        # Reminder events exchange
        self.reminder_exchange = await self.rabbitmq_channel.declare_exchange(
            "reminders",
            aio_pika.ExchangeType.DIRECT
        )

        # Reminder processing queue
        self.reminder_queue = await self.rabbitmq_channel.declare_queue(
            "reminder.process",
            durable=True
        )
        await self.reminder_queue.bind(self.reminder_exchange, routing_key="reminder.process")

        # Notification queue
        self.notification_queue = await self.rabbitmq_channel.declare_queue(
            "reminder.notify",
            durable=True
        )
        await self.notification_queue.bind(self.reminder_exchange, routing_key="reminder.notify")

        logger.info("Messaging setup complete")

    async def _periodic_reminder_check(self) -> None:
        """Periodically check for due and overdue tasks."""
        while self.running:
            try:
                await self._check_due_soon_tasks()
                await self._check_overdue_tasks()
                await asyncio.sleep(settings.CHECK_INTERVAL_SECONDS)
            except Exception as e:
                logger.error(f"Error in periodic reminder check: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _check_due_soon_tasks(self) -> None:
        """Check for tasks that are due soon."""
        try:
            now = datetime.utcnow()
            due_soon_threshold = now + timedelta(minutes=settings.DUE_SOON_MINUTES)

            # Get tasks from API that are due soon
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.TASK_API_URL}/api/v1/tasks/due-soon",
                    params={
                        "start_time": now.isoformat(),
                        "end_time": due_soon_threshold.isoformat()
                    }
                )

                if response.status_code == 200:
                    tasks_data = response.json()
                    tasks = [TaskResponse(**task) for task in tasks_data.get("tasks", [])]

                    for task in tasks:
                        await self._process_due_soon_task(task)

        except Exception as e:
            logger.error(f"Error checking due soon tasks: {e}")

    async def _check_overdue_tasks(self) -> None:
        """Check for overdue tasks."""
        try:
            now = datetime.utcnow()
            overdue_threshold = now - timedelta(minutes=settings.OVERDUE_CHECK_MINUTES)

            # Get overdue tasks from API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.TASK_API_URL}/api/v1/tasks/overdue",
                    params={
                        "overdue_since": overdue_threshold.isoformat()
                    }
                )

                if response.status_code == 200:
                    tasks_data = response.json()
                    tasks = [TaskResponse(**task) for task in tasks_data.get("tasks", [])]

                    for task in tasks:
                        await self._process_overdue_task(task)

        except Exception as e:
            logger.error(f"Error checking overdue tasks: {e}")

    async def _process_due_soon_task(self, task: TaskResponse) -> None:
        """Process a task that is due soon."""
        try:
            # Check if we already sent a due soon notification
            notification_key = f"due_soon_sent:{task.id}"
            already_sent = await self.redis_client.get(notification_key)

            if already_sent:
                return

            # Calculate minutes until due
            due_date = task.due_date
            now = datetime.utcnow()

            # Handle timezone-aware datetime
            if due_date.tzinfo is not None:
                if now.tzinfo is None:
                    now = now.replace(tzinfo=due_date.tzinfo)
            else:
                if now.tzinfo is not None:
                    now = now.replace(tzinfo=None)

            minutes_until_due = int((due_date - now).total_seconds() / 60)

            if minutes_until_due <= settings.DUE_SOON_MINUTES and minutes_until_due > 0:
                # Create due soon event
                event = TaskDueSoonEvent(
                    task_id=task.id,
                    user_id=task.user_id,
                    task_data=task,
                    due_in_minutes=minutes_until_due
                )

                # Publish event
                await self._publish_task_event("task.due_soon", event.model_dump())

                # Send notification
                await self._send_due_soon_notification(task, minutes_until_due)

                # Mark as sent (expire after task due date + 1 day)
                expire_seconds = max(minutes_until_due * 60 + 86400, 3600)
                await self.redis_client.setex(notification_key, expire_seconds, "sent")

                logger.info(f"Processed due soon task: {task.id} (due in {minutes_until_due} minutes)")

        except Exception as e:
            logger.error(f"Error processing due soon task {task.id}: {e}")

    async def _process_overdue_task(self, task: TaskResponse) -> None:
        """Process an overdue task."""
        try:
            # Check if we already sent an overdue notification recently
            notification_key = f"overdue_sent:{task.id}"
            last_sent = await self.redis_client.get(notification_key)

            if last_sent:
                # Don't spam overdue notifications - wait at least 6 hours
                last_sent_time = datetime.fromisoformat(last_sent)
                if datetime.utcnow() - last_sent_time < timedelta(hours=6):
                    return

            # Calculate how long overdue
            due_date = task.due_date
            now = datetime.utcnow()

            # Handle timezone-aware datetime
            if due_date.tzinfo is not None:
                if now.tzinfo is None:
                    now = now.replace(tzinfo=due_date.tzinfo)
            else:
                if now.tzinfo is not None:
                    now = now.replace(tzinfo=None)

            overdue_minutes = int((now - due_date).total_seconds() / 60)

            if overdue_minutes > 0:
                # Create overdue event
                event = TaskOverdueEvent(
                    task_id=task.id,
                    user_id=task.user_id,
                    task_data=task,
                    overdue_minutes=overdue_minutes
                )

                # Publish event
                await self._publish_task_event("task.overdue", event.model_dump())

                # Send notification
                await self._send_overdue_notification(task, overdue_minutes)

                # Mark as sent
                await self.redis_client.setex(
                    notification_key,
                    86400,  # 24 hours
                    datetime.utcnow().isoformat()
                )

                logger.info(f"Processed overdue task: {task.id} (overdue {overdue_minutes} minutes)")

        except Exception as e:
            logger.error(f"Error processing overdue task {task.id}: {e}")

    async def _send_due_soon_notification(self, task: TaskResponse, minutes_until_due: int) -> None:
        """Send due soon notification."""
        async with self.notification_semaphore:
            try:
                # Get user session to find Telegram ID
                user_session = await self._get_user_telegram_session(task.user_id)
                if not user_session:
                    logger.warning(f"No Telegram session found for user {task.user_id}")
                    return

                # Format time
                if minutes_until_due < 60:
                    time_str = f"{minutes_until_due} minutes"
                else:
                    hours = minutes_until_due // 60
                    remaining_minutes = minutes_until_due % 60
                    time_str = f"{hours}h {remaining_minutes}m" if remaining_minutes else f"{hours}h"

                message = f"""⏰ **Task Due Soon!**

📝 **{task.title}**
🕐 Due in: {time_str}
⚡ Priority: {task.priority.value}

{task.description[:100] + '...' if task.description and len(task.description) > 100 else task.description or ''}

💡 Quick actions:
/done {task.id} - Mark as complete
/start_task {task.id} - Start working on it"""

                # Send notification via bot service
                await self._send_telegram_notification(user_session["telegram_id"], message)

            except Exception as e:
                logger.error(f"Error sending due soon notification for task {task.id}: {e}")

    async def _send_overdue_notification(self, task: TaskResponse, overdue_minutes: int) -> None:
        """Send overdue notification."""
        async with self.notification_semaphore:
            try:
                # Get user session to find Telegram ID
                user_session = await self._get_user_telegram_session(task.user_id)
                if not user_session:
                    logger.warning(f"No Telegram session found for user {task.user_id}")
                    return

                # Format overdue time
                if overdue_minutes < 60:
                    time_str = f"{overdue_minutes} minutes"
                elif overdue_minutes < 1440:  # Less than 24 hours
                    hours = overdue_minutes // 60
                    time_str = f"{hours} hours"
                else:
                    days = overdue_minutes // 1440
                    time_str = f"{days} days"

                message = f"""🚨 **Task Overdue!**

📝 **{task.title}**
⏰ Overdue by: {time_str}
⚡ Priority: {task.priority.value}

{task.description[:100] + '...' if task.description and len(task.description) > 100 else task.description or ''}

💡 Actions:
/done {task.id} - Mark as complete
/start_task {task.id} - Start working on it
/cancel {task.id} - Cancel if no longer relevant"""

                # Send notification via bot service
                await self._send_telegram_notification(user_session["telegram_id"], message)

            except Exception as e:
                logger.error(f"Error sending overdue notification for task {task.id}: {e}")

    async def _process_reminder_events(self) -> None:
        """Process reminder events from RabbitMQ."""
        async with self.reminder_queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self.running:
                    break

                await self._handle_reminder_message(message)

    async def _handle_reminder_message(self, message: aio_pika.IncomingMessage) -> None:
        """Handle a single reminder message."""
        async with message.process():
            try:
                event_data = orjson.loads(message.body)
                command_type = event_data.get("command_type")

                if command_type == "process_reminders":
                    command = ProcessRemindersCommand(**event_data)
                    await self._process_scheduled_reminders(command)
                elif command_type == "send_reminder":
                    reminder = ReminderEvent(**event_data)
                    await self._send_custom_reminder(reminder)
                else:
                    logger.warning(f"Unknown reminder command type: {command_type}")

            except Exception as e:
                logger.error(f"Error handling reminder message: {e}")

    async def _process_scheduled_reminders(self, command: ProcessRemindersCommand) -> None:
        """Process scheduled reminders from Redis."""
        try:
            # Get reminders from Redis that are due
            current_time = command.check_time
            pattern = "reminder:*"

            async for key in self.redis_client.scan_iter(match=pattern):
                try:
                    reminder_data = await self.redis_client.get(key)
                    if reminder_data:
                        reminder = orjson.loads(reminder_data)
                        remind_at = datetime.fromisoformat(reminder["remind_at"])

                        # Check if reminder is due
                        if remind_at <= current_time:
                            await self._send_scheduled_reminder(reminder)
                            # Remove processed reminder
                            await self.redis_client.delete(key)

                except Exception as e:
                    logger.error(f"Error processing reminder {key}: {e}")

        except Exception as e:
            logger.error(f"Error processing scheduled reminders: {e}")

    async def _send_scheduled_reminder(self, reminder_data: Dict[str, Any]) -> None:
        """Send a scheduled reminder."""
        try:
            task_id = reminder_data["task_id"]
            user_id = reminder_data["user_id"]

            # Get current task data
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.TASK_API_URL}/api/v1/tasks/{task_id}",
                    headers={"X-User-ID": str(user_id)}
                )

                if response.status_code == 200:
                    task_data = response.json()
                    task = TaskResponse(**task_data)

                    # Don't send reminder for completed/cancelled tasks
                    if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                        return

                    # Get user session
                    user_session = await self._get_user_telegram_session(user_id)
                    if not user_session:
                        return

                    custom_message = reminder_data.get("message", "")
                    message = f"""🔔 **Reminder**

📝 **{task.title}**
⚡ Priority: {task.priority.value}

{custom_message or task.description or 'No description'}

💡 Actions:
/done {task.id} - Mark as complete
/start_task {task.id} - Start working"""

                    await self._send_telegram_notification(user_session["telegram_id"], message)

        except Exception as e:
            logger.error(f"Error sending scheduled reminder: {e}")

    async def _send_custom_reminder(self, reminder: ReminderEvent) -> None:
        """Send a custom reminder event."""
        try:
            if reminder.telegram_user_id:
                await self._send_telegram_notification(reminder.telegram_user_id, reminder.message)
            else:
                # Get user's Telegram ID
                user_session = await self._get_user_telegram_session(reminder.user_id)
                if user_session:
                    await self._send_telegram_notification(user_session["telegram_id"], reminder.message)

        except Exception as e:
            logger.error(f"Error sending custom reminder: {e}")

    async def _get_user_telegram_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's Telegram session data."""
        try:
            # Look for session by user_id pattern
            pattern = "bot_session:*"
            async for key in self.redis_client.scan_iter(match=pattern):
                session_data = await self.redis_client.get(key)
                if session_data:
                    session = orjson.loads(session_data)
                    if session.get("user_id") == user_id:
                        return session
            return None
        except Exception as e:
            logger.error(f"Error getting user session for {user_id}: {e}")
            return None

    async def _send_telegram_notification(self, telegram_id: int, message: str) -> None:
        """Send notification via Telegram bot."""
        try:
            # Send via bot service API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.BOT_API_URL}/send-notification",
                    json={
                        "telegram_id": telegram_id,
                        "message": message
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    logger.info(f"Notification sent to {telegram_id}")
                else:
                    logger.warning(f"Failed to send notification: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")

    async def _cleanup_old_reminders(self) -> None:
        """Cleanup old reminder data from Redis."""
        while self.running:
            try:
                # Clean up every hour
                await asyncio.sleep(3600)

                pattern = "due_soon_sent:*"
                expired_keys = []

                async for key in self.redis_client.scan_iter(match=pattern):
                    ttl = await self.redis_client.ttl(key)
                    if ttl == -1:  # No expiration set
                        expired_keys.append(key)

                if expired_keys:
                    await self.redis_client.delete(*expired_keys)
                    logger.info(f"Cleaned up {len(expired_keys)} old reminder keys")

            except Exception as e:
                logger.error(f"Error in reminder cleanup: {e}")

    async def _publish_task_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish task event to RabbitMQ."""
        try:
            message = aio_pika.Message(
                orjson.dumps(event_data),
                headers={"event_type": event_type}
            )

            await self.task_events_exchange.publish(message, routing_key=event_type)
            logger.debug(f"Published task event: {event_type}")

        except Exception as e:
            logger.error(f"Failed to publish task event {event_type}: {e}")


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
        client_properties={"connection_name": "reminder_worker"}
    )
    rabbitmq_channel = await rabbitmq_connection.channel()
    await rabbitmq_channel.set_qos(prefetch_count=10)
    logger.info("RabbitMQ connection established")

    # Create service
    reminder_service = ReminderWorkerService(redis_client, rabbitmq_channel)

    # Setup graceful shutdown
    def shutdown_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(reminder_service.stop())

    signal.signal(signal.SIGINT, lambda s, f: shutdown_handler())
    signal.signal(signal.SIGTERM, lambda s, f: shutdown_handler())

    try:
        logger.info("Starting reminder worker service...")
        await reminder_service.start()
    except Exception as e:
        logger.error(f"Reminder worker error: {e}")
        raise
    finally:
        # Cleanup
        await redis_client.close()
        await rabbitmq_channel.close()
        await rabbitmq_connection.close()
        logger.info("Reminder worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())