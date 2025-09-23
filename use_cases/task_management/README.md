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

#### **FastAPI Service** (`api_service.py`)
- Task CRUD operations with validation
- User authentication and authorization
- Redis caching for performance
- RabbitMQ event publishing
- HTTP-only data access via data services

#### **Telegram Bot Service** (`bot_service.py`)
- Natural language task creation
- Quick status updates and task management
- File attachment processing
- Real-time notifications
- User session management

#### **AsyncIO Workers**
- **Reminder Worker** (`reminder_worker.py`): Due date monitoring and notifications
- **Analytics Worker** (`analytics_worker.py`): Productivity tracking and insights

#### **Data Services** (from main boilerplate)
- **PostgreSQL Service**: Task storage and relational queries
- **MongoDB Service**: Analytics and activity logging

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

> **📋 DEVELOPMENT COMMANDS**: For complete development setup and commands, see [../../docs/guides/DEVELOPMENT_COMMANDS.md](../../docs/guides/DEVELOPMENT_COMMANDS.md).

```bash
# Follow the standard development workflow from ../../docs/guides/DEVELOPMENT_COMMANDS.md
# Quick version:
uv sync --dev                    # Install dependencies
docker-compose up -d            # Start infrastructure
python api_service.py          # Run services locally
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

## 📊 Task-Specific Monitoring

### Task Service Logs

```bash
# Follow task-specific service logs
docker-compose logs -f task_api_service
docker-compose logs -f task_bot_service
docker-compose logs -f task_reminder_worker
docker-compose logs -f task_analytics_worker
```

### Task-Specific Health Checks

```bash
# Check task management endpoints
curl http://localhost:8000/api/v1/tasks/stats  # Task analytics
curl http://localhost:8000/api/v1/tasks       # Task list
```

> **📋 GENERAL MONITORING**: For complete monitoring setup, observability stack, and generic health checks, see [../README.md](../README.md#monitoring--observability)

## 🧪 Task Management Testing

### Task-Specific Manual Testing

```bash
# Test complete task workflow
curl -X POST http://localhost:8000/api/v1/auth/register ...  # Register user
curl -X POST http://localhost:8000/api/v1/tasks ...         # Create task
# Use Telegram bot to create tasks with natural language
# Check analytics at /api/v1/tasks/stats endpoint
# Verify reminders via bot notifications
```

### Task Bot Testing

```bash
# Test Telegram bot commands
/start                    # Initialize bot
/task Buy groceries      # Create task via bot
/mytasks                 # List tasks
/done 123               # Complete task
```

> **📋 GENERAL TESTING**: For complete testing strategies, load testing, and integration testing patterns, see [../README.md](../README.md#testing-examples)

## 🚀 Production Deployment

### Environment Variables

```env
# Security
SECRET_KEY=your-production-secret-key-here
JWT_ALGORITHM=HS256

# Database URLs (production)
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/tasks
MONGODB_URL=mongodb://user:pass@prod-mongo:27017/analytics

# External services
REDIS_URL=redis://:password@prod-redis:6379/0
RABBITMQ_URL=amqp://user:pass@prod-rabbitmq:5672/

# Bot configuration
BOT_TOKEN=production-bot-token
BOT_USERNAME=prod_taskbot

# Performance tuning
MAX_TASKS_PER_PAGE=100
BATCH_SIZE=200
MAX_CONCURRENT_PROCESSING=20
```

### Scaling

```bash
# Scale API service
docker-compose up -d --scale task_api_service=3

# Scale workers
docker-compose up -d --scale task_analytics_worker=2
```

### Backup

```bash
# Database backups
docker-compose exec postgres pg_dump -U postgres task_management_db > backup.sql
docker-compose exec mongodb mongodump --db task_analytics_db --out /backup/
```

## 🔍 Task Management Troubleshooting

### Task-Specific Issues

#### Telegram Bot Not Responding
```bash
# Check bot service logs
docker-compose logs task_bot_service

# Verify bot token configuration
echo $BOT_TOKEN

# Test bot externally
curl "https://api.telegram.org/bot$BOT_TOKEN/getMe"
```

#### Task Reminders Not Working
```bash
# Check reminder worker logs
docker-compose logs task_reminder_worker

# Verify task due dates are set correctly
curl http://localhost:8000/api/v1/tasks | grep due_date
```

#### Task Analytics Issues
```bash
# Check analytics worker logs
docker-compose logs task_analytics_worker

# Verify analytics data
curl http://localhost:8000/api/v1/tasks/stats
```

> **📋 GENERAL TROUBLESHOOTING**: For database connectivity, infrastructure issues, and general debugging, see [../README.md](../README.md) and [../../docs/reference/troubleshooting.md](../../docs/reference/troubleshooting.md)

## 📚 Task Management Learning Focus

This use case specifically demonstrates:

### ✅ **Task Domain Patterns**
- Personal productivity workflows
- Natural language task creation via Telegram
- Smart reminder systems with due date tracking
- Real-time analytics for productivity insights

### ✅ **Bot Integration Patterns**
- Telegram bot with natural language processing
- File attachment handling via bot
- User session management in chat interfaces
- Command-based task management

### ✅ **Background Processing Patterns**
- Due date monitoring and notification workers
- Analytics aggregation and reporting workers
- Event-driven task lifecycle management

> **📋 GENERAL LEARNING**: For complete architectural patterns, technology integration, and production practices, see [../README.md](../README.md#architecture-patterns-demonstrated)

## 🎯 Next Steps

### Extend the System
1. **Add team collaboration** (shared tasks, assignments)
2. **Implement subtasks** and task dependencies
3. **Add calendar integration** (Google Calendar, Outlook)
4. **Create mobile app** using the REST API
5. **Add voice commands** via Telegram voice messages
6. **Implement task templates** for recurring tasks

### Advanced Features
1. **AI-powered task prioritization**
2. **Productivity coaching** with ML insights
3. **Integration with external tools** (Jira, Trello, Slack)
4. **Advanced analytics** with charts and trends
5. **Multi-language support** for international users

---

## 📞 Support

For questions about this use case:

1. **Check logs**: `docker-compose logs [service-name]`
2. **Review documentation**: See main project README.md
3. **Test individual services**: Use health check endpoints
4. **Validate configuration**: Check environment variables

This use case serves as a complete reference implementation for building production-ready microservices with the boilerplate architecture! 🚀