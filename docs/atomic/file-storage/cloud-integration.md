# Cloud Storage Integration

Comprehensive guide for integrating with AWS S3, Google Cloud Storage, Azure Blob Storage, and multi-cloud strategies with CDN optimization and disaster recovery.

## Universal Storage Interface

```python
from typing import Optional, Dict, List, Any, AsyncIterator, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import hashlib
import mimetypes
from datetime import datetime, timedelta
import json

class StorageProvider(Enum):
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    LOCAL = "local"

@dataclass
class StorageConfig:
    provider: StorageProvider
    bucket_name: str
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None  # For S3-compatible services
    cdn_domain: Optional[str] = None
    encryption_enabled: bool = True
    versioning_enabled: bool = False
    lifecycle_rules: List[Dict] = field(default_factory=list)

@dataclass
class FileMetadata:
    path: str
    size: int
    content_type: str
    etag: str
    last_modified: datetime
    metadata: Dict[str, str] = field(default_factory=dict)
    storage_class: Optional[str] = None
    version_id: Optional[str] = None

class CloudStorageInterface(ABC):
    """Abstract interface for cloud storage providers"""

    @abstractmethod
    async def upload_file(
        self,
        file_data: bytes,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        storage_class: Optional[str] = None
    ) -> str:
        """Upload file and return public URL"""
        pass

    @abstractmethod
    async def download_file(self, path: str) -> bytes:
        """Download file content"""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Delete file"""
        pass

    @abstractmethod
    async def get_file_metadata(self, path: str) -> FileMetadata:
        """Get file metadata"""
        pass

    @abstractmethod
    async def list_files(self, prefix: str = "", limit: int = 1000) -> List[FileMetadata]:
        """List files with optional prefix filter"""
        pass

    @abstractmethod
    async def generate_presigned_url(
        self,
        path: str,
        operation: str = "get",
        expiry_seconds: int = 3600
    ) -> str:
        """Generate presigned URL for direct client access"""
        pass

    @abstractmethod
    async def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy file within storage"""
        pass

class AWSS3Storage(CloudStorageInterface):
    """AWS S3 storage implementation"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._client = None
        self._session = None

    async def _get_client(self):
        """Lazy initialization of S3 client"""
        if not self._client:
            import boto3
            from botocore.config import Config

            session = boto3.Session(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )

            # Configure client with retry and timeout settings
            client_config = Config(
                region_name=self.config.region,
                retries={'max_attempts': 3},
                max_pool_connections=50
            )

            self._client = session.client(
                's3',
                config=client_config,
                endpoint_url=self.config.endpoint_url
            )

        return self._client

    async def upload_file(
        self,
        file_data: bytes,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        storage_class: Optional[str] = None
    ) -> str:
        """Upload file to S3"""
        client = await self._get_client()

        # Guess content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(path)
            content_type = content_type or 'application/octet-stream'

        # Prepare upload parameters
        upload_params = {
            'Bucket': self.config.bucket_name,
            'Key': path,
            'Body': file_data,
            'ContentType': content_type
        }

        # Add metadata
        if metadata:
            upload_params['Metadata'] = metadata

        # Add storage class
        if storage_class:
            upload_params['StorageClass'] = storage_class

        # Add server-side encryption
        if self.config.encryption_enabled:
            upload_params['ServerSideEncryption'] = 'AES256'

        # Perform upload
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: client.put_object(**upload_params))

        # Return URL
        if self.config.cdn_domain:
            return f"https://{self.config.cdn_domain}/{path}"
        else:
            return f"https://{self.config.bucket_name}.s3.{self.config.region}.amazonaws.com/{path}"

    async def download_file(self, path: str) -> bytes:
        """Download file from S3"""
        client = await self._get_client()

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.get_object(Bucket=self.config.bucket_name, Key=path)
        )

        return response['Body'].read()

    async def delete_file(self, path: str) -> bool:
        """Delete file from S3"""
        client = await self._get_client()

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.delete_object(Bucket=self.config.bucket_name, Key=path)
            )
            return True
        except Exception:
            return False

    async def get_file_metadata(self, path: str) -> FileMetadata:
        """Get S3 object metadata"""
        client = await self._get_client()

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.head_object(Bucket=self.config.bucket_name, Key=path)
        )

        return FileMetadata(
            path=path,
            size=response['ContentLength'],
            content_type=response['ContentType'],
            etag=response['ETag'].strip('"'),
            last_modified=response['LastModified'],
            metadata=response.get('Metadata', {}),
            storage_class=response.get('StorageClass'),
            version_id=response.get('VersionId')
        )

    async def list_files(self, prefix: str = "", limit: int = 1000) -> List[FileMetadata]:
        """List S3 objects"""
        client = await self._get_client()

        params = {
            'Bucket': self.config.bucket_name,
            'MaxKeys': limit
        }

        if prefix:
            params['Prefix'] = prefix

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.list_objects_v2(**params)
        )

        files = []
        for obj in response.get('Contents', []):
            files.append(FileMetadata(
                path=obj['Key'],
                size=obj['Size'],
                content_type='',  # Not available in list operation
                etag=obj['ETag'].strip('"'),
                last_modified=obj['LastModified'],
                storage_class=obj.get('StorageClass')
            ))

        return files

    async def generate_presigned_url(
        self,
        path: str,
        operation: str = "get",
        expiry_seconds: int = 3600
    ) -> str:
        """Generate presigned URL for S3 object"""
        client = await self._get_client()

        method_map = {
            'get': 'get_object',
            'put': 'put_object',
            'delete': 'delete_object'
        }

        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            lambda: client.generate_presigned_url(
                method_map[operation],
                Params={'Bucket': self.config.bucket_name, 'Key': path},
                ExpiresIn=expiry_seconds
            )
        )

        return url

    async def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy object within S3"""
        client = await self._get_client()

        try:
            copy_source = {
                'Bucket': self.config.bucket_name,
                'Key': source_path
            }

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.copy_object(
                    CopySource=copy_source,
                    Bucket=self.config.bucket_name,
                    Key=dest_path
                )
            )
            return True
        except Exception:
            return False

class GoogleCloudStorage(CloudStorageInterface):
    """Google Cloud Storage implementation"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._client = None

    async def _get_client(self):
        """Lazy initialization of GCS client"""
        if not self._client:
            from google.cloud import storage

            # Initialize client with service account or default credentials
            self._client = storage.Client()
            self._bucket = self._client.bucket(self.config.bucket_name)

        return self._client

    async def upload_file(
        self,
        file_data: bytes,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        storage_class: Optional[str] = None
    ) -> str:
        """Upload file to Google Cloud Storage"""
        await self._get_client()

        blob = self._bucket.blob(path)

        # Set content type
        if content_type:
            blob.content_type = content_type

        # Set metadata
        if metadata:
            blob.metadata = metadata

        # Set storage class
        if storage_class:
            blob.storage_class = storage_class

        # Upload in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: blob.upload_from_string(file_data)
        )

        # Return public URL
        if self.config.cdn_domain:
            return f"https://{self.config.cdn_domain}/{path}"
        else:
            return blob.public_url

    async def download_file(self, path: str) -> bytes:
        """Download file from GCS"""
        await self._get_client()

        blob = self._bucket.blob(path)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, blob.download_as_bytes)

    async def delete_file(self, path: str) -> bool:
        """Delete file from GCS"""
        await self._get_client()

        try:
            blob = self._bucket.blob(path)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, blob.delete)
            return True
        except Exception:
            return False

    async def get_file_metadata(self, path: str) -> FileMetadata:
        """Get GCS blob metadata"""
        await self._get_client()

        blob = self._bucket.blob(path)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, blob.reload)

        return FileMetadata(
            path=path,
            size=blob.size,
            content_type=blob.content_type or '',
            etag=blob.etag,
            last_modified=blob.updated,
            metadata=blob.metadata or {},
            storage_class=blob.storage_class
        )

    async def list_files(self, prefix: str = "", limit: int = 1000) -> List[FileMetadata]:
        """List GCS blobs"""
        await self._get_client()

        loop = asyncio.get_event_loop()
        blobs = await loop.run_in_executor(
            None,
            lambda: list(self._bucket.list_blobs(prefix=prefix, max_results=limit))
        )

        files = []
        for blob in blobs:
            files.append(FileMetadata(
                path=blob.name,
                size=blob.size,
                content_type=blob.content_type or '',
                etag=blob.etag,
                last_modified=blob.updated,
                metadata=blob.metadata or {},
                storage_class=blob.storage_class
            ))

        return files

    async def generate_presigned_url(
        self,
        path: str,
        operation: str = "get",
        expiry_seconds: int = 3600
    ) -> str:
        """Generate signed URL for GCS blob"""
        await self._get_client()

        blob = self._bucket.blob(path)

        method_map = {
            'get': 'GET',
            'put': 'PUT',
            'delete': 'DELETE'
        }

        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            lambda: blob.generate_signed_url(
                expiration=timedelta(seconds=expiry_seconds),
                method=method_map[operation]
            )
        )

        return url

    async def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy blob within GCS"""
        await self._get_client()

        try:
            source_blob = self._bucket.blob(source_path)
            dest_blob = self._bucket.blob(dest_path)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._bucket.copy_blob(source_blob, self._bucket, dest_path)
            )
            return True
        except Exception:
            return False

class AzureBlobStorage(CloudStorageInterface):
    """Azure Blob Storage implementation"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._client = None

    async def _get_client(self):
        """Lazy initialization of Azure client"""
        if not self._client:
            from azure.storage.blob.aio import BlobServiceClient

            self._client = BlobServiceClient(
                account_url=f"https://{self.config.access_key}.blob.core.windows.net",
                credential=self.config.secret_key
            )

        return self._client

    async def upload_file(
        self,
        file_data: bytes,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        storage_class: Optional[str] = None
    ) -> str:
        """Upload file to Azure Blob Storage"""
        client = await self._get_client()

        blob_client = client.get_blob_client(
            container=self.config.bucket_name,
            blob=path
        )

        upload_params = {
            'data': file_data,
            'overwrite': True
        }

        if content_type:
            upload_params['content_type'] = content_type

        if metadata:
            upload_params['metadata'] = metadata

        await blob_client.upload_blob(**upload_params)

        # Return URL
        if self.config.cdn_domain:
            return f"https://{self.config.cdn_domain}/{path}"
        else:
            return blob_client.url

    async def download_file(self, path: str) -> bytes:
        """Download file from Azure"""
        client = await self._get_client()

        blob_client = client.get_blob_client(
            container=self.config.bucket_name,
            blob=path
        )

        stream = await blob_client.download_blob()
        return await stream.readall()

    async def delete_file(self, path: str) -> bool:
        """Delete file from Azure"""
        client = await self._get_client()

        try:
            blob_client = client.get_blob_client(
                container=self.config.bucket_name,
                blob=path
            )
            await blob_client.delete_blob()
            return True
        except Exception:
            return False

    async def get_file_metadata(self, path: str) -> FileMetadata:
        """Get Azure blob properties"""
        client = await self._get_client()

        blob_client = client.get_blob_client(
            container=self.config.bucket_name,
            blob=path
        )

        properties = await blob_client.get_blob_properties()

        return FileMetadata(
            path=path,
            size=properties.size,
            content_type=properties.content_type or '',
            etag=properties.etag,
            last_modified=properties.last_modified,
            metadata=properties.metadata or {}
        )

    async def list_files(self, prefix: str = "", limit: int = 1000) -> List[FileMetadata]:
        """List Azure blobs"""
        client = await self._get_client()

        container_client = client.get_container_client(self.config.bucket_name)

        files = []
        async for blob in container_client.list_blobs(name_starts_with=prefix):
            if len(files) >= limit:
                break

            files.append(FileMetadata(
                path=blob.name,
                size=blob.size,
                content_type=blob.content_type or '',
                etag=blob.etag,
                last_modified=blob.last_modified,
                metadata=blob.metadata or {}
            ))

        return files

    async def generate_presigned_url(
        self,
        path: str,
        operation: str = "get",
        expiry_seconds: int = 3600
    ) -> str:
        """Generate SAS URL for Azure blob"""
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions

        permissions = BlobSasPermissions()
        if operation == "get":
            permissions.read = True
        elif operation == "put":
            permissions.write = True
        elif operation == "delete":
            permissions.delete = True

        sas_token = generate_blob_sas(
            account_name=self.config.access_key,
            container_name=self.config.bucket_name,
            blob_name=path,
            account_key=self.config.secret_key,
            permission=permissions,
            expiry=datetime.utcnow() + timedelta(seconds=expiry_seconds)
        )

        return f"https://{self.config.access_key}.blob.core.windows.net/{self.config.bucket_name}/{path}?{sas_token}"

    async def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy blob within Azure"""
        client = await self._get_client()

        try:
            source_blob = client.get_blob_client(
                container=self.config.bucket_name,
                blob=source_path
            )

            dest_blob = client.get_blob_client(
                container=self.config.bucket_name,
                blob=dest_path
            )

            await dest_blob.start_copy_from_url(source_blob.url)
            return True
        except Exception:
            return False
```

## Multi-Cloud Storage Manager

```python
class MultiCloudStorageManager:
    """Manages multiple cloud storage providers with failover and replication"""

    def __init__(self, primary_config: StorageConfig, backup_configs: List[StorageConfig] = None):
        self.primary_storage = self._create_storage(primary_config)
        self.backup_storages = [self._create_storage(config) for config in (backup_configs or [])]
        self.all_storages = [self.primary_storage] + self.backup_storages

    def _create_storage(self, config: StorageConfig) -> CloudStorageInterface:
        """Factory method to create storage instances"""
        if config.provider == StorageProvider.AWS_S3:
            return AWSS3Storage(config)
        elif config.provider == StorageProvider.GOOGLE_CLOUD:
            return GoogleCloudStorage(config)
        elif config.provider == StorageProvider.AZURE_BLOB:
            return AzureBlobStorage(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    async def upload_file(
        self,
        file_data: bytes,
        path: str,
        replicate: bool = True,
        **kwargs
    ) -> Dict[str, str]:
        """Upload file with optional replication to backup storages"""
        results = {}
        errors = {}

        # Upload to primary storage
        try:
            primary_url = await self.primary_storage.upload_file(file_data, path, **kwargs)
            results["primary"] = primary_url
        except Exception as e:
            errors["primary"] = str(e)
            raise RuntimeError(f"Primary upload failed: {e}")

        # Replicate to backup storages if requested
        if replicate and self.backup_storages:
            replication_tasks = []
            for i, storage in enumerate(self.backup_storages):
                task = asyncio.create_task(
                    self._upload_with_retry(storage, file_data, path, f"backup_{i}", **kwargs)
                )
                replication_tasks.append(task)

            # Wait for all replications with timeout
            try:
                replication_results = await asyncio.wait_for(
                    asyncio.gather(*replication_tasks, return_exceptions=True),
                    timeout=30.0
                )

                for i, result in enumerate(replication_results):
                    if isinstance(result, Exception):
                        errors[f"backup_{i}"] = str(result)
                    else:
                        results[f"backup_{i}"] = result
            except asyncio.TimeoutError:
                errors["replication"] = "Replication timeout"

        return {
            "urls": results,
            "errors": errors,
            "replicated": len(results) - 1  # Exclude primary
        }

    async def _upload_with_retry(
        self,
        storage: CloudStorageInterface,
        file_data: bytes,
        path: str,
        storage_name: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Upload with retry logic"""
        for attempt in range(max_retries):
            try:
                return await storage.upload_file(file_data, path, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def download_file(self, path: str, prefer_backup: bool = False) -> bytes:
        """Download file with failover to backup storages"""
        storages = self.all_storages if not prefer_backup else self.all_storages[::-1]

        for storage in storages:
            try:
                return await storage.download_file(path)
            except Exception as e:
                continue  # Try next storage

        raise RuntimeError("File not found in any storage")

    async def delete_file(self, path: str, delete_all: bool = True) -> Dict[str, bool]:
        """Delete file from all or just primary storage"""
        results = {}

        if delete_all:
            storages = self.all_storages
            storage_names = ["primary"] + [f"backup_{i}" for i in range(len(self.backup_storages))]
        else:
            storages = [self.primary_storage]
            storage_names = ["primary"]

        for storage, name in zip(storages, storage_names):
            try:
                results[name] = await storage.delete_file(path)
            except Exception:
                results[name] = False

        return results

    async def sync_between_storages(self, path: str) -> Dict[str, str]:
        """Ensure file exists in all configured storages"""
        results = {}

        # Download from primary
        try:
            file_data = await self.primary_storage.download_file(path)
        except Exception as e:
            raise RuntimeError(f"Cannot sync: file not found in primary storage: {e}")

        # Upload to backup storages
        for i, storage in enumerate(self.backup_storages):
            try:
                url = await storage.upload_file(file_data, path)
                results[f"backup_{i}"] = url
            except Exception as e:
                results[f"backup_{i}"] = f"Failed: {e}"

        return results

    async def verify_file_integrity(self, path: str) -> Dict[str, Dict[str, Any]]:
        """Verify file exists and matches across all storages"""
        results = {}
        storage_names = ["primary"] + [f"backup_{i}" for i in range(len(self.backup_storages))]

        for storage, name in zip(self.all_storages, storage_names):
            try:
                metadata = await storage.get_file_metadata(path)
                results[name] = {
                    "exists": True,
                    "size": metadata.size,
                    "etag": metadata.etag,
                    "last_modified": metadata.last_modified
                }
            except Exception as e:
                results[name] = {
                    "exists": False,
                    "error": str(e)
                }

        # Check consistency
        sizes = [r["size"] for r in results.values() if r.get("exists")]
        etags = [r["etag"] for r in results.values() if r.get("exists")]

        consistent = len(set(sizes)) <= 1 and len(set(etags)) <= 1

        return {
            "storages": results,
            "consistent": consistent,
            "total_copies": len(sizes)
        }
```

## CDN Integration

```python
class CDNManager:
    """Manages CDN integration for optimized content delivery"""

    def __init__(self, storage_manager: MultiCloudStorageManager, cdn_configs: Dict[str, Any]):
        self.storage_manager = storage_manager
        self.cdn_configs = cdn_configs

    async def upload_with_cdn_optimization(
        self,
        file_data: bytes,
        path: str,
        content_type: str,
        cache_control: str = "public, max-age=31536000"  # 1 year
    ) -> Dict[str, str]:
        """Upload file optimized for CDN delivery"""

        # Set CDN-optimized metadata
        metadata = {
            "cache-control": cache_control,
            "cdn-optimized": "true"
        }

        # Upload to storage
        upload_result = await self.storage_manager.upload_file(
            file_data=file_data,
            path=path,
            content_type=content_type,
            metadata=metadata
        )

        # Invalidate CDN cache if needed
        if "cloudfront" in self.cdn_configs:
            await self._invalidate_cloudfront(path)

        return upload_result

    async def _invalidate_cloudfront(self, path: str):
        """Invalidate CloudFront cache for updated content"""
        import boto3

        if "distribution_id" not in self.cdn_configs["cloudfront"]:
            return

        cloudfront = boto3.client('cloudfront')

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: cloudfront.create_invalidation(
                DistributionId=self.cdn_configs["cloudfront"]["distribution_id"],
                InvalidationBatch={
                    'Paths': {
                        'Quantity': 1,
                        'Items': [f"/{path}"]
                    },
                    'CallerReference': str(uuid.uuid4())
                }
            )
        )

    async def get_optimized_urls(self, path: str) -> Dict[str, str]:
        """Get URLs optimized for different use cases"""
        urls = {}

        # Original URL
        primary_url = await self.storage_manager.primary_storage.generate_presigned_url(path)
        urls["original"] = primary_url

        # CDN URLs for different optimizations
        base_cdn_url = self.cdn_configs.get("base_url", "")

        if base_cdn_url:
            urls["cdn"] = f"{base_cdn_url}/{path}"
            urls["cdn_compressed"] = f"{base_cdn_url}/{path}?format=auto&quality=80"
            urls["cdn_webp"] = f"{base_cdn_url}/{path}?format=webp"
            urls["cdn_thumbnail"] = f"{base_cdn_url}/{path}?w=300&h=300&fit=cover"

        return urls
```

## Storage Analytics and Monitoring

```python
class StorageAnalytics:
    """Analytics and monitoring for cloud storage usage"""

    def __init__(self, storage_manager: MultiCloudStorageManager):
        self.storage_manager = storage_manager
        self.metrics = {}

    async def collect_storage_metrics(self) -> Dict[str, Any]:
        """Collect storage metrics from all providers"""
        metrics = {
            "timestamp": datetime.utcnow(),
            "storages": {}
        }

        storage_names = ["primary"] + [f"backup_{i}" for i in range(len(self.storage_manager.backup_storages))]

        for storage, name in zip(self.storage_manager.all_storages, storage_names):
            try:
                # Get storage-specific metrics
                storage_metrics = await self._collect_storage_specific_metrics(storage)
                metrics["storages"][name] = storage_metrics
            except Exception as e:
                metrics["storages"][name] = {"error": str(e)}

        return metrics

    async def _collect_storage_specific_metrics(self, storage: CloudStorageInterface) -> Dict[str, Any]:
        """Collect metrics from a specific storage provider"""
        # List recent files to estimate usage
        recent_files = await storage.list_files(limit=1000)

        total_size = sum(f.size for f in recent_files)
        file_count = len(recent_files)

        # Calculate storage classes distribution
        storage_classes = {}
        for file in recent_files:
            sc = file.storage_class or "STANDARD"
            storage_classes[sc] = storage_classes.get(sc, 0) + 1

        return {
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024**3), 2),
            "storage_classes": storage_classes,
            "average_file_size": total_size // max(file_count, 1),
            "collection_time": datetime.utcnow()
        }

    async def generate_cost_estimate(self) -> Dict[str, Any]:
        """Generate cost estimates for storage usage"""
        metrics = await self.collect_storage_metrics()

        # Simplified cost calculation (would need real pricing data)
        cost_estimates = {}

        for storage_name, storage_metrics in metrics["storages"].items():
            if "error" in storage_metrics:
                continue

            size_gb = storage_metrics["total_size_gb"]

            # Example pricing (update with real values)
            if "primary" in storage_name:
                monthly_cost = size_gb * 0.023  # S3 Standard pricing
            else:
                monthly_cost = size_gb * 0.0125  # S3 IA pricing

            cost_estimates[storage_name] = {
                "monthly_storage_cost": round(monthly_cost, 2),
                "size_gb": size_gb,
                "cost_per_gb": 0.023 if "primary" in storage_name else 0.0125
            }

        return cost_estimates

    async def check_redundancy_health(self) -> Dict[str, Any]:
        """Check health of redundant storage setup"""
        health_report = {
            "timestamp": datetime.utcnow(),
            "overall_health": "healthy",
            "issues": [],
            "recommendations": []
        }

        # Sample some files to check consistency
        sample_files = await self.storage_manager.primary_storage.list_files(limit=10)

        inconsistent_files = []
        for file in sample_files:
            integrity_check = await self.storage_manager.verify_file_integrity(file.path)
            if not integrity_check["consistent"]:
                inconsistent_files.append(file.path)

        if inconsistent_files:
            health_report["overall_health"] = "degraded"
            health_report["issues"].append(f"Inconsistent files: {len(inconsistent_files)}")
            health_report["recommendations"].append("Run sync_between_storages for inconsistent files")

        # Check backup storage availability
        for i, storage in enumerate(self.storage_manager.backup_storages):
            try:
                await storage.list_files(limit=1)
            except Exception as e:
                health_report["overall_health"] = "critical"
                health_report["issues"].append(f"Backup storage {i} unavailable: {e}")

        return health_report
```

## Testing Cloud Storage

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestCloudStorage:

    @pytest.fixture
    def s3_config(self):
        return StorageConfig(
            provider=StorageProvider.AWS_S3,
            bucket_name="test-bucket",
            region="us-east-1",
            access_key="test-key",
            secret_key="test-secret"
        )

    @pytest.fixture
    async def s3_storage(self, s3_config):
        with patch('boto3.Session'):
            storage = AWSS3Storage(s3_config)
            return storage

    async def test_file_upload_success(self, s3_storage):
        file_data = b"test file content"
        path = "test/file.txt"

        # Mock the S3 client
        mock_client = AsyncMock()
        s3_storage._client = mock_client

        url = await s3_storage.upload_file(file_data, path, content_type="text/plain")

        assert url.startswith("https://")
        assert path in url
        mock_client.put_object.assert_called_once()

    async def test_multi_cloud_upload_with_replication(self):
        # Mock storage configurations
        primary_config = StorageConfig(
            provider=StorageProvider.AWS_S3,
            bucket_name="primary",
            access_key="key1",
            secret_key="secret1"
        )

        backup_config = StorageConfig(
            provider=StorageProvider.GOOGLE_CLOUD,
            bucket_name="backup",
            access_key="key2",
            secret_key="secret2"
        )

        with patch.multiple(
            'your_module',
            AWSS3Storage=AsyncMock(),
            GoogleCloudStorage=AsyncMock()
        ):
            manager = MultiCloudStorageManager(primary_config, [backup_config])

            # Mock successful uploads
            manager.primary_storage.upload_file.return_value = "https://primary.com/file.txt"
            manager.backup_storages[0].upload_file.return_value = "https://backup.com/file.txt"

            result = await manager.upload_file(b"test data", "test.txt", replicate=True)

            assert "primary" in result["urls"]
            assert "backup_0" in result["urls"]
            assert result["replicated"] == 1

    async def test_failover_download(self):
        """Test download failover when primary storage fails"""
        with patch.multiple(
            'your_module',
            AWSS3Storage=AsyncMock(),
            GoogleCloudStorage=AsyncMock()
        ):
            manager = MultiCloudStorageManager(
                StorageConfig(StorageProvider.AWS_S3, "primary"),
                [StorageConfig(StorageProvider.GOOGLE_CLOUD, "backup")]
            )

            # Primary fails, backup succeeds
            manager.primary_storage.download_file.side_effect = Exception("Primary down")
            manager.backup_storages[0].download_file.return_value = b"file content"

            data = await manager.download_file("test.txt")

            assert data == b"file content"
            manager.primary_storage.download_file.assert_called_once()
            manager.backup_storages[0].download_file.assert_called_once()

    async def test_storage_integrity_check(self):
        """Test file integrity verification across storages"""
        with patch.multiple(
            'your_module',
            AWSS3Storage=AsyncMock(),
            GoogleCloudStorage=AsyncMock()
        ):
            manager = MultiCloudStorageManager(
                StorageConfig(StorageProvider.AWS_S3, "primary"),
                [StorageConfig(StorageProvider.GOOGLE_CLOUD, "backup")]
            )

            # Mock consistent metadata
            consistent_metadata = FileMetadata(
                path="test.txt",
                size=1000,
                etag="abc123",
                content_type="text/plain",
                last_modified=datetime.utcnow()
            )

            manager.primary_storage.get_file_metadata.return_value = consistent_metadata
            manager.backup_storages[0].get_file_metadata.return_value = consistent_metadata

            result = await manager.verify_file_integrity("test.txt")

            assert result["consistent"] is True
            assert result["total_copies"] == 2

    def test_cdn_url_generation(self):
        """Test CDN URL generation for different optimizations"""
        cdn_manager = CDNManager(
            storage_manager=None,
            cdn_configs={"base_url": "https://cdn.example.com"}
        )

        urls = cdn_manager.get_optimized_urls("images/photo.jpg")

        assert "cdn" in urls
        assert "cdn_compressed" in urls
        assert "cdn_webp" in urls
        assert "format=webp" in urls["cdn_webp"]
```

## Related Documentation

- [File Upload Patterns](upload-patterns.md) - File upload and validation
- [Media Processing Patterns](media-processing-patterns.md) - Media processing workflows
- [Backup Strategies](backup-strategies.md) - Backup and disaster recovery
- [External Integrations](../external-integrations/) - Third-party service integrations

## Implementation Notes

1. **Multi-Cloud Strategy**: Use multiple providers for redundancy and cost optimization
2. **Async Operations**: All storage operations should be asynchronous
3. **Error Handling**: Robust error handling with fallback strategies
4. **Cost Optimization**: Monitor usage and optimize storage classes
5. **Security**: Use encryption at rest and in transit
6. **Monitoring**: Track metrics and set up alerts for issues
7. **CDN Integration**: Leverage CDNs for global content delivery
8. **Testing**: Comprehensive testing with mocked cloud services