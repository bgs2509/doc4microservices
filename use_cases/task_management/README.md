# Task Management System Use Case

> **📋 DOCUMENTATION TYPE**: Working Demonstration - Complete functional application
> **👥 TARGET USERS**: Business stakeholders, developers, QA teams
> **🔗 RELATED**: [Learning Patterns](../../docs/LINKS_REFERENCE.md#examples-and-templates) | [AI Generation](../../docs/LINKS_REFERENCE.md#examples-and-templates) | **[Complete Comparison Guide](../../docs/LINKS_REFERENCE.md#core-documentation)**

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

> **⚠️ ARCHITECTURE WARNING**: The flat file structure in this use case (`api_service.py`, `bot_service.py` in the root) is for demonstration purposes only. It is **NOT** the canonical architecture. New projects **MUST** follow the standard project structure with services located in the `src/services/` directory, as detailed in the [Project Structure Guide](../../docs/LINKS_REFERENCE.md#developer-guides).

### Service Types Demonstrated

- **FastAPI Service** (`api_service.py`): Task CRUD, auth, caching, and event publishing.
- **Telegram Bot Service** (`bot_service.py`): NLP-based task creation and management.
- **AsyncIO Workers**:
    - `reminder_worker.py`: Due date monitoring.
    - `analytics_worker.py`: Productivity tracking.
- **Data Services**: Utilizes the project's standard `db_postgres_service` and `db_mongo_service`.

## 🚀 Quick Start

### Prerequisites

1. **Docker & Docker Compose** installed.
2. **Telegram Bot Token** (get from [@BotFather](https://t.me/botfather)).

### 1. Environment Setup

```bash
# Navigate to the use case directory
cd use_cases/task_management

# Copy and edit the environment file
cp .env.example .env && nano .env
```
You must provide your `BOT_TOKEN` in the `.env` file.

### 2. Build and Start Services

```bash
# Start the complete stack with monitoring
docker-compose --profile monitoring up -d --build

# Check service health
docker-compose ps
```

### 3. Verify Setup

```bash
# Test API and data services
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## 📱 Using the System

### REST API Usage

Access the interactive API documentation:
- **Task API**: `http://localhost:8000/docs`
- **PostgreSQL Data API**: `http://localhost:8001/docs`
- **MongoDB Data API**: `http://localhost:8002/docs`

### Telegram Bot Usage

Start a chat with your bot and use these commands:
- `/start`: Initialize bot and authenticate.
- `/task Buy groceries tomorrow high priority`: Create a task with natural language.
- `/mytasks`: List your tasks.
- `/done 123`: Mark task 123 as complete.

## 🔧 Development and Operations

For complete guidance on development, testing, monitoring, and deployment, refer to the canonical project documentation. These guides provide the required patterns and commands.

- **[Development Commands](../../docs/LINKS_REFERENCE.md#developer-guides)**: For local setup, running tests, and quality checks.
- **[Architecture Guide](../../docs/LINKS_REFERENCE.md#core-documentation)**: To understand the mandatory architectural patterns.
- **[Testing Standards](../../docs/LINKS_REFERENCE.md#ide-rules-and-patterns)**: For writing unit, integration, and E2E tests.
- **[Observability Rules](../../docs/LINKS_REFERENCE.md#ide-rules-and-patterns)**: For using logs, metrics, and traces.
- **[Troubleshooting Guide](../../docs/LINKS_REFERENCE.md#developer-guides)**: For resolving common issues.

## 📚 Learning Focus

- **Task Domain**: Personal productivity, natural language processing, smart reminders.
- **Bot Integration**: Telegram commands, file attachments, user sessions.
- **Background Processing**: Due date monitoring, analytics aggregation, event-driven workflows.

> **🚀 This use case is a complete reference implementation for production-ready microservices!**