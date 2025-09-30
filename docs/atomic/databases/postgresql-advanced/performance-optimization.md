# PostgreSQL Performance Optimization

Comprehensive guide for optimizing PostgreSQL performance including query optimization, indexing strategies, connection pooling, and monitoring.

## Prerequisites

- [PostgreSQL Basic Setup](../postgresql/basic-setup.md)
- [Complex Relationship Modeling](complex-relationship-modeling.md)
- Understanding of SQL and database concepts

## Query Optimization Fundamentals

### Query Analysis with EXPLAIN

```sql
-- Basic EXPLAIN to see execution plan
EXPLAIN SELECT * FROM orders WHERE user_id = 123;

-- EXPLAIN ANALYZE for actual execution statistics
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT o.id, o.total_amount, u.username
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.created_at >= '2023-01-01'
AND o.status = 'completed';

-- EXPLAIN with different output formats
EXPLAIN (FORMAT JSON, ANALYZE)
SELECT product_id, SUM(quantity * unit_price) as revenue
FROM order_items
GROUP BY product_id
ORDER BY revenue DESC
LIMIT 10;
```

### Query Optimization Patterns

```python
from sqlalchemy import text, func, Index
from sqlalchemy.orm import load_only, joinedload, selectinload

class OptimizedQueries:
    """Examples of optimized query patterns"""

    @staticmethod
    def efficient_pagination(session, page: int, per_page: int = 20):
        """Cursor-based pagination for better performance"""
        offset = (page - 1) * per_page

        # Use LIMIT/OFFSET for small offsets
        if offset < 1000:
            return session.query(Order).order_by(Order.id).offset(offset).limit(per_page).all()

        # Use cursor-based pagination for large offsets
        cursor_query = session.query(Order).order_by(Order.id)
        if page > 1:
            # Get the last ID from previous page
            last_id = session.query(Order.id).order_by(Order.id).offset(offset - 1).limit(1).scalar()
            cursor_query = cursor_query.filter(Order.id > last_id)

        return cursor_query.limit(per_page).all()

    @staticmethod
    def optimized_aggregations(session, start_date, end_date):
        """Efficient aggregation queries"""
        # Use indexes on date columns
        return session.query(
            func.date_trunc('day', Order.created_at).label('date'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('revenue'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            Order.created_at.between(start_date, end_date),
            Order.status == 'completed'
        ).group_by(
            func.date_trunc('day', Order.created_at)
        ).order_by('date').all()

    @staticmethod
    def bulk_operations(session, order_ids: List[int]):
        """Efficient bulk updates"""
        # Use bulk update instead of individual updates
        session.query(Order).filter(
            Order.id.in_(order_ids)
        ).update(
            {Order.status: 'cancelled'},
            synchronize_session=False
        )

        # For complex bulk operations, use raw SQL
        session.execute(
            text("""
                UPDATE orders
                SET status = 'shipped',
                    shipped_at = NOW()
                WHERE id = ANY(:order_ids)
                AND status = 'confirmed'
            """),
            {'order_ids': order_ids}
        )

    @staticmethod
    def selective_loading(session, user_id: int):
        """Load only needed columns and relationships"""
        # Load only specific columns
        orders = session.query(Order).options(
            load_only(Order.id, Order.total_amount, Order.created_at)
        ).filter(Order.user_id == user_id).all()

        # Eager load relationships to avoid N+1 queries
        orders_with_items = session.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product)
        ).filter(Order.user_id == user_id).all()

        # Use selectinload for one-to-many relationships
        orders_with_select = session.query(Order).options(
            selectinload(Order.items)
        ).filter(Order.user_id == user_id).all()

        return orders_with_select

    @staticmethod
    def window_functions(session):
        """Use window functions for analytics"""
        from sqlalchemy import func

        return session.query(
            Order.id,
            Order.total_amount,
            Order.created_at,
            # Running total
            func.sum(Order.total_amount).over(
                order_by=Order.created_at,
                rows=(None, 0)
            ).label('running_total'),
            # Rank by amount
            func.row_number().over(
                order_by=Order.total_amount.desc()
            ).label('amount_rank'),
            # Previous order amount
            func.lag(Order.total_amount, 1).over(
                order_by=Order.created_at
            ).label('prev_amount')
        ).order_by(Order.created_at).all()
```

## Indexing Strategies

### Index Creation and Management

```sql
-- B-tree indexes (default)
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Composite indexes (order matters!)
CREATE INDEX idx_orders_user_status_date ON orders(user_id, status, created_at);

-- Partial indexes for conditional queries
CREATE INDEX idx_orders_active_user ON orders(user_id)
WHERE status IN ('pending', 'confirmed');

-- Expression indexes for computed values
CREATE INDEX idx_orders_year ON orders(EXTRACT(YEAR FROM created_at));

-- Unique indexes for constraints
CREATE UNIQUE INDEX idx_users_email_unique ON users(email)
WHERE deleted_at IS NULL;

-- GIN indexes for JSONB and arrays
CREATE INDEX idx_product_attributes ON products USING gin(attributes);
CREATE INDEX idx_product_tags ON products USING gin(tags);

-- Full-text search indexes
CREATE INDEX idx_product_search ON products USING gin(to_tsvector('english', name || ' ' || description));

-- Hash indexes for equality comparisons (PostgreSQL 10+)
CREATE INDEX idx_orders_status_hash ON orders USING hash(status);
```

### SQLAlchemy Index Definitions

```python
from sqlalchemy import Index, text

class OptimizedModels(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = Column(JSONB)

    # Define indexes in model
    __table_args__ = (
        # Composite index
        Index('idx_orders_user_status', 'user_id', 'status'),

        # Partial index
        Index('idx_orders_user_active', 'user_id',
              postgresql_where=text("status IN ('pending', 'confirmed')")),

        # Expression index
        Index('idx_orders_date_part', text('EXTRACT(YEAR FROM created_at)')),

        # GIN index for JSONB
        Index('idx_orders_metadata', 'metadata_json', postgresql_using='gin'),

        # Unique constraint with condition
        Index('idx_orders_unique_user_pending', 'user_id', unique=True,
              postgresql_where=text("status = 'pending'"))
    )

class IndexAnalyzer:
    """Tools for analyzing index usage"""

    @staticmethod
    def get_unused_indexes(session):
        """Find unused indexes"""
        return session.execute(text("""
            SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
            FROM pg_stat_user_indexes
            WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
            AND indexname NOT LIKE '%_pkey'
        """)).fetchall()

    @staticmethod
    def get_index_sizes(session):
        """Get index sizes"""
        return session.execute(text("""
            SELECT schemaname, tablename, indexname,
                   pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes
            ORDER BY pg_relation_size(indexrelid) DESC
        """)).fetchall()

    @staticmethod
    def get_duplicate_indexes(session):
        """Find potentially duplicate indexes"""
        return session.execute(text("""
            SELECT table_name, column_names, index_names
            FROM (
                SELECT
                    schemaname||'.'||tablename as table_name,
                    array_to_string(array_agg(attname), ',') as column_names,
                    array_to_string(array_agg(indexname), ',') as index_names,
                    count(*) as index_count
                FROM pg_index i
                JOIN pg_class t ON t.oid = i.indrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                JOIN pg_class idx ON idx.oid = i.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(i.indkey)
                WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
                GROUP BY schemaname, tablename, i.indkey
            ) dup_idx
            WHERE index_count > 1
        """)).fetchall()
```

## Connection Pooling and Configuration

### Connection Pool Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, NullPool
import redis.asyncio as redis

class DatabaseConfig:
    """Optimized database configuration"""

    @staticmethod
    def create_optimized_engine(database_url: str, is_production: bool = False):
        """Create properly configured engine"""

        pool_config = {
            'poolclass': QueuePool,
            'pool_size': 20,          # Core connections
            'max_overflow': 30,       # Additional connections
            'pool_pre_ping': True,    # Validate connections
            'pool_recycle': 3600,     # Recycle after 1 hour
            'pool_timeout': 30,       # Timeout for getting connection
        }

        if is_production:
            # Production optimizations
            pool_config.update({
                'pool_size': 50,
                'max_overflow': 100,
                'echo': False,
                'echo_pool': False,
            })
        else:
            # Development settings
            pool_config.update({
                'echo': True,
                'echo_pool': True,
            })

        return create_engine(
            database_url,
            **pool_config,
            connect_args={
                "application_name": "microservice",
                "options": "-c timezone=UTC"
            }
        )

class ConnectionMonitor:
    """Monitor database connections"""

    def __init__(self, engine):
        self.engine = engine

    def get_pool_status(self):
        """Get connection pool status"""
        pool = self.engine.pool
        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalidated()
        }

    def health_check(self):
        """Basic database health check"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                return result == 1
        except Exception:
            return False

# Redis for caching frequently accessed data
class CacheConfig:
    """Redis caching configuration"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def cache_query_result(self, cache_key: str, data, expiry: int = 300):
        """Cache query results"""
        import json
        await self.redis.setex(
            cache_key,
            expiry,
            json.dumps(data, default=str)
        )

    async def get_cached_result(self, cache_key: str):
        """Get cached query results"""
        import json
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None

    async def invalidate_cache_pattern(self, pattern: str):
        """Invalidate cache keys matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

### PostgreSQL Configuration Tuning

```sql
-- postgresql.conf optimizations

-- Memory settings
shared_buffers = '256MB'              -- 25% of RAM for small instances
work_mem = '4MB'                      -- Per operation memory
maintenance_work_mem = '64MB'         -- For maintenance operations
effective_cache_size = '1GB'          -- OS cache estimate

-- Checkpoint settings
checkpoint_completion_target = 0.7
wal_buffers = '16MB'
checkpoint_timeout = '10min'

-- Connection settings
max_connections = 200
superuser_reserved_connections = 3

-- Query planner settings
random_page_cost = 1.1               -- For SSD storage
effective_io_concurrency = 200       -- For SSD storage
default_statistics_target = 100

-- Logging for monitoring
log_statement = 'mod'                -- Log modifications
log_min_duration_statement = 1000    -- Log slow queries (1s+)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

-- Auto-vacuum settings
autovacuum = on
autovacuum_naptime = '1min'
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
```

## Monitoring and Performance Analysis

### Query Performance Monitoring

```python
import time
from contextlib import contextmanager
from sqlalchemy import event
from sqlalchemy.engine import Engine

class QueryProfiler:
    """Profile database queries"""

    def __init__(self):
        self.queries = []

    @contextmanager
    def profile_queries(self):
        """Context manager for profiling queries"""
        self.queries.clear()

        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()

        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - context._query_start_time
            self.queries.append({
                'statement': statement,
                'parameters': parameters,
                'duration': total,
                'timestamp': time.time()
            })

        try:
            yield self
        finally:
            event.remove(Engine, "before_cursor_execute", receive_before_cursor_execute)
            event.remove(Engine, "after_cursor_execute", receive_after_cursor_execute)

    def get_slow_queries(self, threshold: float = 1.0):
        """Get queries slower than threshold"""
        return [q for q in self.queries if q['duration'] > threshold]

    def get_query_stats(self):
        """Get query statistics"""
        if not self.queries:
            return {}

        durations = [q['duration'] for q in self.queries]
        return {
            'total_queries': len(self.queries),
            'total_time': sum(durations),
            'avg_time': sum(durations) / len(durations),
            'max_time': max(durations),
            'min_time': min(durations)
        }

class DatabaseMonitor:
    """Monitor database performance metrics"""

    def __init__(self, session):
        self.session = session

    def get_active_connections(self):
        """Get active connection count"""
        return self.session.execute(text("""
            SELECT count(*) as active_connections
            FROM pg_stat_activity
            WHERE state = 'active'
        """)).scalar()

    def get_long_running_queries(self, threshold_minutes: int = 5):
        """Get long-running queries"""
        return self.session.execute(text("""
            SELECT
                pid,
                now() - pg_stat_activity.query_start AS duration,
                query,
                state,
                usename,
                application_name
            FROM pg_stat_activity
            WHERE (now() - pg_stat_activity.query_start) > interval :threshold
            AND state != 'idle'
        """), {'threshold': f'{threshold_minutes} minutes'}).fetchall()

    def get_table_stats(self, table_name: str = None):
        """Get table statistics"""
        query = """
            SELECT
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_rows,
                n_dead_tup as dead_rows,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
        """

        if table_name:
            query += " WHERE tablename = :table_name"
            return self.session.execute(text(query), {'table_name': table_name}).fetchall()
        else:
            return self.session.execute(text(query)).fetchall()

    def get_index_usage(self, table_name: str = None):
        """Get index usage statistics"""
        query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_tup_read as reads,
                idx_tup_fetch as fetches,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes
        """

        if table_name:
            query += " WHERE tablename = :table_name"
            return self.session.execute(text(query), {'table_name': table_name}).fetchall()
        else:
            return self.session.execute(text(query)).fetchall()

    def get_database_size(self):
        """Get database size information"""
        return self.session.execute(text("""
            SELECT
                pg_database.datname as database_name,
                pg_size_pretty(pg_database_size(pg_database.datname)) as size
            FROM pg_database
            WHERE pg_database.datname = current_database()
        """)).fetchone()

    def get_blocking_queries(self):
        """Get queries that are blocking others"""
        return self.session.execute(text("""
            SELECT
                blocked_locks.pid AS blocked_pid,
                blocked_activity.usename AS blocked_user,
                blocking_locks.pid AS blocking_pid,
                blocking_activity.usename AS blocking_user,
                blocked_activity.query AS blocked_statement,
                blocking_activity.query AS blocking_statement
            FROM pg_catalog.pg_locks blocked_locks
            JOIN pg_catalog.pg_stat_activity blocked_activity
                ON blocked_activity.pid = blocked_locks.pid
            JOIN pg_catalog.pg_locks blocking_locks
                ON blocking_locks.locktype = blocked_locks.locktype
                AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
                AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                AND blocking_locks.pid != blocked_locks.pid
            JOIN pg_catalog.pg_stat_activity blocking_activity
                ON blocking_activity.pid = blocking_locks.pid
            WHERE NOT blocked_locks.GRANTED
        """)).fetchall()
```

## Maintenance and Optimization Tasks

### Automated Maintenance

```python
import asyncio
from datetime import datetime, timedelta

class DatabaseMaintenance:
    """Automated database maintenance tasks"""

    def __init__(self, session):
        self.session = session

    async def analyze_tables(self, table_names: List[str] = None):
        """Update table statistics"""
        if table_names:
            for table in table_names:
                self.session.execute(text(f"ANALYZE {table}"))
        else:
            self.session.execute(text("ANALYZE"))
        self.session.commit()

    async def vacuum_tables(self, table_names: List[str] = None, full: bool = False):
        """Vacuum tables to reclaim space"""
        vacuum_cmd = "VACUUM FULL" if full else "VACUUM"

        if table_names:
            for table in table_names:
                self.session.execute(text(f"{vacuum_cmd} {table}"))
        else:
            self.session.execute(text(vacuum_cmd))
        self.session.commit()

    async def reindex_tables(self, table_names: List[str]):
        """Rebuild indexes for better performance"""
        for table in table_names:
            self.session.execute(text(f"REINDEX TABLE {table}"))
        self.session.commit()

    async def cleanup_old_data(self, retention_days: int = 90):
        """Clean up old data based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Example: Clean up old audit logs
        deleted_count = self.session.execute(text("""
            DELETE FROM audit_logs
            WHERE created_at < :cutoff_date
        """), {'cutoff_date': cutoff_date}).rowcount

        self.session.commit()
        return deleted_count

class PerformanceOptimizer:
    """Automatic performance optimization"""

    def __init__(self, session):
        self.session = session

    def suggest_indexes(self, slow_query_threshold: float = 1.0):
        """Suggest indexes based on slow queries"""
        # This would analyze query logs and suggest indexes
        # Implementation would require log analysis
        suggestions = []

        # Example suggestions based on common patterns
        missing_indexes = self.session.execute(text("""
            SELECT schemaname, tablename, attname, n_distinct, correlation
            FROM pg_stats
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            AND n_distinct > 100
            AND correlation < 0.1
        """)).fetchall()

        for row in missing_indexes:
            suggestions.append({
                'table': f"{row.schemaname}.{row.tablename}",
                'column': row.attname,
                'reason': 'High cardinality, low correlation',
                'suggested_index': f"CREATE INDEX idx_{row.tablename}_{row.attname} ON {row.schemaname}.{row.tablename}({row.attname})"
            })

        return suggestions

    def check_table_bloat(self):
        """Check for table bloat"""
        return self.session.execute(text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                round(
                    100 * (pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename))::numeric
                    / pg_total_relation_size(schemaname||'.'||tablename), 2
                ) as index_ratio
            FROM pg_tables
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)).fetchall()
```

## Related Documentation

- [Complex Relationship Modeling](complex-relationship-modeling.md)
- [Production Migrations](production-migrations.md)
- [Multi-tenant Patterns](multi-tenant-patterns.md)
- [PostgreSQL Basic Setup](../postgresql/basic-setup.md)

## Best Practices Summary

1. **Query Optimization**:
   - Use EXPLAIN ANALYZE for query analysis
   - Implement proper pagination strategies
   - Avoid N+1 queries with eager loading
   - Use bulk operations for data modifications

2. **Indexing**:
   - Create indexes based on query patterns
   - Use composite indexes wisely
   - Monitor index usage and remove unused ones
   - Consider partial indexes for filtered queries

3. **Connection Management**:
   - Configure connection pooling appropriately
   - Monitor connection pool status
   - Use connection health checks

4. **Monitoring**:
   - Track slow queries and performance metrics
   - Monitor database size and growth
   - Set up alerts for performance issues
   - Regular maintenance schedule

5. **Configuration**:
   - Tune PostgreSQL settings for workload
   - Optimize memory and checkpoint settings
   - Configure appropriate logging
   - Regular database maintenance