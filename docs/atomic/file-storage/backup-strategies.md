# Backup Strategies

Comprehensive guide for implementing file backup strategies with automated scheduling, versioning, disaster recovery, and cross-region replication.

## Backup Architecture

```python
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
import hashlib
import uuid
from pathlib import Path

class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RestoreStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BackupPolicy:
    name: str
    backup_type: BackupType
    schedule_cron: str  # Cron expression for scheduling
    retention_days: int
    source_paths: List[str] = field(default_factory=list)
    destination_config: Dict[str, Any] = field(default_factory=dict)
    compression_enabled: bool = True
    encryption_enabled: bool = True
    verify_integrity: bool = True
    max_concurrent_files: int = 10
    exclude_patterns: List[str] = field(default_factory=list)

@dataclass
class BackupJob:
    id: str
    policy_name: str
    backup_type: BackupType
    status: BackupStatus = BackupStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_files: int = 0
    processed_files: int = 0
    total_size: int = 0
    compressed_size: int = 0
    error_message: Optional[str] = None
    manifest_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RestoreJob:
    id: str
    backup_job_id: str
    restore_type: str  # "full", "selective", "point_in_time"
    status: RestoreStatus = RestoreStatus.PENDING
    target_path: str = ""
    file_filters: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    restored_files: int = 0
    error_message: Optional[str] = None

class BackupService:
    """Core backup service with scheduling and retention management"""

    def __init__(self, storage_backends: Dict[str, Any], temp_dir: str = "/tmp/backups"):
        self.storage_backends = storage_backends
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.active_jobs: Dict[str, BackupJob] = {}
        self.policies: Dict[str, BackupPolicy] = {}

    async def create_backup_policy(self, policy: BackupPolicy) -> str:
        """Create and register a backup policy"""
        self.policies[policy.name] = policy
        return policy.name

    async def execute_backup(self, policy_name: str, force_full: bool = False) -> BackupJob:
        """Execute backup according to policy"""
        if policy_name not in self.policies:
            raise ValueError(f"Policy {policy_name} not found")

        policy = self.policies[policy_name]

        # Determine backup type
        backup_type = BackupType.FULL if force_full else policy.backup_type

        # Create backup job
        job = BackupJob(
            id=str(uuid.uuid4()),
            policy_name=policy_name,
            backup_type=backup_type
        )

        self.active_jobs[job.id] = job

        # Start backup asynchronously
        asyncio.create_task(self._execute_backup_job(job, policy))

        return job

    async def _execute_backup_job(self, job: BackupJob, policy: BackupPolicy):
        """Execute the actual backup job"""
        try:
            job.status = BackupStatus.RUNNING
            job.started_at = datetime.utcnow()

            # Collect files to backup
            files_to_backup = await self._collect_files(policy, job)

            # Create backup manifest
            manifest = await self._create_backup_manifest(job, files_to_backup, policy)

            # Perform backup based on type
            if job.backup_type == BackupType.FULL:
                await self._perform_full_backup(job, files_to_backup, policy)
            elif job.backup_type == BackupType.INCREMENTAL:
                await self._perform_incremental_backup(job, files_to_backup, policy)
            elif job.backup_type == BackupType.DIFFERENTIAL:
                await self._perform_differential_backup(job, files_to_backup, policy)

            # Upload manifest
            job.manifest_path = await self._upload_manifest(manifest, job, policy)

            # Verify backup integrity if enabled
            if policy.verify_integrity:
                await self._verify_backup_integrity(job, policy)

            # Clean up old backups according to retention policy
            await self._cleanup_old_backups(policy)

            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.utcnow()

        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

    async def _collect_files(self, policy: BackupPolicy, job: BackupJob) -> List[Dict[str, Any]]:
        """Collect files to backup based on policy"""
        files_to_backup = []

        for source_path in policy.source_paths:
            source = Path(source_path)

            if source.is_file():
                file_info = await self._get_file_info(source)
                if self._should_include_file(file_info, policy):
                    files_to_backup.append(file_info)
            elif source.is_dir():
                async for file_info in self._scan_directory(source, policy):
                    if self._should_include_file(file_info, policy):
                        files_to_backup.append(file_info)

        job.total_files = len(files_to_backup)
        job.total_size = sum(f["size"] for f in files_to_backup)

        return files_to_backup

    async def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information for backup"""
        stat = file_path.stat()

        # Calculate file hash for integrity checking
        hash_obj = hashlib.sha256()
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                hash_obj.update(chunk)

        return {
            "path": str(file_path),
            "relative_path": str(file_path.relative_to(file_path.parent.parent)),
            "size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "permissions": oct(stat.st_mode),
            "file_hash": hash_obj.hexdigest()
        }

    async def _scan_directory(self, directory: Path, policy: BackupPolicy) -> List[Dict[str, Any]]:
        """Recursively scan directory for files"""
        for item in directory.rglob("*"):
            if item.is_file():
                file_info = await self._get_file_info(item)
                yield file_info

    def _should_include_file(self, file_info: Dict[str, Any], policy: BackupPolicy) -> bool:
        """Check if file should be included in backup"""
        file_path = file_info["path"]

        # Check exclude patterns
        for pattern in policy.exclude_patterns:
            if Path(file_path).match(pattern):
                return False

        # Additional filters can be added here
        return True

    async def _create_backup_manifest(
        self,
        job: BackupJob,
        files: List[Dict[str, Any]],
        policy: BackupPolicy
    ) -> Dict[str, Any]:
        """Create backup manifest with metadata"""
        manifest = {
            "backup_id": job.id,
            "policy_name": policy.name,
            "backup_type": job.backup_type.value,
            "created_at": job.started_at.isoformat(),
            "total_files": len(files),
            "total_size": sum(f["size"] for f in files),
            "compression_enabled": policy.compression_enabled,
            "encryption_enabled": policy.encryption_enabled,
            "files": files,
            "schema_version": "1.0"
        }

        return manifest

    async def _perform_full_backup(
        self,
        job: BackupJob,
        files: List[Dict[str, Any]],
        policy: BackupPolicy
    ):
        """Perform full backup of all files"""
        semaphore = asyncio.Semaphore(policy.max_concurrent_files)

        async def backup_file(file_info: Dict[str, Any]):
            async with semaphore:
                await self._backup_single_file(file_info, job, policy)
                job.processed_files += 1

        # Process all files concurrently
        tasks = [backup_file(file_info) for file_info in files]
        await asyncio.gather(*tasks)

    async def _perform_incremental_backup(
        self,
        job: BackupJob,
        files: List[Dict[str, Any]],
        policy: BackupPolicy
    ):
        """Perform incremental backup (only changed files since last backup)"""
        # Get last backup manifest
        last_manifest = await self._get_last_backup_manifest(policy.name)

        if not last_manifest:
            # No previous backup, perform full backup
            await self._perform_full_backup(job, files, policy)
            return

        # Create hash map of previous files
        previous_files = {f["path"]: f["file_hash"] for f in last_manifest.get("files", [])}

        # Filter files that have changed
        changed_files = []
        for file_info in files:
            path = file_info["path"]
            current_hash = file_info["file_hash"]

            if path not in previous_files or previous_files[path] != current_hash:
                changed_files.append(file_info)

        job.total_files = len(changed_files)
        job.total_size = sum(f["size"] for f in changed_files)

        # Backup only changed files
        semaphore = asyncio.Semaphore(policy.max_concurrent_files)

        async def backup_file(file_info: Dict[str, Any]):
            async with semaphore:
                await self._backup_single_file(file_info, job, policy)
                job.processed_files += 1

        tasks = [backup_file(file_info) for file_info in changed_files]
        await asyncio.gather(*tasks)

    async def _backup_single_file(
        self,
        file_info: Dict[str, Any],
        job: BackupJob,
        policy: BackupPolicy
    ):
        """Backup a single file with compression and encryption"""
        source_path = Path(file_info["path"])

        # Read file data
        async with aiofiles.open(source_path, "rb") as f:
            file_data = await f.read()

        # Compress if enabled
        if policy.compression_enabled:
            file_data = await self._compress_data(file_data)

        # Encrypt if enabled
        if policy.encryption_enabled:
            file_data = await self._encrypt_data(file_data, job.id)

        # Generate backup storage path
        backup_path = self._generate_backup_path(file_info, job, policy)

        # Upload to storage backend
        storage_backend = self.storage_backends[policy.destination_config["provider"]]
        await storage_backend.upload_file(file_data, backup_path)

        # Update job metadata
        if "files_backed_up" not in job.metadata:
            job.metadata["files_backed_up"] = []

        job.metadata["files_backed_up"].append({
            "original_path": file_info["path"],
            "backup_path": backup_path,
            "original_size": file_info["size"],
            "backup_size": len(file_data)
        })

        job.compressed_size += len(file_data)

    async def _compress_data(self, data: bytes) -> bytes:
        """Compress data using gzip"""
        import gzip

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, gzip.compress, data)

    async def _encrypt_data(self, data: bytes, backup_id: str) -> bytes:
        """Encrypt data using AES"""
        from cryptography.fernet import Fernet
        import base64

        # In production, use proper key management
        key = base64.urlsafe_b64encode(backup_id.encode()[:32].ljust(32, b'0'))
        fernet = Fernet(key)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fernet.encrypt, data)

    def _generate_backup_path(
        self,
        file_info: Dict[str, Any],
        job: BackupJob,
        policy: BackupPolicy
    ) -> str:
        """Generate storage path for backup file"""
        relative_path = file_info["relative_path"]
        timestamp = job.started_at.strftime("%Y%m%d_%H%M%S")

        return f"backups/{policy.name}/{job.backup_type.value}/{timestamp}/{job.id}/{relative_path}"

    async def _upload_manifest(
        self,
        manifest: Dict[str, Any],
        job: BackupJob,
        policy: BackupPolicy
    ) -> str:
        """Upload backup manifest to storage"""
        manifest_data = json.dumps(manifest, indent=2, default=str).encode()

        # Compress manifest
        if policy.compression_enabled:
            manifest_data = await self._compress_data(manifest_data)

        # Generate manifest path
        timestamp = job.started_at.strftime("%Y%m%d_%H%M%S")
        manifest_path = f"backups/{policy.name}/manifests/{timestamp}_{job.id}.json"

        # Upload manifest
        storage_backend = self.storage_backends[policy.destination_config["provider"]]
        await storage_backend.upload_file(manifest_data, manifest_path)

        return manifest_path

    async def _verify_backup_integrity(self, job: BackupJob, policy: BackupPolicy):
        """Verify backup integrity by sampling files"""
        if "files_backed_up" not in job.metadata:
            return

        # Sample 10% of files for verification
        files_to_verify = job.metadata["files_backed_up"][:max(1, len(job.metadata["files_backed_up"]) // 10)]

        storage_backend = self.storage_backends[policy.destination_config["provider"]]

        for file_info in files_to_verify:
            try:
                # Download backup file
                backup_data = await storage_backend.download_file(file_info["backup_path"])

                # Decrypt if needed
                if policy.encryption_enabled:
                    backup_data = await self._decrypt_data(backup_data, job.id)

                # Decompress if needed
                if policy.compression_enabled:
                    backup_data = await self._decompress_data(backup_data)

                # Verify hash
                backup_hash = hashlib.sha256(backup_data).hexdigest()
                original_path = Path(file_info["original_path"])

                if original_path.exists():
                    original_hash = await self._calculate_file_hash(original_path)
                    if backup_hash != original_hash:
                        raise ValueError(f"Hash mismatch for {original_path}")

            except Exception as e:
                job.metadata.setdefault("verification_errors", []).append({
                    "file": file_info["original_path"],
                    "error": str(e)
                })

    async def _cleanup_old_backups(self, policy: BackupPolicy):
        """Clean up old backups according to retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_days)

        storage_backend = self.storage_backends[policy.destination_config["provider"]]

        # List backup manifests
        manifest_prefix = f"backups/{policy.name}/manifests/"
        manifests = await storage_backend.list_files(manifest_prefix)

        for manifest_file in manifests:
            if manifest_file.last_modified < cutoff_date:
                # Download and parse manifest to get file list
                manifest_data = await storage_backend.download_file(manifest_file.path)

                if policy.compression_enabled:
                    manifest_data = await self._decompress_data(manifest_data)

                manifest = json.loads(manifest_data.decode())

                # Delete backup files
                for file_info in manifest.get("files", []):
                    if "backup_path" in file_info:
                        await storage_backend.delete_file(file_info["backup_path"])

                # Delete manifest
                await storage_backend.delete_file(manifest_file.path)

    async def restore_backup(
        self,
        backup_job_id: str,
        target_path: str,
        file_filters: List[str] = None
    ) -> RestoreJob:
        """Restore files from backup"""
        restore_job = RestoreJob(
            id=str(uuid.uuid4()),
            backup_job_id=backup_job_id,
            restore_type="selective" if file_filters else "full",
            target_path=target_path,
            file_filters=file_filters or []
        )

        # Start restore asynchronously
        asyncio.create_task(self._execute_restore_job(restore_job))

        return restore_job

    async def _execute_restore_job(self, restore_job: RestoreJob):
        """Execute restore job"""
        try:
            restore_job.status = RestoreStatus.RUNNING
            restore_job.started_at = datetime.utcnow()

            # Find backup manifest
            manifest = await self._find_backup_manifest(restore_job.backup_job_id)
            if not manifest:
                raise ValueError(f"Backup manifest not found for job {restore_job.backup_job_id}")

            # Filter files if needed
            files_to_restore = manifest["files"]
            if restore_job.file_filters:
                files_to_restore = [
                    f for f in files_to_restore
                    if any(Path(f["path"]).match(pattern) for pattern in restore_job.file_filters)
                ]

            # Restore files
            target_base = Path(restore_job.target_path)
            target_base.mkdir(parents=True, exist_ok=True)

            for file_info in files_to_restore:
                await self._restore_single_file(file_info, target_base, manifest, restore_job)
                restore_job.restored_files += 1

            restore_job.status = RestoreStatus.COMPLETED
            restore_job.completed_at = datetime.utcnow()

        except Exception as e:
            restore_job.status = RestoreStatus.FAILED
            restore_job.error_message = str(e)
            restore_job.completed_at = datetime.utcnow()

    async def _restore_single_file(
        self,
        file_info: Dict[str, Any],
        target_base: Path,
        manifest: Dict[str, Any],
        restore_job: RestoreJob
    ):
        """Restore a single file"""
        # Find backup path
        backup_path = None
        for backed_up_file in self.active_jobs.get(restore_job.backup_job_id, {}).metadata.get("files_backed_up", []):
            if backed_up_file["original_path"] == file_info["path"]:
                backup_path = backed_up_file["backup_path"]
                break

        if not backup_path:
            raise ValueError(f"Backup path not found for {file_info['path']}")

        # Download backup file
        storage_backend = list(self.storage_backends.values())[0]  # Use first available
        backup_data = await storage_backend.download_file(backup_path)

        # Decrypt if needed
        if manifest.get("encryption_enabled"):
            backup_data = await self._decrypt_data(backup_data, restore_job.backup_job_id)

        # Decompress if needed
        if manifest.get("compression_enabled"):
            backup_data = await self._decompress_data(backup_data)

        # Write to target location
        relative_path = file_info["relative_path"]
        target_file = target_base / relative_path
        target_file.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(target_file, "wb") as f:
            await f.write(backup_data)

        # Restore permissions
        target_file.chmod(int(file_info["permissions"], 8))

    async def _decrypt_data(self, data: bytes, backup_id: str) -> bytes:
        """Decrypt data"""
        from cryptography.fernet import Fernet
        import base64

        key = base64.urlsafe_b64encode(backup_id.encode()[:32].ljust(32, b'0'))
        fernet = Fernet(key)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fernet.decrypt, data)

    async def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data"""
        import gzip

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, gzip.decompress, data)

    def get_backup_status(self, job_id: str) -> Optional[BackupJob]:
        """Get backup job status"""
        return self.active_jobs.get(job_id)

    async def list_backups(self, policy_name: str = None) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []

        for job in self.active_jobs.values():
            if policy_name and job.policy_name != policy_name:
                continue

            if job.status == BackupStatus.COMPLETED:
                backups.append({
                    "job_id": job.id,
                    "policy_name": job.policy_name,
                    "backup_type": job.backup_type.value,
                    "created_at": job.started_at,
                    "total_files": job.total_files,
                    "total_size": job.total_size,
                    "compressed_size": job.compressed_size
                })

        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
```

## Automated Backup Scheduling

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

class BackupScheduler:
    """Automated backup scheduling with cron-like expressions"""

    def __init__(self, backup_service: BackupService):
        self.backup_service = backup_service
        self.scheduler = AsyncIOScheduler()
        self.scheduled_jobs = {}

    async def start(self):
        """Start the scheduler"""
        self.scheduler.start()

    async def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()

    async def schedule_policy(self, policy_name: str):
        """Schedule backup policy for automatic execution"""
        if policy_name not in self.backup_service.policies:
            raise ValueError(f"Policy {policy_name} not found")

        policy = self.backup_service.policies[policy_name]

        # Parse cron expression
        trigger = CronTrigger.from_crontab(policy.schedule_cron)

        # Schedule job
        job = self.scheduler.add_job(
            self._execute_scheduled_backup,
            trigger=trigger,
            args=[policy_name],
            id=f"backup_{policy_name}",
            replace_existing=True
        )

        self.scheduled_jobs[policy_name] = job

    async def _execute_scheduled_backup(self, policy_name: str):
        """Execute scheduled backup"""
        try:
            backup_job = await self.backup_service.execute_backup(policy_name)
            print(f"Scheduled backup started: {backup_job.id}")
        except Exception as e:
            print(f"Scheduled backup failed for policy {policy_name}: {e}")

    async def unschedule_policy(self, policy_name: str):
        """Remove policy from schedule"""
        if policy_name in self.scheduled_jobs:
            self.scheduler.remove_job(f"backup_{policy_name}")
            del self.scheduled_jobs[policy_name]

    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of scheduled backup jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            if job.id.startswith("backup_"):
                policy_name = job.id.replace("backup_", "")
                jobs.append({
                    "policy_name": policy_name,
                    "next_run_time": job.next_run_time,
                    "trigger": str(job.trigger)
                })
        return jobs
```

## Disaster Recovery Manager

```python
class DisasterRecoveryManager:
    """Manages disaster recovery scenarios with cross-region replication"""

    def __init__(self, backup_service: BackupService, recovery_configs: Dict[str, Any]):
        self.backup_service = backup_service
        self.recovery_configs = recovery_configs

    async def create_dr_plan(
        self,
        plan_name: str,
        primary_region: str,
        backup_regions: List[str],
        recovery_time_objective: int,  # minutes
        recovery_point_objective: int  # minutes
    ) -> Dict[str, Any]:
        """Create disaster recovery plan"""
        dr_plan = {
            "plan_name": plan_name,
            "primary_region": primary_region,
            "backup_regions": backup_regions,
            "rto_minutes": recovery_time_objective,
            "rpo_minutes": recovery_point_objective,
            "created_at": datetime.utcnow(),
            "status": "active"
        }

        # Store DR plan
        await self._store_dr_plan(dr_plan)

        return dr_plan

    async def test_disaster_recovery(self, plan_name: str) -> Dict[str, Any]:
        """Test disaster recovery procedures"""
        dr_plan = await self._get_dr_plan(plan_name)
        if not dr_plan:
            raise ValueError(f"DR plan {plan_name} not found")

        test_results = {
            "test_id": str(uuid.uuid4()),
            "plan_name": plan_name,
            "started_at": datetime.utcnow(),
            "tests": []
        }

        # Test backup availability in each region
        for region in dr_plan["backup_regions"]:
            region_test = await self._test_region_recovery(region)
            test_results["tests"].append({
                "region": region,
                "success": region_test["success"],
                "response_time_seconds": region_test["response_time"],
                "error": region_test.get("error")
            })

        test_results["completed_at"] = datetime.utcnow()
        test_results["overall_success"] = all(t["success"] for t in test_results["tests"])

        return test_results

    async def _test_region_recovery(self, region: str) -> Dict[str, Any]:
        """Test recovery capabilities in a specific region"""
        start_time = datetime.utcnow()

        try:
            # Test storage backend connectivity
            storage_backend = self.backup_service.storage_backends.get(region)
            if not storage_backend:
                return {
                    "success": False,
                    "error": f"No storage backend configured for region {region}",
                    "response_time": 0
                }

            # Test listing backups
            backups = await storage_backend.list_files("backups/", limit=10)

            response_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "response_time": response_time,
                "backup_count": len(backups)
            }

        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time
            }

    async def initiate_failover(
        self,
        plan_name: str,
        target_region: str,
        reason: str
    ) -> Dict[str, Any]:
        """Initiate failover to backup region"""
        dr_plan = await self._get_dr_plan(plan_name)
        if not dr_plan:
            raise ValueError(f"DR plan {plan_name} not found")

        if target_region not in dr_plan["backup_regions"]:
            raise ValueError(f"Region {target_region} not in backup regions")

        failover_job = {
            "failover_id": str(uuid.uuid4()),
            "plan_name": plan_name,
            "target_region": target_region,
            "reason": reason,
            "initiated_at": datetime.utcnow(),
            "status": "in_progress",
            "steps": []
        }

        # Execute failover steps
        try:
            # Step 1: Verify backup integrity in target region
            await self._verify_backup_integrity_in_region(target_region, failover_job)

            # Step 2: Update DNS/load balancer to point to backup region
            await self._update_traffic_routing(target_region, failover_job)

            # Step 3: Start services in backup region
            await self._start_services_in_region(target_region, failover_job)

            # Step 4: Verify application functionality
            await self._verify_application_health(target_region, failover_job)

            failover_job["status"] = "completed"
            failover_job["completed_at"] = datetime.utcnow()

        except Exception as e:
            failover_job["status"] = "failed"
            failover_job["error"] = str(e)
            failover_job["failed_at"] = datetime.utcnow()

        return failover_job

    async def _verify_backup_integrity_in_region(self, region: str, failover_job: Dict):
        """Verify backup integrity in target region"""
        step = {
            "step": "verify_backup_integrity",
            "started_at": datetime.utcnow(),
            "status": "running"
        }

        try:
            storage_backend = self.backup_service.storage_backends[region]

            # List recent backups
            recent_backups = await storage_backend.list_files("backups/", limit=5)

            if not recent_backups:
                raise ValueError("No backups found in target region")

            # Verify a sample of backups
            verified_count = 0
            for backup in recent_backups[:2]:  # Verify 2 most recent
                try:
                    # Download and verify backup file
                    backup_data = await storage_backend.download_file(backup.path)
                    if backup_data:
                        verified_count += 1
                except Exception:
                    continue

            if verified_count == 0:
                raise ValueError("No backups could be verified")

            step["status"] = "completed"
            step["verified_backups"] = verified_count

        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
            raise

        finally:
            step["completed_at"] = datetime.utcnow()
            failover_job["steps"].append(step)

    async def _update_traffic_routing(self, target_region: str, failover_job: Dict):
        """Update traffic routing to target region"""
        step = {
            "step": "update_traffic_routing",
            "started_at": datetime.utcnow(),
            "status": "running"
        }

        try:
            # This would integrate with your DNS/load balancer
            # Implementation depends on your infrastructure
            await asyncio.sleep(2)  # Simulate routing update

            step["status"] = "completed"

        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
            raise

        finally:
            step["completed_at"] = datetime.utcnow()
            failover_job["steps"].append(step)

    async def _start_services_in_region(self, target_region: str, failover_job: Dict):
        """Start services in backup region"""
        step = {
            "step": "start_services",
            "started_at": datetime.utcnow(),
            "status": "running"
        }

        try:
            # This would start your application services in the target region
            # Implementation depends on your orchestration platform
            await asyncio.sleep(5)  # Simulate service startup

            step["status"] = "completed"

        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
            raise

        finally:
            step["completed_at"] = datetime.utcnow()
            failover_job["steps"].append(step)

    async def _verify_application_health(self, target_region: str, failover_job: Dict):
        """Verify application health in target region"""
        step = {
            "step": "verify_application_health",
            "started_at": datetime.utcnow(),
            "status": "running"
        }

        try:
            # This would perform health checks on your application
            # Implementation depends on your application architecture
            await asyncio.sleep(3)  # Simulate health checks

            step["status"] = "completed"
            step["health_check_results"] = {
                "api_responsive": True,
                "database_accessible": True,
                "external_services_available": True
            }

        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
            raise

        finally:
            step["completed_at"] = datetime.utcnow()
            failover_job["steps"].append(step)

    async def _store_dr_plan(self, dr_plan: Dict[str, Any]):
        """Store disaster recovery plan"""
        # Implementation would store in your configuration database
        pass

    async def _get_dr_plan(self, plan_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve disaster recovery plan"""
        # Implementation would retrieve from your configuration database
        return None
```

## FastAPI Integration

```python
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from typing import List

app = FastAPI()

# Initialize services
backup_service = BackupService(storage_backends)
backup_scheduler = BackupScheduler(backup_service)
dr_manager = DisasterRecoveryManager(backup_service, recovery_configs)

@app.on_event("startup")
async def startup_event():
    await backup_scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    await backup_scheduler.stop()

@app.post("/backup/policies")
async def create_backup_policy(
    policy_data: Dict[str, Any],
    user: User = Depends(get_current_admin_user)
):
    """Create backup policy"""
    policy = BackupPolicy(
        name=policy_data["name"],
        backup_type=BackupType(policy_data["backup_type"]),
        schedule_cron=policy_data["schedule_cron"],
        retention_days=policy_data["retention_days"],
        source_paths=policy_data["source_paths"],
        destination_config=policy_data["destination_config"]
    )

    policy_name = await backup_service.create_backup_policy(policy)

    # Schedule if requested
    if policy_data.get("auto_schedule", False):
        await backup_scheduler.schedule_policy(policy_name)

    return {"policy_name": policy_name, "status": "created"}

@app.post("/backup/execute/{policy_name}")
async def execute_backup(
    policy_name: str,
    force_full: bool = False,
    user: User = Depends(get_current_admin_user)
):
    """Execute backup manually"""
    try:
        job = await backup_service.execute_backup(policy_name, force_full)
        return {
            "job_id": job.id,
            "status": job.status.value,
            "message": "Backup started"
        }
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.get("/backup/jobs/{job_id}")
async def get_backup_status(
    job_id: str,
    user: User = Depends(get_current_admin_user)
):
    """Get backup job status"""
    job = backup_service.get_backup_status(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "job_id": job.id,
        "policy_name": job.policy_name,
        "backup_type": job.backup_type.value,
        "status": job.status.value,
        "progress": f"{job.processed_files}/{job.total_files}",
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "error": job.error_message
    }

@app.get("/backup/list")
async def list_backups(
    policy_name: Optional[str] = None,
    user: User = Depends(get_current_admin_user)
):
    """List available backups"""
    backups = await backup_service.list_backups(policy_name)
    return {"backups": backups}

@app.post("/backup/restore")
async def restore_backup(
    restore_request: Dict[str, Any],
    user: User = Depends(get_current_admin_user)
):
    """Restore files from backup"""
    restore_job = await backup_service.restore_backup(
        backup_job_id=restore_request["backup_job_id"],
        target_path=restore_request["target_path"],
        file_filters=restore_request.get("file_filters")
    )

    return {
        "restore_job_id": restore_job.id,
        "status": restore_job.status.value,
        "message": "Restore started"
    }

@app.get("/backup/schedule")
async def get_scheduled_jobs(user: User = Depends(get_current_admin_user)):
    """Get scheduled backup jobs"""
    jobs = backup_scheduler.get_scheduled_jobs()
    return {"scheduled_jobs": jobs}

@app.post("/dr/test/{plan_name}")
async def test_disaster_recovery(
    plan_name: str,
    user: User = Depends(get_current_admin_user)
):
    """Test disaster recovery plan"""
    test_results = await dr_manager.test_disaster_recovery(plan_name)
    return test_results

@app.post("/dr/failover/{plan_name}")
async def initiate_failover(
    plan_name: str,
    failover_request: Dict[str, Any],
    user: User = Depends(get_current_admin_user)
):
    """Initiate disaster recovery failover"""
    failover_job = await dr_manager.initiate_failover(
        plan_name=plan_name,
        target_region=failover_request["target_region"],
        reason=failover_request["reason"]
    )

    return failover_job
```

## Testing Backup Systems

```python
import pytest
import tempfile
import shutil
from unittest.mock import AsyncMock

class TestBackupService:

    @pytest.fixture
    async def backup_service(self):
        storage_backends = {
            "local": AsyncMock(),
            "s3": AsyncMock()
        }
        return BackupService(storage_backends)

    @pytest.fixture
    def sample_policy(self):
        return BackupPolicy(
            name="test_policy",
            backup_type=BackupType.FULL,
            schedule_cron="0 2 * * *",  # Daily at 2 AM
            retention_days=30,
            source_paths=["/tmp/test_source"],
            destination_config={"provider": "local"}
        )

    async def test_policy_creation(self, backup_service, sample_policy):
        policy_name = await backup_service.create_backup_policy(sample_policy)
        assert policy_name == "test_policy"
        assert "test_policy" in backup_service.policies

    async def test_full_backup_execution(self, backup_service, sample_policy):
        # Create test files
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")

            sample_policy.source_paths = [str(test_file)]
            await backup_service.create_backup_policy(sample_policy)

            # Mock storage backend
            backup_service.storage_backends["local"].upload_file = AsyncMock()

            job = await backup_service.execute_backup("test_policy")

            assert job.policy_name == "test_policy"
            assert job.backup_type == BackupType.FULL

    async def test_incremental_backup(self, backup_service, sample_policy):
        # Test incremental backup logic
        sample_policy.backup_type = BackupType.INCREMENTAL
        await backup_service.create_backup_policy(sample_policy)

        # Mock previous backup manifest
        backup_service._get_last_backup_manifest = AsyncMock(return_value=None)

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            sample_policy.source_paths = [str(test_file)]

            job = await backup_service.execute_backup("test_policy")
            # First incremental backup should be full since no previous backup exists

    async def test_backup_restoration(self, backup_service):
        # Mock backup manifest
        manifest = {
            "backup_id": "test_backup",
            "files": [
                {
                    "path": "/tmp/test.txt",
                    "relative_path": "test.txt",
                    "size": 100,
                    "file_hash": "abcdef"
                }
            ],
            "compression_enabled": False,
            "encryption_enabled": False
        }

        backup_service._find_backup_manifest = AsyncMock(return_value=manifest)
        backup_service.storage_backends["local"].download_file = AsyncMock(return_value=b"test content")

        with tempfile.TemporaryDirectory() as temp_dir:
            restore_job = await backup_service.restore_backup(
                "test_backup",
                temp_dir
            )

            assert restore_job.backup_job_id == "test_backup"

    def test_backup_policy_validation(self):
        # Test invalid cron expression
        with pytest.raises(ValueError):
            BackupPolicy(
                name="invalid",
                backup_type=BackupType.FULL,
                schedule_cron="invalid cron",
                retention_days=30,
                source_paths=["/tmp"]
            )

    async def test_disaster_recovery_test(self):
        dr_manager = DisasterRecoveryManager(None, {})

        # Mock DR plan
        dr_manager._get_dr_plan = AsyncMock(return_value={
            "plan_name": "test_plan",
            "primary_region": "us-east-1",
            "backup_regions": ["us-west-2"],
            "rto_minutes": 15,
            "rpo_minutes": 5
        })

        dr_manager._test_region_recovery = AsyncMock(return_value={
            "success": True,
            "response_time": 2.5
        })

        test_results = await dr_manager.test_disaster_recovery("test_plan")

        assert test_results["overall_success"] is True
        assert len(test_results["tests"]) == 1
```

## Related Documentation

- [File Upload Patterns](upload-patterns.md) - File upload and validation
- [Media Processing Patterns](media-processing.md) - Media processing workflows
- [Cloud Storage Integration](cloud-integration.md) - Multi-cloud storage
- [Infrastructure](../infrastructure/) - Infrastructure and deployment guides

## Implementation Notes

1. **3-2-1 Rule**: Keep 3 copies of data, on 2 different media, with 1 offsite
2. **Automation**: Automate backup scheduling and monitoring
3. **Testing**: Regularly test backup restoration and disaster recovery
4. **Encryption**: Always encrypt backups in transit and at rest
5. **Monitoring**: Monitor backup success rates and storage usage
6. **Documentation**: Document recovery procedures and test results
7. **Compliance**: Ensure backup retention meets regulatory requirements
8. **Performance**: Optimize backup performance with compression and parallelization

## Related Documents

- `docs/atomic/file-storage/cloud-integration.md` — Cloud storage integration
- `docs/atomic/infrastructure/docker-volumes.md` — Volume management
- `docs/atomic/file-storage/media-processing.md` — Media file handling
- `docs/atomic/infrastructure/backup-restore.md` — Backup procedures
