# Production Migrations

Comprehensive guide for safe database migrations in production environments with zero-downtime strategies, rollback procedures, and validation.

## Prerequisites

- [PostgreSQL Performance Optimization](performance-optimization.md)
- [Complex Relationship Modeling](complex-relationship-modeling.md)
- Understanding of database locking and transactions

## Migration Strategy Overview

### Zero-Downtime Migration Principles

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

class MigrationType(Enum):
    SCHEMA_CHANGE = "schema_change"
    DATA_MIGRATION = "data_migration"
    INDEX_CREATION = "index_creation"
    CONSTRAINT_ADDITION = "constraint_addition"
    ROLLBACK = "rollback"

class MigrationRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MigrationStep:
    id: str
    description: str
    sql_up: str
    sql_down: str
    migration_type: MigrationType
    risk_level: MigrationRisk
    estimated_duration: int  # seconds
    requires_downtime: bool = False
    validation_query: Optional[str] = None
    rollback_validation: Optional[str] = None

@dataclass
class MigrationPlan:
    version: str
    description: str
    steps: List[MigrationStep]
    total_estimated_duration: int
    requires_maintenance_window: bool
    rollback_strategy: str
    validation_checklist: List[str]

class ProductionMigrationRunner:
    """Safe migration execution for production"""

    def __init__(self, db_session, dry_run: bool = False):
        self.session = db_session
        self.dry_run = dry_run
        self.migration_log = []

    async def execute_migration_plan(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Execute migration plan with safety checks"""

        # Pre-migration validation
        await self._pre_migration_checks(plan)

        # Execute steps
        results = []
        for step in plan.steps:
            try:
                result = await self._execute_step(step)
                results.append(result)

                # Stop on first failure for critical operations
                if not result['success'] and step.risk_level == MigrationRisk.CRITICAL:
                    await self._emergency_rollback(results)
                    break

            except Exception as e:
                self._log_error(f"Step {step.id} failed: {str(e)}")
                await self._emergency_rollback(results)
                raise

        return {
            'migration_version': plan.version,
            'completed_steps': len([r for r in results if r['success']]),
            'total_steps': len(plan.steps),
            'duration': sum(r['duration'] for r in results),
            'success': all(r['success'] for r in results)
        }

    async def _pre_migration_checks(self, plan: MigrationPlan):
        """Perform pre-migration safety checks"""

        # Check database connectivity
        await self._check_database_health()

        # Verify backup completion
        await self._verify_recent_backup()

        # Check replication lag
        await self._check_replication_lag()

        # Validate migration scripts
        await self._validate_migration_syntax(plan)

        # Check disk space
        await self._check_disk_space()

    async def _execute_step(self, step: MigrationStep) -> Dict[str, Any]:
        """Execute individual migration step"""
        start_time = datetime.utcnow()

        self._log_info(f"Executing step {step.id}: {step.description}")

        try:
            if self.dry_run:
                self._log_info(f"DRY RUN - Would execute: {step.sql_up}")
                success = True
            else:
                # Execute the migration
                await self._execute_sql_with_timeout(step.sql_up, timeout=step.estimated_duration * 2)

                # Validate if validation query provided
                if step.validation_query:
                    validation_result = await self._validate_step(step.validation_query)
                    success = validation_result
                else:
                    success = True

            duration = (datetime.utcnow() - start_time).total_seconds()

            return {
                'step_id': step.id,
                'success': success,
                'duration': duration,
                'description': step.description
            }

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_error(f"Step {step.id} failed after {duration}s: {str(e)}")

            return {
                'step_id': step.id,
                'success': False,
                'duration': duration,
                'error': str(e)
            }

    async def _execute_sql_with_timeout(self, sql: str, timeout: int):
        """Execute SQL with timeout protection"""
        from sqlalchemy import text

        try:
            # Set statement timeout
            await self.session.execute(text(f"SET statement_timeout = '{timeout}s'"))

            # Execute the migration SQL
            await self.session.execute(text(sql))
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            # Reset timeout
            await self.session.execute(text("SET statement_timeout = 0"))

    def _log_info(self, message: str):
        """Log info message"""
        log_entry = {
            'timestamp': datetime.utcnow(),
            'level': 'INFO',
            'message': message
        }
        self.migration_log.append(log_entry)
        print(f"[INFO] {message}")

    def _log_error(self, message: str):
        """Log error message"""
        log_entry = {
            'timestamp': datetime.utcnow(),
            'level': 'ERROR',
            'message': message
        }
        self.migration_log.append(log_entry)
        print(f"[ERROR] {message}")
```

## Common Migration Patterns

### Safe Schema Changes

```python
class SafeSchemaChanges:
    """Patterns for safe schema modifications"""

    @staticmethod
    def add_nullable_column() -> MigrationStep:
        """Add nullable column (safe operation)"""
        return MigrationStep(
            id="add_nullable_column",
            description="Add nullable email_verified column to users table",
            sql_up="""
                ALTER TABLE users
                ADD COLUMN email_verified BOOLEAN DEFAULT NULL;
            """,
            sql_down="""
                ALTER TABLE users
                DROP COLUMN email_verified;
            """,
            migration_type=MigrationType.SCHEMA_CHANGE,
            risk_level=MigrationRisk.LOW,
            estimated_duration=5,
            requires_downtime=False,
            validation_query="""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'email_verified'
            """
        )

    @staticmethod
    def add_column_with_default() -> List[MigrationStep]:
        """Add column with default value (multi-step for large tables)"""
        return [
            MigrationStep(
                id="add_column_nullable",
                description="Add status column as nullable first",
                sql_up="ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT NULL;",
                sql_down="ALTER TABLE orders DROP COLUMN status;",
                migration_type=MigrationType.SCHEMA_CHANGE,
                risk_level=MigrationRisk.LOW,
                estimated_duration=10
            ),
            MigrationStep(
                id="backfill_status_column",
                description="Backfill status column with default values",
                sql_up="""
                    UPDATE orders
                    SET status = 'pending'
                    WHERE status IS NULL;
                """,
                sql_down="-- No rollback needed for data",
                migration_type=MigrationType.DATA_MIGRATION,
                risk_level=MigrationRisk.MEDIUM,
                estimated_duration=300,  # 5 minutes for large table
                validation_query="SELECT COUNT(*) FROM orders WHERE status IS NULL"
            ),
            MigrationStep(
                id="add_not_null_constraint",
                description="Add NOT NULL constraint to status column",
                sql_up="ALTER TABLE orders ALTER COLUMN status SET NOT NULL;",
                sql_down="ALTER TABLE orders ALTER COLUMN status DROP NOT NULL;",
                migration_type=MigrationType.CONSTRAINT_ADDITION,
                risk_level=MigrationRisk.MEDIUM,
                estimated_duration=30
            ),
            MigrationStep(
                id="set_default_value",
                description="Set default value for future records",
                sql_up="ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending';",
                sql_down="ALTER TABLE orders ALTER COLUMN status DROP DEFAULT;",
                migration_type=MigrationType.SCHEMA_CHANGE,
                risk_level=MigrationRisk.LOW,
                estimated_duration=5
            )
        ]

    @staticmethod
    def rename_column() -> List[MigrationStep]:
        """Rename column safely using dual-write approach"""
        return [
            MigrationStep(
                id="add_new_column",
                description="Add new column with correct name",
                sql_up="ALTER TABLE users ADD COLUMN username VARCHAR(100);",
                sql_down="ALTER TABLE users DROP COLUMN username;",
                migration_type=MigrationType.SCHEMA_CHANGE,
                risk_level=MigrationRisk.LOW,
                estimated_duration=10
            ),
            MigrationStep(
                id="copy_data_to_new_column",
                description="Copy data from old column to new column",
                sql_up="UPDATE users SET username = user_name WHERE username IS NULL;",
                sql_down="-- Data rollback handled by dropping column",
                migration_type=MigrationType.DATA_MIGRATION,
                risk_level=MigrationRisk.MEDIUM,
                estimated_duration=120
            ),
            MigrationStep(
                id="add_triggers_for_dual_write",
                description="Add triggers to keep columns in sync",
                sql_up="""
                    CREATE OR REPLACE FUNCTION sync_username()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                            NEW.username = NEW.user_name;
                            NEW.user_name = NEW.username;
                            RETURN NEW;
                        END IF;
                        RETURN NULL;
                    END;
                    $$ LANGUAGE plpgsql;

                    CREATE TRIGGER sync_username_trigger
                        BEFORE INSERT OR UPDATE ON users
                        FOR EACH ROW EXECUTE FUNCTION sync_username();
                """,
                sql_down="""
                    DROP TRIGGER IF EXISTS sync_username_trigger ON users;
                    DROP FUNCTION IF EXISTS sync_username();
                """,
                migration_type=MigrationType.SCHEMA_CHANGE,
                risk_level=MigrationRisk.MEDIUM,
                estimated_duration=10
            )
            # Note: Later migration would remove old column and triggers
        ]

    @staticmethod
    def create_index_concurrently() -> MigrationStep:
        """Create index without blocking writes"""
        return MigrationStep(
            id="create_index_concurrent",
            description="Create index on users.email concurrently",
            sql_up="CREATE INDEX CONCURRENTLY idx_users_email ON users(email);",
            sql_down="DROP INDEX IF EXISTS idx_users_email;",
            migration_type=MigrationType.INDEX_CREATION,
            risk_level=MigrationRisk.MEDIUM,
            estimated_duration=600,  # 10 minutes for large table
            requires_downtime=False,
            validation_query="""
                SELECT COUNT(*) FROM pg_indexes
                WHERE tablename = 'users' AND indexname = 'idx_users_email'
            """
        )
```

### Data Migrations

```python
class DataMigrationPatterns:
    """Safe patterns for data migrations"""

    @staticmethod
    def batch_data_migration() -> MigrationStep:
        """Migrate data in batches to avoid long locks"""
        return MigrationStep(
            id="batch_migrate_user_preferences",
            description="Migrate user preferences to JSONB format in batches",
            sql_up="""
                DO $$
                DECLARE
                    batch_size INTEGER := 1000;
                    total_processed INTEGER := 0;
                    batch_count INTEGER;
                BEGIN
                    LOOP
                        -- Process batch
                        UPDATE users
                        SET preferences_json = jsonb_build_object(
                            'theme', COALESCE(theme_preference, 'light'),
                            'language', COALESCE(language_preference, 'en'),
                            'notifications', COALESCE(email_notifications, true)
                        )
                        WHERE id IN (
                            SELECT id FROM users
                            WHERE preferences_json IS NULL
                            ORDER BY id
                            LIMIT batch_size
                        );

                        GET DIAGNOSTICS batch_count = ROW_COUNT;
                        total_processed := total_processed + batch_count;

                        -- Log progress
                        RAISE NOTICE 'Processed % users total', total_processed;

                        -- Exit if no more rows to process
                        EXIT WHEN batch_count = 0;

                        -- Small delay between batches
                        PERFORM pg_sleep(0.1);
                    END LOOP;

                    RAISE NOTICE 'Migration completed. Total users processed: %', total_processed;
                END $$;
            """,
            sql_down="""
                UPDATE users SET preferences_json = NULL
                WHERE preferences_json IS NOT NULL;
            """,
            migration_type=MigrationType.DATA_MIGRATION,
            risk_level=MigrationRisk.MEDIUM,
            estimated_duration=1800,  # 30 minutes
            validation_query="""
                SELECT COUNT(*) FROM users WHERE preferences_json IS NULL
            """
        )

    @staticmethod
    def conditional_data_update() -> MigrationStep:
        """Update data conditionally with validation"""
        return MigrationStep(
            id="normalize_email_addresses",
            description="Normalize email addresses to lowercase",
            sql_up="""
                UPDATE users
                SET email = LOWER(TRIM(email))
                WHERE email != LOWER(TRIM(email))
                AND email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
            """,
            sql_down="""
                -- Cannot reliably rollback email normalization
                -- Original case information is lost
            """,
            migration_type=MigrationType.DATA_MIGRATION,
            risk_level=MigrationRisk.HIGH,
            estimated_duration=300,
            validation_query="""
                SELECT COUNT(*) FROM users
                WHERE email != LOWER(TRIM(email))
            """
        )

class LargeTableMigration:
    """Strategies for migrating large tables"""

    @staticmethod
    def partition_table_migration() -> List[MigrationStep]:
        """Convert table to partitioned table"""
        return [
            MigrationStep(
                id="create_partitioned_table",
                description="Create new partitioned orders table",
                sql_up="""
                    CREATE TABLE orders_partitioned (
                        LIKE orders INCLUDING ALL
                    ) PARTITION BY RANGE (created_at);

                    -- Create partitions for current and future months
                    CREATE TABLE orders_2023_01 PARTITION OF orders_partitioned
                        FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
                    CREATE TABLE orders_2023_02 PARTITION OF orders_partitioned
                        FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');
                    -- Add more partitions as needed
                """,
                sql_down="DROP TABLE IF EXISTS orders_partitioned CASCADE;",
                migration_type=MigrationType.SCHEMA_CHANGE,
                risk_level=MigrationRisk.MEDIUM,
                estimated_duration=60
            ),
            MigrationStep(
                id="migrate_data_to_partitioned",
                description="Migrate data to partitioned table in chunks",
                sql_up="""
                    DO $$
                    DECLARE
                        start_date DATE := '2023-01-01';
                        end_date DATE := '2023-01-02';
                        chunk_size INTEGER := 10000;
                    BEGIN
                        WHILE start_date < CURRENT_DATE LOOP
                            INSERT INTO orders_partitioned
                            SELECT * FROM orders
                            WHERE created_at >= start_date
                            AND created_at < end_date
                            ORDER BY id
                            LIMIT chunk_size;

                            start_date := start_date + INTERVAL '1 day';
                            end_date := end_date + INTERVAL '1 day';

                            -- Progress tracking
                            RAISE NOTICE 'Migrated data for %', start_date - INTERVAL '1 day';

                            -- Prevent overwhelming the system
                            PERFORM pg_sleep(1);
                        END LOOP;
                    END $$;
                """,
                sql_down="TRUNCATE orders_partitioned;",
                migration_type=MigrationType.DATA_MIGRATION,
                risk_level=MigrationRisk.HIGH,
                estimated_duration=7200  # 2 hours
            )
        ]
```

## Rollback Strategies

### Automated Rollback System

```python
class MigrationRollback:
    """Automated rollback capabilities"""

    def __init__(self, db_session):
        self.session = db_session

    async def create_rollback_plan(self, executed_steps: List[Dict]) -> List[MigrationStep]:
        """Create rollback plan from executed steps"""
        rollback_steps = []

        # Reverse the order of executed steps
        for step_result in reversed(executed_steps):
            if step_result['success']:
                # Find original step and create rollback
                rollback_step = MigrationStep(
                    id=f"rollback_{step_result['step_id']}",
                    description=f"Rollback: {step_result['description']}",
                    sql_up=step_result.get('sql_down', '-- No rollback defined'),
                    sql_down=step_result.get('sql_up', '-- Original operation'),
                    migration_type=MigrationType.ROLLBACK,
                    risk_level=MigrationRisk.HIGH,
                    estimated_duration=step_result['duration']
                )
                rollback_steps.append(rollback_step)

        return rollback_steps

    async def validate_rollback_safety(self, rollback_steps: List[MigrationStep]) -> Dict[str, Any]:
        """Validate that rollback is safe to execute"""
        safety_checks = {
            'data_loss_risk': False,
            'dependency_issues': [],
            'validation_failures': [],
            'safe_to_rollback': True
        }

        for step in rollback_steps:
            # Check for potential data loss
            if 'DROP COLUMN' in step.sql_up.upper():
                safety_checks['data_loss_risk'] = True
                safety_checks['safe_to_rollback'] = False

            # Check for dependency issues
            if 'DROP TABLE' in step.sql_up.upper():
                table_name = self._extract_table_name(step.sql_up)
                dependencies = await self._check_table_dependencies(table_name)
                if dependencies:
                    safety_checks['dependency_issues'].append({
                        'table': table_name,
                        'dependencies': dependencies
                    })

        return safety_checks

    async def _check_table_dependencies(self, table_name: str) -> List[str]:
        """Check for foreign key dependencies"""
        from sqlalchemy import text

        result = await self.session.execute(text("""
            SELECT
                tc.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = :table_name
        """), {'table_name': table_name})

        return [f"{row.table_name}.{row.column_name}" for row in result]

class BackupIntegration:
    """Integration with backup systems for safe migrations"""

    def __init__(self, db_session):
        self.session = db_session

    async def create_pre_migration_backup(self, migration_version: str) -> str:
        """Create backup before migration"""
        backup_name = f"pre_migration_{migration_version}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # This would integrate with your backup system
        # Example using pg_dump
        backup_command = f"""
            pg_dump --verbose --format=custom --no-owner --no-privileges
            --file=/backups/{backup_name}.dump
            {self._get_database_url()}
        """

        # Execute backup (implementation depends on your environment)
        # await self._execute_backup_command(backup_command)

        return backup_name

    async def verify_backup_integrity(self, backup_name: str) -> bool:
        """Verify backup integrity"""
        # Implementation would verify backup file
        # and optionally test restore to staging environment
        return True

    async def restore_from_backup(self, backup_name: str, target_db: str = None) -> bool:
        """Restore database from backup"""
        restore_command = f"""
            pg_restore --verbose --clean --no-owner --no-privileges
            --dbname={target_db or self._get_database_url()}
            /backups/{backup_name}.dump
        """

        # Execute restore (implementation depends on your environment)
        # return await self._execute_restore_command(restore_command)
        return True
```

## Migration Testing and Validation

### Migration Testing Framework

```python
class MigrationTester:
    """Framework for testing migrations"""

    def __init__(self, test_db_session):
        self.session = test_db_session

    async def test_migration_plan(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Test complete migration plan"""
        test_results = {
            'plan_version': plan.version,
            'test_passed': True,
            'step_results': [],
            'performance_metrics': {},
            'validation_results': []
        }

        # Create test data
        await self._create_test_data()

        try:
            # Test forward migration
            runner = ProductionMigrationRunner(self.session, dry_run=False)
            migration_result = await runner.execute_migration_plan(plan)

            test_results['step_results'] = migration_result

            # Validate data integrity
            integrity_check = await self._validate_data_integrity()
            test_results['validation_results'].append(integrity_check)

            # Test rollback
            if migration_result['success']:
                rollback_tester = MigrationRollback(self.session)
                rollback_steps = await rollback_tester.create_rollback_plan(
                    migration_result.get('completed_steps', [])
                )

                # Execute rollback
                rollback_plan = MigrationPlan(
                    version=f"{plan.version}_rollback",
                    description=f"Rollback for {plan.version}",
                    steps=rollback_steps,
                    total_estimated_duration=sum(s.estimated_duration for s in rollback_steps),
                    requires_maintenance_window=False,
                    rollback_strategy="automated",
                    validation_checklist=[]
                )

                rollback_result = await runner.execute_migration_plan(rollback_plan)
                test_results['rollback_results'] = rollback_result

        except Exception as e:
            test_results['test_passed'] = False
            test_results['error'] = str(e)

        return test_results

    async def _create_test_data(self):
        """Create realistic test data"""
        # Implementation would create representative test data
        # that exercises the migration paths
        pass

    async def _validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity after migration"""
        from sqlalchemy import text

        checks = {
            'foreign_key_violations': 0,
            'null_constraint_violations': 0,
            'unique_constraint_violations': 0,
            'data_consistency_issues': []
        }

        # Check foreign key constraints
        fk_violations = await self.session.execute(text("""
            SELECT conname, conrelid::regclass, confrelid::regclass
            FROM pg_constraint
            WHERE contype = 'f'
            AND NOT EXISTS (
                SELECT 1 FROM pg_trigger
                WHERE tgconstraint = pg_constraint.oid
                AND tgenabled = 'O'
            )
        """))

        checks['foreign_key_violations'] = len(list(fk_violations))

        return checks

class PerformanceImpactAnalyzer:
    """Analyze performance impact of migrations"""

    def __init__(self, db_session):
        self.session = db_session

    async def analyze_migration_impact(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Analyze potential performance impact"""
        impact_analysis = {
            'estimated_duration': plan.total_estimated_duration,
            'lock_impact': [],
            'index_impact': [],
            'storage_impact': 0,
            'read_performance_impact': 'none',
            'write_performance_impact': 'none'
        }

        for step in plan.steps:
            # Analyze locking impact
            if 'ALTER TABLE' in step.sql_up.upper():
                impact_analysis['lock_impact'].append({
                    'step': step.id,
                    'lock_type': 'ACCESS EXCLUSIVE',
                    'duration': step.estimated_duration,
                    'affected_table': self._extract_table_name(step.sql_up)
                })

            # Analyze index impact
            if 'CREATE INDEX' in step.sql_up.upper():
                if 'CONCURRENTLY' not in step.sql_up.upper():
                    impact_analysis['write_performance_impact'] = 'high'
                else:
                    impact_analysis['write_performance_impact'] = 'low'

        return impact_analysis

    def _extract_table_name(self, sql: str) -> str:
        """Extract table name from SQL statement"""
        # Simple regex to extract table name
        import re
        match = re.search(r'(?:ALTER|DROP|CREATE)\s+TABLE\s+(\w+)', sql, re.IGNORECASE)
        return match.group(1) if match else 'unknown'
```

## Production Deployment Workflow

### Automated Deployment Pipeline

```python
class MigrationDeploymentPipeline:
    """Production deployment pipeline for migrations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.environments = ['staging', 'production']

    async def deploy_migration(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Deploy migration through all environments"""
        deployment_results = {}

        for env in self.environments:
            env_result = await self._deploy_to_environment(plan, env)
            deployment_results[env] = env_result

            # Stop deployment if staging fails
            if env == 'staging' and not env_result['success']:
                break

        return deployment_results

    async def _deploy_to_environment(self, plan: MigrationPlan, environment: str) -> Dict[str, Any]:
        """Deploy to specific environment"""
        env_config = self.config[environment]

        # Create database session for environment
        db_session = self._create_db_session(env_config)

        # Pre-deployment checks
        pre_checks = await self._pre_deployment_checks(db_session, plan)
        if not pre_checks['passed']:
            return {
                'environment': environment,
                'success': False,
                'stage': 'pre_checks',
                'issues': pre_checks['issues']
            }

        # Create backup if production
        backup_name = None
        if environment == 'production':
            backup_integration = BackupIntegration(db_session)
            backup_name = await backup_integration.create_pre_migration_backup(plan.version)

        try:
            # Execute migration
            runner = ProductionMigrationRunner(db_session)
            result = await runner.execute_migration_plan(plan)

            # Post-deployment validation
            validation_result = await self._post_deployment_validation(db_session, plan)

            return {
                'environment': environment,
                'success': result['success'] and validation_result['passed'],
                'migration_result': result,
                'validation_result': validation_result,
                'backup_name': backup_name
            }

        except Exception as e:
            # Automatic rollback on production failure
            if environment == 'production' and backup_name:
                await self._emergency_restore(db_session, backup_name)

            return {
                'environment': environment,
                'success': False,
                'error': str(e),
                'backup_restored': backup_name is not None
            }

    async def _pre_deployment_checks(self, session, plan: MigrationPlan) -> Dict[str, Any]:
        """Pre-deployment safety checks"""
        checks = {
            'passed': True,
            'issues': []
        }

        # Check replication lag
        replication_lag = await self._check_replication_lag(session)
        if replication_lag > 30:  # 30 seconds threshold
            checks['passed'] = False
            checks['issues'].append(f"High replication lag: {replication_lag}s")

        # Check active connections
        active_connections = await self._get_active_connections(session)
        if active_connections > 100:  # Connection threshold
            checks['passed'] = False
            checks['issues'].append(f"Too many active connections: {active_connections}")

        # Validate migration syntax
        syntax_check = await self._validate_migration_syntax(session, plan)
        if not syntax_check['valid']:
            checks['passed'] = False
            checks['issues'].extend(syntax_check['errors'])

        return checks

    async def _post_deployment_validation(self, session, plan: MigrationPlan) -> Dict[str, Any]:
        """Post-deployment validation"""
        validation = {
            'passed': True,
            'checks': []
        }

        # Run validation queries from migration steps
        for step in plan.steps:
            if step.validation_query:
                try:
                    result = await session.execute(text(step.validation_query))
                    validation['checks'].append({
                        'step': step.id,
                        'passed': True,
                        'result': result.scalar()
                    })
                except Exception as e:
                    validation['passed'] = False
                    validation['checks'].append({
                        'step': step.id,
                        'passed': False,
                        'error': str(e)
                    })

        return validation
```

## Related Documentation

- [Performance Optimization](performance-optimization.md)
- [Complex Relationship Modeling](complex-relationship-modeling.md)
- [Multi-tenant Patterns](multi-tenant-patterns.md)
- [PostgreSQL Basic Setup](../postgresql/basic-setup.md)

## Best Practices Summary

1. **Safety First**:
   - Always create backups before production migrations
   - Test migrations thoroughly in staging environment
   - Use concurrent operations where possible
   - Implement proper rollback strategies

2. **Zero-Downtime Strategies**:
   - Add columns as nullable first, then populate and add constraints
   - Use dual-write patterns for column renames
   - Create indexes concurrently
   - Migrate data in batches

3. **Risk Management**:
   - Classify migrations by risk level
   - Have emergency rollback procedures
   - Monitor performance impact
   - Validate data integrity

4. **Automation**:
   - Use automated deployment pipelines
   - Implement comprehensive testing
   - Include performance impact analysis
   - Maintain detailed migration logs

5. **Monitoring**:
   - Track migration progress and performance
   - Monitor replication lag during migrations
   - Set up alerts for migration failures
   - Validate post-migration system health