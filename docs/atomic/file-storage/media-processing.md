# Media Processing Workflows

Comprehensive guide for processing images, videos, and audio files with thumbnails, format conversion, optimization, and real-time processing pipelines.

## Core Media Processing Service

```python
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import subprocess
import tempfile
import aiofiles
from pathlib import Path
from datetime import datetime
import uuid

class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProcessingJob:
    id: str
    media_type: MediaType
    input_path: str
    output_specs: List[Dict[str, Any]]
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OutputSpec:
    """Specification for media output format"""
    format: str
    quality: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    maintain_aspect_ratio: bool = True
    filename_suffix: str = ""

class MediaProcessor:
    """Core media processing service with FFmpeg integration"""

    def __init__(self, storage_backend, temp_dir: str = "/tmp", max_concurrent_jobs: int = 5):
        self.storage_backend = storage_backend
        self.temp_dir = Path(temp_dir)
        self.semaphore = asyncio.Semaphore(max_concurrent_jobs)
        self.active_jobs: Dict[str, ProcessingJob] = {}

    async def process_media(
        self,
        input_path: str,
        output_specs: List[OutputSpec],
        media_type: MediaType,
        callback_url: Optional[str] = None
    ) -> ProcessingJob:
        """Queue media for processing"""

        job = ProcessingJob(
            id=str(uuid.uuid4()),
            media_type=media_type,
            input_path=input_path,
            output_specs=[self._spec_to_dict(spec) for spec in output_specs]
        )

        self.active_jobs[job.id] = job

        # Start processing asynchronously
        asyncio.create_task(self._process_job(job, callback_url))

        return job

    def _spec_to_dict(self, spec: OutputSpec) -> Dict[str, Any]:
        return {
            "format": spec.format,
            "quality": spec.quality,
            "width": spec.width,
            "height": spec.height,
            "maintain_aspect_ratio": spec.maintain_aspect_ratio,
            "filename_suffix": spec.filename_suffix
        }

    async def _process_job(self, job: ProcessingJob, callback_url: Optional[str]):
        """Process media job with error handling"""
        async with self.semaphore:
            try:
                job.status = ProcessingStatus.PROCESSING
                await self._update_job_progress(job, 0.1)

                # Download input file
                input_data = await self.storage_backend.retrieve_file(job.input_path)
                temp_input = self.temp_dir / f"{job.id}_input"

                async with aiofiles.open(temp_input, "wb") as f:
                    await f.write(input_data)

                # Process based on media type
                if job.media_type == MediaType.IMAGE:
                    outputs = await self._process_image(temp_input, job.output_specs, job)
                elif job.media_type == MediaType.VIDEO:
                    outputs = await self._process_video(temp_input, job.output_specs, job)
                elif job.media_type == MediaType.AUDIO:
                    outputs = await self._process_audio(temp_input, job.output_specs, job)

                # Upload outputs
                job.metadata["outputs"] = []
                for output_path, spec in outputs:
                    async with aiofiles.open(output_path, "rb") as f:
                        output_data = await f.read()

                    storage_path = self._generate_output_path(job.input_path, spec["filename_suffix"])
                    public_url = await self.storage_backend.store_file(output_data, storage_path)

                    job.metadata["outputs"].append({
                        "spec": spec,
                        "path": storage_path,
                        "url": public_url,
                        "size": len(output_data)
                    })

                    # Cleanup temp file
                    output_path.unlink()

                job.status = ProcessingStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                await self._update_job_progress(job, 1.0)

                # Cleanup input temp file
                temp_input.unlink()

                # Send callback if provided
                if callback_url:
                    await self._send_callback(callback_url, job)

            except Exception as e:
                job.status = ProcessingStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()

                # Cleanup temp files
                try:
                    temp_input.unlink()
                except:
                    pass

    async def _process_image(self, input_path: Path, output_specs: List[Dict], job: ProcessingJob) -> List[Tuple[Path, Dict]]:
        """Process image using Pillow"""
        from PIL import Image, ImageFilter, ImageEnhance
        import io

        outputs = []

        # Load image
        with Image.open(input_path) as img:
            # Extract metadata
            job.metadata["original"] = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode
            }

            for i, spec in enumerate(output_specs):
                await self._update_job_progress(job, 0.2 + (i * 0.6 / len(output_specs)))

                processed_img = img.copy()

                # Resize if specified
                if spec.get("width") or spec.get("height"):
                    new_size = self._calculate_resize(
                        img.width, img.height,
                        spec.get("width"), spec.get("height"),
                        spec.get("maintain_aspect_ratio", True)
                    )
                    processed_img = processed_img.resize(new_size, Image.Resampling.LANCZOS)

                # Apply format-specific optimizations
                if spec["format"].lower() in ["jpeg", "jpg"]:
                    # JPEG optimization
                    processed_img = processed_img.convert("RGB")
                    if spec.get("quality"):
                        save_kwargs = {"quality": spec["quality"], "optimize": True}
                    else:
                        save_kwargs = {"quality": 85, "optimize": True}
                elif spec["format"].lower() == "png":
                    # PNG optimization
                    save_kwargs = {"optimize": True}
                elif spec["format"].lower() == "webp":
                    # WebP optimization
                    save_kwargs = {"quality": spec.get("quality", 80), "method": 6}
                else:
                    save_kwargs = {}

                # Save processed image
                output_path = self.temp_dir / f"{job.id}_output_{i}.{spec['format'].lower()}"
                processed_img.save(output_path, format=spec["format"], **save_kwargs)

                outputs.append((output_path, spec))

        return outputs

    async def _process_video(self, input_path: Path, output_specs: List[Dict], job: ProcessingJob) -> List[Tuple[Path, Dict]]:
        """Process video using FFmpeg"""
        outputs = []

        # Extract video metadata first
        metadata_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams",
            str(input_path)
        ]

        result = await self._run_command(metadata_cmd)
        metadata = json.loads(result.stdout)

        video_stream = next((s for s in metadata["streams"] if s["codec_type"] == "video"), None)
        if video_stream:
            job.metadata["original"] = {
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "duration": float(metadata["format"].get("duration", 0)),
                "codec": video_stream.get("codec_name"),
                "fps": eval(video_stream.get("r_frame_rate", "0/1"))
            }

        for i, spec in enumerate(output_specs):
            await self._update_job_progress(job, 0.2 + (i * 0.6 / len(output_specs)))

            output_path = self.temp_dir / f"{job.id}_output_{i}.{spec['format'].lower()}"

            # Build FFmpeg command
            cmd = ["ffmpeg", "-i", str(input_path)]

            # Video codec and quality settings
            if spec["format"].lower() == "mp4":
                cmd.extend(["-c:v", "libx264", "-preset", "medium"])
                if spec.get("quality"):
                    cmd.extend(["-crf", str(spec["quality"])])
                else:
                    cmd.extend(["-crf", "23"])  # Default quality
            elif spec["format"].lower() == "webm":
                cmd.extend(["-c:v", "libvpx-vp9", "-crf", str(spec.get("quality", 30))])

            # Resize if specified
            if spec.get("width") or spec.get("height"):
                if spec.get("maintain_aspect_ratio", True):
                    scale_filter = f"scale={spec.get('width', -1)}:{spec.get('height', -1)}"
                else:
                    scale_filter = f"scale={spec.get('width')}:{spec.get('height')}"
                cmd.extend(["-vf", scale_filter])

            # Audio codec
            cmd.extend(["-c:a", "aac", "-b:a", "128k"])

            # Output file
            cmd.extend(["-y", str(output_path)])

            # Execute FFmpeg
            await self._run_command_with_progress(cmd, job, metadata["format"].get("duration"))

            outputs.append((output_path, spec))

        return outputs

    async def _process_audio(self, input_path: Path, output_specs: List[Dict], job: ProcessingJob) -> List[Tuple[Path, Dict]]:
        """Process audio using FFmpeg"""
        outputs = []

        # Extract audio metadata
        metadata_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams",
            str(input_path)
        ]

        result = await self._run_command(metadata_cmd)
        metadata = json.loads(result.stdout)

        audio_stream = next((s for s in metadata["streams"] if s["codec_type"] == "audio"), None)
        if audio_stream:
            job.metadata["original"] = {
                "duration": float(metadata["format"].get("duration", 0)),
                "codec": audio_stream.get("codec_name"),
                "sample_rate": int(audio_stream.get("sample_rate", 0)),
                "channels": int(audio_stream.get("channels", 0))
            }

        for i, spec in enumerate(output_specs):
            await self._update_job_progress(job, 0.2 + (i * 0.6 / len(output_specs)))

            output_path = self.temp_dir / f"{job.id}_output_{i}.{spec['format'].lower()}"

            # Build FFmpeg command
            cmd = ["ffmpeg", "-i", str(input_path)]

            # Audio codec and quality settings
            if spec["format"].lower() == "mp3":
                cmd.extend(["-c:a", "libmp3lame"])
                if spec.get("quality"):
                    cmd.extend(["-q:a", str(spec["quality"])])  # VBR quality 0-9
                else:
                    cmd.extend(["-b:a", "192k"])  # Default bitrate
            elif spec["format"].lower() == "aac":
                cmd.extend(["-c:a", "aac", "-b:a", f"{spec.get('quality', 128)}k"])
            elif spec["format"].lower() == "ogg":
                cmd.extend(["-c:a", "libvorbis", "-q:a", str(spec.get("quality", 5))])

            # Output file
            cmd.extend(["-y", str(output_path)])

            # Execute FFmpeg
            await self._run_command_with_progress(cmd, job, metadata["format"].get("duration"))

            outputs.append((output_path, spec))

        return outputs

    async def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run subprocess command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Command failed: {stderr.decode()}")

        return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)

    async def _run_command_with_progress(self, cmd: List[str], job: ProcessingJob, duration: Optional[float]):
        """Run FFmpeg command with progress tracking"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Monitor progress if duration is available
        if duration:
            asyncio.create_task(self._monitor_ffmpeg_progress(process, job, duration))

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

    async def _monitor_ffmpeg_progress(self, process, job: ProcessingJob, total_duration: float):
        """Monitor FFmpeg progress through stderr output"""
        import re

        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

        while process.returncode is None:
            try:
                line = await asyncio.wait_for(process.stderr.readline(), timeout=1.0)
                if not line:
                    break

                line_str = line.decode()
                match = time_pattern.search(line_str)
                if match:
                    hours, minutes, seconds = match.groups()
                    current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    progress = min(current_time / total_duration, 0.95)  # Cap at 95% until complete
                    await self._update_job_progress(job, 0.2 + progress * 0.6)

            except asyncio.TimeoutError:
                continue

    def _calculate_resize(self, orig_width: int, orig_height: int, new_width: Optional[int],
                         new_height: Optional[int], maintain_aspect: bool) -> Tuple[int, int]:
        """Calculate new dimensions for resizing"""
        if not maintain_aspect:
            return (new_width or orig_width, new_height or orig_height)

        aspect_ratio = orig_width / orig_height

        if new_width and new_height:
            # Fit within bounds
            if new_width / new_height > aspect_ratio:
                return (int(new_height * aspect_ratio), new_height)
            else:
                return (new_width, int(new_width / aspect_ratio))
        elif new_width:
            return (new_width, int(new_width / aspect_ratio))
        elif new_height:
            return (int(new_height * aspect_ratio), new_height)
        else:
            return (orig_width, orig_height)

    def _generate_output_path(self, input_path: str, suffix: str) -> str:
        """Generate output storage path"""
        path_obj = Path(input_path)
        stem = path_obj.stem
        parent = path_obj.parent
        return str(parent / f"{stem}{suffix}")

    async def _update_job_progress(self, job: ProcessingJob, progress: float):
        """Update job progress and notify if needed"""
        job.progress = progress
        # Here you could emit websocket updates or save to database
        print(f"Job {job.id}: {progress:.1%} complete")

    async def _send_callback(self, url: str, job: ProcessingJob):
        """Send job completion callback"""
        import aiohttp

        payload = {
            "job_id": job.id,
            "status": job.status.value,
            "outputs": job.metadata.get("outputs", []),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as response:
                    if response.status >= 400:
                        print(f"Callback failed: {response.status}")
            except Exception as e:
                print(f"Callback error: {e}")

    def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get current job status"""
        return self.active_jobs.get(job_id)
```

## Image Processing Pipelines

```python
class ImageProcessingPipeline:
    """Specialized image processing with filters and effects"""

    def __init__(self, media_processor: MediaProcessor):
        self.processor = media_processor

    async def create_thumbnails(self, input_path: str, user_id: str) -> ProcessingJob:
        """Generate standard thumbnail sizes"""
        output_specs = [
            OutputSpec(format="jpeg", width=150, height=150, filename_suffix="_thumb_150"),
            OutputSpec(format="jpeg", width=300, height=300, filename_suffix="_thumb_300"),
            OutputSpec(format="jpeg", width=800, height=600, filename_suffix="_thumb_800"),
            OutputSpec(format="webp", width=300, height=300, filename_suffix="_thumb_300_webp")
        ]

        return await self.processor.process_media(
            input_path, output_specs, MediaType.IMAGE
        )

    async def optimize_for_web(self, input_path: str) -> ProcessingJob:
        """Optimize images for web delivery"""
        output_specs = [
            OutputSpec(format="jpeg", quality=85, filename_suffix="_optimized"),
            OutputSpec(format="webp", quality=80, filename_suffix="_webp"),
            OutputSpec(format="avif", quality=75, filename_suffix="_avif")  # Modern format
        ]

        return await self.processor.process_media(
            input_path, output_specs, MediaType.IMAGE
        )

    async def apply_filters(self, input_path: str, filters: List[str]) -> ProcessingJob:
        """Apply Instagram-style filters"""
        # This would extend the image processing to include PIL filters
        # Implementation would modify _process_image to apply specific filters
        pass

class VideoProcessingPipeline:
    """Specialized video processing workflows"""

    def __init__(self, media_processor: MediaProcessor):
        self.processor = media_processor

    async def create_streaming_formats(self, input_path: str) -> ProcessingJob:
        """Create multiple formats for adaptive streaming"""
        output_specs = [
            # Different quality levels for adaptive streaming
            OutputSpec(format="mp4", width=1920, height=1080, quality=23, filename_suffix="_1080p"),
            OutputSpec(format="mp4", width=1280, height=720, quality=25, filename_suffix="_720p"),
            OutputSpec(format="mp4", width=854, height=480, quality=28, filename_suffix="_480p"),
            OutputSpec(format="webm", width=1280, height=720, quality=30, filename_suffix="_720p_webm")
        ]

        return await self.processor.process_media(
            input_path, output_specs, MediaType.VIDEO
        )

    async def extract_thumbnail(self, input_path: str, timestamp: float = 1.0) -> ProcessingJob:
        """Extract video thumbnail at specific timestamp"""
        # This would require extending FFmpeg commands to extract frames
        pass

    async def create_gif_preview(self, input_path: str, start_time: float = 0, duration: float = 3) -> ProcessingJob:
        """Create animated GIF preview from video"""
        # FFmpeg command to create GIF from video segment
        pass
```

## FastAPI Integration

```python
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import StreamingResponse
import aiohttp

app = FastAPI()

# Initialize processor
media_processor = MediaProcessor(storage_backend, max_concurrent_jobs=10)
image_pipeline = ImageProcessingPipeline(media_processor)
video_pipeline = VideoProcessingPipeline(media_processor)

@app.post("/media/process")
async def process_media(
    input_path: str,
    media_type: str,
    output_formats: List[Dict[str, Any]],
    callback_url: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Start media processing job"""

    # Convert output_formats to OutputSpec objects
    output_specs = []
    for fmt in output_formats:
        spec = OutputSpec(
            format=fmt["format"],
            quality=fmt.get("quality"),
            width=fmt.get("width"),
            height=fmt.get("height"),
            filename_suffix=fmt.get("suffix", "")
        )
        output_specs.append(spec)

    # Validate file access
    if not await user_can_access_file(user.id, input_path):
        raise HTTPException(403, "Access denied")

    job = await media_processor.process_media(
        input_path,
        output_specs,
        MediaType(media_type),
        callback_url
    )

    return {
        "job_id": job.id,
        "status": job.status.value,
        "estimated_completion": "2-5 minutes"  # Based on file size and complexity
    }

@app.get("/media/jobs/{job_id}")
async def get_job_status(job_id: str, user: User = Depends(get_current_user)):
    """Get processing job status"""

    job = media_processor.get_job_status(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "job_id": job.id,
        "status": job.status.value,
        "progress": job.progress,
        "error": job.error_message,
        "outputs": job.metadata.get("outputs", []),
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }

@app.post("/media/thumbnails")
async def generate_thumbnails(
    input_path: str,
    user: User = Depends(get_current_user)
):
    """Quick thumbnail generation endpoint"""

    if not await user_can_access_file(user.id, input_path):
        raise HTTPException(403, "Access denied")

    job = await image_pipeline.create_thumbnails(input_path, user.id)

    return {
        "job_id": job.id,
        "message": "Thumbnail generation started"
    }

@app.post("/media/optimize")
async def optimize_for_web(
    input_path: str,
    user: User = Depends(get_current_user)
):
    """Optimize images for web delivery"""

    job = await image_pipeline.optimize_for_web(input_path)

    return {
        "job_id": job.id,
        "message": "Web optimization started"
    }

@app.post("/video/streaming")
async def create_streaming_versions(
    input_path: str,
    user: User = Depends(get_current_user)
):
    """Create multiple video formats for streaming"""

    job = await video_pipeline.create_streaming_formats(input_path)

    return {
        "job_id": job.id,
        "message": "Streaming format creation started"
    }

@app.websocket("/media/jobs/{job_id}/progress")
async def job_progress_websocket(websocket: WebSocket, job_id: str):
    """Real-time job progress updates"""
    await websocket.accept()

    try:
        while True:
            job = media_processor.get_job_status(job_id)
            if not job:
                await websocket.send_json({"error": "Job not found"})
                break

            await websocket.send_json({
                "job_id": job.id,
                "status": job.status.value,
                "progress": job.progress,
                "error": job.error_message
            })

            if job.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
                break

            await asyncio.sleep(1)

    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
```

## Real-time Processing with WebRTC

```python
import aiortc
from aiortc import VideoStreamTrack, RTCPeerConnection

class MediaProcessingTrack(VideoStreamTrack):
    """Real-time video processing track for WebRTC"""

    def __init__(self, track, processor_func):
        super().__init__()
        self.track = track
        self.processor_func = processor_func

    async def recv(self):
        frame = await self.track.recv()

        # Apply real-time processing
        processed_frame = await self.processor_func(frame)

        return processed_frame

async def apply_real_time_filter(frame):
    """Apply real-time filters to video frame"""
    # Convert aiortc frame to PIL Image
    import cv2
    import numpy as np

    # Convert frame to numpy array
    img = frame.to_ndarray(format="bgr24")

    # Apply OpenCV filters
    img = cv2.GaussianBlur(img, (15, 15), 0)  # Blur filter
    # img = cv2.Canny(img, 100, 200)  # Edge detection

    # Convert back to aiortc frame
    new_frame = aiortc.VideoFrame.from_ndarray(img, format="bgr24")
    new_frame.pts = frame.pts
    new_frame.time_base = frame.time_base

    return new_frame

@app.websocket("/rtc/connect")
async def webrtc_endpoint(websocket: WebSocket):
    """WebRTC endpoint for real-time media processing"""
    await websocket.accept()

    pc = RTCPeerConnection()

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            # Add processed track
            processed_track = MediaProcessingTrack(track, apply_real_time_filter)
            pc.addTrack(processed_track)

    # Handle WebRTC signaling
    async for message in websocket.iter_json():
        if message["type"] == "offer":
            offer = RTCSessionDescription(sdp=message["sdp"], type=message["type"])
            await pc.setRemoteDescription(offer)

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            await websocket.send_json({
                "type": answer.type,
                "sdp": answer.sdp
            })
```

## Testing Media Processing

```python
import pytest
import tempfile
from PIL import Image
import subprocess

class TestMediaProcessing:

    @pytest.fixture
    async def media_processor(self):
        from unittest.mock import AsyncMock
        storage_backend = AsyncMock()
        return MediaProcessor(storage_backend, max_concurrent_jobs=2)

    async def test_image_thumbnail_generation(self, media_processor):
        # Create test image
        img = Image.new('RGB', (1000, 800), color='red')
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            img.save(f.name, 'JPEG')
            input_path = f.name

        output_specs = [
            OutputSpec(format="jpeg", width=300, height=300, filename_suffix="_thumb")
        ]

        # Mock storage backend
        media_processor.storage_backend.retrieve_file.return_value = open(input_path, 'rb').read()
        media_processor.storage_backend.store_file.return_value = "http://example.com/thumb.jpg"

        job = await media_processor.process_media(
            input_path, output_specs, MediaType.IMAGE
        )

        # Wait for processing
        while job.status == ProcessingStatus.PROCESSING:
            await asyncio.sleep(0.1)

        assert job.status == ProcessingStatus.COMPLETED
        assert len(job.metadata["outputs"]) == 1

    async def test_video_format_conversion(self, media_processor):
        # This test would require a sample video file
        # In practice, you'd use a small test video
        pass

    def test_image_optimization_quality(self):
        """Test image quality optimization"""
        # Create test image
        img = Image.new('RGB', (1000, 1000), color='blue')
        original_buffer = io.BytesIO()
        img.save(original_buffer, format='JPEG', quality=100)
        original_size = original_buffer.tell()

        # Optimize
        optimized_buffer = io.BytesIO()
        img.save(optimized_buffer, format='JPEG', quality=85, optimize=True)
        optimized_size = optimized_buffer.tell()

        # Should be smaller
        assert optimized_size < original_size
        assert optimized_size / original_size < 0.8  # At least 20% reduction

    def test_video_metadata_extraction(self):
        """Test FFmpeg metadata extraction"""
        # This would test the actual FFmpeg integration
        # Requires sample video file for testing
        pass
```

## Related Documentation

- [File Upload Patterns](upload-patterns.md) - File upload and validation
- [Cloud Storage Integration](cloud-storage-integration.md) - Storage backends
- [Backup Strategies](backup-strategies.md) - Media backup and archival
- [External Integrations](../external-integrations/) - Third-party media services

## Implementation Notes

1. **Async Processing**: Always process media asynchronously to avoid blocking
2. **Progress Tracking**: Provide real-time progress updates for long operations
3. **Format Support**: Support modern formats (WebP, AVIF) for better compression
4. **Quality Control**: Balance file size and quality based on use case
5. **Resource Management**: Limit concurrent jobs to prevent resource exhaustion
6. **Error Handling**: Robust error handling with detailed error messages
7. **Security**: Validate input files and sanitize metadata
8. **Monitoring**: Track processing times and resource usage for optimization