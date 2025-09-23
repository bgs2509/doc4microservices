# AI-Generated Project Structure Example

> **📋 Documentation Example** - Shows the standardized structure that AI agents generate for new microservices projects.

## 🎯 Purpose

This document demonstrates the **standardized project structure** that AI agents create when generating new microservices applications. This is **NOT a runnable project** - it's documentation showing the organizational patterns.

## 🏗️ Generated Project Structure

When AI creates a new microservices application, it generates this structure in the **user's new repository**:

> **📋 COMPLETE PROJECT STRUCTURE**: See [../docs/reference/PROJECT_STRUCTURE.md](../docs/reference/PROJECT_STRUCTURE.md) for the authoritative, detailed project structure guide.

**AI Generation Summary:** AI generates the complete standardized structure including:
- Root-level configuration files (`pyproject.toml`, `Makefile`, `.gitignore`, `.env.example`)
- `src/` folder with all application code
- Service-specific Dockerfiles and configuration
- Shared components and centralized configuration
- Comprehensive test suites with proper organization

## 📋 Key Structure Principles

### 1. **Root-Level Configuration**
- **docker-compose.yml**: Complete infrastructure and service orchestration
- **.env.example**: Environment configuration template with all variables
- **pyproject.toml**: Python dependencies and project metadata
- **Makefile**: Development automation (build, test, deploy commands)

### 2. **Source Code Organization (`src/`)**
- **All source code** lives under `src/` folder
- **Clear separation** between services, shared code, config, and tests
- **Service-specific folders** contain everything needed for that service

### 3. **Service-Specific Dockerfiles**
- Each service has its **own Dockerfile** in its service folder
- **Context is root** (`.`) but dockerfile path is `./src/services/[service]/Dockerfile`
- **Shared modules** are copied to all services that need them

### 4. **Shared Components**
- **`src/shared/`**: Common DTOs, events, utilities used across services
- **`src/config/`**: Centralized settings and logging configuration
- **No code duplication** across services

### 5. **Comprehensive Testing**
- **Unit tests**: Per-service testing with mocks
- **Integration tests**: Real service communication via testcontainers
- **Test configuration**: Centralized fixtures and setup

## 🐳 Docker Compose Integration

The generated `docker-compose.yml` in the root demonstrates the new build approach:

```yaml
# Example of generated docker-compose.yml structure
version: '3.8'

services:
  # Business Services (using new src/ structure)
  api_service:
    build:
      context: "."                                      # Root context
      dockerfile: "./src/services/api_service/Dockerfile"  # Service-specific Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DB_POSTGRES_SERVICE_URL=http://db_postgres_service:8000
      - DB_MONGO_SERVICE_URL=http://db_mongo_service:8000
    depends_on:
      - db_postgres_service
      - db_mongo_service

  bot_service:
    build:
      context: "."
      dockerfile: "./src/services/bot_service/Dockerfile"
    environment:
      - API_SERVICE_URL=http://api_service:8000
    depends_on:
      - api_service

  # Data Services (following same pattern)
  db_postgres_service:
    build:
      context: "."
      dockerfile: "./src/services/db_postgres_service/Dockerfile"
    ports:
      - "8001:8000"
    depends_on:
      - postgres

  # Infrastructure Services
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: project_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📁 Example Service Dockerfile

Each service gets a Dockerfile that follows this pattern:

```dockerfile
# Example: src/services/api_service/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements
COPY src/services/api_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules first (for better caching)
COPY src/shared/ ./shared/
COPY src/config/ ./config/

# Copy service-specific code
COPY src/services/api_service/ ./

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the service
CMD ["python", "main.py"]
```

## 🎯 Example Business Requirements → Generated Structure

### Input: Business Requirements
```
"Create a task management application with:
- REST API for task CRUD operations
- Telegram bot for quick task creation
- Background workers for email reminders
- PostgreSQL for tasks, MongoDB for analytics"
```

### Output: Generated Project
The AI would create a new repository with:

1. **Complete docker-compose.yml** with all infrastructure + services
2. **API Service** (`src/services/api_service/`) - FastAPI with task endpoints
3. **Bot Service** (`src/services/bot_service/`) - Telegram bot with task commands
4. **Reminder Worker** (`src/services/reminder_worker/`) - Email notification worker
5. **Data Services** - PostgreSQL and MongoDB HTTP APIs
6. **Shared DTOs** (`src/shared/dtos.py`) - Task, User, Project models
7. **Configuration** (`src/config/`) - Settings and logging setup
8. **Tests** (`src/tests/`) - Unit and integration test suites

## 🔄 AI Generation Workflow

1. **User creates repository**: `mkdir my_task_app && cd my_task_app && git init`
2. **AI reads this documentation** to understand patterns and constraints
3. **AI generates complete structure** following this exact organization
4. **User deploys**: `cp .env.example .env && docker-compose up -d`

## ✅ Benefits of This Structure

### **For Development**
- **Clear organization**: Easy to find and modify service-specific code
- **Shared components**: No code duplication across services
- **Independent services**: Each service can be developed and deployed separately

### **For Docker**
- **Efficient builds**: Shared modules cached separately from service code
- **Service isolation**: Each service has its own container and dependencies
- **Easy scaling**: Services can be scaled independently

### **For AI Generation**
- **Standardized**: Same structure for all generated projects
- **Predictable**: AI knows exactly where to place each type of code
- **Maintainable**: Clear patterns for AI to follow and extend

## 🚫 What This Document Is NOT

- ❌ **Not a runnable project** - This is documentation only
- ❌ **Not in this repository** - Generated projects go in user's own repos
- ❌ **Not a template to copy** - AI generates from scratch using patterns
- ❌ **Not the old use_cases approach** - This is the new AI-first workflow

## 🔗 Related Documentation

- **[README.md](../README.md)**: Complete project overview and AI workflow
- **[USE_CASE_IMPLEMENTATION_GUIDE.md](../docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md)**: Detailed generation guide
- **[ai_agents/](../ai_agents/)**: AI framework for automated generation
- **[examples/](../examples/)**: Educational patterns and service templates

---

**🤖 This structure is generated by AI agents using the doc4microservices framework patterns.**