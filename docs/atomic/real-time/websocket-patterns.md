# WebSocket Integration Patterns

Comprehensive guide for implementing WebSocket connections with FastAPI, connection management, authentication, scaling, and real-time communication patterns.

## Prerequisites

- [FastAPI Basic Setup](../services/fastapi/basic-setup.md)
- [Authentication & Authorization Guide](../security/authentication-authorization-guide.md)
- [Redis Integration](../integrations/redis/connection-management.md)
- Understanding of WebSocket protocol

## Core WebSocket Service

### FastAPI WebSocket Implementation

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, List, Optional, Any, Set
import asyncio
import json
import uuid
import logging
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class MessageType(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    BROADCAST = "broadcast"
    PRIVATE = "private"
    TYPING = "typing"
    PRESENCE = "presence"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

@dataclass
class WebSocketMessage:
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    channel: Optional[str] = None

@dataclass
class ConnectionInfo:
    connection_id: str
    user_id: Optional[str]
    username: Optional[str]
    channels: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class WebSocketManager:
    """Manage WebSocket connections and messaging"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.channel_subscribers: Dict[str, Set[str]] = {}
        self.heartbeat_interval = 30  # seconds

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """Accept WebSocket connection and register it"""
        await websocket.accept()

        # Store connection
        self.active_connections[connection_id] = websocket
        self.connection_info[connection_id] = ConnectionInfo(
            connection_id=connection_id,
            user_id=user_id,
            username=username,
            metadata=metadata or {}
        )

        # Store connection info in Redis for distributed scaling
        await self._store_connection_in_redis(connection_id)

        # Send connection confirmation
        await self._send_message(connection_id, WebSocketMessage(
            type=MessageType.CONNECT,
            data={
                "connection_id": connection_id,
                "status": "connected",
                "server_time": datetime.utcnow().isoformat()
            }
        ))

        # Start heartbeat task
        asyncio.create_task(self._heartbeat_monitor(connection_id))

        logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")

    async def disconnect(self, connection_id: str, code: int = 1000):
        """Handle WebSocket disconnection"""
        if connection_id in self.active_connections:
            # Remove from all channels
            connection = self.connection_info.get(connection_id)
            if connection:
                for channel in connection.channels.copy():
                    await self.leave_channel(connection_id, channel)

            # Clean up local state
            del self.active_connections[connection_id]
            del self.connection_info[connection_id]

            # Remove from Redis
            await self._remove_connection_from_redis(connection_id)

            logger.info(f"WebSocket disconnected: {connection_id} (code: {code})")

    async def send_to_connection(self, connection_id: str, message: WebSocketMessage):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            await self._send_message(connection_id, message)
        else:
            # Try to send via Redis for distributed setup
            await self._send_via_redis(connection_id, message)

    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a user"""
        user_connections = [
            conn_id for conn_id, info in self.connection_info.items()
            if info.user_id == user_id
        ]

        for connection_id in user_connections:
            await self.send_to_connection(connection_id, message)

        # Also send via Redis for distributed setup
        await self._send_to_user_via_redis(user_id, message)

    async def broadcast_to_channel(self, channel: str, message: WebSocketMessage, exclude: Set[str] = None):
        """Broadcast message to all subscribers of a channel"""
        exclude = exclude or set()
        subscribers = self.channel_subscribers.get(channel, set())

        for connection_id in subscribers:
            if connection_id not in exclude:
                await self.send_to_connection(connection_id, message)

        # Broadcast via Redis for distributed setup
        await self._broadcast_via_redis(channel, message, exclude)

    async def join_channel(self, connection_id: str, channel: str) -> bool:
        """Add connection to channel"""
        if connection_id not in self.connection_info:
            return False

        # Add to local channel
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(connection_id)

        # Update connection info
        self.connection_info[connection_id].channels.add(channel)

        # Store in Redis
        await self._join_channel_in_redis(connection_id, channel)

        # Notify channel about new subscriber
        await self.broadcast_to_channel(channel, WebSocketMessage(
            type=MessageType.PRESENCE,
            data={
                "action": "joined",
                "connection_id": connection_id,
                "user_id": self.connection_info[connection_id].user_id,
                "channel": channel
            }
        ), exclude={connection_id})

        logger.info(f"Connection {connection_id} joined channel {channel}")
        return True

    async def leave_channel(self, connection_id: str, channel: str) -> bool:
        """Remove connection from channel"""
        if connection_id not in self.connection_info:
            return False

        # Remove from local channel
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(connection_id)
            if not self.channel_subscribers[channel]:
                del self.channel_subscribers[channel]

        # Update connection info
        self.connection_info[connection_id].channels.discard(channel)

        # Remove from Redis
        await self._leave_channel_in_redis(connection_id, channel)

        # Notify channel about subscriber leaving
        await self.broadcast_to_channel(channel, WebSocketMessage(
            type=MessageType.PRESENCE,
            data={
                "action": "left",
                "connection_id": connection_id,
                "user_id": self.connection_info[connection_id].user_id,
                "channel": channel
            }
        ))

        logger.info(f"Connection {connection_id} left channel {channel}")
        return True

    async def _send_message(self, connection_id: str, message: WebSocketMessage):
        """Send message to WebSocket connection"""
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps({
                    "type": message.type.value,
                    "data": message.data,
                    "timestamp": message.timestamp.isoformat(),
                    "message_id": message.message_id,
                    "sender_id": message.sender_id,
                    "recipient_id": message.recipient_id,
                    "channel": message.channel
                }))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                await self.disconnect(connection_id, code=1011)

    async def _heartbeat_monitor(self, connection_id: str):
        """Monitor connection heartbeat"""
        while connection_id in self.active_connections:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                if connection_id not in self.active_connections:
                    break

                # Send heartbeat
                await self._send_message(connection_id, WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    data={"timestamp": datetime.utcnow().isoformat()}
                ))

                # Update last heartbeat
                if connection_id in self.connection_info:
                    self.connection_info[connection_id].last_heartbeat = datetime.utcnow()

            except Exception as e:
                logger.error(f"Heartbeat failed for {connection_id}: {e}")
                await self.disconnect(connection_id, code=1011)
                break

    # Redis integration methods for distributed WebSocket support
    async def _store_connection_in_redis(self, connection_id: str):
        """Store connection info in Redis"""
        connection = self.connection_info[connection_id]
        await self.redis.hset(
            f"ws:connections:{connection_id}",
            mapping={
                "user_id": connection.user_id or "",
                "username": connection.username or "",
                "connected_at": connection.connected_at.isoformat(),
                "server_id": self._get_server_id(),
                "metadata": json.dumps(connection.metadata)
            }
        )
        await self.redis.expire(f"ws:connections:{connection_id}", 3600)

    async def _remove_connection_from_redis(self, connection_id: str):
        """Remove connection info from Redis"""
        await self.redis.delete(f"ws:connections:{connection_id}")

    async def _send_via_redis(self, connection_id: str, message: WebSocketMessage):
        """Send message via Redis pub/sub for distributed setup"""
        await self.redis.publish(
            f"ws:direct:{connection_id}",
            json.dumps({
                "type": message.type.value,
                "data": message.data,
                "timestamp": message.timestamp.isoformat(),
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "channel": message.channel
            })
        )

    def _get_server_id(self) -> str:
        """Get unique server identifier"""
        import socket
        return f"{socket.gethostname()}:{id(self)}"

# FastAPI WebSocket endpoints
app = FastAPI()
security = HTTPBearer(auto_error=False)

# Initialize WebSocket manager
redis_client = redis.from_url("redis://localhost:6379")
ws_manager = WebSocketManager(redis_client)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Public WebSocket endpoint"""
    connection_id = str(uuid.uuid4())

    try:
        await ws_manager.connect(websocket, connection_id)

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                await handle_websocket_message(connection_id, message_data)
            except json.JSONDecodeError:
                await ws_manager.send_to_connection(connection_id, WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"error": "Invalid JSON format"}
                ))

    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        await ws_manager.disconnect(connection_id, code=1011)

@app.websocket("/ws/authenticated")
async def authenticated_websocket_endpoint(websocket: WebSocket, token: str = None):
    """Authenticated WebSocket endpoint"""
    connection_id = str(uuid.uuid4())

    # Authenticate user
    user = None
    if token:
        try:
            user = await authenticate_token(token)
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return

    try:
        await ws_manager.connect(
            websocket,
            connection_id,
            user_id=user.id if user else None,
            username=user.username if user else None,
            metadata={"authenticated": user is not None}
        )

        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                await handle_authenticated_message(connection_id, message_data, user)
            except json.JSONDecodeError:
                await ws_manager.send_to_connection(connection_id, WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"error": "Invalid JSON format"}
                ))

    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Authenticated WebSocket error for {connection_id}: {e}")
        await ws_manager.disconnect(connection_id, code=1011)

async def handle_websocket_message(connection_id: str, message_data: Dict[str, Any]):
    """Handle incoming WebSocket message"""
    message_type = message_data.get("type")
    data = message_data.get("data", {})

    if message_type == "join_channel":
        channel = data.get("channel")
        if channel:
            await ws_manager.join_channel(connection_id, channel)

    elif message_type == "leave_channel":
        channel = data.get("channel")
        if channel:
            await ws_manager.leave_channel(connection_id, channel)

    elif message_type == "message":
        channel = data.get("channel")
        if channel:
            await ws_manager.broadcast_to_channel(channel, WebSocketMessage(
                type=MessageType.MESSAGE,
                data=data,
                sender_id=connection_id,
                channel=channel
            ))

    elif message_type == "heartbeat":
        # Update heartbeat timestamp
        if connection_id in ws_manager.connection_info:
            ws_manager.connection_info[connection_id].last_heartbeat = datetime.utcnow()

async def handle_authenticated_message(connection_id: str, message_data: Dict[str, Any], user):
    """Handle incoming authenticated WebSocket message"""
    message_type = message_data.get("type")
    data = message_data.get("data", {})

    if message_type == "private_message":
        recipient_id = data.get("recipient_id")
        if recipient_id:
            await ws_manager.send_to_user(recipient_id, WebSocketMessage(
                type=MessageType.PRIVATE,
                data=data,
                sender_id=user.id if user else connection_id,
                recipient_id=recipient_id
            ))

    else:
        # Handle regular message with user context
        data["user_id"] = user.id if user else None
        data["username"] = user.username if user else None
        await handle_websocket_message(connection_id, message_data)

async def authenticate_token(token: str):
    """Authenticate JWT token"""
    # Implementation depends on your auth system
    # Return user object or raise exception
    pass
```

## Advanced WebSocket Patterns

### Chat Application Pattern

```python
class ChatService:
    """Real-time chat service using WebSockets"""

    def __init__(self, ws_manager: WebSocketManager, db_session):
        self.ws_manager = ws_manager
        self.db_session = db_session
        self.typing_users: Dict[str, Set[str]] = {}  # channel -> set of typing users

    async def send_chat_message(
        self,
        sender_id: str,
        channel: str,
        content: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send chat message to channel"""

        # Store message in database
        message_record = await self._store_message(sender_id, channel, content, message_type)

        # Broadcast to channel subscribers
        await self.ws_manager.broadcast_to_channel(channel, WebSocketMessage(
            type=MessageType.MESSAGE,
            data={
                "message_id": message_record["id"],
                "sender_id": sender_id,
                "sender_username": message_record["sender_username"],
                "content": content,
                "message_type": message_type,
                "timestamp": message_record["created_at"]
            },
            sender_id=sender_id,
            channel=channel
        ))

        return message_record

    async def handle_typing_indicator(self, user_id: str, channel: str, is_typing: bool):
        """Handle typing indicators"""
        if channel not in self.typing_users:
            self.typing_users[channel] = set()

        if is_typing:
            self.typing_users[channel].add(user_id)
        else:
            self.typing_users[channel].discard(user_id)

        # Broadcast typing status
        await self.ws_manager.broadcast_to_channel(channel, WebSocketMessage(
            type=MessageType.TYPING,
            data={
                "user_id": user_id,
                "is_typing": is_typing,
                "typing_users": list(self.typing_users[channel])
            },
            channel=channel
        ))

        # Auto-stop typing after timeout
        if is_typing:
            asyncio.create_task(self._auto_stop_typing(user_id, channel))

    async def _auto_stop_typing(self, user_id: str, channel: str):
        """Automatically stop typing indicator after timeout"""
        await asyncio.sleep(5)  # 5 seconds timeout

        if channel in self.typing_users and user_id in self.typing_users[channel]:
            await self.handle_typing_indicator(user_id, channel, False)

    async def get_chat_history(self, channel: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get chat message history"""
        # Implementation would query database for chat history
        return []

    async def _store_message(self, sender_id: str, channel: str, content: str, message_type: str) -> Dict:
        """Store chat message in database"""
        # Implementation would store in database and return message record
        return {
            "id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "sender_username": "user",  # Get from database
            "channel": channel,
            "content": content,
            "message_type": message_type,
            "created_at": datetime.utcnow().isoformat()
        }

class CollaborativeEditingService:
    """Real-time collaborative editing using WebSockets"""

    def __init__(self, ws_manager: WebSocketManager, redis_client: redis.Redis):
        self.ws_manager = ws_manager
        self.redis = redis_client

    async def handle_document_operation(
        self,
        user_id: str,
        document_id: str,
        operation: Dict[str, Any]
    ):
        """Handle collaborative editing operation"""

        # Apply operational transformation
        transformed_operation = await self._transform_operation(document_id, operation)

        # Store operation in Redis for conflict resolution
        await self._store_operation(document_id, transformed_operation)

        # Broadcast to all document collaborators
        channel = f"document:{document_id}"
        await self.ws_manager.broadcast_to_channel(channel, WebSocketMessage(
            type=MessageType.MESSAGE,
            data={
                "operation_type": "document_operation",
                "document_id": document_id,
                "operation": transformed_operation,
                "user_id": user_id
            },
            sender_id=user_id,
            channel=channel
        ))

    async def handle_cursor_position(self, user_id: str, document_id: str, position: Dict[str, int]):
        """Handle cursor position updates"""
        channel = f"document:{document_id}"

        await self.ws_manager.broadcast_to_channel(channel, WebSocketMessage(
            type=MessageType.MESSAGE,
            data={
                "operation_type": "cursor_position",
                "document_id": document_id,
                "user_id": user_id,
                "position": position
            },
            sender_id=user_id,
            channel=channel
        ))

    async def _transform_operation(self, document_id: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply operational transformation for conflict resolution"""
        # Simplified OT implementation
        # In production, use a library like ShareJS or Yjs
        return operation

    async def _store_operation(self, document_id: str, operation: Dict[str, Any]):
        """Store operation for replay and conflict resolution"""
        operation_id = str(uuid.uuid4())
        await self.redis.lpush(
            f"document_operations:{document_id}",
            json.dumps({
                "id": operation_id,
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat()
            })
        )

        # Keep only last 1000 operations
        await self.redis.ltrim(f"document_operations:{document_id}", 0, 999)
```

## WebSocket Scaling and Load Balancing

### Redis-based Scaling

```python
class DistributedWebSocketManager:
    """WebSocket manager with Redis-based distributed scaling"""

    def __init__(self, redis_client: redis.Redis, server_id: str):
        self.redis = redis_client
        self.server_id = server_id
        self.local_manager = WebSocketManager(redis_client)
        self.pubsub = None

    async def start_distributed_mode(self):
        """Start listening to Redis pub/sub for distributed messages"""
        self.pubsub = self.redis.pubsub()

        # Subscribe to relevant channels
        await self.pubsub.subscribe(
            f"ws:server:{self.server_id}",
            "ws:broadcast:*",
            "ws:user:*"
        )

        # Start message processing task
        asyncio.create_task(self._process_distributed_messages())

    async def _process_distributed_messages(self):
        """Process messages from other WebSocket servers"""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await self._handle_distributed_message(message["channel"], data)
                except Exception as e:
                    logger.error(f"Error processing distributed message: {e}")

    async def _handle_distributed_message(self, channel: str, data: Dict[str, Any]):
        """Handle message from other WebSocket servers"""
        if channel.startswith("ws:broadcast:"):
            # Handle broadcast message
            target_channel = channel.replace("ws:broadcast:", "")
            message = WebSocketMessage(
                type=MessageType(data["type"]),
                data=data["data"],
                sender_id=data.get("sender_id"),
                channel=target_channel
            )
            await self.local_manager.broadcast_to_channel(target_channel, message)

        elif channel.startswith("ws:user:"):
            # Handle user-specific message
            user_id = channel.replace("ws:user:", "")
            message = WebSocketMessage(
                type=MessageType(data["type"]),
                data=data["data"],
                sender_id=data.get("sender_id"),
                recipient_id=user_id
            )
            await self.local_manager.send_to_user(user_id, message)

        elif channel == f"ws:server:{self.server_id}":
            # Handle server-specific message
            connection_id = data.get("connection_id")
            if connection_id:
                message = WebSocketMessage(
                    type=MessageType(data["type"]),
                    data=data["data"],
                    sender_id=data.get("sender_id")
                )
                await self.local_manager.send_to_connection(connection_id, message)

    async def broadcast_across_servers(self, channel: str, message: WebSocketMessage):
        """Broadcast message across all WebSocket servers"""
        await self.redis.publish(
            f"ws:broadcast:{channel}",
            json.dumps({
                "type": message.type.value,
                "data": message.data,
                "sender_id": message.sender_id,
                "timestamp": message.timestamp.isoformat()
            })
        )

    async def send_to_user_across_servers(self, user_id: str, message: WebSocketMessage):
        """Send message to user across all servers"""
        await self.redis.publish(
            f"ws:user:{user_id}",
            json.dumps({
                "type": message.type.value,
                "data": message.data,
                "sender_id": message.sender_id,
                "timestamp": message.timestamp.isoformat()
            })
        )

class WebSocketLoadBalancer:
    """Load balancer for WebSocket connections"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.server_stats = {}

    async def get_best_server(self) -> str:
        """Get the best server for new WebSocket connection"""
        servers = await self._get_active_servers()

        if not servers:
            raise Exception("No active WebSocket servers available")

        # Simple round-robin or least connections algorithm
        best_server = min(servers, key=lambda s: s["connection_count"])
        return best_server["server_id"]

    async def _get_active_servers(self) -> List[Dict[str, Any]]:
        """Get list of active WebSocket servers"""
        servers = []
        server_keys = await self.redis.keys("ws:server:*:stats")

        for key in server_keys:
            stats = await self.redis.hgetall(key)
            if stats:
                servers.append({
                    "server_id": key.split(":")[2],
                    "connection_count": int(stats.get("connections", 0)),
                    "last_heartbeat": stats.get("last_heartbeat"),
                    "cpu_usage": float(stats.get("cpu_usage", 0)),
                    "memory_usage": float(stats.get("memory_usage", 0))
                })

        # Filter out stale servers
        current_time = datetime.utcnow()
        active_servers = []

        for server in servers:
            try:
                last_heartbeat = datetime.fromisoformat(server["last_heartbeat"])
                if (current_time - last_heartbeat).seconds < 60:  # 1 minute threshold
                    active_servers.append(server)
            except (ValueError, TypeError):
                continue

        return active_servers

    async def update_server_stats(self, server_id: str, stats: Dict[str, Any]):
        """Update server statistics"""
        await self.redis.hset(
            f"ws:server:{server_id}:stats",
            mapping={
                "connections": stats.get("connections", 0),
                "cpu_usage": stats.get("cpu_usage", 0),
                "memory_usage": stats.get("memory_usage", 0),
                "last_heartbeat": datetime.utcnow().isoformat()
            }
        )
        await self.redis.expire(f"ws:server:{server_id}:stats", 120)  # 2 minutes TTL
```

## Testing WebSocket Implementation

### WebSocket Testing Framework

```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

class WebSocketTester:
    """Testing utilities for WebSocket functionality"""

    def __init__(self, app):
        self.app = app
        self.client = TestClient(app)

    async def test_websocket_connection(self):
        """Test basic WebSocket connection"""
        with self.client.websocket_connect("/ws") as websocket:
            # Test connection established
            data = websocket.receive_json()
            assert data["type"] == "connect"
            assert "connection_id" in data["data"]

    async def test_channel_join_leave(self):
        """Test joining and leaving channels"""
        with self.client.websocket_connect("/ws") as websocket:
            # Receive connection message
            websocket.receive_json()

            # Join channel
            websocket.send_json({
                "type": "join_channel",
                "data": {"channel": "test_channel"}
            })

            # Send message to channel
            websocket.send_json({
                "type": "message",
                "data": {
                    "channel": "test_channel",
                    "content": "Hello, channel!"
                }
            })

            # Receive echoed message
            message = websocket.receive_json()
            assert message["type"] == "message"
            assert message["data"]["content"] == "Hello, channel!"

    async def test_multiple_connections(self):
        """Test multiple WebSocket connections"""
        async def client_handler(client_id: str, messages: List):
            with self.client.websocket_connect("/ws") as websocket:
                websocket.receive_json()  # Connection message

                # Join test channel
                websocket.send_json({
                    "type": "join_channel",
                    "data": {"channel": "multi_test"}
                })

                # Send message
                websocket.send_json({
                    "type": "message",
                    "data": {
                        "channel": "multi_test",
                        "content": f"Message from {client_id}"
                    }
                })

                # Collect messages
                for _ in range(2):  # Expect 2 messages (one from each client)
                    msg = websocket.receive_json()
                    if msg["type"] == "message":
                        messages.append(msg)

        messages1 = []
        messages2 = []

        # Run both clients concurrently
        await asyncio.gather(
            client_handler("client1", messages1),
            client_handler("client2", messages2)
        )

        # Verify both clients received messages
        assert len(messages1) >= 1
        assert len(messages2) >= 1

    async def test_authentication_required(self):
        """Test authenticated WebSocket endpoint"""
        # Test without token (should fail)
        with pytest.raises(WebSocketDisconnect):
            with self.client.websocket_connect("/ws/authenticated"):
                pass

        # Test with valid token
        valid_token = "valid_jwt_token"  # Generate valid token for test
        with self.client.websocket_connect(
            f"/ws/authenticated?token={valid_token}"
        ) as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connect"

class WebSocketPerformanceTester:
    """Performance testing for WebSocket implementation"""

    async def test_connection_throughput(self, concurrent_connections: int = 100):
        """Test handling multiple concurrent connections"""
        connections = []
        start_time = asyncio.get_event_loop().time()

        try:
            # Create concurrent connections
            for i in range(concurrent_connections):
                websocket = self.client.websocket_connect("/ws")
                connections.append(websocket)
                await asyncio.sleep(0.01)  # Small delay between connections

            connection_time = asyncio.get_event_loop().time() - start_time

            # Test message broadcasting
            start_time = asyncio.get_event_loop().time()

            # Send messages from each connection
            for i, websocket in enumerate(connections):
                websocket.send_json({
                    "type": "join_channel",
                    "data": {"channel": "performance_test"}
                })

                websocket.send_json({
                    "type": "message",
                    "data": {
                        "channel": "performance_test",
                        "content": f"Message {i}"
                    }
                })

            broadcast_time = asyncio.get_event_loop().time() - start_time

            return {
                "concurrent_connections": concurrent_connections,
                "connection_time": connection_time,
                "broadcast_time": broadcast_time,
                "avg_connection_time": connection_time / concurrent_connections,
                "messages_per_second": concurrent_connections / broadcast_time
            }

        finally:
            # Clean up connections
            for websocket in connections:
                try:
                    websocket.close()
                except:
                    pass

# pytest fixtures and test cases
@pytest.fixture
def websocket_tester():
    return WebSocketTester(app)

@pytest.mark.asyncio
async def test_basic_websocket_functionality(websocket_tester):
    await websocket_tester.test_websocket_connection()

@pytest.mark.asyncio
async def test_channel_operations(websocket_tester):
    await websocket_tester.test_channel_join_leave()

@pytest.mark.asyncio
async def test_concurrent_connections(websocket_tester):
    await websocket_tester.test_multiple_connections()
```

## Related Documentation

- [Server-Sent Events Implementation](sse-implementation.md)
- [Push Notifications](push-notifications.md)
- [Real-time Sync Patterns](real-time-sync-patterns.md)
- [FastAPI Basic Setup](../services/fastapi/basic-setup.md)

## Best Practices

1. **Connection Management**:
   - Implement proper heartbeat mechanisms
   - Handle disconnections gracefully
   - Use connection pooling for scaling

2. **Message Handling**:
   - Validate all incoming messages
   - Implement message queuing for reliability
   - Use structured message formats

3. **Security**:
   - Authenticate WebSocket connections
   - Validate user permissions for channels
   - Implement rate limiting

4. **Scaling**:
   - Use Redis for distributed WebSocket coordination
   - Implement load balancing strategies
   - Monitor connection metrics

5. **Performance**:
   - Optimize message serialization
   - Use efficient data structures
   - Implement proper error handling