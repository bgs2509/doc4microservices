# Use Case Integration Example

> **🎯 PURPOSE**: Complete guide for structuring and integrating use cases into the microservices architecture

This example demonstrates how to properly structure, integrate, and deploy complete use cases using the Improved Hybrid Approach architecture.

## 📋 Table of Contents

- [Use Case Structure](#use-case-structure)
- [Integration Patterns](#integration-patterns)
- [Service Communication](#service-communication)
- [Data Flow](#data-flow)
- [Event-Driven Architecture](#event-driven-architecture)
- [Testing Strategy](#testing-strategy)
- [Deployment Integration](#deployment-integration)
- [Complete Example: Task Management](#complete-example-task-management)

## 🏗️ Use Case Structure

### Recommended Directory Structure

```
use_cases/
├── your_use_case/
│   ├── README.md                    # Complete use case documentation
│   ├── docker-compose.yml          # Use case orchestration
│   ├── docker-compose.override.yml # Development overrides
│   ├── .env.example                # Environment template
│   ├── .env                        # Local configuration
│   │
│   ├── services/                   # Business logic services
│   │   ├── api_service.py          # FastAPI REST API
│   │   ├── bot_service.py          # Telegram/Discord bot
│   │   ├── worker_service.py       # AsyncIO background workers
│   │   └── shared_dtos.py          # Common data transfer objects
│   │
│   ├── tests/                      # Use case specific tests
│   │   ├── test_integration.py     # Cross-service integration tests
│   │   ├── test_api_service.py     # API service unit tests
│   │   ├── test_bot_service.py     # Bot service unit tests
│   │   └── test_workers.py         # Worker service unit tests
│   │
│   ├── docs/                       # Use case documentation
│   │   ├── api_reference.md        # API endpoint documentation
│   │   ├── bot_commands.md         # Bot command reference
│   │   ├── architecture.md         # Use case specific architecture
│   │   └── deployment.md           # Deployment instructions
│   │
│   └── config/                     # Configuration files
│       ├── nginx.conf              # Custom nginx configuration
│       ├── monitoring.yml          # Custom monitoring rules
│       └── alerts.yml              # Custom alerting rules
```

### Core Integration Principles

#### 1. **Service Isolation**
```python
# ❌ WRONG: Direct database access in business service
class TaskService:
    def __init__(self):
        self.db = Database()  # Direct DB connection

    async def create_task(self, task_data):
        return await self.db.tasks.insert(task_data)

# ✅ CORRECT: HTTP-only data access
class TaskService:
    def __init__(self):
        self.postgres_client = HttpClient("http://db_postgres_service:8001")
        self.mongo_client = HttpClient("http://db_mongo_service:8002")

    async def create_task(self, task_data):
        # Business logic validation
        validated_task = self._validate_task(task_data)

        # Store via data service
        task = await self.postgres_client.post("/tasks", validated_task)

        # Log activity via MongoDB service
        await self.mongo_client.post("/activity_logs", {
            "action": "task_created",
            "task_id": task["id"],
            "user_id": validated_task["user_id"]
        })

        return task
```

#### 2. **Event-Driven Communication**
```python
# Use case event publisher
class UseCase EventPublisher:
    def __init__(self, rabbitmq_client):
        self.rabbitmq = rabbitmq_client

    async def publish_task_event(self, event_type: str, task_data: dict):
        """Publish task-related events for cross-service communication"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": task_data,
            "source_service": "task_api_service"
        }

        # Publish to multiple exchanges for different consumers
        await self.rabbitmq.publish(
            exchange="task_events",
            routing_key=f"task.{event_type}",
            message=event
        )

        # Specific routing for urgent tasks
        if task_data.get("priority") == "urgent":
            await self.rabbitmq.publish(
                exchange="urgent_notifications",
                routing_key="urgent.task",
                message=event
            )

# Event consumer in worker service
class TaskEventConsumer:
    async def handle_task_created(self, event_data):
        """Handle task creation events"""
        task = event_data["data"]

        # Schedule reminder if due date exists
        if task.get("due_date"):
            await self._schedule_reminder(task)

        # Update analytics
        await self._update_task_analytics(task)

    async def handle_task_completed(self, event_data):
        """Handle task completion events"""
        task = event_data["data"]

        # Cancel any pending reminders
        await self._cancel_reminders(task["id"])

        # Update completion statistics
        await self._update_completion_stats(task)
```

## 🔄 Service Communication Patterns

### 1. **Synchronous Communication (HTTP)**

```python
# API Service → Data Service communication
class TaskAPIService:
    def __init__(self):
        self.postgres_service = DataServiceClient("http://db_postgres_service:8001")
        self.mongo_service = DataServiceClient("http://db_mongo_service:8002")

    async def get_user_tasks(self, user_id: int, filters: dict):
        """Get user tasks with filtering and analytics"""

        # Get tasks from PostgreSQL service
        tasks_response = await self.postgres_service.get(
            f"/users/{user_id}/tasks",
            params=filters
        )

        # Get analytics from MongoDB service
        analytics_response = await self.mongo_service.get(
            f"/users/{user_id}/task_analytics"
        )

        # Combine data in business logic layer
        return {
            "tasks": tasks_response["data"],
            "analytics": analytics_response["data"],
            "pagination": tasks_response["pagination"]
        }

# Data Service Client with error handling
class DataServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )

    async def get(self, endpoint: str, params: dict = None):
        """GET request with retry logic"""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(3):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        raise NotFoundError(f"Resource not found: {url}")
                    else:
                        response.raise_for_status()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == 2:  # Last attempt
                    raise ServiceUnavailableError(f"Data service unavailable: {e}")
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
```

### 2. **Asynchronous Communication (Events)**

```python
# Event-driven worker coordination
class TaskReminderWorker:
    def __init__(self):
        self.rabbitmq = RabbitMQClient()
        self.postgres_service = DataServiceClient("http://db_postgres_service:8001")
        self.telegram_service = TelegramNotificationService()

    async def start(self):
        """Start consuming task events"""
        # Consume task creation events
        await self.rabbitmq.consume(
            queue="task_reminders",
            callback=self.handle_task_event
        )

    async def handle_task_event(self, event):
        """Process task events for reminder scheduling"""
        event_type = event["event_type"]
        task_data = event["data"]

        if event_type == "task_created" and task_data.get("due_date"):
            await self._schedule_reminder(task_data)

        elif event_type == "task_updated":
            await self._update_reminder(task_data)

        elif event_type == "task_completed":
            await self._cancel_reminder(task_data["id"])

    async def _schedule_reminder(self, task_data):
        """Schedule reminder for task"""
        due_date = datetime.fromisoformat(task_data["due_date"])
        reminder_time = due_date - timedelta(hours=1)  # 1 hour before

        if reminder_time > datetime.utcnow():
            # Schedule reminder job
            reminder_job = {
                "task_id": task_data["id"],
                "user_id": task_data["user_id"],
                "reminder_time": reminder_time.isoformat(),
                "message": f"Reminder: '{task_data['title']}' is due in 1 hour"
            }

            # Store reminder in database via data service
            await self.postgres_service.post("/reminders", reminder_job)
```

## 📊 Data Flow Patterns

### Complete Use Case Data Flow

```mermaid
graph TD
    A[User Request] --> B[API Gateway/Load Balancer]
    B --> C[API Service FastAPI]

    C --> D[PostgreSQL Data Service]
    C --> E[MongoDB Data Service]
    C --> F[Redis Cache]

    C --> G[RabbitMQ Events]
    G --> H[Bot Service Aiogram]
    G --> I[Worker Services]

    I --> D
    I --> E
    I --> J[External APIs]

    H --> K[Telegram API]
    H --> G

    D --> L[PostgreSQL Database]
    E --> M[MongoDB Database]
    F --> N[Redis Database]
```

### Data Consistency Patterns

```python
# Eventual consistency with event sourcing
class TaskTransactionService:
    def __init__(self):
        self.postgres_service = DataServiceClient("http://db_postgres_service:8001")
        self.mongo_service = DataServiceClient("http://db_mongo_service:8002")
        self.event_publisher = EventPublisher()

    async def create_task_with_consistency(self, task_data):
        """Create task with eventual consistency guarantees"""
        transaction_id = str(uuid.uuid4())

        try:
            # 1. Store primary data (PostgreSQL)
            task = await self.postgres_service.post("/tasks", {
                **task_data,
                "transaction_id": transaction_id,
                "status": "pending"
            })

            # 2. Publish event for secondary systems
            await self.event_publisher.publish("task_created", {
                "task": task,
                "transaction_id": transaction_id
            })

            # 3. Mark transaction as committed
            await self.postgres_service.patch(f"/tasks/{task['id']}", {
                "status": "active"
            })

            return task

        except Exception as e:
            # Compensation: cleanup partial state
            await self.event_publisher.publish("task_creation_failed", {
                "transaction_id": transaction_id,
                "error": str(e)
            })
            raise
```

## 🧪 Testing Strategy

### Integration Testing

```python
# Complete use case integration test
class TestTaskManagementIntegration:
    def __init__(self):
        self.api_client = TestClient(app)
        self.postgres_service = TestDataServiceClient("http://localhost:8001")
        self.mongo_service = TestDataServiceClient("http://localhost:8002")
        self.rabbitmq_client = TestRabbitMQClient()

    async def test_complete_task_workflow(self):
        """Test complete task creation to completion workflow"""

        # 1. Create user account
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }

        auth_response = self.api_client.post("/api/v1/auth/register", json=user_data)
        assert auth_response.status_code == 201
        auth_token = auth_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {auth_token}"}

        # 2. Create task via API
        task_data = {
            "title": "Test Integration Task",
            "description": "Testing complete workflow",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }

        task_response = self.api_client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=headers
        )
        assert task_response.status_code == 201
        task = task_response.json()

        # 3. Verify task stored in PostgreSQL
        postgres_task = await self.postgres_service.get(f"/tasks/{task['id']}")
        assert postgres_task["title"] == task_data["title"]

        # 4. Verify event published to RabbitMQ
        events = await self.rabbitmq_client.get_messages("task_events")
        creation_event = next(e for e in events if e["event_type"] == "task_created")
        assert creation_event["data"]["id"] == task["id"]

        # 5. Wait for worker processing
        await asyncio.sleep(1)

        # 6. Verify analytics recorded in MongoDB
        analytics = await self.mongo_service.get(f"/task_analytics/task/{task['id']}")
        assert analytics["action"] == "created"

        # 7. Complete task
        complete_response = self.api_client.patch(
            f"/api/v1/tasks/{task['id']}",
            json={"status": "completed"},
            headers=headers
        )
        assert complete_response.status_code == 200

        # 8. Verify completion analytics
        await asyncio.sleep(1)
        completion_analytics = await self.mongo_service.get(
            f"/task_analytics/task/{task['id']}/completion"
        )
        assert completion_analytics["completed_at"] is not None

# Load testing for use case
class TestTaskManagementLoad:
    async def test_concurrent_task_creation(self):
        """Test system under concurrent load"""

        async def create_tasks_batch(user_token, batch_size=10):
            tasks = []
            for i in range(batch_size):
                task_data = {
                    "title": f"Load Test Task {i}",
                    "description": f"Batch task number {i}",
                    "priority": random.choice(["low", "medium", "high"])
                }

                response = self.api_client.post(
                    "/api/v1/tasks",
                    json=task_data,
                    headers={"Authorization": f"Bearer {user_token}"}
                )
                tasks.append(response.json())

            return tasks

        # Create test users
        users = []
        for i in range(5):
            user_response = self.api_client.post("/api/v1/auth/register", json={
                "username": f"loaduser{i}",
                "email": f"load{i}@example.com",
                "password": "loadtest123"
            })
            users.append(user_response.json()["access_token"])

        # Concurrent task creation
        start_time = time.time()

        tasks = await asyncio.gather(*[
            create_tasks_batch(user_token) for user_token in users
        ])

        end_time = time.time()

        # Verify performance
        total_tasks = sum(len(user_tasks) for user_tasks in tasks)
        duration = end_time - start_time
        tasks_per_second = total_tasks / duration

        assert tasks_per_second > 50  # Minimum performance requirement
        assert duration < 10  # Should complete within 10 seconds
```

## 🚀 Deployment Integration

### Docker Compose Integration

```yaml
# use_cases/task_management/docker-compose.yml
version: '3.8'

services:
  # Business Logic Services
  task_api_service:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_SERVICE_URL=http://db_postgres_service:8001
      - ANALYTICS_SERVICE_URL=http://db_mongo_service:8002
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
    depends_on:
      - db_postgres_service
      - db_mongo_service
      - redis
      - rabbitmq
    networks:
      - microservices_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  task_bot_service:
    build:
      context: .
      dockerfile: Dockerfile.bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - API_SERVICE_URL=http://task_api_service:8000
      - RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
    depends_on:
      - task_api_service
      - rabbitmq
    networks:
      - microservices_network
    restart: unless-stopped

  task_reminder_worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: ["python", "reminder_worker.py"]
    environment:
      - DATABASE_SERVICE_URL=http://db_postgres_service:8001
      - RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
      - CHECK_INTERVAL_SECONDS=300
    depends_on:
      - db_postgres_service
      - rabbitmq
    networks:
      - microservices_network
    restart: unless-stopped

  task_analytics_worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: ["python", "analytics_worker.py"]
    environment:
      - ANALYTICS_SERVICE_URL=http://db_mongo_service:8002
      - RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
      - BATCH_SIZE=100
    depends_on:
      - db_mongo_service
      - rabbitmq
    networks:
      - microservices_network
    restart: unless-stopped

  # Data Services (from main boilerplate)
  db_postgres_service:
    extends:
      file: ../../docker-compose.yml
      service: db_postgres_service

  db_mongo_service:
    extends:
      file: ../../docker-compose.yml
      service: db_mongo_service

  # Infrastructure (from main boilerplate)
  postgres:
    extends:
      file: ../../docker-compose.yml
      service: postgres

  mongodb:
    extends:
      file: ../../docker-compose.yml
      service: mongodb

  redis:
    extends:
      file: ../../docker-compose.yml
      service: redis

  rabbitmq:
    extends:
      file: ../../docker-compose.yml
      service: rabbitmq

networks:
  microservices_network:
    external: true

volumes:
  postgres_data:
  mongodb_data:
  redis_data:
  rabbitmq_data:
```

### Environment Configuration

```bash
# use_cases/task_management/.env.example
# Core Configuration
SECRET_KEY=your-secret-key-here
DEBUG=true
LOG_LEVEL=INFO

# Service URLs (auto-configured in Docker)
DATABASE_SERVICE_URL=http://db_postgres_service:8001
ANALYTICS_SERVICE_URL=http://db_mongo_service:8002
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/

# Bot Configuration
BOT_TOKEN=your-telegram-bot-token-here
BOT_USERNAME=your_bot_username

# Database Passwords (should match main compose)
POSTGRES_PASSWORD=postgres123
MONGO_PASSWORD=mongo123
REDIS_PASSWORD=redis123
RABBITMQ_PASSWORD=admin123

# Performance Tuning
MAX_TASKS_PER_PAGE=50
WORKER_BATCH_SIZE=100
MAX_CONCURRENT_REQUESTS=50
CONNECTION_POOL_SIZE=20

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
JAEGER_ENDPOINT=http://jaeger:14268/api/traces
```

## 📋 Complete Example: Task Management

The task management use case (`use_cases/task_management/`) serves as the reference implementation demonstrating all integration patterns:

### Architecture Overview

```mermaid
graph TB
    subgraph "User Interfaces"
        A[REST API Clients]
        B[Telegram Bot]
    end

    subgraph "Business Logic Layer"
        C[API Service FastAPI]
        D[Bot Service Aiogram]
        E[Reminder Worker]
        F[Analytics Worker]
    end

    subgraph "Data Access Layer"
        G[PostgreSQL Data Service]
        H[MongoDB Data Service]
    end

    subgraph "Infrastructure Layer"
        I[PostgreSQL Database]
        J[MongoDB Database]
        K[Redis Cache]
        L[RabbitMQ Message Broker]
    end

    A --> C
    B --> D

    C --> G
    C --> H
    C --> K
    C --> L

    D --> C
    D --> L

    E --> G
    E --> L

    F --> H
    F --> L

    G --> I
    H --> J

    L --> E
    L --> F
```

### Key Integration Points

1. **API → Data Services**: HTTP-only communication for all data operations
2. **Event-Driven Workers**: RabbitMQ for asynchronous task processing
3. **Cross-Service Communication**: Events for real-time updates between services
4. **Shared Infrastructure**: Redis, RabbitMQ, databases shared across all services
5. **Monitoring Integration**: Built-in health checks, metrics, and logging

### Usage Patterns

```bash
# Start complete use case
cd use_cases/task_management
docker-compose up -d

# Test integration
curl http://localhost:8000/health
curl http://localhost:8001/health  # PostgreSQL service
curl http://localhost:8002/health  # MongoDB service

# Monitor events
docker-compose logs -f task_reminder_worker
docker-compose logs -f task_analytics_worker

# Scale services
docker-compose up -d --scale task_api_service=3
docker-compose up -d --scale task_analytics_worker=2
```

## 📚 Best Practices Summary

### ✅ Do
- **Isolate services** by business domain and technology stack
- **Use HTTP APIs** for all data access from business services
- **Implement event-driven** communication for loose coupling
- **Include comprehensive health checks** and monitoring
- **Test integration scenarios** with real infrastructure
- **Document API contracts** and service dependencies
- **Use consistent naming** following project conventions
- **Implement proper error handling** and retry logic

### ❌ Don't
- **Mix event loop types** in the same process/container
- **Access databases directly** from business logic services
- **Create tight coupling** between services
- **Skip integration testing** for complex workflows
- **Ignore monitoring** and observability requirements
- **Hardcode service URLs** or configuration
- **Deploy without health checks** and readiness probes
- **Forget to handle service failures** gracefully

This use case integration example provides a complete template for building production-ready microservices that properly integrate with the Improved Hybrid Approach architecture! 🚀