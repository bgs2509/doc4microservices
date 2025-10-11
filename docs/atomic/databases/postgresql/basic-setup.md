# PostgreSQL Basic Setup

Foundational guide for PostgreSQL installation, configuration, and initial setup in microservices architecture.

## Prerequisites

```yaml
# Required versions
PostgreSQL: 15.x or 16.x
Python: 3.12+
Docker: 24.0+
```

## Docker-based PostgreSQL Setup

### Development Configuration

```yaml
# docker-compose.yml (PostgreSQL service)
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: ${PROJECT_NAME:-myapp}-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-microservices_db}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-microservices_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - backend

volumes:
  postgres_data:
    driver: local

networks:
  backend:
    driver: bridge
```

### Production Configuration

```yaml
# docker-compose.prod.yml (PostgreSQL optimizations)
services:
  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      # Performance tuning
      POSTGRES_SHARED_BUFFERS: 256MB
      POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
      POSTGRES_MAINTENANCE_WORK_MEM: 64MB
      POSTGRES_CHECKPOINT_COMPLETION_TARGET: 0.9
      POSTGRES_WAL_BUFFERS: 16MB
      POSTGRES_DEFAULT_STATISTICS_TARGET: 100
      POSTGRES_RANDOM_PAGE_COST: 1.1
      POSTGRES_EFFECTIVE_IO_CONCURRENCY: 200
      POSTGRES_WORK_MEM: 4MB
      POSTGRES_MIN_WAL_SIZE: 1GB
      POSTGRES_MAX_WAL_SIZE: 4GB
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf:ro
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Database Initialization Script

```bash
#!/bin/bash
# scripts/init-db.sh

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable required extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    CREATE EXTENSION IF NOT EXISTS "btree_gist";

    -- Create application user (if different from POSTGRES_USER)
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'app_user') THEN
            CREATE USER app_user WITH PASSWORD '${APP_USER_PASSWORD:-changeme}';
        END IF;
    END
    \$\$;

    -- Grant privileges
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO app_user;
    GRANT USAGE ON SCHEMA public TO app_user;
    GRANT CREATE ON SCHEMA public TO app_user;

    -- Set default privileges for future tables
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;

    -- Create schemas for microservices
    CREATE SCHEMA IF NOT EXISTS users AUTHORIZATION app_user;
    CREATE SCHEMA IF NOT EXISTS orders AUTHORIZATION app_user;
    CREATE SCHEMA IF NOT EXISTS products AUTHORIZATION app_user;

    GRANT ALL ON SCHEMA users TO app_user;
    GRANT ALL ON SCHEMA orders TO app_user;
    GRANT ALL ON SCHEMA products TO app_user;
EOSQL

echo "PostgreSQL initialization completed successfully"
```

## Environment Configuration

```bash
# .env (PostgreSQL configuration)

# PostgreSQL connection
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=microservices_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme_in_production

# Application user
APP_USER_PASSWORD=changeme_in_production

# Connection pool settings
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=10
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=3600

# Database URL (for SQLAlchemy)
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```

## Python Dependencies

```txt
# requirements.txt (PostgreSQL dependencies)

# Async PostgreSQL driver
asyncpg==0.29.0

# SQLAlchemy ORM
sqlalchemy[asyncio]==2.0.23
alembic==1.13.1

# Connection pooling
sqlalchemy-utils==0.41.1

# Type stubs
types-asyncpg==0.27.0
```

## Basic Connection Configuration

```python
# src/core/database.py

from typing import AsyncGenerator
import asyncpg
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
import os

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


class DatabaseConfig:
    """PostgreSQL configuration"""

    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.database = os.getenv("POSTGRES_DB", "microservices_db")
        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "")

        # Pool settings
        self.pool_size = int(os.getenv("POSTGRES_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("POSTGRES_MAX_OVERFLOW", "10"))
        self.pool_timeout = int(os.getenv("POSTGRES_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("POSTGRES_POOL_RECYCLE", "3600"))

    @property
    def url(self) -> str:
        """Build database URL"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


# Global engine and session factory
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def create_engine(config: DatabaseConfig) -> AsyncEngine:
    """Create async SQLAlchemy engine"""
    return create_async_engine(
        config.url,
        echo=False,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_recycle=config.pool_recycle,
        pool_pre_ping=True,
    )


def init_database(config: DatabaseConfig) -> None:
    """Initialize database engine and session factory"""
    global _engine, _session_factory

    _engine = create_engine(config)
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_database() -> None:
    """Close database connections"""
    global _engine
    if _engine:
        await _engine.dispose()
```

## Health Check Endpoint

```python
# src/api/health.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.database import get_session

router = APIRouter(tags=["health"])


@router.get("/health/db")
async def database_health(
    session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    """Check PostgreSQL database health"""
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar_one()

        # Check current connections
        conn_result = await session.execute(text("""
            SELECT count(*)
            FROM pg_stat_activity
            WHERE datname = current_database()
        """))
        active_connections = conn_result.scalar_one()

        return {
            "status": "healthy",
            "database": "postgresql",
            "active_connections": str(active_connections),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database unhealthy: {str(e)}"
        )
```

## Application Lifecycle Integration

```python
# src/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.core.database import init_database, close_database, DatabaseConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    config = DatabaseConfig()
    init_database(config)
    print("✓ PostgreSQL connection initialized")

    yield

    # Shutdown
    await close_database()
    print("✓ PostgreSQL connection closed")


app = FastAPI(lifespan=lifespan)
```

## Verification Commands

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs -f postgres

# Connect to PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d microservices_db

# Check database size
docker-compose exec postgres psql -U postgres -d microservices_db -c "\l+"

# Check active connections
docker-compose exec postgres psql -U postgres -d microservices_db -c "SELECT * FROM pg_stat_activity;"

# Run migrations (Alembic)
alembic upgrade head

# Test database connection from Python
python -c "import asyncio; from src.core.database import *; config = DatabaseConfig(); asyncio.run(test_connection())"
```

## Security Best Practices

1. **Never commit credentials**
   ```bash
   # .gitignore
   .env
   .env.local
   .env.production
   ```

2. **Use secrets management in production**
   ```python
   # Use AWS Secrets Manager, HashiCorp Vault, etc.
   import boto3

   def get_db_password():
       client = boto3.client('secretsmanager')
       secret = client.get_secret_value(SecretId='prod/postgres/password')
       return secret['SecretString']
   ```

3. **Restrict network access**
   ```yaml
   # docker-compose.yml - Remove exposed ports in production
   services:
     postgres:
       # ports:  # <-- Comment out for production
       #   - "5432:5432"
       networks:
         - backend  # Internal network only
   ```

4. **Enable SSL/TLS**
   ```python
   # For production connections
   DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}?ssl=require"
   ```

## Common Issues and Solutions

### Issue: Connection Refused

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Issue: Too Many Connections

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Increase max_connections (postgresql.conf)
max_connections = 200
```

### Issue: Slow Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Related Documentation

- [SQLAlchemy Integration](sqlalchemy-integration.md) - ORM patterns and best practices
- [Complex Relationship Modeling](../postgresql-advanced/complex-relationship-modeling.md) - Advanced entity relationships
- [Performance Optimization](../postgresql-advanced/performance-optimization.md) - Query optimization and indexing
- [Production Migrations](../postgresql-advanced/production-migrations.md) - Safe migration strategies
- [Database Service Setup](../../services/data-services/postgres-service-setup.md) - HTTP data service wrapper
