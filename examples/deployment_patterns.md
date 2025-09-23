# Deployment Patterns Example

> **🚀 PURPOSE**: Complete guide for deployment strategies, database migrations, service versioning, and production deployment patterns

This example demonstrates production-ready deployment patterns for the Improved Hybrid Approach microservices architecture, including zero-downtime deployments, database migrations, and service versioning strategies.

## 📋 Table of Contents

- [Deployment Strategies](#deployment-strategies)
- [Database Migration Patterns](#database-migration-patterns)
- [Service Versioning](#service-versioning)
- [Zero-Downtime Deployment](#zero-downtime-deployment)
- [Environment Management](#environment-management)
- [Health Check Strategies](#health-check-strategies)
- [Rollback Procedures](#rollback-procedures)
- [Production Deployment](#production-deployment)

## 🚀 Deployment Strategies

### Blue-Green Deployment

```yaml
# deployment/blue-green/docker-compose.blue.yml
version: '3.8'

services:
  # Blue environment (current production)
  api_service_blue:
    image: microservices/api_service:v1.2.3
    container_name: api_service_blue
    environment:
      - ENVIRONMENT=production
      - VERSION=v1.2.3
      - DATABASE_URL=postgresql://user:pass@postgres:5432/prod_db
      - REDIS_URL=redis://redis:6379/0
    networks:
      - production_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api-blue.rule=Host(`api.example.com`)"
      - "traefik.http.routers.api-blue.priority=100"
      - "traefik.http.services.api-blue.loadbalancer.server.port=8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  bot_service_blue:
    image: microservices/bot_service:v1.2.3
    container_name: bot_service_blue
    environment:
      - ENVIRONMENT=production
      - VERSION=v1.2.3
      - BOT_TOKEN=${BOT_TOKEN}
      - API_URL=http://api_service_blue:8000
    networks:
      - production_network
    depends_on:
      - api_service_blue
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 60s
      timeout: 15s
      retries: 3

# deployment/blue-green/docker-compose.green.yml
version: '3.8'

services:
  # Green environment (new version)
  api_service_green:
    image: microservices/api_service:v1.3.0
    container_name: api_service_green
    environment:
      - ENVIRONMENT=staging
      - VERSION=v1.3.0
      - DATABASE_URL=postgresql://user:pass@postgres:5432/prod_db
      - REDIS_URL=redis://redis:6379/1  # Different Redis DB
    networks:
      - production_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api-green.rule=Host(`api-staging.example.com`)"
      - "traefik.http.services.api-green.loadbalancer.server.port=8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 2
```

### Rolling Deployment

```yaml
# deployment/rolling/docker-compose.yml
version: '3.8'

services:
  api_service:
    image: microservices/api_service:${VERSION:-latest}
    deploy:
      replicas: 4
      update_config:
        parallelism: 1          # Update 1 container at a time
        delay: 30s              # Wait 30s between updates
        failure_action: rollback
        monitor: 60s            # Monitor for 60s after update
        max_failure_ratio: 0.3  # Allow 30% failure rate
      rollback_config:
        parallelism: 2
        delay: 10s
        failure_action: pause
        monitor: 60s
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
    environment:
      - ENVIRONMENT=production
      - VERSION=${VERSION}
    networks:
      - production_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api_service
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
```

### Canary Deployment

```yaml
# deployment/canary/docker-compose.yml
version: '3.8'

services:
  # Stable version (90% traffic)
  api_service_stable:
    image: microservices/api_service:v1.2.3
    deploy:
      replicas: 9
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.api-stable.rule=Host(`api.example.com`)"
        - "traefik.http.services.api-stable.loadbalancer.server.port=8000"
        - "traefik.http.services.api-stable.loadbalancer.sticky.cookie=true"
    environment:
      - ENVIRONMENT=production
      - VERSION=v1.2.3
      - CANARY=false
    networks:
      - production_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Canary version (10% traffic)
  api_service_canary:
    image: microservices/api_service:v1.3.0
    deploy:
      replicas: 1
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.api-canary.rule=Host(`api.example.com`) && Header(`X-Canary`, `true`)"
        - "traefik.http.routers.api-canary.priority=200"
        - "traefik.http.services.api-canary.loadbalancer.server.port=8000"
    environment:
      - ENVIRONMENT=production
      - VERSION=v1.3.0
      - CANARY=true
    networks:
      - production_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s  # More frequent health checks for canary
      timeout: 5s
      retries: 2

  # Traffic splitter
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--metrics.prometheus=true"
    ports:
      - "80:80"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
    networks:
      - production_network
```

## 🗄️ Database Migration Patterns

### Forward-Compatible Migrations

```python
# migrations/postgresql/migration_v1_3_0.py
"""
Migration v1.3.0: Add user preferences table
Forward-compatible migration strategy for zero-downtime deployment
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json

# Migration metadata
revision = 'v1_3_0'
down_revision = 'v1_2_3'
branch_labels = None
depends_on = None

def upgrade():
    """Forward-compatible upgrade"""

    # Step 1: Add new table (safe - doesn't affect existing code)
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('preferences', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.Index('idx_user_preferences_user_id', 'user_id')
    )

    # Step 2: Add new column with default value (safe - backward compatible)
    op.add_column(
        'users',
        sa.Column('notification_settings', postgresql.JSONB(),
                 nullable=True,
                 server_default='{}')
    )

    # Step 3: Create index concurrently (safe for PostgreSQL)
    op.execute(
        "CREATE INDEX CONCURRENTLY idx_users_notification_settings "
        "ON users USING GIN (notification_settings)"
    )

    # Step 4: Add new enum value (requires careful handling)
    # First, create new enum type
    new_status_enum = postgresql.ENUM(
        'active', 'inactive', 'pending', 'suspended', 'archived',  # new value
        name='user_status_new'
    )
    new_status_enum.create(op.get_bind())

    # Step 5: Migrate data in batches to avoid locks
    migrate_user_data_in_batches()

def migrate_user_data_in_batches():
    """Migrate existing user data in small batches"""
    connection = op.get_bind()

    # Get total count
    result = connection.execute("SELECT COUNT(*) FROM users WHERE notification_settings IS NULL")
    total_users = result.scalar()

    batch_size = 1000
    processed = 0

    while processed < total_users:
        # Update in small batches to avoid long-running transactions
        connection.execute(f"""
            UPDATE users
            SET notification_settings = '{{"email": true, "sms": false, "push": true}}'::jsonb
            WHERE id IN (
                SELECT id FROM users
                WHERE notification_settings IS NULL
                LIMIT {batch_size}
            )
        """)

        processed += batch_size

        # Log progress
        print(f"Migrated {min(processed, total_users)}/{total_users} users")

        # Small delay to reduce database load
        if processed < total_users:
            import time
            time.sleep(0.1)

def downgrade():
    """Safe downgrade (removes only new features)"""

    # Drop new index
    op.drop_index('idx_users_notification_settings', 'users')

    # Drop new column (data loss - should be confirmed)
    op.drop_column('users', 'notification_settings')

    # Drop new table
    op.drop_table('user_preferences')

    # Drop new enum type
    op.execute("DROP TYPE user_status_new")

# Migration execution script
class MigrationExecutor:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = sa.create_engine(database_url)

    async def execute_migration(self, migration_version: str):
        """Execute migration with safety checks"""

        # Pre-migration checks
        await self._pre_migration_checks()

        # Create database backup
        backup_name = await self._create_backup(migration_version)

        try:
            # Execute migration
            await self._run_migration(migration_version)

            # Post-migration validation
            await self._post_migration_validation()

            # Cleanup old backup (keep last 5)
            await self._cleanup_old_backups()

            print(f"✅ Migration {migration_version} completed successfully")

        except Exception as e:
            print(f"❌ Migration failed: {e}")

            # Automatic rollback
            await self._rollback_migration(backup_name)
            raise

    async def _pre_migration_checks(self):
        """Validate system state before migration"""

        # Check database connectivity
        with self.engine.connect() as conn:
            conn.execute("SELECT 1")

        # Check disk space
        disk_usage = await self._check_disk_space()
        if disk_usage > 90:
            raise Exception("Insufficient disk space for migration")

        # Check active connections
        active_connections = await self._check_active_connections()
        if active_connections > 100:
            print("⚠️ High number of active connections detected")

        # Validate data integrity
        await self._validate_data_integrity()

    async def _create_backup(self, version: str) -> str:
        """Create database backup before migration"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{version}_{timestamp}.sql"

        # For PostgreSQL
        backup_command = [
            "pg_dump",
            "--host", "localhost",
            "--port", "5432",
            "--username", "postgres",
            "--format", "custom",
            "--compress", "9",
            "--file", f"/backups/{backup_name}",
            "microservices_db"
        ]

        process = await asyncio.create_subprocess_exec(
            *backup_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Backup failed: {stderr.decode()}")

        print(f"✅ Database backup created: {backup_name}")
        return backup_name
```

### MongoDB Migration Patterns

```python
# migrations/mongodb/migration_v1_3_0.py
"""
MongoDB migration for analytics schema changes
"""

from pymongo import MongoClient
from datetime import datetime
import asyncio

class MongoMigration:
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client.analytics_db

    async def upgrade_v1_3_0(self):
        """Add new analytics collections and update existing documents"""

        # Step 1: Create new collections with validation
        await self._create_user_behavior_collection()

        # Step 2: Add new fields to existing documents
        await self._add_new_fields_to_events()

        # Step 3: Create new indexes
        await self._create_new_indexes()

        # Step 4: Migrate existing data
        await self._migrate_event_data()

    async def _create_user_behavior_collection(self):
        """Create new collection with schema validation"""

        # Define schema validation
        schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "action", "timestamp"],
                "properties": {
                    "user_id": {"bsonType": "int"},
                    "action": {"bsonType": "string"},
                    "timestamp": {"bsonType": "date"},
                    "metadata": {"bsonType": "object"},
                    "session_id": {"bsonType": "string"},
                    "device_info": {
                        "bsonType": "object",
                        "properties": {
                            "platform": {"bsonType": "string"},
                            "browser": {"bsonType": "string"},
                            "ip_address": {"bsonType": "string"}
                        }
                    }
                }
            }
        }

        # Create collection with validation
        self.db.create_collection(
            "user_behavior",
            validator=schema,
            validationLevel="strict",
            validationAction="error"
        )

        print("✅ Created user_behavior collection with schema validation")

    async def _add_new_fields_to_events(self):
        """Add new fields to existing event documents"""

        # Add new fields with default values
        result = self.db.events.update_many(
            {"version": {"$exists": False}},  # Only update documents without version
            {
                "$set": {
                    "version": "1.3.0",
                    "processing_status": "pending",
                    "enriched_at": None
                }
            }
        )

        print(f"✅ Updated {result.modified_count} event documents")

    async def _create_new_indexes(self):
        """Create new indexes for better performance"""

        indexes = [
            # User behavior indexes
            ("user_behavior", [("user_id", 1), ("timestamp", -1)]),
            ("user_behavior", [("action", 1), ("timestamp", -1)]),
            ("user_behavior", [("session_id", 1)]),

            # Events indexes
            ("events", [("processing_status", 1), ("created_at", 1)]),
            ("events", [("version", 1)]),

            # Compound indexes for analytics queries
            ("events", [("user_id", 1), ("event_type", 1), ("timestamp", -1)]),
        ]

        for collection_name, index_spec in indexes:
            collection = self.db[collection_name]
            collection.create_index(index_spec, background=True)
            print(f"✅ Created index on {collection_name}: {index_spec}")

    async def _migrate_event_data(self):
        """Migrate existing event data to new format"""

        # Process in batches to avoid memory issues
        batch_size = 1000
        total_processed = 0

        cursor = self.db.events.find({"migrated_v1_3_0": {"$ne": True}})

        batch = []
        for document in cursor:
            # Transform document to new format
            transformed = self._transform_event_document(document)
            batch.append(transformed)

            if len(batch) >= batch_size:
                await self._process_batch(batch)
                total_processed += len(batch)
                batch = []

                print(f"Processed {total_processed} documents...")

        # Process remaining documents
        if batch:
            await self._process_batch(batch)
            total_processed += len(batch)

        print(f"✅ Migration completed. Processed {total_processed} documents")

    def _transform_event_document(self, document):
        """Transform event document to new format"""

        # Extract device info from user_agent if available
        device_info = {}
        if "user_agent" in document:
            device_info = self._parse_user_agent(document["user_agent"])

        # Create new user behavior document
        return {
            "_id": document["_id"],
            "user_id": document["user_id"],
            "action": document["event_type"],
            "timestamp": document["timestamp"],
            "metadata": document.get("metadata", {}),
            "session_id": document.get("session_id"),
            "device_info": device_info,
            "original_event_id": document["_id"],
            "migrated_v1_3_0": True
        }

    async def _process_batch(self, batch):
        """Process a batch of transformed documents"""

        if not batch:
            return

        # Insert into new collection
        self.db.user_behavior.insert_many(batch, ordered=False)

        # Mark original documents as migrated
        document_ids = [doc["_id"] for doc in batch]
        self.db.events.update_many(
            {"_id": {"$in": document_ids}},
            {"$set": {"migrated_v1_3_0": True}}
        )
```

## 🏷️ Service Versioning

### Semantic Versioning Strategy

```yaml
# .github/workflows/version-and-deploy.yml
name: Version and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: microservices

jobs:
  version:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
      should_deploy: ${{ steps.version.outputs.should_deploy }}

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Full history for conventional commits

    - name: Calculate Version
      id: version
      run: |
        # Install conventional changelog tools
        npm install -g conventional-changelog-cli conventional-recommended-bump

        # Determine version bump type
        BUMP=$(conventional-recommended-bump -p angular)

        # Get current version
        CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")

        # Calculate new version
        if [ "$BUMP" = "major" ]; then
          NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print ($1+1)".0.0"}')
        elif [ "$BUMP" = "minor" ]; then
          NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."($2+1)".0"}')
        elif [ "$BUMP" = "patch" ]; then
          NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2"."($3+1)}')
        else
          NEW_VERSION="$CURRENT_VERSION-$(git rev-parse --short HEAD)"
        fi

        echo "version=$NEW_VERSION" >> $GITHUB_OUTPUT
        echo "should_deploy=$([[ '${{ github.ref }}' == 'refs/heads/main' ]] && echo 'true' || echo 'false')" >> $GITHUB_OUTPUT

        echo "Current version: $CURRENT_VERSION"
        echo "New version: $NEW_VERSION"
        echo "Bump type: $BUMP"

  build:
    needs: version
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api_service, bot_service, worker_service, db_postgres_service, db_mongo_service]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: ./services/${{ matrix.service }}
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ github.repository }}/${{ matrix.service }}:${{ needs.version.outputs.version }}
          ${{ env.REGISTRY }}/${{ github.repository }}/${{ matrix.service }}:latest
        labels: |
          org.opencontainers.image.source=${{ github.repository }}
          org.opencontainers.image.version=${{ needs.version.outputs.version }}
          org.opencontainers.image.revision=${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    if: needs.version.outputs.should_deploy == 'true'
    needs: [version, build]
    runs-on: ubuntu-latest
    environment: production

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Production
      env:
        VERSION: ${{ needs.version.outputs.version }}
      run: |
        # Update deployment files with new version
        sed -i "s/image: .*/image: ${{ env.REGISTRY }}/${{ github.repository }}\/api_service:$VERSION/" deployment/production/docker-compose.yml

        # Deploy using your preferred method (Docker Compose, Kubernetes, etc.)
        ./scripts/deploy-production.sh $VERSION

    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ needs.version.outputs.version }}
        release_name: Release ${{ needs.version.outputs.version }}
        body: |
          ## Changes in this Release
          $(conventional-changelog -p angular -r 2 | tail -n +2)
        draft: false
        prerelease: false
```

### API Versioning Strategy

```python
# services/api_service/versioning.py
"""
API versioning strategy for backward compatibility
"""

from fastapi import FastAPI, Request, Header
from typing import Optional
import semver

class APIVersioning:
    def __init__(self, app: FastAPI):
        self.app = app
        self.supported_versions = ["1.0", "1.1", "1.2", "1.3"]
        self.default_version = "1.3"
        self.deprecated_versions = ["1.0"]

    def get_version_from_request(self, request: Request,
                               accept_version: Optional[str] = Header(None)) -> str:
        """Extract API version from request"""

        # Priority order:
        # 1. Accept-Version header
        # 2. URL path prefix (/api/v1.2/...)
        # 3. Query parameter (?version=1.2)
        # 4. Default version

        version = None

        # Check header
        if accept_version:
            version = accept_version

        # Check URL path
        elif request.url.path.startswith("/api/v"):
            path_parts = request.url.path.split("/")
            if len(path_parts) > 2 and path_parts[2].startswith("v"):
                version = path_parts[2][1:]  # Remove 'v' prefix

        # Check query parameter
        elif "version" in request.query_params:
            version = request.query_params["version"]

        # Use default if no version specified
        if not version:
            version = self.default_version

        # Validate version
        if version not in self.supported_versions:
            raise ValueError(f"Unsupported API version: {version}")

        return version

    def is_deprecated(self, version: str) -> bool:
        """Check if version is deprecated"""
        return version in self.deprecated_versions

    def get_compatible_version(self, requested_version: str) -> str:
        """Find compatible version for requested version"""

        # If exact version exists, use it
        if requested_version in self.supported_versions:
            return requested_version

        # Find the highest compatible version
        compatible_versions = [
            v for v in self.supported_versions
            if semver.compare(v, requested_version) <= 0
        ]

        if compatible_versions:
            return max(compatible_versions, key=lambda v: semver.VersionInfo.parse(v))

        # No compatible version found, use default
        return self.default_version

# Version-specific response transformation
class ResponseTransformer:
    @staticmethod
    def transform_user_response(user_data: dict, version: str) -> dict:
        """Transform user response based on API version"""

        if version == "1.0":
            # v1.0 format (legacy)
            return {
                "id": user_data["id"],
                "name": user_data["username"],  # Changed field name
                "email": user_data["email"],
                "active": user_data["is_active"]  # Changed field name
            }

        elif version == "1.1":
            # v1.1 format (added created_at)
            return {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "is_active": user_data["is_active"],
                "created_at": user_data["created_at"].isoformat()
            }

        elif version in ["1.2", "1.3"]:
            # v1.2+ format (full format)
            response = {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "is_active": user_data["is_active"],
                "created_at": user_data["created_at"].isoformat(),
                "updated_at": user_data["updated_at"].isoformat(),
                "profile": {
                    "first_name": user_data.get("first_name"),
                    "last_name": user_data.get("last_name"),
                    "avatar_url": user_data.get("avatar_url")
                }
            }

            # v1.3 adds preferences
            if version == "1.3":
                response["preferences"] = user_data.get("preferences", {})

            return response

        # Unknown version, return full format
        return user_data

# Versioned endpoint decorator
def versioned_endpoint(min_version: str = "1.0", max_version: str = None):
    """Decorator for version-specific endpoints"""

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            versioning = APIVersioning(None)

            try:
                version = versioning.get_version_from_request(request)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

            # Check version compatibility
            if semver.compare(version, min_version) < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"API version {version} is not supported. Minimum version: {min_version}"
                )

            if max_version and semver.compare(version, max_version) > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"API version {version} is not supported. Maximum version: {max_version}"
                )

            # Add deprecation warning
            if versioning.is_deprecated(version):
                response = await func(request, *args, **kwargs)
                response.headers["Warning"] = f"299 - API version {version} is deprecated"
                return response

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator

# Usage example
@app.get("/api/v{version}/users/{user_id}")
@versioned_endpoint(min_version="1.0")
async def get_user(
    user_id: int,
    request: Request,
    version: str = Path(..., description="API version")
):
    """Get user by ID with version-specific response format"""

    # Get user data from service
    user_data = await user_service.get_user(user_id)

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Transform response based on version
    response_data = ResponseTransformer.transform_user_response(user_data, version)

    return response_data
```

## ⚡ Zero-Downtime Deployment

### Health Check Strategy

```python
# services/shared/health_checks.py
"""
Comprehensive health check system for zero-downtime deployments
"""

from fastapi import FastAPI, Response, status
from typing import Dict, List, Optional
import asyncio
import httpx
import psycopg
import pymongo
import redis
import time
from datetime import datetime, timedelta

class HealthChecker:
    def __init__(self):
        self.checks = {}
        self.startup_time = datetime.utcnow()
        self.ready = False
        self.shutdown_requested = False

    def add_check(self, name: str, check_func, critical: bool = True):
        """Add a health check"""
        self.checks[name] = {
            "func": check_func,
            "critical": critical,
            "last_success": None,
            "last_error": None,
            "consecutive_failures": 0
        }

    async def run_checks(self) -> Dict:
        """Run all health checks"""
        results = {}
        overall_status = "healthy"

        for name, check_config in self.checks.items():
            try:
                start_time = time.time()
                await check_config["func"]()
                duration = (time.time() - start_time) * 1000  # ms

                results[name] = {
                    "status": "healthy",
                    "duration_ms": round(duration, 2),
                    "last_success": datetime.utcnow().isoformat(),
                    "consecutive_failures": 0
                }

                # Update check state
                check_config["last_success"] = datetime.utcnow()
                check_config["last_error"] = None
                check_config["consecutive_failures"] = 0

            except Exception as e:
                check_config["consecutive_failures"] += 1
                check_config["last_error"] = str(e)

                results[name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "consecutive_failures": check_config["consecutive_failures"],
                    "last_error": datetime.utcnow().isoformat()
                }

                # Mark overall status as unhealthy if critical check fails
                if check_config["critical"]:
                    overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
            "ready": self.ready and not self.shutdown_requested,
            "checks": results
        }

class ServiceHealthChecks:
    def __init__(self, settings):
        self.settings = settings
        self.health_checker = HealthChecker()
        self._setup_checks()

    def _setup_checks(self):
        """Setup all health checks"""

        # Database connectivity
        self.health_checker.add_check(
            "postgres",
            self._check_postgres,
            critical=True
        )

        self.health_checker.add_check(
            "mongodb",
            self._check_mongodb,
            critical=True
        )

        # Cache connectivity
        self.health_checker.add_check(
            "redis",
            self._check_redis,
            critical=True
        )

        # Message broker
        self.health_checker.add_check(
            "rabbitmq",
            self._check_rabbitmq,
            critical=True
        )

        # External dependencies
        self.health_checker.add_check(
            "data_services",
            self._check_data_services,
            critical=True
        )

        # Internal checks
        self.health_checker.add_check(
            "memory_usage",
            self._check_memory_usage,
            critical=False
        )

        self.health_checker.add_check(
            "disk_space",
            self._check_disk_space,
            critical=False
        )

    async def _check_postgres(self):
        """Check PostgreSQL connectivity"""
        async with psycopg.AsyncConnection.connect(
            self.settings.DATABASE_URL,
            connect_timeout=5
        ) as conn:
            await conn.execute("SELECT 1")

    async def _check_mongodb(self):
        """Check MongoDB connectivity"""
        client = pymongo.AsyncMongoClient(
            self.settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        try:
            await client.admin.command('ping')
        finally:
            client.close()

    async def _check_redis(self):
        """Check Redis connectivity"""
        redis_client = redis.from_url(
            self.settings.REDIS_URL,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        try:
            await redis_client.ping()
        finally:
            await redis_client.close()

    async def _check_rabbitmq(self):
        """Check RabbitMQ connectivity"""
        # Implementation depends on your RabbitMQ client
        # This is a simplified version
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{self.settings.RABBITMQ_MANAGEMENT_URL}/api/healthchecks/node",
                auth=(self.settings.RABBITMQ_USER, self.settings.RABBITMQ_PASSWORD)
            )
            response.raise_for_status()

    async def _check_data_services(self):
        """Check data services availability"""
        services = [
            "http://db_postgres_service:8000/health",
            "http://db_mongo_service:8000/health"
        ]

        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_url in services:
                response = await client.get(service_url)
                response.raise_for_status()

    async def _check_memory_usage(self):
        """Check memory usage"""
        import psutil

        memory = psutil.virtual_memory()
        if memory.percent > 90:
            raise Exception(f"High memory usage: {memory.percent}%")

    async def _check_disk_space(self):
        """Check disk space"""
        import psutil

        disk = psutil.disk_usage('/')
        usage_percent = (disk.used / disk.total) * 100

        if usage_percent > 90:
            raise Exception(f"Low disk space: {usage_percent:.1f}% used")

# FastAPI integration
def setup_health_endpoints(app: FastAPI, health_checks: ServiceHealthChecks):
    """Setup health check endpoints"""

    @app.get("/health")
    async def health_check(response: Response):
        """Basic health check for load balancers"""
        results = await health_checks.health_checker.run_checks()

        if results["status"] != "healthy":
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return results

    @app.get("/health/ready")
    async def readiness_check(response: Response):
        """Readiness check for Kubernetes"""
        if not health_checks.health_checker.ready:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "not_ready", "message": "Service is starting up"}

        results = await health_checks.health_checker.run_checks()

        # Only check critical components for readiness
        critical_checks = {
            name: result for name, result in results["checks"].items()
            if health_checks.health_checker.checks[name]["critical"]
        }

        critical_failures = [
            name for name, result in critical_checks.items()
            if result["status"] != "healthy"
        ]

        if critical_failures:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {
                "status": "not_ready",
                "failed_checks": critical_failures,
                "checks": critical_checks
            }

        return {"status": "ready", "checks": critical_checks}

    @app.get("/health/live")
    async def liveness_check(response: Response):
        """Liveness check for Kubernetes"""
        if health_checks.health_checker.shutdown_requested:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "shutting_down"}

        # Basic liveness - just check if service is responding
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (
                datetime.utcnow() - health_checks.health_checker.startup_time
            ).total_seconds()
        }

    @app.on_event("startup")
    async def startup_event():
        """Mark service as ready after startup"""
        # Give services time to initialize
        await asyncio.sleep(5)
        health_checks.health_checker.ready = True

    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle graceful shutdown"""
        health_checks.health_checker.shutdown_requested = True

        # Give time for load balancer to detect unhealthy state
        await asyncio.sleep(10)
```

### Graceful Shutdown

```python
# services/shared/graceful_shutdown.py
"""
Graceful shutdown handling for zero-downtime deployments
"""

import asyncio
import signal
import logging
from typing import List, Callable
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class GracefulShutdownManager:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.shutdown_handlers: List[Callable] = []
        self.is_shutting_down = False
        self.active_requests = 0
        self._shutdown_event = asyncio.Event()

    def add_shutdown_handler(self, handler: Callable):
        """Add a shutdown handler"""
        self.shutdown_handlers.append(handler)

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())

        # Handle SIGTERM (docker stop, kubernetes)
        signal.signal(signal.SIGTERM, signal_handler)

        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)

    async def shutdown(self):
        """Perform graceful shutdown"""
        if self.is_shutting_down:
            return

        self.is_shutting_down = True
        logger.info("Starting graceful shutdown...")

        # Step 1: Stop accepting new requests (health checks will fail)
        logger.info("Stopping acceptance of new requests...")

        # Step 2: Wait for active requests to complete
        if self.active_requests > 0:
            logger.info(f"Waiting for {self.active_requests} active requests to complete...")

            wait_start = asyncio.get_event_loop().time()
            while self.active_requests > 0:
                if asyncio.get_event_loop().time() - wait_start > self.timeout:
                    logger.warning(
                        f"Shutdown timeout reached, {self.active_requests} requests still active"
                    )
                    break

                await asyncio.sleep(0.1)

        # Step 3: Run shutdown handlers
        logger.info("Running shutdown handlers...")
        for handler in self.shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
                logger.info(f"Executed shutdown handler: {handler.__name__}")
            except Exception as e:
                logger.error(f"Error in shutdown handler {handler.__name__}: {e}")

        # Step 4: Signal shutdown complete
        self._shutdown_event.set()
        logger.info("Graceful shutdown completed")

    @asynccontextmanager
    async def request_context(self):
        """Context manager for tracking active requests"""
        if self.is_shutting_down:
            raise Exception("Service is shutting down")

        self.active_requests += 1
        try:
            yield
        finally:
            self.active_requests -= 1

    async def wait_for_shutdown(self):
        """Wait for shutdown to complete"""
        await self._shutdown_event.wait()

# FastAPI integration
def setup_graceful_shutdown(app: FastAPI, shutdown_manager: GracefulShutdownManager):
    """Setup graceful shutdown for FastAPI"""

    @app.middleware("http")
    async def track_requests(request, call_next):
        """Middleware to track active requests"""

        # Reject new requests during shutdown
        if shutdown_manager.is_shutting_down:
            return Response(
                content="Service is shutting down",
                status_code=503,
                headers={"Connection": "close"}
            )

        async with shutdown_manager.request_context():
            response = await call_next(request)

            # Add connection close header during shutdown
            if shutdown_manager.is_shutting_down:
                response.headers["Connection"] = "close"

            return response

    # Add database cleanup handler
    shutdown_manager.add_shutdown_handler(cleanup_database_connections)

    # Add cache cleanup handler
    shutdown_manager.add_shutdown_handler(cleanup_redis_connections)

    # Add message broker cleanup handler
    shutdown_manager.add_shutdown_handler(cleanup_rabbitmq_connections)

async def cleanup_database_connections():
    """Cleanup database connections"""
    logger.info("Closing database connections...")
    # Close your database connections here

async def cleanup_redis_connections():
    """Cleanup Redis connections"""
    logger.info("Closing Redis connections...")
    # Close Redis connections here

async def cleanup_rabbitmq_connections():
    """Cleanup RabbitMQ connections"""
    logger.info("Closing RabbitMQ connections...")
    # Close RabbitMQ connections here

# Usage in main application
if __name__ == "__main__":
    shutdown_manager = GracefulShutdownManager(timeout=30)
    shutdown_manager.setup_signal_handlers()

    app = FastAPI()
    setup_graceful_shutdown(app, shutdown_manager)

    # Run server
    import uvicorn

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

    server = uvicorn.Server(config)

    # Add server shutdown to shutdown manager
    shutdown_manager.add_shutdown_handler(server.shutdown)

    # Run server
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())

    # Wait for graceful shutdown
    loop.run_until_complete(shutdown_manager.wait_for_shutdown())
```

This deployment patterns example provides comprehensive strategies for production deployments, database migrations, service versioning, and zero-downtime deployment patterns! 🚀