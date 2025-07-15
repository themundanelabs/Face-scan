from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ImageData(BaseModel):
    step: int = Field(..., ge=0, le=2, description="Capture step: 0=front, 1=left, 2=right")
    data: str = Field(..., description="Base64 encoded image data")
    timestamp: str = Field(..., description="ISO timestamp of capture")

class FaceAnalysisRequest(BaseModel):
    images: List[ImageData] = Field(..., min_items=1, max_items=3, description="Captured images")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    @validator('images')
    def validate_images(cls, v):
        if not v:
            raise ValueError("At least one image is required")
        
        # Check for duplicate steps
        steps = [img.step for img in v]
        if len(set(steps)) != len(steps):
            raise ValueError("Duplicate steps found in images")
        
        return v

class ColorAnalysis(BaseModel):
    skin_tone: str = Field(..., description="Skin tone HEX color")
    eye_color: str = Field(..., description="Eye color HEX color") 
    lip_color: str = Field(..., description="Lip color HEX color")
    hair_color: str = Field(..., description="Hair color HEX color")
    
    @validator('skin_tone', 'eye_color', 'lip_color', 'hair_color')
    def validate_hex_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError("Invalid HEX color format")
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError("Invalid HEX color value")
        return v

class AnalysisMetadata(BaseModel):
    total_images: int = Field(..., description="Total number of images processed")
    images_analyzed: int = Field(..., description="Number of images with detected faces")
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")
    algorithm: str = Field(default="MediaPipe + K-means clustering", description="Analysis algorithm used")
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0, description="Overall confidence score")

class FaceAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether analysis was successful")
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analysis ID")
    colors: Optional[ColorAnalysis] = Field(None, description="Extracted color analysis")
    metadata: Optional[AnalysisMetadata] = Field(None, description="Analysis metadata")
    error: Optional[str] = Field(None, description="Error message if analysis failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class AnalysisRecord(BaseModel):
    """Database model for storing analysis results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = Field(None)
    colors: ColorAnalysis
    metadata: AnalysisMetadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)

class AnalysisStats(BaseModel):
    """Statistics model for analysis tracking"""
    total_analyses: int = Field(default=0)
    successful_analyses: int = Field(default=0)
    failed_analyses: int = Field(default=0)
    average_processing_time: float = Field(default=0.0)
    most_common_skin_tones: List[str] = Field(default=[])
    most_common_eye_colors: List[str] = Field(default=[])
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)