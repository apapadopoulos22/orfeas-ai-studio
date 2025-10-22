"""
API Models for ORFEAS Backend
Pydantic models for request/response validation and documentation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import re

class OutputFormat(str, Enum):
    """Supported output formats for 3D models"""
    STL = "stl"
    OBJ = "obj"
    PLY = "ply"
    GLTF = "gltf"
    FBX = "fbx"
    PNG = "png"
    SVG = "svg"
    RAW = "raw"

class ArtStyle(str, Enum):
    """Available art styles for text-to-image generation"""
    REALISTIC = "realistic"
    ARTISTIC = "artistic"
    ANIME = "anime"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    MINIMALIST = "minimalist"
    PHOTOGRAPHIC = "photographic"
    DIGITAL_ART = "digital_art"

class JobStatus(str, Enum):
    """Job processing status"""
    QUEUED = "queued"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    GENERATING = "generating"
    GENERATING_3D = "generating_3d"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ModelDimensions(BaseModel):
    """3D model dimensions in millimeters"""
    width: float = Field(default=100.0, ge=1.0, le=500.0, description="Width in mm")
    height: float = Field(default=100.0, ge=1.0, le=500.0, description="Height in mm")
    depth: float = Field(default=20.0, ge=1.0, le=500.0, description="Depth in mm")

class ImageUploadRequest(BaseModel):
    """Request model for image upload"""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the image")
    file_size: int = Field(..., ge=1, le=50*1024*1024, description="File size in bytes")

class ImageUploadResponse(BaseModel):
    """Response model for image upload"""
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Stored filename")
    status: str = Field(..., description="Upload status")
    image_info: Dict[str, Any] = Field(..., description="Image metadata")

class TextToImageRequest(BaseModel):
    """Request model for text-to-image generation"""
    prompt: str = Field(..., min_length=1, max_length=500, description="Text prompt for image generation")
    style: ArtStyle = Field(default=ArtStyle.REALISTIC, description="Art style for generation")
    width: int = Field(default=512, ge=256, le=1024, description="Image width in pixels")
    height: int = Field(default=512, ge=256, le=1024, description="Image height in pixels")
    steps: int = Field(default=50, ge=10, le=100, description="Number of generation steps")
    guidance_scale: float = Field(default=7.0, ge=1.0, le=20.0, description="Guidance scale for generation")
    seed: Optional[int] = Field(default=None, ge=0, description="Random seed for reproducible results")
    negative_prompt: Optional[str] = Field(default=None, max_length=200, description="Negative prompt")

    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or v.isspace():
            raise ValueError('Prompt cannot be empty or whitespace only')
        # Remove excessive whitespace
        return re.sub(r'\s+', ' ', v.strip())

class TextToImageResponse(BaseModel):
    """Response model for text-to-image generation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Generation status")
    prompt: str = Field(..., description="Text prompt used")
    style: ArtStyle = Field(..., description="Art style used")

class Generate3DRequest(BaseModel):
    """Request model for 3D model generation"""
    job_id: str = Field(..., description="Job ID from image upload or text-to-image")
    format: OutputFormat = Field(default=OutputFormat.STL, description="Output format for 3D model")
    dimensions: ModelDimensions = Field(default_factory=ModelDimensions, description="Model dimensions")
    quality: int = Field(default=7, ge=1, le=10, description="Generation quality (1=draft, 10=high)")
    texture: bool = Field(default=False, description="Generate textured model")
    steps: int = Field(default=50, ge=10, le=100, description="Number of 3D generation steps")

class Generate3DResponse(BaseModel):
    """Response model for 3D generation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Generation status")
    format: OutputFormat = Field(..., description="Output format")
    dimensions: ModelDimensions = Field(..., description="Model dimensions")

class JobProgressUpdate(BaseModel):
    """WebSocket progress update model"""
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current status")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    step: str = Field(..., description="Current processing step")
    eta_seconds: Optional[int] = Field(default=None, description="Estimated time remaining in seconds")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class JobStatusResponse(BaseModel):
    """Response model for job status query"""
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current status")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    step: str = Field(..., description="Current processing step")
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    output_file: Optional[str] = Field(default=None, description="Output filename if completed")
    download_url: Optional[str] = Field(default=None, description="Download URL if completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional job metadata")

class SystemInfoResponse(BaseModel):
    """Response model for system information"""
    gpu: Dict[str, Any] = Field(..., description="GPU information")
    cpu: Dict[str, Any] = Field(..., description="CPU information")
    memory: Dict[str, Any] = Field(..., description="Memory information")
    active_jobs: int = Field(..., description="Number of active jobs")
    queue_length: int = Field(..., description="Number of queued jobs")
    uptime_seconds: int = Field(..., description="Server uptime in seconds")

class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Server status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")
    gpu_info: Dict[str, Any] = Field(..., description="GPU availability info")
    active_jobs: int = Field(..., description="Number of active jobs")
    queue_length: int = Field(..., description="Number of queued jobs")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    timestamp: str = Field(..., description="Error timestamp")
    job_id: Optional[str] = Field(default=None, description="Related job ID if applicable")

class FileListResponse(BaseModel):
    """Response model for file listing"""
    files: List[Dict[str, Any]] = Field(..., description="List of files")
    total_count: int = Field(..., description="Total number of files")
    total_size_bytes: int = Field(..., description="Total size in bytes")

class ModelInfo(BaseModel):
    """Information about loaded AI models"""
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type (text-to-image, image-to-3d, etc.)")
    status: str = Field(..., description="Loading status")
    device: str = Field(..., description="Device (cuda/cpu)")
    memory_usage_mb: Optional[float] = Field(default=None, description="Memory usage in MB")
    version: Optional[str] = Field(default=None, description="Model version")

class ModelsInfoResponse(BaseModel):
    """Response model for models information"""
    models: List[ModelInfo] = Field(..., description="List of loaded models")
    total_memory_usage_mb: float = Field(..., description="Total memory usage")
    hunyuan3d_available: bool = Field(..., description="Whether Hunyuan3D is available")

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: str = Field(..., description="Message timestamp")

class BatchProcessRequest(BaseModel):
    """Request model for batch processing multiple images"""
    job_ids: List[str] = Field(..., min_items=1, max_items=10, description="List of job IDs to process")
    format: OutputFormat = Field(default=OutputFormat.STL, description="Output format for all models")
    dimensions: ModelDimensions = Field(default_factory=ModelDimensions, description="Dimensions for all models")
    quality: int = Field(default=7, ge=1, le=10, description="Quality for all models")

class BatchProcessResponse(BaseModel):
    """Response model for batch processing"""
    batch_id: str = Field(..., description="Batch processing ID")
    job_ids: List[str] = Field(..., description="Individual job IDs")
    status: JobStatus = Field(..., description="Batch status")
    total_jobs: int = Field(..., description="Total number of jobs in batch")

# Request/Response type aliases for better type hints
ApiResponse = Union[
    ImageUploadResponse,
    TextToImageResponse,
    Generate3DResponse,
    JobStatusResponse,
    SystemInfoResponse,
    HealthCheckResponse,
    ErrorResponse,
    FileListResponse,
    ModelsInfoResponse,
    BatchProcessResponse
]

ApiRequest = Union[
    ImageUploadRequest,
    TextToImageRequest,
    Generate3DRequest,
    BatchProcessRequest
]
