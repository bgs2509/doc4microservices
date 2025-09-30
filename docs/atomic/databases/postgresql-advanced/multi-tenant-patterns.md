# Multi-tenant Patterns in PostgreSQL

Comprehensive guide for implementing multi-tenancy patterns including database-per-tenant, schema-per-tenant, and row-level security approaches.

## Prerequisites

- [Complex Relationship Modeling](complex-relationship-modeling.md)
- [Performance Optimization](performance-optimization.md)
- [Production Migrations](production-migrations.md)
- Understanding of PostgreSQL security and permissions

## Multi-tenancy Strategy Overview

### Tenancy Models Comparison

```python
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

class TenancyModel(Enum):
    DATABASE_PER_TENANT = "database_per_tenant"
    SCHEMA_PER_TENANT = "schema_per_tenant"
    ROW_LEVEL_SECURITY = "row_level_security"
    HYBRID = "hybrid"

@dataclass
class TenancyRequirements:
    tenant_count: int
    data_isolation_level: str  # "strict", "moderate", "basic"
    customization_needs: str   # "high", "medium", "low"
    scaling_requirements: str  # "horizontal", "vertical", "both"
    compliance_requirements: List[str]  # ["GDPR", "HIPAA", "SOX", etc.]
    budget_constraints: str    # "cost_optimized", "balanced", "performance_first"

class TenancyModelSelector:
    """Helper to select appropriate tenancy model"""

    @staticmethod
    def recommend_model(requirements: TenancyRequirements) -> TenancyModel:
        """Recommend tenancy model based on requirements"""

        # High isolation requirements -> Database per tenant
        if (requirements.data_isolation_level == "strict" or
            "HIPAA" in requirements.compliance_requirements or
            requirements.customization_needs == "high"):
            return TenancyModel.DATABASE_PER_TENANT

        # Medium isolation with cost constraints -> Schema per tenant
        elif (requirements.data_isolation_level == "moderate" and
              requirements.tenant_count < 1000):
            return TenancyModel.SCHEMA_PER_TENANT

        # Large scale with basic isolation -> Row-level security
        elif (requirements.tenant_count > 1000 or
              requirements.budget_constraints == "cost_optimized"):
            return TenancyModel.ROW_LEVEL_SECURITY

        # Mixed requirements -> Hybrid approach
        else:
            return TenancyModel.HYBRID

    @staticmethod
    def get_model_characteristics(model: TenancyModel) -> Dict[str, str]:
        """Get characteristics of tenancy model"""
        characteristics = {
            TenancyModel.DATABASE_PER_TENANT: {
                "isolation": "Maximum",
                "scalability": "Good",
                "cost": "High",
                "complexity": "Medium",
                "customization": "High"
            },
            TenancyModel.SCHEMA_PER_TENANT: {
                "isolation": "Good",
                "scalability": "Medium",
                "cost": "Medium",
                "complexity": "Medium",
                "customization": "Medium"
            },
            TenancyModel.ROW_LEVEL_SECURITY: {
                "isolation": "Basic",
                "scalability": "Excellent",
                "cost": "Low",
                "complexity": "High",
                "customization": "Low"
            },
            TenancyModel.HYBRID: {
                "isolation": "Variable",
                "scalability": "Good",
                "cost": "Medium",
                "complexity": "High",
                "customization": "High"
            }
        }
        return characteristics.get(model, {})
```

## Database-per-Tenant Pattern

### Database Management Service

```python
import asyncio
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class DatabasePerTenantManager:
    """Manage separate databases for each tenant"""

    def __init__(self, master_db_url: str, db_template: str = "template_app"):
        self.master_db_url = master_db_url
        self.db_template = db_template
        self.tenant_databases = {}
        self.connection_pools = {}

    async def create_tenant_database(self, tenant_id: str, tenant_config: Dict[str, Any] = None) -> str:
        """Create new database for tenant"""
        db_name = f"tenant_{tenant_id}"

        # Connect to master database
        master_conn = await asyncpg.connect(self.master_db_url)

        try:
            # Create database from template
            await master_conn.execute(f"""
                CREATE DATABASE {db_name}
                WITH TEMPLATE {self.db_template}
                OWNER tenant_owner
                ENCODING 'UTF8'
                LC_COLLATE 'en_US.UTF-8'
                LC_CTYPE 'en_US.UTF-8'
            """)

            # Create tenant-specific connection pool
            tenant_db_url = self.master_db_url.rsplit('/', 1)[0] + f'/{db_name}'
            self.tenant_databases[tenant_id] = {
                'db_name': db_name,
                'db_url': tenant_db_url,
                'created_at': datetime.utcnow(),
                'config': tenant_config or {}
            }

            # Initialize connection pool
            await self._create_connection_pool(tenant_id, tenant_db_url)

            # Run tenant-specific initialization
            await self._initialize_tenant_database(tenant_id, tenant_config)

            return tenant_db_url

        finally:
            await master_conn.close()

    async def _create_connection_pool(self, tenant_id: str, db_url: str):
        """Create optimized connection pool for tenant"""
        engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.connection_pools[tenant_id] = sessionmaker(bind=engine)

    async def _initialize_tenant_database(self, tenant_id: str, config: Dict[str, Any]):
        """Initialize tenant-specific configuration"""
        session_maker = self.connection_pools[tenant_id]

        with session_maker() as session:
            # Set tenant-specific configuration
            if config:
                # Create tenant settings table
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS tenant_settings (
                        key VARCHAR(100) PRIMARY KEY,
                        value JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))

                # Insert tenant configuration
                for key, value in config.items():
                    session.execute(text("""
                        INSERT INTO tenant_settings (key, value)
                        VALUES (:key, :value)
                        ON CONFLICT (key) DO UPDATE
                        SET value = EXCLUDED.value, updated_at = NOW()
                    """), {'key': key, 'value': json.dumps(value)})

            # Create tenant-specific indexes or customizations
            await self._apply_tenant_customizations(session, tenant_id, config)

            session.commit()

    async def _apply_tenant_customizations(self, session, tenant_id: str, config: Dict[str, Any]):
        """Apply tenant-specific database customizations"""
        customizations = config.get('database_customizations', {})

        # Custom indexes
        for index_config in customizations.get('indexes', []):
            session.execute(text(index_config['sql']))

        # Custom stored procedures
        for proc_config in customizations.get('procedures', []):
            session.execute(text(proc_config['sql']))

        # Tenant-specific data seeding
        seed_data = customizations.get('seed_data', {})
        for table, records in seed_data.items():
            for record in records:
                columns = ', '.join(record.keys())
                placeholders = ', '.join(f':{k}' for k in record.keys())
                session.execute(
                    text(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"),
                    record
                )

    def get_tenant_session(self, tenant_id: str):
        """Get database session for specific tenant"""
        if tenant_id not in self.connection_pools:
            raise ValueError(f"Tenant {tenant_id} database not found")

        return self.connection_pools[tenant_id]()

    async def backup_tenant_database(self, tenant_id: str, backup_location: str) -> str:
        """Create backup of tenant database"""
        tenant_info = self.tenant_databases.get(tenant_id)
        if not tenant_info:
            raise ValueError(f"Tenant {tenant_id} not found")

        db_name = tenant_info['db_name']
        backup_filename = f"{backup_location}/{db_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.dump"

        # Use pg_dump for backup
        backup_command = [
            'pg_dump',
            '--host', self._extract_host(self.master_db_url),
            '--port', str(self._extract_port(self.master_db_url)),
            '--username', self._extract_username(self.master_db_url),
            '--format=custom',
            '--no-owner',
            '--no-privileges',
            '--file', backup_filename,
            db_name
        ]

        # Execute backup (implementation depends on environment)
        # subprocess.run(backup_command, check=True)

        return backup_filename

    async def restore_tenant_database(self, tenant_id: str, backup_file: str) -> bool:
        """Restore tenant database from backup"""
        tenant_info = self.tenant_databases.get(tenant_id)
        if not tenant_info:
            raise ValueError(f"Tenant {tenant_id} not found")

        # Implementation for restore operation
        # This would use pg_restore
        return True

    async def migrate_tenant(self, tenant_id: str, migration_scripts: List[str]) -> Dict[str, Any]:
        """Run migrations on specific tenant database"""
        session_maker = self.connection_pools[tenant_id]
        results = []

        with session_maker() as session:
            for script in migration_scripts:
                try:
                    session.execute(text(script))
                    results.append({'script': script[:50], 'success': True})
                except Exception as e:
                    session.rollback()
                    results.append({'script': script[:50], 'success': False, 'error': str(e)})
                    break

            session.commit()

        return {
            'tenant_id': tenant_id,
            'migration_results': results,
            'success': all(r['success'] for r in results)
        }

    def _extract_host(self, db_url: str) -> str:
        """Extract host from database URL"""
        from urllib.parse import urlparse
        return urlparse(db_url).hostname

    def _extract_port(self, db_url: str) -> int:
        """Extract port from database URL"""
        from urllib.parse import urlparse
        return urlparse(db_url).port or 5432

    def _extract_username(self, db_url: str) -> str:
        """Extract username from database URL"""
        from urllib.parse import urlparse
        return urlparse(db_url).username
```

## Schema-per-Tenant Pattern

### Schema-based Multi-tenancy

```python
class SchemaPerTenantManager:
    """Manage separate schemas for each tenant"""

    def __init__(self, db_session):
        self.session = db_session
        self.tenant_schemas = {}

    async def create_tenant_schema(self, tenant_id: str, schema_config: Dict[str, Any] = None) -> str:
        """Create schema for tenant"""
        schema_name = f"tenant_{tenant_id}"

        # Create schema
        await self.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

        # Create tenant-specific role
        role_name = f"tenant_{tenant_id}_role"
        await self.session.execute(text(f"""
            CREATE ROLE {role_name} WITH
            LOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOINHERIT
            NOREPLICATION
            CONNECTION LIMIT 20
        """))

        # Grant schema permissions
        await self.session.execute(text(f"""
            GRANT USAGE ON SCHEMA {schema_name} TO {role_name};
            GRANT CREATE ON SCHEMA {schema_name} TO {role_name};
            ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name}
            GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role_name};
        """))

        # Create tables in tenant schema
        await self._create_tenant_tables(schema_name)

        # Apply schema-specific configuration
        if schema_config:
            await self._apply_schema_configuration(schema_name, schema_config)

        self.tenant_schemas[tenant_id] = {
            'schema_name': schema_name,
            'role_name': role_name,
            'created_at': datetime.utcnow(),
            'config': schema_config or {}
        }

        self.session.commit()
        return schema_name

    async def _create_tenant_tables(self, schema_name: str):
        """Create standard tables in tenant schema"""
        table_definitions = [
            f"""
            CREATE TABLE {schema_name}.users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,
            f"""
            CREATE TABLE {schema_name}.orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES {schema_name}.users(id),
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,
            f"""
            CREATE TABLE {schema_name}.order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES {schema_name}.orders(id),
                product_name VARCHAR(255) NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """
        ]

        for table_sql in table_definitions:
            await self.session.execute(text(table_sql))

    async def _apply_schema_configuration(self, schema_name: str, config: Dict[str, Any]):
        """Apply tenant-specific schema configuration"""

        # Custom indexes
        for index_config in config.get('indexes', []):
            index_sql = index_config['sql'].replace('{schema}', schema_name)
            await self.session.execute(text(index_sql))

        # Custom views
        for view_config in config.get('views', []):
            view_sql = view_config['sql'].replace('{schema}', schema_name)
            await self.session.execute(text(view_sql))

        # Tenant-specific functions
        for function_config in config.get('functions', []):
            function_sql = function_config['sql'].replace('{schema}', schema_name)
            await self.session.execute(text(function_sql))

class SchemaContextManager:
    """Manage schema context for queries"""

    def __init__(self, db_session):
        self.session = db_session
        self.current_schema = None

    async def set_tenant_context(self, tenant_id: str):
        """Set current tenant schema context"""
        schema_name = f"tenant_{tenant_id}"
        await self.session.execute(text(f"SET search_path = {schema_name}, public"))
        self.current_schema = schema_name

    async def reset_context(self):
        """Reset to default schema context"""
        await self.session.execute(text("SET search_path = public"))
        self.current_schema = None

    def __enter__(self):
        return self

    async def __aenter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.current_schema:
            asyncio.create_task(self.reset_context())

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.current_schema:
            await self.reset_context()

# SQLAlchemy integration with schema context
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

class TenantAwareBase:
    """Base class for tenant-aware models"""

    @classmethod
    def set_schema(cls, schema_name: str):
        """Dynamically set schema for model"""
        cls.__table__.schema = schema_name

def create_tenant_models(schema_name: str):
    """Create models bound to specific schema"""
    Base = declarative_base(cls=TenantAwareBase)

    class TenantUser(Base):
        __tablename__ = 'users'
        __table_args__ = {'schema': schema_name}

        id = Column(Integer, primary_key=True)
        username = Column(String(100), unique=True, nullable=False)
        email = Column(String(255), unique=True, nullable=False)
        password_hash = Column(String(255), nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)

        orders = relationship("TenantOrder", back_populates="user")

    class TenantOrder(Base):
        __tablename__ = 'orders'
        __table_args__ = {'schema': schema_name}

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey(f'{schema_name}.users.id'))
        total_amount = Column(Numeric(10, 2), nullable=False)
        status = Column(String(20), default='pending')
        created_at = Column(DateTime, default=datetime.utcnow)

        user = relationship("TenantUser", back_populates="orders")
        items = relationship("TenantOrderItem", back_populates="order")

    class TenantOrderItem(Base):
        __tablename__ = 'order_items'
        __table_args__ = {'schema': schema_name}

        id = Column(Integer, primary_key=True)
        order_id = Column(Integer, ForeignKey(f'{schema_name}.orders.id'))
        product_name = Column(String(255), nullable=False)
        quantity = Column(Integer, nullable=False)
        unit_price = Column(Numeric(10, 2), nullable=False)

        order = relationship("TenantOrder", back_populates="items")

    return {
        'User': TenantUser,
        'Order': TenantOrder,
        'OrderItem': TenantOrderItem
    }
```

## Row-Level Security (RLS) Pattern

### RLS Implementation

```python
class RowLevelSecurityManager:
    """Implement row-level security for multi-tenancy"""

    def __init__(self, db_session):
        self.session = db_session

    async def setup_rls_tables(self):
        """Setup tables with RLS policies"""

        # Enable RLS on tables
        rls_tables = ['users', 'orders', 'order_items', 'products']

        for table in rls_tables:
            await self.session.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))

        # Create RLS policies
        await self._create_rls_policies()

        self.session.commit()

    async def _create_rls_policies(self):
        """Create row-level security policies"""

        # Policy for users table
        await self.session.execute(text("""
            CREATE POLICY tenant_isolation_users ON users
            FOR ALL
            TO tenant_role
            USING (tenant_id = current_setting('app.current_tenant')::INTEGER)
            WITH CHECK (tenant_id = current_setting('app.current_tenant')::INTEGER)
        """))

        # Policy for orders table
        await self.session.execute(text("""
            CREATE POLICY tenant_isolation_orders ON orders
            FOR ALL
            TO tenant_role
            USING (tenant_id = current_setting('app.current_tenant')::INTEGER)
            WITH CHECK (tenant_id = current_setting('app.current_tenant')::INTEGER)
        """))

        # Policy for order_items table with JOIN
        await self.session.execute(text("""
            CREATE POLICY tenant_isolation_order_items ON order_items
            FOR ALL
            TO tenant_role
            USING (EXISTS (
                SELECT 1 FROM orders
                WHERE orders.id = order_items.order_id
                AND orders.tenant_id = current_setting('app.current_tenant')::INTEGER
            ))
            WITH CHECK (EXISTS (
                SELECT 1 FROM orders
                WHERE orders.id = order_items.order_id
                AND orders.tenant_id = current_setting('app.current_tenant')::INTEGER
            ))
        """))

        # Bypass policy for superusers/admin
        await self.session.execute(text("""
            CREATE POLICY bypass_rls_for_admin ON users
            FOR ALL
            TO admin_role
            USING (true)
        """))

    async def set_tenant_context(self, tenant_id: int):
        """Set tenant context for RLS"""
        await self.session.execute(text(f"SELECT set_config('app.current_tenant', '{tenant_id}', false)"))

    async def create_tenant_user(self, tenant_id: int, username: str) -> str:
        """Create database user for tenant with appropriate permissions"""
        role_name = f"tenant_{tenant_id}_user"

        # Create role
        await self.session.execute(text(f"""
            CREATE ROLE {role_name} WITH
            LOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            INHERIT
            NOREPLICATION
            CONNECTION LIMIT 10
            IN ROLE tenant_role
        """))

        # Set default tenant context for this user
        await self.session.execute(text(f"""
            ALTER ROLE {role_name}
            SET app.current_tenant = '{tenant_id}'
        """))

        self.session.commit()
        return role_name

# SQLAlchemy models with RLS support
class RLSBase(Base):
    """Base class for RLS-enabled models"""

    tenant_id = Column(Integer, nullable=False, index=True)

    @classmethod
    def for_tenant(cls, session, tenant_id: int):
        """Query scoped to specific tenant"""
        return session.query(cls).filter(cls.tenant_id == tenant_id)

class User(RLSBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")

    __table_args__ = (
        Index('idx_users_tenant_email', 'tenant_id', 'email', unique=True),
        Index('idx_users_tenant_username', 'tenant_id', 'username', unique=True),
    )

class Order(RLSBase):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

    __table_args__ = (
        Index('idx_orders_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_orders_tenant_status', 'tenant_id', 'status'),
    )

class RLSQueryHelper:
    """Helper for RLS queries"""

    @staticmethod
    def ensure_tenant_context(session, tenant_id: int):
        """Ensure tenant context is set"""
        session.execute(text(f"SELECT set_config('app.current_tenant', '{tenant_id}', true)"))

    @staticmethod
    def get_tenant_stats(session, tenant_id: int) -> Dict[str, Any]:
        """Get statistics for specific tenant"""
        RLSQueryHelper.ensure_tenant_context(session, tenant_id)

        stats = session.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM users) as user_count,
                (SELECT COUNT(*) FROM orders) as order_count,
                (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status = 'completed') as total_revenue
        """)).fetchone()

        return {
            'tenant_id': tenant_id,
            'user_count': stats.user_count,
            'order_count': stats.order_count,
            'total_revenue': float(stats.total_revenue)
        }
```

## Hybrid Multi-tenancy Pattern

### Flexible Multi-tenancy Architecture

```python
class HybridTenancyManager:
    """Manage hybrid multi-tenancy approach"""

    def __init__(self, master_db_session):
        self.master_session = master_db_session
        self.tenant_configs = {}
        self.tenant_managers = {}

    async def setup_tenant(self, tenant_id: str, tenancy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup tenant using appropriate tenancy model"""

        tenant_tier = tenancy_config.get('tier', 'standard')
        data_sensitivity = tenancy_config.get('data_sensitivity', 'normal')
        expected_scale = tenancy_config.get('expected_scale', 'medium')

        # Determine tenancy model based on requirements
        if tenant_tier == 'enterprise' or data_sensitivity == 'high':
            tenancy_model = TenancyModel.DATABASE_PER_TENANT
            manager = DatabasePerTenantManager(self.master_db_url)
            connection_info = await manager.create_tenant_database(tenant_id, tenancy_config)

        elif tenant_tier == 'business' or expected_scale == 'medium':
            tenancy_model = TenancyModel.SCHEMA_PER_TENANT
            manager = SchemaPerTenantManager(self.master_session)
            connection_info = await manager.create_tenant_schema(tenant_id, tenancy_config)

        else:
            tenancy_model = TenancyModel.ROW_LEVEL_SECURITY
            manager = RowLevelSecurityManager(self.master_session)
            await manager.setup_rls_tables()
            connection_info = await manager.create_tenant_user(int(tenant_id), f"tenant_{tenant_id}")

        # Store tenant configuration
        self.tenant_configs[tenant_id] = {
            'tenancy_model': tenancy_model,
            'tier': tenant_tier,
            'connection_info': connection_info,
            'created_at': datetime.utcnow(),
            'config': tenancy_config
        }

        self.tenant_managers[tenant_id] = manager

        return {
            'tenant_id': tenant_id,
            'tenancy_model': tenancy_model.value,
            'connection_info': connection_info,
            'setup_completed': True
        }

    def get_tenant_session(self, tenant_id: str):
        """Get appropriate session for tenant"""
        tenant_config = self.tenant_configs.get(tenant_id)
        if not tenant_config:
            raise ValueError(f"Tenant {tenant_id} not configured")

        tenancy_model = tenant_config['tenancy_model']

        if tenancy_model == TenancyModel.DATABASE_PER_TENANT:
            manager = self.tenant_managers[tenant_id]
            return manager.get_tenant_session(tenant_id)

        elif tenancy_model == TenancyModel.SCHEMA_PER_TENANT:
            # Return session with schema context
            session = self.master_session
            schema_context = SchemaContextManager(session)
            asyncio.create_task(schema_context.set_tenant_context(tenant_id))
            return session

        else:  # RLS
            # Return session with RLS context
            session = self.master_session
            rls_manager = self.tenant_managers[tenant_id]
            asyncio.create_task(rls_manager.set_tenant_context(int(tenant_id)))
            return session

    async def migrate_tenant(self, tenant_id: str, new_tenancy_model: TenancyModel) -> Dict[str, Any]:
        """Migrate tenant to different tenancy model"""
        current_config = self.tenant_configs.get(tenant_id)
        if not current_config:
            raise ValueError(f"Tenant {tenant_id} not found")

        current_model = current_config['tenancy_model']
        if current_model == new_tenancy_model:
            return {'message': 'Tenant already using target tenancy model'}

        # Export current data
        export_data = await self._export_tenant_data(tenant_id)

        # Setup new tenancy model
        migration_config = {
            **current_config['config'],
            'migration_source': current_model.value,
            'migration_data': export_data
        }

        # Create tenant with new model
        new_setup = await self.setup_tenant(tenant_id, migration_config)

        # Import data to new tenant setup
        await self._import_tenant_data(tenant_id, export_data)

        # Archive old tenant setup
        await self._archive_old_tenant_setup(tenant_id, current_model)

        return {
            'tenant_id': tenant_id,
            'migration_from': current_model.value,
            'migration_to': new_tenancy_model.value,
            'completed_at': datetime.utcnow(),
            'data_migrated': True
        }

    async def _export_tenant_data(self, tenant_id: str) -> Dict[str, Any]:
        """Export all tenant data for migration"""
        session = self.get_tenant_session(tenant_id)

        # Export all tables
        tables_data = {}

        # This would export data from all tenant tables
        # Implementation depends on tenancy model
        return tables_data

    async def _import_tenant_data(self, tenant_id: str, data: Dict[str, Any]):
        """Import data to new tenant setup"""
        session = self.get_tenant_session(tenant_id)

        # Import data to all tables
        # Implementation depends on tenancy model and data structure
        pass

class TenantMetricsCollector:
    """Collect metrics across different tenancy models"""

    def __init__(self, hybrid_manager: HybridTenancyManager):
        self.hybrid_manager = hybrid_manager

    async def collect_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Collect metrics for specific tenant"""
        tenant_config = self.hybrid_manager.tenant_configs.get(tenant_id)
        if not tenant_config:
            return {}

        tenancy_model = tenant_config['tenancy_model']
        session = self.hybrid_manager.get_tenant_session(tenant_id)

        # Base metrics common to all models
        base_metrics = await self._collect_base_metrics(session, tenancy_model)

        # Model-specific metrics
        if tenancy_model == TenancyModel.DATABASE_PER_TENANT:
            specific_metrics = await self._collect_database_metrics(session, tenant_id)
        elif tenancy_model == TenancyModel.SCHEMA_PER_TENANT:
            specific_metrics = await self._collect_schema_metrics(session, tenant_id)
        else:  # RLS
            specific_metrics = await self._collect_rls_metrics(session, tenant_id)

        return {
            'tenant_id': tenant_id,
            'tenancy_model': tenancy_model.value,
            'collection_time': datetime.utcnow(),
            **base_metrics,
            **specific_metrics
        }

    async def _collect_base_metrics(self, session, tenancy_model: TenancyModel) -> Dict[str, Any]:
        """Collect base metrics"""
        # Common metrics like row counts, activity, etc.
        return {
            'tenancy_model': tenancy_model.value,
            'active_connections': 0,  # Implementation specific
            'query_performance': {},   # Implementation specific
        }

    async def _collect_database_metrics(self, session, tenant_id: str) -> Dict[str, Any]:
        """Collect database-specific metrics"""
        return {
            'database_size': 0,        # pg_database_size
            'connection_limit': 0,     # Database-specific limits
            'backup_status': 'current' # Backup information
        }

    async def _collect_schema_metrics(self, session, tenant_id: str) -> Dict[str, Any]:
        """Collect schema-specific metrics"""
        return {
            'schema_size': 0,          # Schema size calculation
            'shared_resources': {},    # Shared resource usage
        }

    async def _collect_rls_metrics(self, session, tenant_id: str) -> Dict[str, Any]:
        """Collect RLS-specific metrics"""
        return {
            'rls_policy_performance': {},  # RLS policy efficiency
            'tenant_data_distribution': {} # Data distribution analysis
        }
```

## Security and Compliance

### Security Implementation

```python
class TenantSecurityManager:
    """Manage security across tenancy models"""

    def __init__(self):
        self.audit_log = []
        self.security_policies = {}

    async def setup_tenant_security(self, tenant_id: str, security_config: Dict[str, Any]):
        """Setup security for tenant"""

        # Encryption at rest
        if security_config.get('encryption_required'):
            await self._setup_encryption(tenant_id, security_config)

        # Audit logging
        if security_config.get('audit_logging'):
            await self._setup_audit_logging(tenant_id)

        # Access controls
        await self._setup_access_controls(tenant_id, security_config)

        # Compliance controls
        compliance_requirements = security_config.get('compliance', [])
        for requirement in compliance_requirements:
            await self._apply_compliance_controls(tenant_id, requirement)

    async def _setup_encryption(self, tenant_id: str, config: Dict[str, Any]):
        """Setup encryption for tenant data"""
        encryption_config = {
            'algorithm': config.get('encryption_algorithm', 'AES-256'),
            'key_rotation_days': config.get('key_rotation_days', 90),
            'encrypted_fields': config.get('encrypted_fields', [])
        }

        # Implementation would setup column-level encryption
        # or database-level encryption depending on requirements

    async def _setup_audit_logging(self, tenant_id: str):
        """Setup comprehensive audit logging"""

        # Create audit table for tenant
        audit_table_sql = f"""
            CREATE TABLE IF NOT EXISTS tenant_{tenant_id}_audit_log (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(100) NOT NULL,
                operation VARCHAR(10) NOT NULL,
                old_values JSONB,
                new_values JSONB,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT NOW(),
                ip_address INET,
                user_agent TEXT
            )
        """

        # Create audit triggers
        audit_trigger_function = f"""
            CREATE OR REPLACE FUNCTION tenant_{tenant_id}_audit_trigger()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO tenant_{tenant_id}_audit_log (
                    table_name, operation, old_values, new_values, user_id, timestamp
                ) VALUES (
                    TG_TABLE_NAME,
                    TG_OP,
                    CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
                    CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) ELSE NULL END,
                    COALESCE(current_setting('app.current_user_id', true)::INTEGER, 0),
                    NOW()
                );
                RETURN COALESCE(NEW, OLD);
            END;
            $$ LANGUAGE plpgsql;
        """

        # Apply to all tenant tables
        # Implementation would create triggers on all relevant tables

    async def _apply_compliance_controls(self, tenant_id: str, requirement: str):
        """Apply compliance-specific controls"""

        if requirement == 'GDPR':
            await self._apply_gdpr_controls(tenant_id)
        elif requirement == 'HIPAA':
            await self._apply_hipaa_controls(tenant_id)
        elif requirement == 'SOX':
            await self._apply_sox_controls(tenant_id)

    async def _apply_gdpr_controls(self, tenant_id: str):
        """Apply GDPR compliance controls"""
        # Right to be forgotten
        # Data portability
        # Consent management
        # Data retention policies
        pass

    async def get_tenant_audit_trail(self, tenant_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get audit trail for tenant"""
        # Implementation would query audit logs
        return []

class DataResidencyManager:
    """Manage data residency requirements"""

    def __init__(self):
        self.regional_databases = {}

    async def setup_regional_tenant(self, tenant_id: str, region: str, compliance_requirements: List[str]):
        """Setup tenant in specific geographic region"""

        # Select appropriate regional database
        regional_db_config = self.regional_databases.get(region)
        if not regional_db_config:
            raise ValueError(f"Region {region} not supported")

        # Create tenant in regional database
        regional_manager = DatabasePerTenantManager(regional_db_config['db_url'])
        await regional_manager.create_tenant_database(tenant_id, {
            'region': region,
            'compliance': compliance_requirements,
            'data_residency': True
        })

        return {
            'tenant_id': tenant_id,
            'region': region,
            'database_location': regional_db_config['location'],
            'compliance_met': compliance_requirements
        }
```

## Related Documentation

- [Complex Relationship Modeling](complex-relationship-modeling.md)
- [Performance Optimization](performance-optimization.md)
- [Production Migrations](production-migrations.md)
- [PostgreSQL Basic Setup](../postgresql/basic-setup.md)

## Best Practices Summary

1. **Model Selection**:
   - Choose tenancy model based on isolation, scale, and cost requirements
   - Consider compliance and regulatory requirements
   - Plan for future migration between models

2. **Security**:
   - Implement proper access controls and authentication
   - Use encryption for sensitive data
   - Maintain comprehensive audit logs
   - Regular security reviews and updates

3. **Performance**:
   - Optimize for your specific tenancy model
   - Monitor per-tenant performance metrics
   - Plan for tenant-specific scaling needs
   - Use appropriate indexing strategies

4. **Operations**:
   - Automate tenant provisioning and management
   - Implement proper backup and disaster recovery
   - Plan for tenant migration strategies
   - Monitor tenant health and resource usage

5. **Compliance**:
   - Understand regulatory requirements for your industry
   - Implement data residency controls where needed
   - Maintain audit trails for compliance reporting
   - Regular compliance assessments and updates