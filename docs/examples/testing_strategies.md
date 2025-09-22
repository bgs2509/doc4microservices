## Complete Testing Examples

### FastAPI Service Testing
```python
# tests/test_user_api.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
import pytest_asyncio

from src.main import app
from src.core.database import get_db_session
from src.schemas.user import UserCreate, UserResponse

@pytest.fixture
async def async_client():
    """Async test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    """Test user creation endpoint."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }

    response = await async_client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201

    user = response.json()
    assert user["email"] == user_data["email"]
    assert user["username"] == user_data["username"]
    assert user["full_name"] == user_data["full_name"]
    assert "id" in user
    assert "created_at" in user

@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    """Test get user endpoint."""
    # First create a user
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "testpassword123"
    }

    create_response = await async_client.post("/api/v1/users/", json=user_data)
    created_user = create_response.json()
    user_id = created_user["id"]

    # Then get the user
    response = await async_client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200

    user = response.json()
    assert user["id"] == user_id
    assert user["email"] == user_data["email"]
    assert user["username"] == user_data["username"]

@pytest.mark.asyncio
async def test_get_nonexistent_user(async_client: AsyncClient):
    """Test getting a non-existent user."""
    response = await async_client.get("/api/v1/users/99999")

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]
```

### Aiogram Bot Testing
```python
# tests/test_bot_handlers.py
import pytest
from unittest.mock import AsyncMock, Mock
from aiogram.types import Message, User, Chat
from aiogram import Bot

from src.bot.handlers.start import handle_start

@pytest.fixture
def mock_message():
    """Mock Telegram message."""
    user = User(id=123, is_bot=False, first_name="Test", username="testuser")
    chat = Chat(id=123, type="private")

    message = Mock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()
    message.bot = Mock(spec=Bot)

    return message

@pytest.mark.asyncio
async def test_start_handler(mock_message):
    """Test /start command handler."""
    await handle_start(mock_message)

    mock_message.reply.assert_called_once()
    call_args = mock_message.reply.call_args[0][0]
    assert "Welcome" in call_args
    assert "testuser" in call_args
```

### Worker Service Testing
```python
# tests/test_media_processor.py
import pytest
from unittest.mock import AsyncMock, Mock
from io import BytesIO
from PIL import Image

from src.workers.media_processor import MediaProcessor

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.setex = AsyncMock()
    redis_mock.get = AsyncMock()
    return redis_mock

@pytest.fixture
def mock_rabbitmq_channel():
    """Mock RabbitMQ channel."""
    channel_mock = AsyncMock()
    channel_mock.declare_exchange = AsyncMock()
    channel_mock.declare_queue = AsyncMock()
    return channel_mock

@pytest.fixture
def sample_image_data():
    """Create sample image data."""
    image = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()

@pytest.mark.asyncio
async def test_process_image(mock_redis, mock_rabbitmq_channel, sample_image_data):
    """Test image processing."""
    processor = MediaProcessor(mock_redis, mock_rabbitmq_channel)

    result = await processor._process_image(
        file_data=sample_image_data,
        processing_id="test-123",
        user_id=456
    )

    assert result["success"] is True
    assert "thumbnail_key" in result
    assert "compressed_key" in result
    assert "metadata" in result
    assert result["original_size"] > 0
    assert result["compressed_size"] > 0
    assert 0 < result["compression_ratio"] <= 1

    # Verify Redis calls
    assert mock_redis.setex.call_count == 2  # thumbnail + compressed
```
