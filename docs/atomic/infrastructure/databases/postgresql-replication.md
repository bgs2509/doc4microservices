# PostgreSQL Replication Setup

Comprehensive guide for PostgreSQL master-slave replication configuration for high availability and read scalability in production deployments (Maturity Level 4).

## Overview

PostgreSQL replication ensures data redundancy, high availability, and improved read performance by maintaining synchronized copies of the database across multiple servers.

**Use Cases**:
- **High Availability**: Automatic failover when master fails
- **Read Scalability**: Distribute read queries across replicas
- **Disaster Recovery**: Geographic replication for business continuity
- **Zero-Downtime Maintenance**: Upgrade replicas without service interruption

**Required for**: Maturity Level 4 (Production) with SLA requirements >99.9%

## Prerequisites

```yaml
# Minimum requirements
PostgreSQL: 15.x or 16.x
Docker Compose: 3.8+
Network: Low-latency connection between nodes (<10ms recommended)
Storage: Fast disk I/O (SSD recommended)
```

## Replication Architecture

### Streaming Replication (Recommended)

PostgreSQL streaming replication provides near real-time data synchronization using Write-Ahead Log (WAL) shipping.

```
┌─────────────┐         WAL Stream          ┌─────────────┐
│   Master    │ ───────────────────────────> │  Replica 1  │
│ (Read/Write)│                              │ (Read-Only) │
└─────────────┘                              └─────────────┘
       │
       │         WAL Stream
       └──────────────────────────────> ┌─────────────┐
                                         │  Replica 2  │
                                         │ (Read-Only) │
                                         └─────────────┘
```

### Replication Modes

| Mode | Description | Use Case | Data Loss Risk |
|------|-------------|----------|----------------|
| **Asynchronous** | Master doesn't wait for replica confirmation | High performance, eventual consistency | Minimal (<1s of transactions) |
| **Synchronous** | Master waits for at least one replica | Strong consistency, slower writes | Zero |
| **Logical Replication** | Selective table/row replication | Multi-tenant, partial replication | Depends on configuration |

## Docker Compose Configuration

### Basic Master-Replica Setup

```yaml
# docker-compose.replication.yml
version: '3.8'

services:
  postgres_master:
    image: postgres:16-alpine
    container_name: postgres-master
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-microservices_db}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_REPLICATION_USER: ${POSTGRES_REPL_USER:-replicator}
      POSTGRES_REPLICATION_PASSWORD: ${POSTGRES_REPL_PASSWORD:-repl_changeme}
    volumes:
      - postgres_master_data:/var/lib/postgresql/data
      - ./config/master/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./config/master/pg_hba.conf:/etc/postgresql/pg_hba.conf:ro
      - ./scripts/init-master.sh:/docker-entrypoint-initdb.d/init-master.sh:ro
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    networks:
      - postgres_replication
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres_replica1:
    image: postgres:16-alpine
    container_name: postgres-replica1
    environment:
      POSTGRES_MASTER_HOST: postgres_master
      POSTGRES_MASTER_PORT: 5432
      POSTGRES_REPLICATION_USER: ${POSTGRES_REPL_USER:-replicator}
      POSTGRES_REPLICATION_PASSWORD: ${POSTGRES_REPL_PASSWORD:-repl_changeme}
    volumes:
      - postgres_replica1_data:/var/lib/postgresql/data
      - ./config/replica/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./scripts/init-replica.sh:/docker-entrypoint-initdb.d/init-replica.sh:ro
    ports:
      - "5433:5432"
    depends_on:
      postgres_master:
        condition: service_healthy
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    networks:
      - postgres_replication
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres_replica2:
    image: postgres:16-alpine
    container_name: postgres-replica2
    environment:
      POSTGRES_MASTER_HOST: postgres_master
      POSTGRES_MASTER_PORT: 5432
      POSTGRES_REPLICATION_USER: ${POSTGRES_REPL_USER:-replicator}
      POSTGRES_REPLICATION_PASSWORD: ${POSTGRES_REPL_PASSWORD:-repl_changeme}
    volumes:
      - postgres_replica2_data:/var/lib/postgresql/data
      - ./config/replica/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./scripts/init-replica.sh:/docker-entrypoint-initdb.d/init-replica.sh:ro
    ports:
      - "5434:5432"
    depends_on:
      postgres_master:
        condition: service_healthy
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    networks:
      - postgres_replication
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_master_data:
  postgres_replica1_data:
  postgres_replica2_data:

networks:
  postgres_replication:
    driver: bridge
```

## Master Configuration

### postgresql.conf (Master)

```ini
# config/master/postgresql.conf

# Connection settings
listen_addresses = '*'
max_connections = 200

# Replication settings
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
synchronous_commit = on
synchronous_standby_names = 'replica1,replica2'  # For synchronous replication

# Performance tuning
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_replication_commands = on
```

### pg_hba.conf (Master)

```ini
# config/master/pg_hba.conf

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# Replication connections
host    replication     replicator      0.0.0.0/0               md5
host    replication     replicator      ::0/0                   md5

# Application connections
host    all             all             0.0.0.0/0               md5
host    all             all             ::0/0                   md5
```

### Master Initialization Script

```bash
#!/bin/bash
# scripts/init-master.sh

set -e

echo "Initializing PostgreSQL master..."

# Create replication user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create replication user
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${POSTGRES_REPLICATION_USER}') THEN
            CREATE USER ${POSTGRES_REPLICATION_USER} WITH REPLICATION ENCRYPTED PASSWORD '${POSTGRES_REPLICATION_PASSWORD}';
        END IF;
    END
    \$\$;

    -- Create replication slot for each replica
    SELECT pg_create_physical_replication_slot('replica1_slot');
    SELECT pg_create_physical_replication_slot('replica2_slot');
EOSQL

echo "PostgreSQL master initialization completed"
```

## Replica Configuration

### postgresql.conf (Replica)

```ini
# config/replica/postgresql.conf

# Connection settings
listen_addresses = '*'
max_connections = 200

# Replication settings
hot_standby = on
max_standby_streaming_delay = 30s
wal_receiver_status_interval = 10s
hot_standby_feedback = on

# Performance tuning (same as master)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 4MB

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Replica Initialization Script

```bash
#!/bin/bash
# scripts/init-replica.sh

set -e

echo "Initializing PostgreSQL replica..."

# Wait for master to be ready
until pg_isready -h ${POSTGRES_MASTER_HOST} -p ${POSTGRES_MASTER_PORT}; do
  echo "Waiting for master to be ready..."
  sleep 2
done

# Remove existing data directory
rm -rf ${PGDATA}/*

# Clone data from master using pg_basebackup
PGPASSWORD=${POSTGRES_REPLICATION_PASSWORD} pg_basebackup \
    -h ${POSTGRES_MASTER_HOST} \
    -p ${POSTGRES_MASTER_PORT} \
    -U ${POSTGRES_REPLICATION_USER} \
    -D ${PGDATA} \
    -Fp \
    -Xs \
    -P \
    -R

echo "PostgreSQL replica initialization completed"
```

## Monitoring Replication Status

### Check Replication on Master

```sql
-- View active replication connections
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state
FROM pg_stat_replication;

-- Check replication slots
SELECT slot_name, slot_type, active, restart_lsn
FROM pg_replication_slots;

-- Calculate replication lag (bytes)
SELECT
    client_addr,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;
```

### Check Replication on Replica

```sql
-- Check if replica is in recovery mode
SELECT pg_is_in_recovery();

-- View replication status
SELECT
    status,
    receive_start_lsn,
    receive_start_tli,
    received_lsn,
    last_msg_send_time,
    last_msg_receipt_time
FROM pg_stat_wal_receiver;

-- Calculate replication lag (seconds)
SELECT
    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;
```

## Application Integration

### Connection Pooling with Read Replicas

```python
# src/core/database_replication.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
import os

class ReplicationDatabaseConfig:
    """PostgreSQL replication configuration"""

    def __init__(self):
        # Master (write) connection
        self.master_url = self._build_url(
            host=os.getenv("POSTGRES_MASTER_HOST", "postgres_master"),
            port=int(os.getenv("POSTGRES_MASTER_PORT", "5432"))
        )

        # Replica (read) connections
        self.replica_urls = [
            self._build_url(
                host=os.getenv("POSTGRES_REPLICA1_HOST", "postgres_replica1"),
                port=int(os.getenv("POSTGRES_REPLICA1_PORT", "5433"))
            ),
            self._build_url(
                host=os.getenv("POSTGRES_REPLICA2_HOST", "postgres_replica2"),
                port=int(os.getenv("POSTGRES_REPLICA2_PORT", "5434"))
            ),
        ]

    def _build_url(self, host: str, port: int) -> str:
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        database = os.getenv("POSTGRES_DB", "microservices_db")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


# Master engine (writes)
_master_engine: AsyncEngine | None = None
_master_session_factory: async_sessionmaker[AsyncSession] | None = None

# Replica engines (reads)
_replica_engines: list[AsyncEngine] = []
_replica_session_factory: async_sessionmaker[AsyncSession] | None = None
_current_replica_idx = 0


def init_replication_database(config: ReplicationDatabaseConfig) -> None:
    """Initialize master and replica engines"""
    global _master_engine, _master_session_factory, _replica_engines, _replica_session_factory

    # Create master engine
    _master_engine = create_async_engine(config.master_url, pool_size=20, max_overflow=10)
    _master_session_factory = async_sessionmaker(_master_engine, expire_on_commit=False)

    # Create replica engines (round-robin)
    _replica_engines = [
        create_async_engine(url, pool_size=20, max_overflow=10)
        for url in config.replica_urls
    ]


async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    """Get session for write operations (master)"""
    if _master_session_factory is None:
        raise RuntimeError("Database not initialized")

    async with _master_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
    """Get session for read operations (replicas, round-robin)"""
    global _current_replica_idx

    if not _replica_engines:
        raise RuntimeError("Replicas not initialized")

    # Round-robin replica selection
    engine = _replica_engines[_current_replica_idx]
    _current_replica_idx = (_current_replica_idx + 1) % len(_replica_engines)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
```

### FastAPI Dependency Injection

```python
# src/api/dependencies.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database_replication import get_write_session, get_read_session


async def get_db_write(session: AsyncSession = Depends(get_write_session)) -> AsyncSession:
    """Dependency for write operations"""
    return session


async def get_db_read(session: AsyncSession = Depends(get_read_session)) -> AsyncSession:
    """Dependency for read operations"""
    return session
```

### Usage Example

```python
# src/api/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db_read, get_db_write

router = APIRouter()


@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_read)):
    """Read from replica"""
    # Query executes on replica
    return await user_repository.get_by_id(db, user_id)


@router.post("/users")
async def create_user(user_data: dict, db: AsyncSession = Depends(get_db_write)):
    """Write to master"""
    # Insert executes on master, then replicates to replicas
    return await user_repository.create(db, user_data)
```

## High Availability with Patroni (Advanced)

For automatic failover and cluster management, use Patroni with etcd/Consul:

```yaml
# docker-compose.patroni.yml
version: '3.8'

services:
  etcd:
    image: quay.io/coreos/etcd:v3.5.0
    environment:
      ETCD_LISTEN_CLIENT_URLS: http://0.0.0.0:2379
      ETCD_ADVERTISE_CLIENT_URLS: http://etcd:2379

  patroni1:
    image: patroni/patroni:3.0.0
    environment:
      PATRONI_NAME: patroni1
      PATRONI_RESTAPI_CONNECT_ADDRESS: patroni1:8008
      PATRONI_POSTGRESQL_CONNECT_ADDRESS: patroni1:5432
      PATRONI_POSTGRESQL_DATA_DIR: /data/patroni
      PATRONI_ETCD3_HOSTS: etcd:2379
```

For complete Patroni setup, see [Patroni documentation](https://patroni.readthedocs.io/).

## Troubleshooting

### Issue: Replication Lag

```bash
# Check lag on master
docker exec postgres-master psql -U postgres -c "
  SELECT client_addr, pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
  FROM pg_stat_replication;"

# Check lag on replica
docker exec postgres-replica1 psql -U postgres -c "
  SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;"
```

### Issue: Replication Stopped

```bash
# Check replica logs
docker logs postgres-replica1

# Restart replication
docker exec postgres-replica1 psql -U postgres -c "SELECT pg_wal_replay_resume();"
```

### Issue: Split-Brain (Multiple Masters)

```bash
# Verify which node is master
docker exec postgres-master psql -U postgres -c "SELECT pg_is_in_recovery();"
docker exec postgres-replica1 psql -U postgres -c "SELECT pg_is_in_recovery();"

# If replica shows false (is master), force back to replica:
docker exec postgres-replica1 pg_ctl promote
```

## Related Documentation

- [PostgreSQL Basic Setup](../../databases/postgresql/basic-setup.md) - Initial PostgreSQL configuration
- [Connection Pooling](connection-pooling.md) - Connection management patterns
- [Performance Optimization](performance-optimization.md) - Query and indexing optimization
- [Maturity Levels](../../../reference/maturity-levels.md) - Level 4 (Production) requirements

## Production Checklist

- [ ] Synchronous replication enabled for critical transactions
- [ ] At least 2 replicas in different availability zones
- [ ] Replication lag monitoring (<5 seconds)
- [ ] Automatic failover configured (Patroni or similar)
- [ ] Regular backup verification (restore test)
- [ ] Connection pooling for replicas (PgBouncer/application-level)
- [ ] Read-write split implemented in application
- [ ] Replication slots monitored (prevent WAL bloat)
- [ ] Network latency between nodes <10ms
- [ ] Disk I/O capacity sufficient (>1000 IOPS)
