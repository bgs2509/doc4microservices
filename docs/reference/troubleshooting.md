# Troubleshooting Guide

This guide covers common issues and solutions when working with the microservices architecture.

## Table of Contents
- [Development Environment Issues](#development-environment-issues)
- [Docker and Compose Issues](#docker-and-compose-issues)
- [Service Communication Issues](#service-communication-issues)
- [Database and Migration Issues](#database-and-migration-issues)
- [Event Loop and Async Issues](#event-loop-and-async-issues)
- [Observability and Monitoring Issues](#observability-and-monitoring-issues)
- [Performance Issues](#performance-issues)

## Development Environment Issues

### Python Version Conflicts
**Problem**: Services fail to start due to Python version mismatch
```
Error: Python 3.11 found, but 3.12+ required
```

**Solution**:
```bash
# Check current Python version
python --version

# Install Python 3.12+ using pyenv (recommended)
pyenv install 3.12.7
pyenv local 3.12.7

# Or update using system package manager
sudo apt update && sudo apt install python3.12
```

### UV Package Manager Issues
**Problem**: `uv` commands fail or dependencies not installing
```
Error: uv: command not found
```

**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell
source ~/.bashrc

# Verify installation
uv --version

# If dependencies fail to install
uv sync --refresh
```

### Environment Variables Missing
**Problem**: Services fail with configuration errors
```
Error: DATABASE_URL not found
```

**Solution**:
```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env

# Verify environment variables are loaded
docker-compose config
```

## Docker and Compose Issues

### Port Conflicts
**Problem**: Services fail to start due to port conflicts
```
Error: bind: address already in use
```

**Solution**:
```bash
# Check what's using the port
sudo netstat -tulpn | grep :5432

# Kill process using the port
sudo kill -9 <PID>

# Or change port in docker-compose.yml
# ports:
#   - "5433:5432"  # Use different host port
```

### Container Build Failures
**Problem**: Docker build fails with dependency errors
```
Error: Unable to locate package python3.12
```

**Solution**:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Dockerfile base image
# Ensure using: FROM python:3.12-slim
```

### Volume Mount Issues
**Problem**: Database data not persisting or permission errors
```
Error: permission denied
```

**Solution**:
```bash
# Fix permissions
sudo chown -R $USER:$USER ./data

# Reset volumes
docker-compose down -v
docker-compose up
```

## Service Communication Issues

### RabbitMQ Connection Failures
**Problem**: Services can't connect to RabbitMQ
```
Error: ConnectionError: [Errno 111] Connection refused
```

**Solution**:
```bash
# Check RabbitMQ is running
docker-compose ps rabbitmq

# Check RabbitMQ logs
docker-compose logs -f rabbitmq

# Restart RabbitMQ
docker-compose restart rabbitmq

# Access management UI
# http://localhost:15672 (admin/admin123)
```

### Redis Connection Issues
**Problem**: Services can't connect to Redis
```
Error: redis.exceptions.ConnectionError
```

**Solution**:
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs -f redis

# Restart Redis
docker-compose restart redis
```

### Inter-Service HTTP Communication
**Problem**: HTTP requests between services fail
```
Error: ConnectionError: Cannot connect to host api_service
```

**Solution**:
```bash
# Check services are in same network
docker network ls
docker network inspect try_microservices_default

# Use service names in URLs
# http://api_service:8000/api/v1/users
# http://localhost:8000/api/v1/users

# Check service health endpoints
curl http://localhost:8000/health
```

## Database and Migration Issues

### PostgreSQL Connection Failures
**Problem**: Cannot connect to PostgreSQL database
```
Error: could not connect to server: Connection refused
```

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs -f postgres

# Test connection
docker-compose exec postgres psql -U postgres -d microservices_db

# Reset database
docker-compose down
docker volume rm try_microservices_postgres_data
docker-compose up postgres
```

### Migration Failures
**Problem**: Alembic migrations fail
```
Error: Target database is not up to date
```

**Solution**:
```bash
# Check current migration status
uv run alembic current

# Run migrations
uv run alembic upgrade head

# If migrations conflict, reset
uv run alembic downgrade base
uv run alembic upgrade head

# Generate new migration
uv run alembic revision --autogenerate -m "description"
```

### SQLAlchemy Session Issues
**Problem**: Database sessions hanging or errors
```
Error: QueuePool limit of size 5 overflow 10 reached
```

**Solution**:
```python
# Check connection pool configuration
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@host/db?pool_size=20&max_overflow=30"

# Ensure proper session management
async with get_db_session() as session:
    # Use session
    pass  # Session automatically closed
```

## Event Loop and Async Issues

### Event Loop Conflicts
**Problem**: Multiple event loops causing conflicts
```
Error: RuntimeError: There is no current event loop
```

**Solution**:
```python
# DON'T run multiple event loop managers in same process
# app = FastAPI()  # Creates event loop
# asyncio.run(main())  # Creates another event loop

# DO use separate containers/processes
# FastAPI in one container
# Aiogram in another container
# AsyncIO workers in third container
```

### Blocking Code in Async Context
**Problem**: Synchronous code blocking event loop
```
Warning: Synchronous code in async context
```

**Solution**:
```python
# DON'T use blocking code
def blocking_operation():
    time.sleep(5)  # Blocks event loop

await blocking_operation()  # Will block everything

# DO use async alternatives
async def async_operation():
    await asyncio.sleep(5)  # Non-blocking

# Or run in thread pool
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    result = await loop.run_in_executor(executor, blocking_operation)
```

### Async Library Compatibility
**Problem**: Mixing sync and async libraries
```
Error: SyncError: You have tried to use a sync method
```

**Solution**:
```python
# DON'T use sync libraries in async code
import pika      # Sync library (deprecated)

# DO use async libraries
import asyncpg    # Async PostgreSQL
import aio_pika   # Async RabbitMQ
```

## Observability and Monitoring Issues

### Prometheus Metrics Not Appearing
**Problem**: Metrics not showing in Prometheus
```
Error: No targets found
```

**Solution**:
```bash
# Check Prometheus configuration
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Verify service metrics endpoints
curl http://localhost:8000/metrics

# Check Prometheus targets
# http://localhost:9090/targets

# Restart Prometheus
docker-compose restart prometheus
```

### Grafana Dashboard Issues
**Problem**: Grafana shows no data
```
Error: No data points
```

**Solution**:
```bash
# Check Grafana data source
# http://localhost:3000/datasources

# Verify Prometheus connection
# URL: http://prometheus:9090

# Import dashboard JSON
# Copy from infrastructure/observability/grafana/dashboards/

# Check time range in dashboard
```

### ELK Stack Issues
**Problem**: Logs not appearing in Kibana
```
Error: No indices found
```

**Solution**:
```bash
# Check Elasticsearch health
curl http://localhost:9200/_health

# Check Logstash pipeline
docker-compose logs -f logstash

# Create index pattern in Kibana
# http://localhost:5601
# Management > Index Patterns > Create
# Pattern: logstash-*
```

### Jaeger Tracing Issues
**Problem**: Traces not appearing in Jaeger
```
Error: No traces found
```

**Solution**:
```python
# Check OpenTelemetry configuration
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Ensure proper setup
tracer = trace.get_tracer(__name__)

# Add spans to your code
with tracer.start_as_current_span("operation_name"):
    # Your code here
    pass
```

## Performance Issues

### High Memory Usage
**Problem**: Services consuming too much memory
```
Error: OOMKilled
```

**Solution**:
```yaml
# Add memory limits to docker-compose.yml
services:
  api_service:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

```python
# Optimize database connections
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@host/db?pool_size=5&max_overflow=10"
```

### Slow Database Queries
**Problem**: Database operations are slow
```
Warning: Query took 5.2 seconds
```

**Solution**:
```sql
-- Add database indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

```python
# Use connection pooling
async def get_db_session():
    async with SessionLocal() as session:
        yield session
```

### High CPU Usage
**Problem**: Services using too much CPU
```
Error: CPU usage at 100%
```

**Solution**:
```python
# Add async delays to prevent busy loops
async def worker_loop():
    while True:
        await process_tasks()
        await asyncio.sleep(0.1)  # Prevent busy loop

# Use connection pooling for external services
async def make_request():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## Quick Diagnostic Commands

> **FULL COMMAND REFERENCE**: For complete development and troubleshooting commands, see [Development Commands](../guides/DEVELOPMENT_COMMANDS.md).

**Essential diagnostic commands:**
```bash
# Check services status and logs
docker-compose ps
docker-compose logs -f [service_name]

# Test connectivity (full commands in DEVELOPMENT_COMMANDS.md)
curl http://localhost:8000/health  # API service
curl http://localhost:8001/health  # PostgreSQL data service
curl http://localhost:8002/health  # MongoDB data service
```

## Getting Help

If you encounter issues not covered in this guide:

1. **Check logs**: Always start with service logs using `docker-compose logs -f <service>`
2. **Verify configuration**: Use `docker-compose config` to validate compose files
3. **Check connectivity**: Test service-to-service communication
4. **Review documentation**: Refer to [Main Entry Point](../LINKS_REFERENCE.md#core-documentation) and [Technical Specifications](../LINKS_REFERENCE.md#core-documentation)
5. **Check IDE rules**: Review relevant `../*/*.mdc` files (architecture/, services/, infrastructure/, observability/, quality/)

For more detailed debugging, enable debug logging in your services by setting `LOG_LEVEL=DEBUG` in your `.env` file.