# Telegram Bot Service Template

**Status**: 🚧 In Development
**Purpose**: Aiogram-based Telegram bot for business logic

## Overview

This template provides an Aiogram 3.x based Telegram bot service following the framework's architecture principles for user interaction through messaging.

## Key Features

- Aiogram 3.x async bot framework
- Command and message handlers
- Inline keyboards and callbacks
- State management with FSM
- Middleware for logging and auth
- HTTP calls to data services
- Integration with RabbitMQ for events

## Architecture Compliance

Following the mandatory service separation:
- Runs as separate container/process
- Calls data services via HTTP only
- Publishes events to RabbitMQ
- No direct database access
- Stateless design (state in Redis)

## Service Structure

```
template_business_bot/
├── src/
│   ├── main.py              # Bot entry point
│   ├── config.py            # Configuration
│   ├── bot.py              # Bot instance setup
│   ├── handlers/            # Command and message handlers
│   │   ├── commands.py     # /start, /help, etc.
│   │   ├── messages.py     # Text message handlers
│   │   └── callbacks.py    # Inline button callbacks
│   ├── keyboards/           # Keyboard layouts
│   ├── middleware/          # Custom middleware
│   ├── states/              # FSM states
│   ├── services/            # Business logic
│   └── clients/             # HTTP clients for data services
├── locales/                 # i18n translations
├── tests/                   # Unit tests
├── Dockerfile               # Container definition
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Usage

When using this template:

1. **Rename the service**: Replace `template_business_bot` with your actual service name (e.g., `healthcare_appointment_bot`)
2. **Set bot token**: Configure TELEGRAM_BOT_TOKEN in environment
3. **Define handlers**: Create command and message handlers
4. **Setup keyboards**: Design user interaction flows
5. **Implement business logic**: Add service layer methods
6. **Configure data access**: Setup HTTP clients for data services

## Example Handlers

```python
# /start command
@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Welcome to the bot!")

# Text message handler
@router.message(F.text)
async def text_handler(message: Message):
    # Process text message
    pass

# Inline button callback
@router.callback_query(F.data.startswith("action_"))
async def callback_handler(callback: CallbackQuery):
    # Handle button press
    pass
```

## Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
REDIS_URL=redis://redis:6379/0
DATA_SERVICE_URL=http://template_data_postgres_api:8001
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
LOG_LEVEL=INFO
```

## Bot Commands

- `/start` - Initialize bot interaction
- `/help` - Show available commands
- `/menu` - Display main menu
- `/cancel` - Cancel current operation
- `/status` - Check service status

## Related Documentation

- [Aiogram Patterns](../../../docs/atomic/services/aiogram/)
- [Redis Integration](../../../docs/atomic/integrations/redis/)
- [RabbitMQ Events](../../../docs/atomic/integrations/rabbitmq/)
- [HTTP Communication](../../../docs/atomic/integrations/http-communication/)

---

**Note**: This is a template. Full implementation coming soon.