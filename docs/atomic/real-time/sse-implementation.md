# Server-Sent Events (SSE) Implementation

Comprehensive guide for implementing Server-Sent Events with FastAPI, event streaming, connection management, and real-time data delivery patterns.

## Prerequisites

- [FastAPI Basic Setup](../services/fastapi/basic-setup.md)
- [WebSocket Patterns](websocket-patterns.md)
- [Authentication & Authorization Guide](../security/authentication-authorization-guide.md)
- Understanding of HTTP streaming and SSE protocol

## Core SSE Implementation

### FastAPI SSE Service

```python
from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
import asyncio
import json
import uuid
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class EventType(Enum):
    MESSAGE = "message"
    NOTIFICATION = "notification"
    UPDATE = "update"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    CUSTOM = "custom"

@dataclass
class SSEEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event: str = "message"
    data: Any = None
    retry: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def format(self) -> str:
        """Format event for SSE protocol"""
        lines = []

        if self.id:
            lines.append(f"id: {self.id}")

        if self.event:
            lines.append(f"event: {self.event}")

        if self.retry is not None:
            lines.append(f"retry: {self.retry}")

        if self.data is not None:
            if isinstance(self.data, (dict, list)):
                data_str = json.dumps(self.data)
            else:
                data_str = str(self.data)

            # Handle multiline data
            for line in data_str.split('\n'):
                lines.append(f"data: {line}")

        lines.append("")  # Empty line to end event
        return "\n".join(lines) + "\n"

@dataclass
class SSEConnection:
    connection_id: str
    user_id: Optional[str]
    channels: set = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_event_id: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class SSEManager:
    """Manage Server-Sent Events connections and streaming"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.active_connections: Dict[str, SSEConnection] = {}
        self.event_queues: Dict[str, asyncio.Queue] = {}
        self.channel_subscribers: Dict[str, set] = {}
        self.heartbeat_interval = 30  # seconds

    async def create_event_stream(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        channels: List[str] = None,
        filters: Dict[str, Any] = None,
        last_event_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Create SSE event stream for client"""

        # Create connection
        connection = SSEConnection(
            connection_id=connection_id,
            user_id=user_id,
            channels=set(channels or []),
            last_event_id=last_event_id,
            filters=filters or {}
        )

        self.active_connections[connection_id] = connection
        self.event_queues[connection_id] = asyncio.Queue()

        # Subscribe to channels
        for channel in connection.channels:
            await self._subscribe_to_channel(connection_id, channel)

        # Store connection in Redis for distributed support
        await self._store_connection_in_redis(connection)

        try:
            # Send initial connection event
            initial_event = SSEEvent(
                event="connected",
                data={
                    "connection_id": connection_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "channels": list(connection.channels)
                }
            )
            yield initial_event.format()

            # Replay missed events if last_event_id provided
            if last_event_id:
                async for missed_event in self._replay_missed_events(connection_id, last_event_id):
                    yield missed_event

            # Start heartbeat task
            heartbeat_task = asyncio.create_task(self._heartbeat_sender(connection_id))

            # Stream events
            while connection_id in self.active_connections:
                try:
                    # Wait for event with timeout
                    event_data = await asyncio.wait_for(
                        self.event_queues[connection_id].get(),
                        timeout=1.0
                    )

                    if event_data:
                        yield event_data

                        # Update last event ID
                        if isinstance(event_data, str) and "id:" in event_data:
                            lines = event_data.split('\n')
                            for line in lines:
                                if line.startswith("id:"):
                                    self.active_connections[connection_id].last_event_id = line[3:].strip()
                                    break

                except asyncio.TimeoutError:
                    # Timeout is normal, continue loop
                    continue
                except Exception as e:
                    logger.error(f"Error in SSE stream for {connection_id}: {e}")
                    break

        finally:
            # Clean up connection
            heartbeat_task.cancel()
            await self._cleanup_connection(connection_id)

    async def send_event_to_connection(self, connection_id: str, event: SSEEvent):
        """Send event to specific connection"""
        if connection_id in self.event_queues:
            await self.event_queues[connection_id].put(event.format())
        else:
            # Try to send via Redis for distributed setup
            await self._send_event_via_redis(connection_id, event)

    async def send_event_to_user(self, user_id: str, event: SSEEvent):
        """Send event to all connections of a user"""
        user_connections = [
            conn_id for conn_id, conn in self.active_connections.items()
            if conn.user_id == user_id
        ]

        for connection_id in user_connections:
            await self.send_event_to_connection(connection_id, event)

        # Also send via Redis for distributed setup
        await self._send_event_to_user_via_redis(user_id, event)

    async def broadcast_to_channel(self, channel: str, event: SSEEvent, exclude: set = None):
        """Broadcast event to all subscribers of a channel"""
        exclude = exclude or set()
        subscribers = self.channel_subscribers.get(channel, set())

        # Apply channel-specific filtering
        filtered_subscribers = await self._apply_channel_filters(channel, subscribers, event)

        for connection_id in filtered_subscribers:
            if connection_id not in exclude:
                await self.send_event_to_connection(connection_id, event)

        # Store event for replay
        await self._store_event_for_replay(channel, event)

        # Broadcast via Redis for distributed setup
        await self._broadcast_via_redis(channel, event, exclude)

    async def _subscribe_to_channel(self, connection_id: str, channel: str):
        """Subscribe connection to channel"""
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()

        self.channel_subscribers[channel].add(connection_id)

        # Store subscription in Redis
        await self.redis.sadd(f"sse:channel:{channel}", connection_id)
        await self.redis.expire(f"sse:channel:{channel}", 3600)

    async def _apply_channel_filters(self, channel: str, subscribers: set, event: SSEEvent) -> set:
        """Apply event filters for channel subscribers"""
        filtered_subscribers = set()

        for connection_id in subscribers:
            connection = self.active_connections.get(connection_id)
            if connection and self._event_matches_filters(event, connection.filters):
                filtered_subscribers.add(connection_id)

        return filtered_subscribers

    def _event_matches_filters(self, event: SSEEvent, filters: Dict[str, Any]) -> bool:
        """Check if event matches connection filters"""
        if not filters:
            return True

        event_data = event.data if isinstance(event.data, dict) else {}

        for filter_key, filter_value in filters.items():
            if filter_key in event_data:
                if isinstance(filter_value, list):
                    if event_data[filter_key] not in filter_value:
                        return False
                else:
                    if event_data[filter_key] != filter_value:
                        return False

        return True

    async def _heartbeat_sender(self, connection_id: str):
        """Send periodic heartbeat events"""
        while connection_id in self.active_connections:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                if connection_id not in self.active_connections:
                    break

                heartbeat_event = SSEEvent(
                    event="heartbeat",
                    data={"timestamp": datetime.utcnow().isoformat()}
                )

                await self.send_event_to_connection(connection_id, heartbeat_event)

            except Exception as e:
                logger.error(f"Heartbeat error for {connection_id}: {e}")
                break

    async def _replay_missed_events(self, connection_id: str, last_event_id: str) -> AsyncGenerator[str, None]:
        """Replay events missed since last_event_id"""
        connection = self.active_connections.get(connection_id)
        if not connection:
            return

        for channel in connection.channels:
            # Get stored events from Redis
            events = await self.redis.lrange(f"sse:events:{channel}", 0, -1)

            found_last_event = False
            for event_data in reversed(events):
                try:
                    event_info = json.loads(event_data)

                    if not found_last_event:
                        if event_info.get("id") == last_event_id:
                            found_last_event = True
                        continue

                    # Reconstruct and yield event
                    event = SSEEvent(
                        id=event_info.get("id"),
                        event=event_info.get("event", "message"),
                        data=event_info.get("data")
                    )

                    if self._event_matches_filters(event, connection.filters):
                        yield event.format()

                except json.JSONDecodeError:
                    continue

    async def _store_event_for_replay(self, channel: str, event: SSEEvent):
        """Store event for replay functionality"""
        event_data = {
            "id": event.id,
            "event": event.event,
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        }

        # Store in Redis list (keep last 1000 events)
        await self.redis.lpush(f"sse:events:{channel}", json.dumps(event_data))
        await self.redis.ltrim(f"sse:events:{channel}", 0, 999)
        await self.redis.expire(f"sse:events:{channel}", 86400)  # 24 hours

    async def _cleanup_connection(self, connection_id: str):
        """Clean up connection resources"""
        connection = self.active_connections.get(connection_id)
        if connection:
            # Remove from channels
            for channel in connection.channels:
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].discard(connection_id)
                    if not self.channel_subscribers[channel]:
                        del self.channel_subscribers[channel]

            # Clean up local state
            del self.active_connections[connection_id]

            if connection_id in self.event_queues:
                del self.event_queues[connection_id]

        # Remove from Redis
        await self._remove_connection_from_redis(connection_id)

        logger.info(f"SSE connection cleaned up: {connection_id}")

    # Redis integration methods for distributed SSE
    async def _store_connection_in_redis(self, connection: SSEConnection):
        """Store connection info in Redis"""
        await self.redis.hset(
            f"sse:connections:{connection.connection_id}",
            mapping={
                "user_id": connection.user_id or "",
                "channels": json.dumps(list(connection.channels)),
                "connected_at": connection.connected_at.isoformat(),
                "server_id": self._get_server_id(),
                "last_event_id": connection.last_event_id or "",
                "filters": json.dumps(connection.filters),
                "metadata": json.dumps(connection.metadata)
            }
        )
        await self.redis.expire(f"sse:connections:{connection.connection_id}", 3600)

    async def _remove_connection_from_redis(self, connection_id: str):
        """Remove connection info from Redis"""
        await self.redis.delete(f"sse:connections:{connection_id}")

    def _get_server_id(self) -> str:
        """Get unique server identifier"""
        import socket
        return f"{socket.gethostname()}:{id(self)}"

# FastAPI SSE endpoints
app = FastAPI()
security = HTTPBearer(auto_error=False)

# Initialize SSE manager
redis_client = redis.from_url("redis://localhost:6379")
sse_manager = SSEManager(redis_client)

@app.get("/events")
async def sse_endpoint(
    request: Request,
    channels: str = "",
    filters: str = "{}",
    last_event_id: Optional[str] = None
):
    """Public SSE endpoint"""
    connection_id = str(uuid.uuid4())

    # Parse channels and filters
    channel_list = [ch.strip() for ch in channels.split(",") if ch.strip()]
    try:
        filter_dict = json.loads(filters) if filters else {}
    except json.JSONDecodeError:
        filter_dict = {}

    # Get last event ID from headers if not in query
    if not last_event_id:
        last_event_id = request.headers.get("Last-Event-ID")

    return StreamingResponse(
        sse_manager.create_event_stream(
            connection_id=connection_id,
            channels=channel_list,
            filters=filter_dict,
            last_event_id=last_event_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control,Last-Event-ID",
        }
    )

@app.get("/events/authenticated")
async def authenticated_sse_endpoint(
    request: Request,
    channels: str = "",
    filters: str = "{}",
    last_event_id: Optional[str] = None,
    token: str = Depends(security)
):
    """Authenticated SSE endpoint"""
    # Authenticate user
    try:
        user = await authenticate_token(token.credentials if token else None)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    connection_id = str(uuid.uuid4())

    # Parse channels and filters
    channel_list = [ch.strip() for ch in channels.split(",") if ch.strip()]
    try:
        filter_dict = json.loads(filters) if filters else {}
    except json.JSONDecodeError:
        filter_dict = {}

    # Get last event ID from headers if not in query
    if not last_event_id:
        last_event_id = request.headers.get("Last-Event-ID")

    return StreamingResponse(
        sse_manager.create_event_stream(
            connection_id=connection_id,
            user_id=user.id,
            channels=channel_list,
            filters=filter_dict,
            last_event_id=last_event_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control,Last-Event-ID",
        }
    )

async def authenticate_token(token: str):
    """Authenticate JWT token"""
    # Implementation depends on your auth system
    pass
```

## Advanced SSE Patterns

### Real-time Dashboard Updates

```python
class DashboardSSEService:
    """SSE service for real-time dashboard updates"""

    def __init__(self, sse_manager: SSEManager, db_session):
        self.sse_manager = sse_manager
        self.db_session = db_session
        self.metric_cache = {}

    async def start_dashboard_updates(self):
        """Start periodic dashboard metric updates"""
        asyncio.create_task(self._update_metrics_loop())

    async def _update_metrics_loop(self):
        """Periodically update and broadcast dashboard metrics"""
        while True:
            try:
                # Collect current metrics
                metrics = await self._collect_dashboard_metrics()

                # Check for changes
                if self._metrics_changed(metrics):
                    # Broadcast updates to dashboard subscribers
                    await self.sse_manager.broadcast_to_channel(
                        "dashboard",
                        SSEEvent(
                            event="metrics_update",
                            data={
                                "metrics": metrics,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                    )

                    self.metric_cache = metrics

                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error(f"Dashboard metrics update error: {e}")
                await asyncio.sleep(10)  # Wait longer on error

    async def _collect_dashboard_metrics(self) -> Dict[str, Any]:
        """Collect dashboard metrics from various sources"""
        return {
            "active_users": await self._get_active_users_count(),
            "orders_today": await self._get_orders_today_count(),
            "revenue_today": await self._get_revenue_today(),
            "system_health": await self._get_system_health(),
            "recent_activities": await self._get_recent_activities()
        }

    def _metrics_changed(self, new_metrics: Dict[str, Any]) -> bool:
        """Check if metrics have changed significantly"""
        if not self.metric_cache:
            return True

        # Check for significant changes (you can customize thresholds)
        for key, value in new_metrics.items():
            if key not in self.metric_cache:
                return True

            old_value = self.metric_cache[key]
            if isinstance(value, (int, float)) and isinstance(old_value, (int, float)):
                # Check for 5% change or absolute difference > 10
                if abs(value - old_value) > max(old_value * 0.05, 10):
                    return True
            elif value != old_value:
                return True

        return False

    async def send_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Send alert to dashboard subscribers"""
        await self.sse_manager.broadcast_to_channel(
            "dashboard",
            SSEEvent(
                event="alert",
                data={
                    "type": alert_type,
                    "message": message,
                    "severity": severity,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        )

class NotificationSSEService:
    """SSE service for user notifications"""

    def __init__(self, sse_manager: SSEManager):
        self.sse_manager = sse_manager

    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        data: Dict[str, Any] = None
    ):
        """Send notification to specific user"""
        notification_event = SSEEvent(
            event="notification",
            data={
                "title": title,
                "message": message,
                "type": notification_type,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        await self.sse_manager.send_event_to_user(user_id, notification_event)

    async def send_bulk_notification(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        notification_type: str = "info"
    ):
        """Send notification to multiple users"""
        notification_event = SSEEvent(
            event="notification",
            data={
                "title": title,
                "message": message,
                "type": notification_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        for user_id in user_ids:
            await self.sse_manager.send_event_to_user(user_id, notification_event)

class LiveDataStreamService:
    """SSE service for live data streaming"""

    def __init__(self, sse_manager: SSEManager):
        self.sse_manager = sse_manager
        self.data_sources = {}

    async def register_data_source(
        self,
        source_id: str,
        data_generator: Callable,
        interval: int = 1,
        channel: str = None
    ):
        """Register a data source for live streaming"""
        channel = channel or f"data:{source_id}"

        self.data_sources[source_id] = {
            "generator": data_generator,
            "interval": interval,
            "channel": channel,
            "task": None
        }

        # Start streaming task
        self.data_sources[source_id]["task"] = asyncio.create_task(
            self._stream_data_source(source_id)
        )

    async def _stream_data_source(self, source_id: str):
        """Stream data from registered source"""
        source_config = self.data_sources[source_id]

        while source_id in self.data_sources:
            try:
                # Generate data
                data = await source_config["generator"]()

                # Stream to subscribers
                await self.sse_manager.broadcast_to_channel(
                    source_config["channel"],
                    SSEEvent(
                        event="data_update",
                        data={
                            "source_id": source_id,
                            "data": data,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )

                await asyncio.sleep(source_config["interval"])

            except Exception as e:
                logger.error(f"Data streaming error for {source_id}: {e}")
                await asyncio.sleep(source_config["interval"] * 2)

    async def unregister_data_source(self, source_id: str):
        """Unregister data source"""
        if source_id in self.data_sources:
            task = self.data_sources[source_id].get("task")
            if task:
                task.cancel()

            del self.data_sources[source_id]

# Example data generators
async def stock_price_generator():
    """Generate mock stock price data"""
    import random
    return {
        "symbol": "AAPL",
        "price": round(150 + random.uniform(-5, 5), 2),
        "change": round(random.uniform(-2, 2), 2),
        "volume": random.randint(1000000, 5000000)
    }

async def system_metrics_generator():
    """Generate system metrics data"""
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "active_connections": len(sse_manager.active_connections)
    }
```

## SSE Client Integration

### JavaScript Client

```javascript
class SSEClient {
    constructor(url, options = {}) {
        this.url = url;
        this.options = {
            retry: 3000,
            maxRetries: 5,
            reconnectDelay: 1000,
            ...options
        };

        this.eventSource = null;
        this.retryCount = 0;
        this.lastEventId = null;
        this.listeners = new Map();
        this.connectionState = 'disconnected';
    }

    connect() {
        if (this.eventSource) {
            this.disconnect();
        }

        const url = this.buildUrl();
        this.eventSource = new EventSource(url);

        this.eventSource.onopen = (event) => {
            this.connectionState = 'connected';
            this.retryCount = 0;
            this.emit('connected', { event });
            console.log('SSE connected');
        };

        this.eventSource.onmessage = (event) => {
            this.handleMessage(event);
        };

        this.eventSource.onerror = (event) => {
            this.connectionState = 'error';
            this.emit('error', { event });

            if (this.retryCount < this.options.maxRetries) {
                this.scheduleReconnect();
            } else {
                console.error('SSE max retries exceeded');
                this.emit('maxRetriesExceeded', { retryCount: this.retryCount });
            }
        };

        // Handle custom event types
        this.setupCustomEventHandlers();
    }

    buildUrl() {
        let url = this.url;
        const params = new URLSearchParams();

        if (this.options.channels) {
            params.append('channels', this.options.channels.join(','));
        }

        if (this.options.filters) {
            params.append('filters', JSON.stringify(this.options.filters));
        }

        if (this.lastEventId) {
            params.append('last_event_id', this.lastEventId);
        }

        if (params.toString()) {
            url += '?' + params.toString();
        }

        return url;
    }

    setupCustomEventHandlers() {
        const customEvents = [
            'connected', 'notification', 'metrics_update',
            'alert', 'data_update', 'heartbeat'
        ];

        customEvents.forEach(eventType => {
            this.eventSource.addEventListener(eventType, (event) => {
                this.handleMessage(event);
            });
        });
    }

    handleMessage(event) {
        try {
            // Update last event ID
            if (event.lastEventId) {
                this.lastEventId = event.lastEventId;
                localStorage.setItem('sse_last_event_id', this.lastEventId);
            }

            // Parse data
            let data;
            try {
                data = JSON.parse(event.data);
            } catch {
                data = event.data;
            }

            // Emit to listeners
            this.emit(event.type, {
                id: event.lastEventId,
                type: event.type,
                data: data,
                timestamp: new Date()
            });

        } catch (error) {
            console.error('Error handling SSE message:', error);
        }
    }

    scheduleReconnect() {
        this.retryCount++;
        const delay = this.options.reconnectDelay * Math.pow(2, this.retryCount - 1);

        console.log(`SSE reconnecting in ${delay}ms (attempt ${this.retryCount})`);

        setTimeout(() => {
            if (this.connectionState === 'error') {
                this.connect();
            }
        }, delay);
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.connectionState = 'disconnected';
        this.emit('disconnected');
    }

    // Event listener management
    on(eventType, callback) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, []);
        }
        this.listeners.get(eventType).push(callback);
    }

    off(eventType, callback) {
        if (this.listeners.has(eventType)) {
            const callbacks = this.listeners.get(eventType);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    emit(eventType, data) {
        if (this.listeners.has(eventType)) {
            this.listeners.get(eventType).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in SSE event listener for ${eventType}:`, error);
                }
            });
        }
    }

    // Utility methods
    getConnectionState() {
        return this.connectionState;
    }

    getLastEventId() {
        return this.lastEventId;
    }

    updateChannels(channels) {
        this.options.channels = channels;
        if (this.connectionState === 'connected') {
            this.connect(); // Reconnect with new channels
        }
    }

    updateFilters(filters) {
        this.options.filters = filters;
        if (this.connectionState === 'connected') {
            this.connect(); // Reconnect with new filters
        }
    }
}

// Usage examples
const sseClient = new SSEClient('/events/authenticated', {
    channels: ['dashboard', 'notifications'],
    filters: { user_id: '123' },
    retry: 3000,
    maxRetries: 5
});

// Listen for events
sseClient.on('notification', (event) => {
    console.log('Received notification:', event.data);
    showNotification(event.data.title, event.data.message);
});

sseClient.on('metrics_update', (event) => {
    console.log('Metrics updated:', event.data.metrics);
    updateDashboard(event.data.metrics);
});

sseClient.on('alert', (event) => {
    console.log('Alert received:', event.data);
    showAlert(event.data.message, event.data.severity);
});

sseClient.on('connected', () => {
    console.log('SSE connection established');
});

sseClient.on('error', (error) => {
    console.error('SSE connection error:', error);
});

// Connect
sseClient.connect();

// Utility functions
function showNotification(title, message) {
    // Implementation for showing notifications
    if (Notification.permission === 'granted') {
        new Notification(title, { body: message });
    }
}

function updateDashboard(metrics) {
    // Implementation for updating dashboard
    document.getElementById('active-users').textContent = metrics.active_users;
    document.getElementById('orders-today').textContent = metrics.orders_today;
    // ... update other metrics
}

function showAlert(message, severity) {
    // Implementation for showing alerts
    const alertClass = severity === 'error' ? 'alert-danger' :
                      severity === 'warning' ? 'alert-warning' : 'alert-info';

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass}`;
    alertDiv.textContent = message;

    document.getElementById('alerts-container').appendChild(alertDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
```

## Testing SSE Implementation

### SSE Testing Framework

```python
import pytest
import asyncio
import aiohttp
from typing import List, Dict, Any

class SSETester:
    """Testing utilities for SSE functionality"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def test_sse_connection(self):
        """Test basic SSE connection"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/events") as response:
                assert response.status == 200
                assert response.headers['content-type'] == 'text/event-stream'

                # Read first event (connection confirmation)
                line = await response.content.readline()
                assert line.startswith(b'event: connected')

    async def test_event_streaming(self):
        """Test receiving events via SSE"""
        events_received = []

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/events?channels=test_channel"
            ) as response:

                # Create task to collect events
                async def collect_events():
                    try:
                        async for line in response.content:
                            line_str = line.decode().strip()
                            if line_str.startswith('data: '):
                                events_received.append(line_str[6:])
                            if len(events_received) >= 2:  # Stop after 2 events
                                break
                    except asyncio.CancelledError:
                        pass

                collect_task = asyncio.create_task(collect_events())

                # Wait a bit for connection
                await asyncio.sleep(0.1)

                # Send test event via API
                await self._trigger_test_event("test_channel")

                # Wait for events
                try:
                    await asyncio.wait_for(collect_task, timeout=5.0)
                except asyncio.TimeoutError:
                    collect_task.cancel()

        assert len(events_received) >= 1

    async def test_event_replay(self):
        """Test event replay functionality"""
        # First, send some events
        for i in range(3):
            await self._trigger_test_event("replay_test", f"Event {i}")

        # Get events with replay
        events = await self._get_events_with_replay("replay_test")

        assert len(events) >= 3

    async def test_filtered_events(self):
        """Test event filtering"""
        filters = {"user_id": "123"}

        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/events?channels=filter_test&filters={json.dumps(filters)}"

            async with session.get(url) as response:
                # Implementation for testing filtered events
                pass

    async def _trigger_test_event(self, channel: str, data: str = "test data"):
        """Trigger a test event via internal API"""
        # This would call your internal API to trigger an SSE event
        # Implementation depends on your application structure
        pass

    async def _get_events_with_replay(self, channel: str) -> List[str]:
        """Get events with replay functionality"""
        events = []

        async with aiohttp.ClientSession() as session:
            # Set last event ID to trigger replay
            headers = {"Last-Event-ID": "some-old-event-id"}

            async with session.get(
                f"{self.base_url}/events?channels={channel}",
                headers=headers
            ) as response:

                async for line in response.content:
                    line_str = line.decode().strip()
                    if line_str.startswith('data: '):
                        events.append(line_str[6:])
                    if len(events) >= 5:  # Limit for test
                        break

        return events

class SSEPerformanceTester:
    """Performance testing for SSE implementation"""

    async def test_concurrent_connections(self, connection_count: int = 100):
        """Test multiple concurrent SSE connections"""
        connections = []
        start_time = asyncio.get_event_loop().time()

        try:
            async with aiohttp.ClientSession() as session:
                # Create concurrent connections
                tasks = []
                for i in range(connection_count):
                    task = asyncio.create_task(
                        self._create_sse_connection(session, f"connection_{i}")
                    )
                    tasks.append(task)

                # Wait for all connections
                connections = await asyncio.gather(*tasks, return_exceptions=True)

                connection_time = asyncio.get_event_loop().time() - start_time

                # Test broadcasting to all connections
                start_time = asyncio.get_event_loop().time()
                await self._broadcast_test_event()
                broadcast_time = asyncio.get_event_loop().time() - start_time

                return {
                    "concurrent_connections": connection_count,
                    "successful_connections": len([c for c in connections if not isinstance(c, Exception)]),
                    "connection_time": connection_time,
                    "broadcast_time": broadcast_time
                }

        finally:
            # Clean up connections
            for connection in connections:
                if hasattr(connection, 'close'):
                    connection.close()

    async def _create_sse_connection(self, session: aiohttp.ClientSession, connection_id: str):
        """Create individual SSE connection for testing"""
        try:
            response = await session.get(f"{self.base_url}/events?channels=performance_test")
            return response
        except Exception as e:
            return e

    async def _broadcast_test_event(self):
        """Broadcast test event for performance testing"""
        # Implementation for triggering broadcast event
        pass

# pytest fixtures and test cases
@pytest.fixture
def sse_tester():
    return SSETester("http://localhost:8000")

@pytest.mark.asyncio
async def test_basic_sse_functionality(sse_tester):
    await sse_tester.test_sse_connection()

@pytest.mark.asyncio
async def test_sse_event_streaming(sse_tester):
    await sse_tester.test_event_streaming()

@pytest.mark.asyncio
async def test_sse_event_replay(sse_tester):
    await sse_tester.test_event_replay()
```

## Related Documentation

- [WebSocket Patterns](websocket-patterns.md)
- [Push Notifications](push-notifications.md)
- [Real-time Sync Patterns](real-time-sync-patterns.md)
- [FastAPI Basic Setup](../services/fastapi/basic-setup.md)

## Best Practices

1. **Connection Management**:
   - Implement proper connection cleanup
   - Use heartbeats to detect stale connections
   - Handle reconnection gracefully

2. **Event Design**:
   - Use structured event formats
   - Implement event replay for reliability
   - Apply filtering to reduce bandwidth

3. **Performance**:
   - Monitor active connection count
   - Implement connection limits
   - Use efficient event serialization

4. **Reliability**:
   - Store events for replay
   - Implement proper error handling
   - Use Redis for distributed coordination

5. **Security**:
   - Authenticate connections when needed
   - Validate event permissions
   - Implement rate limiting