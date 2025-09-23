# Task Management System Use Case

> **📋 DOCUMENTATION TYPE**: Working Demonstration - Complete functional application
> **👥 TARGET USERS**: Business stakeholders, developers, QA teams
> **🔗 RELATED**: [Learning Patterns](../../examples/) | [AI Generation](../../ai_agents/) | **[Complete Comparison Guide](../../CLAUDE.md#documentation-types-guide)**

A complete personal task management system demonstrating all microservices patterns from the boilerplate. This use case showcases the **Improved Hybrid Approach** with centralized data services and business logic separation.

## 🎯 Use Case Overview

This system provides a comprehensive task management solution with:

- **REST API** for task CRUD operations
- **Telegram Bot** for natural language task creation and management
- **Smart Reminders** with due date notifications
- **Analytics** for productivity insights and reporting
- **File Attachments** via Telegram
- **Real-time Events** between all services

## 🏗️ Architecture

### Service Types Demonstrated

#### FastAPI Service (`api_service.py`)
- Task CRUD operations with validation
- User authentication and authorization
- Redis caching for performance
- RabbitMQ event publishing
- HTTP-only data access via data services

#### Telegram Bot Service (`bot_service.py`)
- Natural language task creation
- Quick status updates and task management
- File attachment processing
- Real-time notifications
- User session management

#### AsyncIO Workers
- **Reminder Worker** (`reminder_worker.py`): Due date monitoring and notifications
- **Analytics Worker** (`analytics_worker.py`): Productivity tracking and insights

#### Data Services (from main boilerplate)
- **db_postgres_service**: Task storage and relational queries
- **db_mongo_service**: Analytics and activity logging

## 🚀 Quick Start

### Prerequisites

1. **Docker & Docker Compose** installed
2. **Telegram Bot Token** (get from [@BotFather](https://t.me/botfather))
3. **Python 3.12+** (for local development)

### 1. Environment Setup

```bash
# Clone and navigate to use case
cd use_cases/task_management

# Copy environment template
cp .env.example .env

# Edit .env with your Telegram bot token
nano .env
```

Required environment variables:
```env
BOT_TOKEN=your-telegram-bot-token-here
BOT_USERNAME=your_bot_username

# Optional: Database passwords (defaults provided)
POSTGRES_PASSWORD=postgres123
MONGO_PASSWORD=mongo123
REDIS_PASSWORD=redis123
RABBITMQ_PASSWORD=admin123
```

### 2. Build and Start Services

```bash
# Start complete stack
docker-compose up -d

# Or start with monitoring
docker-compose --profile monitoring up -d

# Check service health
docker-compose ps
```

### 3. Verify Setup

```bash
# Test API service
curl http://localhost:8000/health

# Test data services
curl http://localhost:8001/health  # PostgreSQL service
curl http://localhost:8002/health  # MongoDB service

# Check RabbitMQ management
open http://localhost:15672  # admin/admin123
```

## 📱 Using the System

### REST API Usage

Access the interactive API documentation:
- **Task API**: http://localhost:8000/docs
- **PostgreSQL Data API**: http://localhost:8001/docs
- **MongoDB Data API**: http://localhost:8002/docs

#### Example API Calls

```bash
# Create a user account
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Create a task
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "medium",
    "due_date": "2025-01-16T18:00:00Z"
  }'

# Get tasks
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tasks"

# Get productivity stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tasks/stats"
```

### Telegram Bot Usage

Start a chat with your bot and use these commands:

#### Basic Commands
```
/start                    - Initialize bot and authenticate
/task Buy groceries tomorrow high priority  - Create task with natural language
/mytasks                  - List your tasks
/pending                  - Show pending tasks
/completed                - Show completed tasks
/stats                    - Your productivity statistics
```

#### Task Management
```
/done 123                 - Mark task 123 as complete
/start_task 123           - Mark task 123 as in progress
/cancel 123               - Cancel task 123
```

#### Natural Language Examples
```
/task Meeting at 3pm due today urgent
/task Write report by friday
/task Call mom tomorrow
/task Buy groceries !!!  (urgent priority)
/task Review document low priority
```

#### File Attachments
- Send any photo or document to attach to tasks
- Supported formats: Images, PDFs, Word docs, text files
- Files are processed by workers for analysis

### Smart Features

#### Automatic Reminders
- **Due Soon**: 1 hour before due time
- **Overdue**: Daily notifications for overdue tasks
- **Custom Reminders**: Set specific reminder times

#### Analytics Dashboard
- Completion rate tracking
- Most productive hours analysis
- Priority distribution insights
- Overdue task patterns
- Historical performance trends

## 🔧 Development

### Local Development Setup

> **📋 Complete development guide**: [Development Commands](../../docs/guides/DEVELOPMENT_COMMANDS.md)

```bash
# Quick setup
uv sync --dev
docker-compose up -d
python api_service.py
```

### Custom Configuration

Edit `docker-compose.yml` for custom settings:

```yaml
# Adjust reminder intervals
task_reminder_worker:
  environment:
    CHECK_INTERVAL_SECONDS: 300    # Check every 5 minutes
    DUE_SOON_MINUTES: 60          # Notify 1 hour before due

# Scale analytics processing
task_analytics_worker:
  environment:
    BATCH_SIZE: 100
    MAX_CONCURRENT_PROCESSING: 10
```

### Adding New Features

1. **Extend DTOs**: Add new fields to `shared_dtos.py`
2. **API Endpoints**: Add routes to `api_service.py`
3. **Bot Commands**: Add handlers to `bot_service.py`
4. **Background Processing**: Add workers or extend existing ones
5. **Events**: Add new event types for cross-service communication

## 📊 Monitoring

### Task Service Logs
```bash
# Task-specific service logs
docker-compose logs -f task_api_service
docker-compose logs -f task_bot_service
docker-compose logs -f task_reminder_worker
docker-compose logs -f task_analytics_worker
```

### Task API Health Checks
```bash
curl http://localhost:8000/api/v1/tasks/stats
curl http://localhost:8000/api/v1/tasks
```

> **📋 Complete monitoring guide**: [Use Cases Monitoring](../README.md#monitoring--observability)

## 🧪 Testing

### Quick Task Workflow Test
```bash
# API testing
curl -X POST http://localhost:8000/api/v1/auth/register ...
curl -X POST http://localhost:8000/api/v1/tasks ...
curl http://localhost:8000/api/v1/tasks/stats
```

### Bot Commands Test
```
/start /task Buy groceries /mytasks /done 123
```

> **📋 Complete testing guide**: [Use Cases Testing](../README.md#testing-examples)

## 🚀 Production Deployment

### Key Configuration
```env
SECRET_KEY=production-secret-key
BOT_TOKEN=production-bot-token
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/tasks
MONGODB_URL=mongodb://user:pass@prod-mongo:27017/analytics
```

### Scaling
```bash
docker-compose up -d --scale task_api_service=3
docker-compose up -d --scale task_analytics_worker=2
```

> **📋 Complete deployment guide**: [Use Cases Deployment](../README.md#quick-start-any-use-case)

## 🔍 Troubleshooting

### Common Issues

**Bot not responding**: Check `docker-compose logs task_bot_service` and verify `$BOT_TOKEN`

**Reminders not working**: Check `docker-compose logs task_reminder_worker`

**Analytics issues**: Check `docker-compose logs task_analytics_worker`

> **📋 Complete troubleshooting guide**: [Use Cases Troubleshooting](../README.md) | [General Troubleshooting](../../docs/reference/troubleshooting.md)

## 📚 Learning Focus

**Task Domain**: Personal productivity, natural language processing, smart reminders
**Bot Integration**: Telegram commands, file attachments, user sessions
**Background Processing**: Due date monitoring, analytics aggregation, event-driven workflows

> **📋 Complete architecture patterns**: [Use Cases Architecture](../README.md#architecture-patterns-demonstrated)

## 🎯 Next Steps

**Extensions**: Team collaboration, subtasks, calendar integration, mobile app, voice commands, task templates
**Advanced**: AI prioritization, ML insights, external integrations (Jira, Trello, Slack), advanced analytics, multi-language

## 📞 Support

1. Check logs: `docker-compose logs [service-name]`
2. Review: [Main documentation](../../README.md)
3. Test: Health check endpoints
4. Validate: Environment variables

> **🚀 Complete reference implementation for production-ready microservices!**