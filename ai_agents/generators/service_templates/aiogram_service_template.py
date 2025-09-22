# Aiogram Bot Service Template for AI Code Generation
# Template variables are marked with {{variable_name}} format

"""
{{bot_service_name}} - Telegram Bot Service

This service implements the {{business_domain}} Telegram bot interface
following the Improved Hybrid Approach architecture pattern.

Generated from business requirements:
{{business_requirements}}
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable

import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import structlog

# Configuration
from .config import BotSettings
from .models import {{bot_model_imports}}

# Initialize structured logging
logger = structlog.get_logger(__name__)

# Settings
settings = BotSettings()

# Bot and dispatcher
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()

# HTTP client for data service communication
http_client: Optional[httpx.AsyncClient] = None

# Data service client
class BotDataServiceClient:
    """Client for bot to communicate with data services"""

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
            logger.error("bot_postgres_service_error", error=str(e), endpoint=endpoint)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("bot_postgres_service_http_error", status_code=e.response.status_code, endpoint=endpoint)
            raise

    async def mongo_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make request to MongoDB data service"""
        url = f"{self.mongo_url}{endpoint}"

        try:
            response = await http_client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error("bot_mongo_service_error", error=str(e), endpoint=endpoint)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("bot_mongo_service_http_error", status_code=e.response.status_code, endpoint=endpoint)
            raise

# Global data client instance
data_client = BotDataServiceClient()

# User management utilities
async def get_or_create_user(telegram_user: types.User) -> Dict[str, Any]:
    """Get or create user in the system"""
    try:
        # Try to get existing user
        user_data = await data_client.postgres_request(
            "GET",
            f"/users/telegram/{telegram_user.id}"
        )
        return user_data
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # Create new user
            new_user = {
                "telegram_id": telegram_user.id,
                "username": telegram_user.username,
                "first_name": telegram_user.first_name,
                "last_name": telegram_user.last_name,
            }
            user_data = await data_client.postgres_request(
                "POST",
                "/users",
                json=new_user
            )
            logger.info("new_telegram_user_created", user_id=user_data["id"], telegram_id=telegram_user.id)
            return user_data
        else:
            raise

# Middleware for request logging and user tracking
@dp.message.middleware()
async def logging_middleware(handler: Callable, event: Message, data: Dict[str, Any]):
    """Log all bot interactions"""
    logger.info(
        "bot_message_received",
        user_id=event.from_user.id,
        username=event.from_user.username,
        message_type=event.content_type,
        chat_type=event.chat.type
    )

    # Ensure user exists in system
    try:
        user_data = await get_or_create_user(event.from_user)
        data["system_user"] = user_data
    except Exception as e:
        logger.error("user_creation_failed", error=str(e), telegram_user_id=event.from_user.id)
        await event.answer("❌ Service temporarily unavailable. Please try again later.")
        return

    return await handler(event, data)

@dp.callback_query.middleware()
async def callback_middleware(handler: Callable, event: CallbackQuery, data: Dict[str, Any]):
    """Log callback queries"""
    logger.info(
        "bot_callback_received",
        user_id=event.from_user.id,
        callback_data=event.data
    )

    # Ensure user exists in system
    try:
        user_data = await get_or_create_user(event.from_user)
        data["system_user"] = user_data
    except Exception as e:
        logger.error("user_creation_failed", error=str(e), telegram_user_id=event.from_user.id)
        await event.answer("❌ Service temporarily unavailable. Please try again later.")
        return

    return await handler(event, data)

# Command handlers for {{business_domain}}
@dp.message(Command("start"))
async def start_command(message: Message, system_user: Dict[str, Any]):
    """Handle /start command"""
    welcome_text = f"""
🚀 Welcome to {{bot_title}}, {system_user['first_name']}!

{{bot_description}}

Available commands:
{{command_list}}

Use /help to see all available commands.
    """

    keyboard = InlineKeyboardBuilder()
    {{start_command_buttons}}

    await message.answer(
        welcome_text.strip(),
        reply_markup=keyboard.as_markup()
    )

    # Log user activity
    await data_client.mongo_request(
        "POST",
        "/analytics/user_activities",
        json={
            "user_id": system_user["id"],
            "activity_type": "bot_start",
            "timestamp": message.date.isoformat(),
            "metadata": {"telegram_id": message.from_user.id}
        }
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    help_text = """
📚 Available Commands:

{{help_commands_list}}

💡 Tips:
{{help_tips}}
    """

    await message.answer(help_text.strip())

{{business_command_handlers}}

# Callback query handlers
{{callback_handlers}}

# Message handlers
{{message_handlers}}

# Error handler
@dp.error()
async def error_handler(event: types.ErrorEvent):
    """Handle bot errors"""
    logger.error(
        "bot_error_occurred",
        error=str(event.exception),
        update=event.update.model_dump() if event.update else None
    )

    # Try to send error message to user if possible
    if event.update and event.update.message:
        try:
            await event.update.message.answer(
                "❌ An error occurred. Please try again or contact support."
            )
        except Exception:
            pass  # Can't send error message

# Utility functions for {{business_domain}}
{{utility_functions}}

# Notification functions
async def send_notification_to_user(user_id: int, message: str, keyboard: Optional[InlineKeyboardMarkup] = None):
    """Send notification to specific user"""
    try:
        # Get user's Telegram ID
        user_data = await data_client.postgres_request("GET", f"/users/{user_id}")
        telegram_id = user_data["telegram_id"]

        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            reply_markup=keyboard
        )

        logger.info("notification_sent", user_id=user_id, telegram_id=telegram_id)

    except Exception as e:
        logger.error("notification_failed", user_id=user_id, error=str(e))

async def broadcast_notification(message: str, user_filter: Optional[Dict] = None):
    """Broadcast notification to multiple users"""
    try:
        # Get users from PostgreSQL service
        endpoint = "/users"
        if user_filter:
            # Add query parameters for filtering
            params = "&".join([f"{k}={v}" for k, v in user_filter.items()])
            endpoint += f"?{params}"

        users_data = await data_client.postgres_request("GET", endpoint)

        for user in users_data:
            if user.get("telegram_id"):
                try:
                    await bot.send_message(
                        chat_id=user["telegram_id"],
                        text=message
                    )
                except Exception as e:
                    logger.error("broadcast_failed_for_user", user_id=user["id"], error=str(e))

        logger.info("broadcast_completed", total_users=len(users_data))

    except Exception as e:
        logger.error("broadcast_failed", error=str(e))

# Health check for bot service
async def health_check() -> bool:
    """Check if bot service is healthy"""
    try:
        # Check bot connection
        bot_info = await bot.get_me()
        logger.info("bot_health_check", bot_username=bot_info.username)

        # Check data services
        await data_client.postgres_request("GET", "/health")
        await data_client.mongo_request("GET", "/health")

        return True
    except Exception as e:
        logger.error("bot_health_check_failed", error=str(e))
        return False

# Main function
async def main():
    """Main bot function"""
    global http_client

    # Initialize HTTP client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=50)
    )

    try:
        logger.info("starting_{{bot_service_name}}")

        # Verify data service connections
        await data_client.postgres_request("GET", "/health")
        await data_client.mongo_request("GET", "/health")
        logger.info("data_services_connected")

        # Start bot polling
        await dp.start_polling(bot)

    except Exception as e:
        logger.error("bot_startup_failed", error=str(e))
        raise
    finally:
        # Cleanup
        if http_client:
            await http_client.aclose()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())