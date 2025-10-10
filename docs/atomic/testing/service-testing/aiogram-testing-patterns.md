# Aiogram Service Testing Patterns

Test Aiogram bot handlers, FSM states, middleware, and filters to verify message processing, state transitions, and callback handling without connecting to real Telegram servers. Service-level bot tests validate business logic and user interaction flows in isolation.

This document covers testing patterns for Aiogram 3.x bots using pytest-aiogram, mocking Telegram API calls, testing FSM state machines, handler validation, and middleware verification. Aiogram service tests ensure your bot responds correctly to user interactions.

Testing Aiogram bots validates that handlers process messages correctly, FSM transitions work as expected, filters match appropriate updates, and keyboard interactions trigger correct responses. These tests run quickly while providing confidence in bot behavior.

## Setup and Configuration

### Basic Test Setup

```python
# tests/service/test_bot_handlers.py
import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, User, Chat
from aiogram.enums import ChatType
from unittest.mock import AsyncMock


@pytest.fixture
def bot():
    """Provide mocked bot instance."""
    bot = Bot(token="TEST_TOKEN:test")
    bot.session = AsyncMock()
    return bot


@pytest.fixture
def dispatcher():
    """Provide dispatcher with memory storage."""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    # Register handlers here
    return dp


@pytest.fixture
def user():
    """Provide test user."""
    return User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="en"
    )


@pytest.fixture
def chat():
    """Provide test chat."""
    return Chat(
        id=123456789,
        type=ChatType.PRIVATE
    )
```

### Mocking Message Objects

```python
# CORRECT: Create mock Message for testing
def create_message(text: str, user: User, chat: Chat, bot: Bot) -> Message:
    """Create Message object for testing."""
    return Message(
        message_id=1,
        date=1234567890,
        chat=chat,
        from_user=user,
        text=text,
        bot=bot
    )


# CORRECT: Helper for quick message creation
@pytest.fixture
def message_factory(bot, user, chat):
    """Provide factory for creating test messages."""
    def _create(text: str) -> Message:
        return create_message(text=text, user=user, chat=chat, bot=bot)
    return _create
```

## Testing Message Handlers

### Basic Command Handlers

```python
# src/handlers/start.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(f"Welcome, {message.from_user.first_name}!")


# CORRECT: Test command handler
@pytest.mark.service
@pytest.mark.asyncio
async def test_start_command(bot, user, chat, message_factory):
    """Test /start command sends welcome message."""
    from src.handlers.start import cmd_start

    # Create message
    message = message_factory("/start")
    message.answer = AsyncMock()

    # Call handler
    await cmd_start(message)

    # Verify response
    message.answer.assert_called_once()
    call_args = message.answer.call_args[1] if message.answer.call_args[1] else {}
    response_text = message.answer.call_args[0][0] if message.answer.call_args[0] else call_args.get("text", "")
    assert "Welcome" in response_text
    assert user.first_name in response_text


# CORRECT: Test command with parameters
@pytest.mark.service
@pytest.mark.asyncio
async def test_help_command(message_factory):
    """Test /help command returns help text."""
    from src.handlers.help import cmd_help

    message = message_factory("/help")
    message.answer = AsyncMock()

    await cmd_help(message)

    message.answer.assert_called_once()
    response_text = message.answer.call_args[0][0]
    assert "Available commands" in response_text
```

### Text Message Handlers

```python
# CORRECT: Test text message handler
@pytest.mark.service
@pytest.mark.asyncio
async def test_echo_handler(message_factory):
    """Test echo handler repeats message."""
    from src.handlers.echo import echo_handler

    message = message_factory("Hello, bot!")
    message.answer = AsyncMock()

    await echo_handler(message)

    message.answer.assert_called_once_with("You said: Hello, bot!")


# CORRECT: Test message with specific content
@pytest.mark.service
@pytest.mark.asyncio
async def test_loan_request_handler(message_factory):
    """Test loan request extracts amount."""
    from src.handlers.loans import handle_loan_request

    message = message_factory("I need a loan of $5000")
    message.answer = AsyncMock()

    await handle_loan_request(message)

    message.answer.assert_called_once()
    response = message.answer.call_args[0][0]
    assert "5000" in response
    assert "loan application" in response.lower()
```

## Testing FSM (Finite State Machine)

### FSM State Testing

```python
# src/states/loan_application.py
from aiogram.fsm.state import State, StatesGroup


class LoanApplicationStates(StatesGroup):
    """States for loan application flow."""
    waiting_for_amount = State()
    waiting_for_purpose = State()
    waiting_for_confirmation = State()


# CORRECT: Test FSM state transitions
@pytest.mark.service
@pytest.mark.asyncio
async def test_loan_application_flow(bot, user, chat, message_factory):
    """Test complete loan application FSM flow."""
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.memory import MemoryStorage
    from src.handlers.loan import start_loan_application, process_loan_amount, process_loan_purpose

    storage = MemoryStorage()
    state = FSMContext(storage=storage, key=f"user:{user.id}:chat:{chat.id}")

    # Step 1: Start application
    message = message_factory("/apply_loan")
    message.answer = AsyncMock()
    await start_loan_application(message, state)

    # Verify state transition
    current_state = await state.get_state()
    assert current_state == LoanApplicationStates.waiting_for_amount.state

    # Step 2: Provide amount
    message = message_factory("10000")
    message.answer = AsyncMock()
    await process_loan_amount(message, state)

    # Verify data stored and state updated
    data = await state.get_data()
    assert data["amount"] == 10000
    current_state = await state.get_state()
    assert current_state == LoanApplicationStates.waiting_for_purpose.state

    # Step 3: Provide purpose
    message = message_factory("Business expansion")
    message.answer = AsyncMock()
    await process_loan_purpose(message, state)

    # Verify completion
    data = await state.get_data()
    assert data["purpose"] == "Business expansion"


# CORRECT: Test FSM cancellation
@pytest.mark.service
@pytest.mark.asyncio
async def test_cancel_fsm(message_factory):
    """Test cancelling FSM flow."""
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.memory import MemoryStorage
    from src.handlers.common import cmd_cancel

    storage = MemoryStorage()
    state = FSMContext(storage=storage, key="test:123")

    # Set initial state
    await state.set_state(LoanApplicationStates.waiting_for_amount)

    # Cancel
    message = message_factory("/cancel")
    message.answer = AsyncMock()
    await cmd_cancel(message, state)

    # Verify state cleared
    current_state = await state.get_state()
    assert current_state is None

    # Verify confirmation message
    message.answer.assert_called_once()
    response = message.answer.call_args[0][0]
    assert "cancelled" in response.lower()
```

## Testing Callback Query Handlers

### Inline Keyboard Callbacks

```python
# CORRECT: Test callback query handler
@pytest.mark.service
@pytest.mark.asyncio
async def test_callback_approve_loan(bot, user):
    """Test loan approval callback."""
    from aiogram.types import CallbackQuery, Message as Msg
    from src.handlers.loan import callback_approve_loan

    # Create callback query
    callback = CallbackQuery(
        id="callback-123",
        from_user=user,
        message=Msg(
            message_id=1,
            date=1234567890,
            chat=Chat(id=user.id, type=ChatType.PRIVATE),
            text="Approve this loan?",
            bot=bot
        ),
        data="approve_loan:12345",
        chat_instance="test"
    )
    callback.answer = AsyncMock()
    callback.message.edit_text = AsyncMock()

    # Call handler
    await callback_approve_loan(callback)

    # Verify callback answered
    callback.answer.assert_called_once()

    # Verify message edited
    callback.message.edit_text.assert_called_once()
    edit_text = callback.message.edit_text.call_args[0][0]
    assert "approved" in edit_text.lower()


# CORRECT: Test callback with data extraction
@pytest.mark.service
@pytest.mark.asyncio
async def test_callback_select_option(bot, user):
    """Test callback extracts option from data."""
    from aiogram.types import CallbackQuery, Message as Msg
    from src.handlers.menu import callback_select_option

    callback = CallbackQuery(
        id="cb-456",
        from_user=user,
        message=Msg(
            message_id=2,
            date=1234567890,
            chat=Chat(id=user.id, type=ChatType.PRIVATE),
            text="Select an option:",
            bot=bot
        ),
        data="option:premium",
        chat_instance="test"
    )
    callback.answer = AsyncMock()
    callback.message.answer = AsyncMock()

    await callback_select_option(callback)

    # Verify correct option processed
    callback.message.answer.assert_called_once()
    response = callback.message.answer.call_args[0][0]
    assert "premium" in response.lower()
```

## Testing Filters

### Custom Filter Testing

```python
# src/filters/user_role.py
from aiogram.filters import Filter
from aiogram.types import Message


class IsAdminFilter(Filter):
    """Filter messages from admin users."""

    async def __call__(self, message: Message) -> bool:
        """Check if user is admin."""
        admin_ids = [111111, 222222, 333333]
        return message.from_user.id in admin_ids


# CORRECT: Test custom filter
@pytest.mark.service
@pytest.mark.asyncio
async def test_admin_filter_accepts_admin(bot, chat):
    """Test admin filter accepts admin users."""
    from src.filters.user_role import IsAdminFilter

    # Admin user
    admin_user = User(id=111111, is_bot=False, first_name="Admin")
    message = create_message("test", admin_user, chat, bot)

    filter_instance = IsAdminFilter()
    result = await filter_instance(message)

    assert result is True


@pytest.mark.service
@pytest.mark.asyncio
async def test_admin_filter_rejects_regular_user(bot, user, chat):
    """Test admin filter rejects regular users."""
    from src.filters.user_role import IsAdminFilter

    # Regular user (ID not in admin list)
    message = create_message("test", user, chat, bot)

    filter_instance = IsAdminFilter()
    result = await filter_instance(message)

    assert result is False
```

## Testing Middleware

### Custom Middleware Testing

```python
# src/middleware/logging.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class LoggingMiddleware(BaseMiddleware):
    """Middleware to log all messages."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Log message before and after processing."""
        print(f"Received: {event.text}")
        result = await handler(event, data)
        print(f"Processed: {event.text}")
        return result


# CORRECT: Test middleware
@pytest.mark.service
@pytest.mark.asyncio
async def test_logging_middleware(bot, user, chat, capsys):
    """Test logging middleware logs messages."""
    from src.middleware.logging import LoggingMiddleware

    middleware = LoggingMiddleware()
    message = create_message("test message", user, chat, bot)

    # Mock handler
    async def mock_handler(event: Message, data: dict) -> None:
        await event.answer("Response")

    # Call middleware
    await middleware(mock_handler, message, {})

    # Verify logs
    captured = capsys.readouterr()
    assert "Received: test message" in captured.out
    assert "Processed: test message" in captured.out


# CORRECT: Test middleware modifies data
@pytest.mark.service
@pytest.mark.asyncio
async def test_user_enrichment_middleware(bot, user, chat):
    """Test middleware enriches handler data."""
    from src.middleware.user_enrichment import UserEnrichmentMiddleware

    middleware = UserEnrichmentMiddleware()
    message = create_message("test", user, chat, bot)

    handler_data = {}

    async def mock_handler(event: Message, data: dict) -> None:
        # Capture data passed to handler
        handler_data.update(data)

    await middleware(mock_handler, message, {})

    # Verify data enriched
    assert "user_profile" in handler_data
    assert handler_data["user_profile"]["user_id"] == user.id
```

## Testing Keyboards

### Inline Keyboard Testing

```python
# CORRECT: Test inline keyboard generation
@pytest.mark.service
def test_create_approval_keyboard():
    """Test approval keyboard has correct buttons."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from src.keyboards.loan import create_approval_keyboard

    keyboard = create_approval_keyboard(loan_id="loan-123")

    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1  # One row
    assert len(keyboard.inline_keyboard[0]) == 2  # Two buttons

    # Check button data
    approve_button = keyboard.inline_keyboard[0][0]
    reject_button = keyboard.inline_keyboard[0][1]

    assert approve_button.text == "✅ Approve"
    assert approve_button.callback_data == "approve_loan:loan-123"

    assert reject_button.text == "❌ Reject"
    assert reject_button.callback_data == "reject_loan:loan-123"


# CORRECT: Test reply keyboard
@pytest.mark.service
def test_create_main_menu_keyboard():
    """Test main menu keyboard."""
    from aiogram.types import ReplyKeyboardMarkup
    from src.keyboards.main_menu import create_main_menu

    keyboard = create_main_menu()

    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert len(keyboard.keyboard) >= 2  # At least 2 rows

    # Verify buttons exist
    all_buttons = [btn.text for row in keyboard.keyboard for btn in row]
    assert "📝 Apply for Loan" in all_buttons
    assert "📊 My Loans" in all_buttons
    assert "ℹ️ Help" in all_buttons
```

## Testing Bot Integration

### Full Handler Registration

```python
# CORRECT: Test dispatcher with registered handlers
@pytest.mark.service
@pytest.mark.asyncio
async def test_dispatcher_routes_command(bot, user, chat, message_factory):
    """Test dispatcher routes command to correct handler."""
    from aiogram import Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from src.handlers import register_handlers

    # Create dispatcher
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    register_handlers(dp)

    # Create message
    message = message_factory("/start")
    message.answer = AsyncMock()

    # Process update
    await dp.feed_update(bot, {"message": message.model_dump(mode="json")})

    # Verify handler called
    message.answer.assert_called()
```

## Best Practices

### DO: Mock Telegram API Calls

```python
# CORRECT: Mock bot API methods
@pytest.mark.service
@pytest.mark.asyncio
async def test_with_mocked_bot_methods(bot, user, chat):
    """Mock bot.send_message to test handler."""
    from src.handlers.notification import send_notification

    bot.send_message = AsyncMock()

    await send_notification(bot, user_id=user.id, text="Test notification")

    bot.send_message.assert_called_once_with(
        chat_id=user.id,
        text="Test notification"
    )


# INCORRECT: Don't call real Telegram API
@pytest.mark.service
@pytest.mark.asyncio
async def test_without_mocking():
    """WRONG: Calls real Telegram API."""
    real_bot = Bot(token="REAL_TOKEN")
    # This will make real API call
    await real_bot.send_message(chat_id=123, text="test")
```

### DO: Test State Transitions

```python
# CORRECT: Verify FSM state changes
@pytest.mark.service
@pytest.mark.asyncio
async def test_state_transitions():
    """Test FSM transitions through states."""
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.memory import MemoryStorage
    from src.states.registration import RegistrationStates

    storage = MemoryStorage()
    state = FSMContext(storage=storage, key="test:123")

    # Initial state
    await state.set_state(RegistrationStates.waiting_for_name)
    assert await state.get_state() == RegistrationStates.waiting_for_name.state

    # Transition
    await state.set_state(RegistrationStates.waiting_for_email)
    assert await state.get_state() == RegistrationStates.waiting_for_email.state

    # Clear state
    await state.clear()
    assert await state.get_state() is None
```

### DON'T: Test Multiple Handlers Together

```python
# INCORRECT: Testing multiple handlers in one test
@pytest.mark.service
@pytest.mark.asyncio
async def test_multiple_handlers_together(message_factory):
    """WRONG: Tests multiple handlers at once."""
    msg1 = message_factory("/start")
    await cmd_start(msg1)

    msg2 = message_factory("/help")
    await cmd_help(msg2)

    # Hard to debug which handler failed


# CORRECT: Test each handler separately
@pytest.mark.service
@pytest.mark.asyncio
async def test_start_handler_alone(message_factory):
    """Test only start handler."""
    message = message_factory("/start")
    message.answer = AsyncMock()
    await cmd_start(message)
    # Clear assertions


@pytest.mark.service
@pytest.mark.asyncio
async def test_help_handler_alone(message_factory):
    """Test only help handler."""
    message = message_factory("/help")
    message.answer = AsyncMock()
    await cmd_help(message)
    # Clear assertions
```

## Checklist

- [ ] Test all bot commands (/start, /help, custom commands)
- [ ] Test message handlers (text, photos, documents)
- [ ] Test callback query handlers
- [ ] Test FSM state transitions and data storage
- [ ] Test custom filters accept/reject correctly
- [ ] Test middleware modifies data as expected
- [ ] Test keyboard generation (inline and reply)
- [ ] Mock all Telegram API calls (don't call real API)
- [ ] Test error handling in handlers
- [ ] Use `@pytest.mark.service` to mark service tests
- [ ] Clean up FSM state after tests

## Related Documents

- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking external dependencies with AsyncMock
- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Pytest fixture patterns for bot testing
- `docs/atomic/services/aiogram-service/handler-patterns.md` — Aiogram handler implementation
- `docs/atomic/services/aiogram-service/fsm-patterns.md` — FSM state machine patterns
- `docs/atomic/services/aiogram-service/middleware-patterns.md` — Custom middleware implementation
