"""
Task Management Telegram Bot Service - Aiogram Implementation.

This service provides a Telegram bot interface for managing tasks with natural
language commands, file attachments, and real-time notifications. It communicates
with the API service via HTTP and publishes events via RabbitMQ.

Key Features:
- Natural language task creation
- Quick task status updates
- File attachment support
- Due date parsing
- Task reminders via chat
- User productivity stats
- Inline keyboards for task actions
"""

from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import re
from io import BytesIO

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    BufferedInputFile, FSInputFile
)
from aiogram.filters import Command, CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
import redis.asyncio as redis
import aio_pika
import httpx
import orjson
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dateutil import parser as date_parser

from shared_dtos import (
    TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority,
    BotTaskCreateRequest, BotCommandResponse, AttachmentInfo,
    AttachmentUploadedEvent, ReminderEvent
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Bot service configuration."""

    # Bot settings
    BOT_TOKEN: str
    BOT_USERNAME: str = "taskmanager_bot"

    # External services
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://admin:admin123@rabbitmq:5672/"
    TASK_API_URL: str = "http://api_service:8000"

    # File handling
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif",
        "application/pdf", "text/plain",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


class UserSession(BaseModel):
    """User session data."""
    user_id: int
    telegram_id: int
    auth_token: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None


class TaskBotService:
    """Service layer for bot operations."""

    def __init__(
        self,
        redis_client: redis.Redis,
        rabbitmq_channel: aio_pika.Channel,
        api_base_url: str
    ):
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel
        self.api_base_url = api_base_url

    async def get_user_session(self, telegram_id: int) -> Optional[UserSession]:
        """Get user session from Redis."""
        session_data = await self.redis_client.get(f"bot_session:{telegram_id}")
        if session_data:
            return UserSession(**orjson.loads(session_data))
        return None

    async def save_user_session(self, session: UserSession) -> None:
        """Save user session to Redis."""
        await self.redis_client.setex(
            f"bot_session:{session.telegram_id}",
            86400,  # 24 hours
            orjson.dumps(session.model_dump())
        )

    async def authenticate_user(self, telegram_id: int, username: str) -> UserSession:
        """Authenticate user and create session."""
        # Try to get existing user via API
        async with httpx.AsyncClient() as client:
            try:
                # First try to login/register user
                response = await client.post(
                    f"{self.api_base_url}/auth/telegram",
                    json={
                        "telegram_id": telegram_id,
                        "username": username
                    }
                )
                response.raise_for_status()
                auth_data = response.json()

                session = UserSession(
                    user_id=auth_data["user_id"],
                    telegram_id=telegram_id,
                    auth_token=auth_data["access_token"],
                    username=username
                )

                await self.save_user_session(session)
                return session

            except httpx.HTTPError as e:
                logger.error(f"Authentication failed for {telegram_id}: {e}")
                raise

    async def create_task_from_text(
        self,
        session: UserSession,
        text: str
    ) -> BotCommandResponse:
        """Create task from natural language text."""
        try:
            # Parse the text for task details
            parsed = self._parse_task_text(text)

            task_data = TaskCreate(
                title=parsed["title"],
                description=parsed.get("description"),
                priority=parsed.get("priority", TaskPriority.MEDIUM),
                due_date=parsed.get("due_date")
            )

            # Create task via API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/api/v1/tasks",
                    json=task_data.model_dump(),
                    headers={"Authorization": f"Bearer {session.auth_token}"}
                )
                response.raise_for_status()
                task = TaskResponse(**response.json())

                return BotCommandResponse(
                    success=True,
                    message=f"✅ Task created: {task.title}\n"
                           f"📝 ID: {task.id}\n"
                           f"⚡ Priority: {task.priority.value}\n"
                           + (f"📅 Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}" if task.due_date else ""),
                    data={"task_id": task.id, "task": task.model_dump()}
                )

        except httpx.HTTPError as e:
            logger.error(f"Failed to create task: {e}")
            return BotCommandResponse(
                success=False,
                message="❌ Failed to create task. Please try again."
            )
        except Exception as e:
            logger.error(f"Error parsing task: {e}")
            return BotCommandResponse(
                success=False,
                message="❌ Could not understand the task. Please try: /task [title] [description]"
            )

    async def get_user_tasks(
        self,
        session: UserSession,
        status_filter: Optional[str] = None
    ) -> BotCommandResponse:
        """Get user's tasks with optional status filter."""
        try:
            params = {"per_page": 10}
            if status_filter:
                params["status"] = status_filter

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/api/v1/tasks",
                    params=params,
                    headers={"Authorization": f"Bearer {session.auth_token}"}
                )
                response.raise_for_status()
                task_list = response.json()

                if not task_list["tasks"]:
                    message = "📂 No tasks found."
                    if status_filter:
                        message += f" (Status: {status_filter})"
                    return BotCommandResponse(success=True, message=message)

                # Format task list
                message_lines = ["📋 Your tasks:\n"]
                for task in task_list["tasks"]:
                    status_emoji = {
                        "todo": "⏳",
                        "in_progress": "🔄",
                        "completed": "✅",
                        "cancelled": "❌"
                    }.get(task["status"], "❓")

                    priority_emoji = {
                        "low": "🟢",
                        "medium": "🟡",
                        "high": "🟠",
                        "urgent": "🔴"
                    }.get(task["priority"], "⚪")

                    due_text = ""
                    if task["due_date"]:
                        due_date = datetime.fromisoformat(task["due_date"].replace("Z", "+00:00"))
                        if due_date < datetime.now(due_date.tzinfo):
                            due_text = f" 🚨 OVERDUE"
                        else:
                            due_text = f" 📅 {due_date.strftime('%m/%d %H:%M')}"

                    message_lines.append(
                        f"{status_emoji} {priority_emoji} {task['id']}: {task['title'][:30]}"
                        + ("..." if len(task['title']) > 30 else "") + due_text
                    )

                return BotCommandResponse(
                    success=True,
                    message="\n".join(message_lines),
                    data={"tasks": task_list["tasks"], "total": task_list["total"]}
                )

        except httpx.HTTPError as e:
            logger.error(f"Failed to get tasks: {e}")
            return BotCommandResponse(
                success=False,
                message="❌ Failed to retrieve tasks. Please try again."
            )

    async def update_task_status(
        self,
        session: UserSession,
        task_id: int,
        new_status: TaskStatus
    ) -> BotCommandResponse:
        """Update task status."""
        try:
            task_data = TaskUpdate(status=new_status)

            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.api_base_url}/api/v1/tasks/{task_id}",
                    json=task_data.model_dump(exclude_unset=True),
                    headers={"Authorization": f"Bearer {session.auth_token}"}
                )

                if response.status_code == 404:
                    return BotCommandResponse(
                        success=False,
                        message="❌ Task not found."
                    )

                response.raise_for_status()
                task = TaskResponse(**response.json())

                status_messages = {
                    TaskStatus.TODO: "⏳ Task marked as Todo",
                    TaskStatus.IN_PROGRESS: "🔄 Task marked as In Progress",
                    TaskStatus.COMPLETED: "✅ Task completed! Great job!",
                    TaskStatus.CANCELLED: "❌ Task cancelled"
                }

                return BotCommandResponse(
                    success=True,
                    message=f"{status_messages[new_status]}\n📝 {task.title}",
                    data={"task": task.model_dump()}
                )

        except httpx.HTTPError as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return BotCommandResponse(
                success=False,
                message="❌ Failed to update task. Please try again."
            )

    async def get_task_stats(self, session: UserSession) -> BotCommandResponse:
        """Get user productivity statistics."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/api/v1/tasks/stats",
                    headers={"Authorization": f"Bearer {session.auth_token}"}
                )
                response.raise_for_status()
                stats = response.json()

                message = f"""📊 Your Productivity Stats:

📋 Total Tasks: {stats['total_tasks']}
✅ Completed: {stats['completed_tasks']}
⏳ Pending: {stats['pending_tasks']}
🚨 Overdue: {stats['overdue_tasks']}
📈 Completion Rate: {stats['completion_rate']:.1%}

📊 By Priority:
🔴 Urgent: {stats['tasks_by_priority'].get('urgent', 0)}
🟠 High: {stats['tasks_by_priority'].get('high', 0)}
🟡 Medium: {stats['tasks_by_priority'].get('medium', 0)}
🟢 Low: {stats['tasks_by_priority'].get('low', 0)}"""

                return BotCommandResponse(
                    success=True,
                    message=message,
                    data=stats
                )

        except httpx.HTTPError as e:
            logger.error(f"Failed to get stats: {e}")
            return BotCommandResponse(
                success=False,
                message="❌ Failed to retrieve statistics."
            )

    def _parse_task_text(self, text: str) -> Dict[str, Any]:
        """Parse natural language text into task components."""
        result = {"title": text.strip()}

        # Extract priority keywords
        priority_patterns = {
            TaskPriority.URGENT: [r'\burgent\b', r'\basap\b', r'!!!'],
            TaskPriority.HIGH: [r'\bhigh\b', r'\bimportant\b', r'!!'],
            TaskPriority.LOW: [r'\blow\b', r'\blater\b', r'\bmaybe\b']
        }

        for priority, patterns in priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    result["priority"] = priority
                    # Remove priority keywords from title
                    result["title"] = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                    break
            if "priority" in result:
                break

        # Extract due date patterns
        due_patterns = [
            r'due\s+(.+?)(?:\s|$)',
            r'by\s+(.+?)(?:\s|$)',
            r'on\s+(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
            r'(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'in\s+(\d+)\s+(hour|hours|day|days|week|weeks)'
        ]

        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_text = match.group(1)
                try:
                    # Try to parse the date
                    if date_text.lower() == "today":
                        result["due_date"] = datetime.now().replace(hour=23, minute=59)
                    elif date_text.lower() == "tomorrow":
                        result["due_date"] = (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59)
                    elif "in" in text.lower() and ("hour" in date_text or "day" in date_text):
                        # Handle "in X hours/days"
                        amount = int(re.search(r'(\d+)', date_text).group(1))
                        if "hour" in date_text:
                            result["due_date"] = datetime.now() + timedelta(hours=amount)
                        else:
                            result["due_date"] = datetime.now() + timedelta(days=amount)
                    else:
                        # Try to parse with dateutil
                        result["due_date"] = date_parser.parse(date_text)

                    # Remove due date from title
                    result["title"] = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                    break
                except (ValueError, AttributeError):
                    continue

        # Clean up title
        result["title"] = re.sub(r'\s+', ' ', result["title"]).strip()

        # Extract description if title is very long
        if len(result["title"]) > 100:
            words = result["title"].split()
            result["title"] = " ".join(words[:10])
            result["description"] = " ".join(words[10:])

        return result

    async def process_file_attachment(
        self,
        session: UserSession,
        file_id: str,
        file_name: str,
        file_size: int,
        content_type: str,
        file_data: bytes,
        task_id: Optional[int] = None
    ) -> BotCommandResponse:
        """Process file attachment for a task."""
        try:
            # Validate file
            if file_size > settings.MAX_FILE_SIZE:
                return BotCommandResponse(
                    success=False,
                    message=f"❌ File too large. Maximum size is {settings.MAX_FILE_SIZE // 1024 // 1024}MB."
                )

            if content_type not in settings.ALLOWED_FILE_TYPES:
                return BotCommandResponse(
                    success=False,
                    message="❌ File type not allowed."
                )

            # Create attachment info
            attachment = AttachmentInfo(
                id=file_id,
                task_id=task_id or 0,  # Will be set later if task is created
                filename=file_name,
                content_type=content_type,
                size=file_size,
                uploaded_at=datetime.utcnow(),
                telegram_file_id=file_id
            )

            # Publish attachment uploaded event for processing
            event = AttachmentUploadedEvent(
                task_id=task_id or 0,
                user_id=session.user_id,
                attachment_info=attachment,
                file_data=file_data
            )

            await self._publish_event("attachment.uploaded", event.model_dump())

            return BotCommandResponse(
                success=True,
                message=f"📎 File uploaded: {file_name}\n"
                       f"📏 Size: {file_size} bytes\n"
                       f"🔄 Processing...",
                data={"attachment": attachment.model_dump()}
            )

        except Exception as e:
            logger.error(f"Failed to process attachment: {e}")
            return BotCommandResponse(
                success=False,
                message="❌ Failed to process file attachment."
            )

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


# Bot setup
async def setup_bot_and_services() -> tuple[Bot, Dispatcher, TaskBotService]:
    """Setup bot, dispatcher and services."""
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

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
        client_properties={"connection_name": "task_bot_service"}
    )
    rabbitmq_channel = await rabbitmq_connection.channel()
    logger.info("RabbitMQ connection established")

    # Create service
    bot_service = TaskBotService(redis_client, rabbitmq_channel, settings.TASK_API_URL)

    # Store in dispatcher data for handlers
    dp["bot_service"] = bot_service
    dp["redis_client"] = redis_client
    dp["rabbitmq_connection"] = rabbitmq_connection
    dp["rabbitmq_channel"] = rabbitmq_channel

    return bot, dp, bot_service


# Handlers
router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, bot_service: TaskBotService = None):
    """Handle /start command."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    try:
        session = await bot_service.authenticate_user(
            message.from_user.id,
            message.from_user.username or f"user_{message.from_user.id}"
        )

        welcome_text = f"""👋 Welcome to Task Manager Bot!

I'll help you manage your tasks efficiently. Here's what I can do:

📝 **Create Tasks:**
• /task Buy groceries tomorrow high priority
• /task Meeting at 3pm due today
• /task Write report

📋 **Manage Tasks:**
• /mytasks - Show your tasks
• /done 123 - Mark task as complete
• /start_task 123 - Mark as in progress
• /cancel 123 - Cancel a task

📊 **Track Progress:**
• /stats - Your productivity statistics
• /pending - Show pending tasks
• /completed - Show completed tasks

📎 **Attachments:**
Just send me files and I'll attach them to your tasks!

💡 **Pro Tips:**
• Use keywords like "urgent", "high", "low" for priority
• Say "due tomorrow", "by friday" for due dates
• Use "!!" for high priority, "!!!" for urgent

Ready to boost your productivity? Try: /task Test task"""

        await message.reply(welcome_text)

    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.reply("❌ Authentication failed. Please try again later.")


@router.message(Command("task"))
async def handle_create_task(message: Message, bot_service: TaskBotService = None):
    """Handle task creation."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    # Extract task text after command
    task_text = message.text[5:].strip()  # Remove "/task"
    if not task_text:
        await message.reply("❌ Please provide a task description.\nExample: /task Buy groceries tomorrow")
        return

    result = await bot_service.create_task_from_text(session, task_text)
    await message.reply(result.message)


@router.message(Command("mytasks"))
async def handle_my_tasks(message: Message, bot_service: TaskBotService = None):
    """Handle task listing."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    result = await bot_service.get_user_tasks(session)
    await message.reply(result.message)


@router.message(Command("pending"))
async def handle_pending_tasks(message: Message, bot_service: TaskBotService = None):
    """Handle pending task listing."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    result = await bot_service.get_user_tasks(session, "todo")
    await message.reply(result.message)


@router.message(Command("completed"))
async def handle_completed_tasks(message: Message, bot_service: TaskBotService = None):
    """Handle completed task listing."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    result = await bot_service.get_user_tasks(session, "completed")
    await message.reply(result.message)


@router.message(Command("done"))
async def handle_task_done(message: Message, bot_service: TaskBotService = None):
    """Handle task completion."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    # Extract task ID
    try:
        task_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.reply("❌ Please provide a task ID.\nExample: /done 123")
        return

    result = await bot_service.update_task_status(session, task_id, TaskStatus.COMPLETED)
    await message.reply(result.message)


@router.message(Command("start_task"))
async def handle_start_task(message: Message, bot_service: TaskBotService = None):
    """Handle starting a task."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    try:
        task_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.reply("❌ Please provide a task ID.\nExample: /start_task 123")
        return

    result = await bot_service.update_task_status(session, task_id, TaskStatus.IN_PROGRESS)
    await message.reply(result.message)


@router.message(Command("cancel"))
async def handle_cancel_task(message: Message, bot_service: TaskBotService = None):
    """Handle task cancellation."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    try:
        task_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.reply("❌ Please provide a task ID.\nExample: /cancel 123")
        return

    result = await bot_service.update_task_status(session, task_id, TaskStatus.CANCELLED)
    await message.reply(result.message)


@router.message(Command("stats"))
async def handle_stats(message: Message, bot_service: TaskBotService = None):
    """Handle statistics request."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    result = await bot_service.get_task_stats(session)
    await message.reply(result.message)


@router.message(F.document)
async def handle_document(message: Message, bot_service: TaskBotService = None):
    """Handle document uploads."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    doc = message.document

    try:
        # Download file
        file_info = await message.bot.get_file(doc.file_id)
        file_data = await message.bot.download_file(file_info.file_path)

        result = await bot_service.process_file_attachment(
            session,
            doc.file_id,
            doc.file_name or f"document_{doc.file_id}",
            doc.file_size,
            doc.mime_type or "application/octet-stream",
            file_data.read()
        )

        await message.reply(result.message)

    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await message.reply("❌ Failed to process document.")


@router.message(F.photo)
async def handle_photo(message: Message, bot_service: TaskBotService = None):
    """Handle photo uploads."""
    if not bot_service:
        bot_service = message.bot.get('dp')["bot_service"]

    session = await bot_service.get_user_session(message.from_user.id)
    if not session:
        await message.reply("❌ Please start with /start first.")
        return

    photo = message.photo[-1]  # Get largest size

    try:
        # Download photo
        file_info = await message.bot.get_file(photo.file_id)
        file_data = await message.bot.download_file(file_info.file_path)

        result = await bot_service.process_file_attachment(
            session,
            photo.file_id,
            f"photo_{photo.file_id}.jpg",
            photo.file_size,
            "image/jpeg",
            file_data.read()
        )

        await message.reply(result.message)

    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await message.reply("❌ Failed to process photo.")


async def shutdown_handler(dp: Dispatcher) -> None:
    """Graceful shutdown handler."""
    logger.info("Shutting down bot service...")

    # Close external connections
    redis_client = dp["redis_client"]
    rabbitmq_connection = dp["rabbitmq_connection"]
    rabbitmq_channel = dp["rabbitmq_channel"]

    await redis_client.close()
    await rabbitmq_channel.close()
    await rabbitmq_connection.close()

    logger.info("Bot service shutdown complete")


async def main() -> None:
    """Main function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup bot and services
    bot, dp, bot_service = await setup_bot_and_services()

    # Include routers
    dp.include_router(router)

    # Setup graceful shutdown
    def signal_handler():
        asyncio.create_task(shutdown_handler(dp))

    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

    try:
        logger.info("Starting Task Management Bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await shutdown_handler(dp)


if __name__ == "__main__":
    asyncio.run(main())