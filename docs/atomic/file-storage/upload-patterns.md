# File Upload Patterns

Comprehensive guide for handling file uploads in microservices with validation, processing, security, and multi-storage backend support.

## Core Upload Service

```python
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import mimetypes
import asyncio
import aiofiles
import magic
from pathlib import Path
from datetime import datetime, timedelta
import uuid

class FileType(Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    TEXT = "text"

@dataclass
class FileUploadConfig:
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_mime_types: List[str] = field(default_factory=list)
    allowed_extensions: List[str] = field(default_factory=list)
    require_authentication: bool = True
    virus_scan_enabled: bool = True
    process_async: bool = True
    generate_thumbnails: bool = False
    storage_backend: str = "local"  # local, s3, gcs, azure

@dataclass
class UploadedFile:
    id: str
    original_filename: str
    content_type: str
    size: int
    file_hash: str
    upload_path: str
    public_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

class FileValidator:
    """Validates uploaded files for security and compliance"""

    def __init__(self, config: FileUploadConfig):
        self.config = config

    async def validate_file(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Comprehensive file validation"""
        errors = []
        warnings = []

        # Size validation
        if len(file_data) > self.config.max_file_size:
            errors.append(f"File size {len(file_data)} exceeds maximum {self.config.max_file_size}")

        # Extension validation
        if self.config.allowed_extensions:
            ext = Path(filename).suffix.lower()
            if ext not in self.config.allowed_extensions:
                errors.append(f"Extension {ext} not allowed")

        # MIME type validation
        detected_mime = magic.from_buffer(file_data, mime=True)
        if content_type != detected_mime:
            warnings.append(f"Declared MIME {content_type} differs from detected {detected_mime}")

        if self.config.allowed_mime_types and detected_mime not in self.config.allowed_mime_types:
            errors.append(f"MIME type {detected_mime} not allowed")

        # Malware scanning (placeholder for real implementation)
        if self.config.virus_scan_enabled:
            is_safe = await self._scan_for_malware(file_data)
            if not is_safe:
                errors.append("File failed malware scan")

        # Content-specific validation
        content_errors = await self._validate_content(file_data, detected_mime)
        errors.extend(content_errors)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "detected_mime": detected_mime,
            "file_size": len(file_data)
        }

    async def _scan_for_malware(self, file_data: bytes) -> bool:
        """Integrate with ClamAV or similar antivirus"""
        # Placeholder for actual malware scanning
        # In production, integrate with ClamAV daemon or cloud scanning service
        suspicious_patterns = [b"<script", b"javascript:", b"eval("]
        return not any(pattern in file_data.lower() for pattern in suspicious_patterns)

    async def _validate_content(self, file_data: bytes, mime_type: str) -> List[str]:
        """Content-specific validation based on file type"""
        errors = []

        if mime_type.startswith("image/"):
            errors.extend(await self._validate_image(file_data))
        elif mime_type == "application/pdf":
            errors.extend(await self._validate_pdf(file_data))
        elif mime_type.startswith("text/"):
            errors.extend(await self._validate_text(file_data))

        return errors

    async def _validate_image(self, file_data: bytes) -> List[str]:
        """Validate image files"""
        try:
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(file_data))

            # Check for suspicious metadata
            if hasattr(image, '_getexif') and image._getexif():
                # Remove or validate EXIF data
                pass

            # Validate image dimensions
            width, height = image.size
            if width > 10000 or height > 10000:
                return ["Image dimensions too large"]

        except Exception as e:
            return [f"Invalid image file: {str(e)}"]
        return []

    async def _validate_pdf(self, file_data: bytes) -> List[str]:
        """Validate PDF files"""
        # Check for PDF structure
        if not file_data.startswith(b"%PDF"):
            return ["Invalid PDF header"]

        # Check for embedded JavaScript (security risk)
        if b"/JavaScript" in file_data or b"/JS" in file_data:
            return ["PDF contains JavaScript"]

        return []

    async def _validate_text(self, file_data: bytes) -> List[str]:
        """Validate text files"""
        try:
            # Attempt to decode as UTF-8
            text = file_data.decode('utf-8')

            # Check for suspiciously long lines (potential attack)
            lines = text.split('\n')
            if any(len(line) > 10000 for line in lines):
                return ["Text file contains suspiciously long lines"]

        except UnicodeDecodeError:
            return ["Text file contains invalid UTF-8"]

        return []

class FileUploadService:
    """Main service for handling file uploads"""

    def __init__(self, storage_backends: Dict[str, Any], default_config: FileUploadConfig):
        self.storage_backends = storage_backends
        self.default_config = default_config
        self.validator = FileValidator(default_config)

    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        user_id: Optional[str] = None,
        config: Optional[FileUploadConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UploadedFile:
        """Process and store uploaded file"""

        config = config or self.default_config
        metadata = metadata or {}

        # Validate file
        validation_result = await self.validator.validate_file(file_data, filename, content_type)
        if not validation_result["valid"]:
            raise FileUploadError(f"Validation failed: {', '.join(validation_result['errors'])}")

        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        file_hash = hashlib.sha256(file_data).hexdigest()

        # Check for duplicate files
        existing_file = await self._check_duplicate(file_hash)
        if existing_file:
            return existing_file

        # Determine file type and storage path
        file_type = self._determine_file_type(validation_result["detected_mime"])
        storage_path = self._generate_storage_path(file_id, filename, file_type, user_id)

        # Store file
        storage_backend = self.storage_backends[config.storage_backend]
        public_url = await storage_backend.store_file(file_data, storage_path)

        # Create file record
        uploaded_file = UploadedFile(
            id=file_id,
            original_filename=filename,
            content_type=validation_result["detected_mime"],
            size=len(file_data),
            file_hash=file_hash,
            upload_path=storage_path,
            public_url=public_url,
            metadata={
                **metadata,
                "user_id": user_id,
                "validation_warnings": validation_result.get("warnings", [])
            }
        )

        # Save to database
        await self._save_file_record(uploaded_file)

        # Process asynchronously if configured
        if config.process_async:
            asyncio.create_task(self._process_file_async(uploaded_file, config))

        return uploaded_file

    async def _check_duplicate(self, file_hash: str) -> Optional[UploadedFile]:
        """Check if file already exists based on hash"""
        # Implementation would query database for existing file with same hash
        # This enables deduplication to save storage space
        pass

    def _determine_file_type(self, mime_type: str) -> FileType:
        """Determine file category from MIME type"""
        if mime_type.startswith("image/"):
            return FileType.IMAGE
        elif mime_type.startswith("video/"):
            return FileType.VIDEO
        elif mime_type.startswith("audio/"):
            return FileType.AUDIO
        elif mime_type in ["application/pdf", "text/plain", "application/msword"]:
            return FileType.DOCUMENT
        elif mime_type in ["application/zip", "application/x-rar", "application/x-tar"]:
            return FileType.ARCHIVE
        else:
            return FileType.DOCUMENT

    def _generate_storage_path(self, file_id: str, filename: str, file_type: FileType, user_id: Optional[str]) -> str:
        """Generate organized storage path"""
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        extension = Path(filename).suffix

        if user_id:
            return f"uploads/{file_type.value}/{user_id}/{date_path}/{file_id}{extension}"
        else:
            return f"uploads/{file_type.value}/anonymous/{date_path}/{file_id}{extension}"

    async def _save_file_record(self, file_record: UploadedFile):
        """Save file metadata to database"""
        # Implementation would save to your database
        # Include fields: id, original_filename, content_type, size, file_hash,
        # upload_path, public_url, metadata, created_at, user_id
        pass

    async def _process_file_async(self, uploaded_file: UploadedFile, config: FileUploadConfig):
        """Asynchronous post-upload processing"""
        try:
            if uploaded_file.content_type.startswith("image/") and config.generate_thumbnails:
                await self._generate_thumbnails(uploaded_file)

            # Extract metadata
            await self._extract_metadata(uploaded_file)

            # Mark as processed
            uploaded_file.processed = True
            await self._update_file_record(uploaded_file)

        except Exception as e:
            # Log error but don't fail the upload
            print(f"Async processing failed for {uploaded_file.id}: {e}")

    async def _generate_thumbnails(self, uploaded_file: UploadedFile):
        """Generate image thumbnails"""
        from PIL import Image
        import io

        # Download original file
        storage_backend = self.storage_backends[self.default_config.storage_backend]
        file_data = await storage_backend.retrieve_file(uploaded_file.upload_path)

        image = Image.open(io.BytesIO(file_data))

        # Generate different thumbnail sizes
        thumbnail_sizes = [(150, 150), (300, 300), (800, 600)]

        for width, height in thumbnail_sizes:
            thumbnail = image.copy()
            thumbnail.thumbnail((width, height), Image.Resampling.LANCZOS)

            # Save thumbnail
            thumb_buffer = io.BytesIO()
            thumbnail.save(thumb_buffer, format=image.format)

            thumb_path = uploaded_file.upload_path.replace(
                Path(uploaded_file.upload_path).suffix,
                f"_thumb_{width}x{height}{Path(uploaded_file.upload_path).suffix}"
            )

            await storage_backend.store_file(thumb_buffer.getvalue(), thumb_path)

    async def _extract_metadata(self, uploaded_file: UploadedFile):
        """Extract and store file metadata"""
        storage_backend = self.storage_backends[self.default_config.storage_backend]
        file_data = await storage_backend.retrieve_file(uploaded_file.upload_path)

        if uploaded_file.content_type.startswith("image/"):
            metadata = await self._extract_image_metadata(file_data)
        elif uploaded_file.content_type.startswith("video/"):
            metadata = await self._extract_video_metadata(file_data)
        else:
            metadata = {}

        # Update file record with metadata
        uploaded_file.metadata.update(metadata)

    async def _extract_image_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract EXIF and other image metadata"""
        from PIL import Image
        from PIL.ExifTags import TAGS
        import io

        try:
            image = Image.open(io.BytesIO(file_data))
            metadata = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode
            }

            # Extract EXIF data (be careful with privacy)
            if hasattr(image, '_getexif') and image._getexif():
                exif = {TAGS.get(k, k): v for k, v in image._getexif().items()}
                # Only include safe metadata, exclude GPS and personal info
                safe_exif = {k: v for k, v in exif.items()
                           if k not in ['GPS', 'UserComment', 'ImageDescription']}
                metadata["exif"] = safe_exif

            return metadata
        except Exception:
            return {}

    async def _extract_video_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract video metadata using ffprobe"""
        # Implementation would use ffmpeg-python or similar
        # to extract duration, resolution, codec, etc.
        return {}

class FileUploadError(Exception):
    pass
```

## FastAPI Upload Endpoints

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from typing import List, Optional
import aiofiles

app = FastAPI()
security = HTTPBearer()

# Initialize upload service
upload_service = FileUploadService(storage_backends, default_config)

@app.post("/upload/single")
async def upload_single_file(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    generate_thumbnails: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    token: str = Depends(security)
):
    """Upload a single file"""

    # Validate token and get user
    user = await validate_token(token.credentials)
    if not user and upload_service.default_config.require_authentication:
        raise HTTPException(401, "Authentication required")

    try:
        # Read file data
        file_data = await file.read()

        # Configure upload
        config = FileUploadConfig(
            generate_thumbnails=generate_thumbnails,
            process_async=True
        )

        # Upload file
        uploaded_file = await upload_service.upload_file(
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type,
            user_id=user.id if user else None,
            config=config
        )

        return {
            "file_id": uploaded_file.id,
            "filename": uploaded_file.original_filename,
            "size": uploaded_file.size,
            "content_type": uploaded_file.content_type,
            "public_url": uploaded_file.public_url,
            "upload_path": uploaded_file.upload_path
        }

    except FileUploadError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    user_id: Optional[str] = Form(None),
    token: str = Depends(security)
):
    """Upload multiple files"""

    user = await validate_token(token.credentials)
    if not user and upload_service.default_config.require_authentication:
        raise HTTPException(401, "Authentication required")

    if len(files) > 10:  # Limit batch uploads
        raise HTTPException(400, "Maximum 10 files per batch")

    results = []
    errors = []

    for file in files:
        try:
            file_data = await file.read()
            uploaded_file = await upload_service.upload_file(
                file_data=file_data,
                filename=file.filename,
                content_type=file.content_type,
                user_id=user.id if user else None
            )

            results.append({
                "file_id": uploaded_file.id,
                "filename": uploaded_file.original_filename,
                "size": uploaded_file.size,
                "status": "success"
            })

        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e),
                "status": "error"
            })

    return {
        "uploaded": results,
        "errors": errors,
        "total_files": len(files),
        "successful_uploads": len(results)
    }

@app.post("/upload/chunked")
async def upload_chunked_file(
    chunk: UploadFile = File(...),
    chunk_number: int = Form(...),
    total_chunks: int = Form(...),
    file_id: str = Form(...),
    filename: str = Form(...),
    token: str = Depends(security)
):
    """Handle chunked file uploads for large files"""

    user = await validate_token(token.credentials)
    if not user:
        raise HTTPException(401, "Authentication required")

    chunk_dir = f"/tmp/chunks/{file_id}"
    Path(chunk_dir).mkdir(parents=True, exist_ok=True)

    # Save chunk
    chunk_path = f"{chunk_dir}/chunk_{chunk_number}"
    async with aiofiles.open(chunk_path, "wb") as f:
        chunk_data = await chunk.read()
        await f.write(chunk_data)

    # Check if all chunks received
    existing_chunks = list(Path(chunk_dir).glob("chunk_*"))
    if len(existing_chunks) == total_chunks:
        # Reassemble file
        complete_file_data = b""
        for i in range(total_chunks):
            chunk_file = f"{chunk_dir}/chunk_{i}"
            async with aiofiles.open(chunk_file, "rb") as f:
                chunk_content = await f.read()
                complete_file_data += chunk_content

        # Upload complete file
        try:
            uploaded_file = await upload_service.upload_file(
                file_data=complete_file_data,
                filename=filename,
                content_type="application/octet-stream",  # Will be detected
                user_id=user.id
            )

            # Cleanup chunks
            import shutil
            shutil.rmtree(chunk_dir)

            return {
                "file_id": uploaded_file.id,
                "status": "complete",
                "filename": uploaded_file.original_filename,
                "size": uploaded_file.size
            }

        except Exception as e:
            # Cleanup on error
            import shutil
            shutil.rmtree(chunk_dir)
            raise HTTPException(500, f"Assembly failed: {str(e)}")

    return {
        "status": "chunk_received",
        "chunk_number": chunk_number,
        "total_chunks": total_chunks,
        "received_chunks": len(existing_chunks)
    }

@app.get("/files/{file_id}")
async def get_file_info(file_id: str, token: str = Depends(security)):
    """Get file information"""
    user = await validate_token(token.credentials)

    # Get file record from database
    file_record = await get_file_by_id(file_id)
    if not file_record:
        raise HTTPException(404, "File not found")

    # Check permissions
    if file_record.user_id != user.id and not user.is_admin:
        raise HTTPException(403, "Access denied")

    return {
        "file_id": file_record.id,
        "filename": file_record.original_filename,
        "content_type": file_record.content_type,
        "size": file_record.size,
        "public_url": file_record.public_url,
        "created_at": file_record.created_at,
        "processed": file_record.processed,
        "metadata": file_record.metadata
    }

@app.delete("/files/{file_id}")
async def delete_file(file_id: str, token: str = Depends(security)):
    """Delete uploaded file"""
    user = await validate_token(token.credentials)

    file_record = await get_file_by_id(file_id)
    if not file_record:
        raise HTTPException(404, "File not found")

    # Check permissions
    if file_record.user_id != user.id and not user.is_admin:
        raise HTTPException(403, "Access denied")

    # Delete from storage
    storage_backend = upload_service.storage_backends[upload_service.default_config.storage_backend]
    await storage_backend.delete_file(file_record.upload_path)

    # Delete from database
    await delete_file_record(file_id)

    return {"message": "File deleted successfully"}

async def validate_token(token: str):
    """Validate JWT token and return user"""
    # Implementation depends on your auth system
    pass

async def get_file_by_id(file_id: str):
    """Get file record from database"""
    # Implementation depends on your database
    pass

async def delete_file_record(file_id: str):
    """Delete file record from database"""
    # Implementation depends on your database
    pass
```

## Storage Backend Implementations

```python
from abc import ABC, abstractmethod
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs

class StorageBackend(ABC):
    @abstractmethod
    async def store_file(self, file_data: bytes, path: str) -> str:
        """Store file and return public URL"""
        pass

    @abstractmethod
    async def retrieve_file(self, path: str) -> bytes:
        """Retrieve file data"""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Delete file"""
        pass

class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str, public_url_base: str):
        self.base_path = Path(base_path)
        self.public_url_base = public_url_base.rstrip('/')

    async def store_file(self, file_data: bytes, path: str) -> str:
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_data)

        return f"{self.public_url_base}/{path}"

    async def retrieve_file(self, path: str) -> bytes:
        full_path = self.base_path / path
        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete_file(self, path: str) -> bool:
        full_path = self.base_path / path
        try:
            full_path.unlink()
            return True
        except FileNotFoundError:
            return False

class S3StorageBackend(StorageBackend):
    def __init__(self, bucket_name: str, aws_access_key: str, aws_secret_key: str, region: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

    async def store_file(self, file_data: bytes, path: str) -> str:
        # Run S3 upload in thread pool since boto3 is synchronous
        import asyncio
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(
            None,
            lambda: self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=path,
                Body=file_data,
                ContentType=self._guess_content_type(path)
            )
        )

        return f"https://{self.bucket_name}.s3.amazonaws.com/{path}"

    async def retrieve_file(self, path: str) -> bytes:
        import asyncio
        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: self.s3_client.get_object(Bucket=self.bucket_name, Key=path)
        )

        return response['Body'].read()

    async def delete_file(self, path: str) -> bool:
        import asyncio
        loop = asyncio.get_event_loop()

        try:
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(Bucket=self.bucket_name, Key=path)
            )
            return True
        except Exception:
            return False

    def _guess_content_type(self, path: str) -> str:
        content_type, _ = mimetypes.guess_type(path)
        return content_type or 'application/octet-stream'
```

## Testing File Uploads

```python
import pytest
from fastapi.testclient import TestClient
import tempfile
import io

class TestFileUpload:

    @pytest.fixture
    def upload_service(self):
        config = FileUploadConfig(
            max_file_size=1024 * 1024,  # 1MB for testing
            allowed_extensions=['.txt', '.jpg', '.png'],
            allowed_mime_types=['text/plain', 'image/jpeg', 'image/png']
        )

        storage_backends = {
            'local': LocalStorageBackend('/tmp/test_uploads', 'http://localhost/files')
        }

        return FileUploadService(storage_backends, config)

    async def test_valid_file_upload(self, upload_service):
        file_data = b"Test file content"
        filename = "test.txt"
        content_type = "text/plain"

        uploaded_file = await upload_service.upload_file(
            file_data, filename, content_type
        )

        assert uploaded_file.id is not None
        assert uploaded_file.original_filename == filename
        assert uploaded_file.size == len(file_data)
        assert uploaded_file.file_hash == hashlib.sha256(file_data).hexdigest()

    async def test_file_too_large(self, upload_service):
        large_file_data = b"x" * (2 * 1024 * 1024)  # 2MB

        with pytest.raises(FileUploadError):
            await upload_service.upload_file(
                large_file_data, "large.txt", "text/plain"
            )

    async def test_invalid_extension(self, upload_service):
        file_data = b"executable content"

        with pytest.raises(FileUploadError):
            await upload_service.upload_file(
                file_data, "malware.exe", "application/x-executable"
            )

    def test_upload_endpoint(self):
        client = TestClient(app)

        # Create test file
        test_file = io.BytesIO(b"Test file content")

        response = client.post(
            "/upload/single",
            files={"file": ("test.txt", test_file, "text/plain")},
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test.txt"

    def test_multiple_upload_endpoint(self):
        client = TestClient(app)

        files = [
            ("files", ("test1.txt", io.BytesIO(b"File 1"), "text/plain")),
            ("files", ("test2.txt", io.BytesIO(b"File 2"), "text/plain"))
        ]

        response = client.post(
            "/upload/multiple",
            files=files,
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["uploaded"]) == 2
        assert data["successful_uploads"] == 2

    async def test_image_validation(self, upload_service):
        # Create a simple PNG file
        from PIL import Image
        import io

        img = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()

        uploaded_file = await upload_service.upload_file(
            img_data, "test.png", "image/png"
        )

        assert uploaded_file.content_type == "image/png"
        assert uploaded_file.size == len(img_data)

    async def test_malicious_file_detection(self, upload_service):
        # File with suspicious content
        malicious_data = b'<script>alert("xss")</script>'

        with pytest.raises(FileUploadError):
            await upload_service.upload_file(
                malicious_data, "innocent.txt", "text/plain"
            )
```

## Related Documentation

- [Media Processing Patterns](media-processing-patterns.md) - Image/video processing workflows
- [Cloud Storage Integration](cloud-storage-integration.md) - AWS S3, Google Cloud, Azure storage
- [Backup Strategies](backup-strategies.md) - File backup and disaster recovery
- [Authentication Guide](../security/authentication-authorization-guide.md) - User authentication for uploads

## Implementation Notes

1. **Security First**: Always validate file types, scan for malware, and sanitize metadata
2. **Chunked Uploads**: Support large file uploads through chunking
3. **Async Processing**: Process thumbnails and metadata extraction asynchronously
4. **Deduplication**: Use file hashes to prevent storing duplicate files
5. **Storage Abstraction**: Support multiple storage backends through common interface
6. **Monitoring**: Log upload patterns and failures for security analysis