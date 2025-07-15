from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import logging
import time
from datetime import datetime

from models.analysis import (
    FaceAnalysisRequest, 
    FaceAnalysisResponse, 
    ColorAnalysis, 
    AnalysisMetadata,
    AnalysisRecord
)
from services.face_analyzer import FaceAnalyzer
from server import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Initialize face analyzer
face_analyzer = FaceAnalyzer()

@router.post("/analyze-face", response_model=FaceAnalysisResponse)
async def analyze_face(request: FaceAnalysisRequest, http_request: Request):
    """
    Analyze facial features from uploaded images and extract color palette
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting face analysis for {len(request.images)} images")
        
        # Extract base64 image data
        image_data = [img.data for img in request.images]
        
        # Perform face analysis
        analysis_result = face_analyzer.analyze_multiple_images(image_data)
        
        processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        if not analysis_result['success']:
            logger.error(f"Face analysis failed: {analysis_result.get('error', 'Unknown error')}")
            return FaceAnalysisResponse(
                success=False,
                error=analysis_result.get('error', 'Analysis failed'),
                metadata=AnalysisMetadata(
                    total_images=len(request.images),
                    images_analyzed=0,
                    processing_time_ms=processing_time
                )
            )
        
        # Create color analysis result
        colors = ColorAnalysis(
            skin_tone=analysis_result['results']['skin_tone'],
            eye_color=analysis_result['results']['eye_color'],
            lip_color=analysis_result['results']['lip_color'],
            hair_color=analysis_result['results']['hair_color']
        )
        
        # Create metadata
        metadata = AnalysisMetadata(
            total_images=analysis_result['total_images'],
            images_analyzed=analysis_result['images_analyzed'],
            processing_time_ms=processing_time,
            confidence_score=0.85 + (analysis_result['images_analyzed'] / analysis_result['total_images']) * 0.15
        )
        
        # Create response
        response = FaceAnalysisResponse(
            success=True,
            colors=colors,
            metadata=metadata
        )
        
        # Store analysis in database
        try:
            analysis_record = AnalysisRecord(
                session_id=request.session_id,
                colors=colors,
                metadata=metadata,
                ip_address=http_request.client.host,
                user_agent=http_request.headers.get("user-agent")
            )
            
            await db.face_analyses.insert_one(analysis_record.dict())
            logger.info(f"Analysis record stored with ID: {analysis_record.id}")
            
        except Exception as e:
            logger.error(f"Error storing analysis record: {e}")
            # Don't fail the request if database storage fails
        
        logger.info(f"Face analysis completed successfully in {processing_time}ms")
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error during face analysis: {e}")
        processing_time = int((time.time() - start_time) * 1000)
        
        return FaceAnalysisResponse(
            success=False,
            error=f"Analysis failed: {str(e)}",
            metadata=AnalysisMetadata(
                total_images=len(request.images),
                images_analyzed=0,
                processing_time_ms=processing_time
            )
        )

@router.get("/stats")
async def get_analysis_stats():
    """Get analysis statistics"""
    try:
        # Get total count
        total_count = await db.face_analyses.count_documents({})
        
        # Get successful analyses
        successful_count = await db.face_analyses.count_documents({"colors": {"$exists": True}})
        
        # Get recent analyses for common colors
        recent_analyses = await db.face_analyses.find(
            {"colors": {"$exists": True}},
            {"colors": 1}
        ).limit(100).to_list(100)
        
        skin_tones = [analysis["colors"]["skin_tone"] for analysis in recent_analyses]
        eye_colors = [analysis["colors"]["eye_color"] for analysis in recent_analyses]
        
        # Get most common colors (simple approach)
        from collections import Counter
        common_skin_tones = [color for color, count in Counter(skin_tones).most_common(5)]
        common_eye_colors = [color for color, count in Counter(eye_colors).most_common(5)]
        
        return {
            "total_analyses": total_count,
            "successful_analyses": successful_count,
            "failed_analyses": total_count - successful_count,
            "success_rate": (successful_count / total_count * 100) if total_count > 0 else 0,
            "most_common_skin_tones": common_skin_tones,
            "most_common_eye_colors": common_eye_colors
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analysis statistics")

@router.get("/history/{session_id}")
async def get_analysis_history(session_id: str):
    """Get analysis history for a specific session"""
    try:
        analyses = await db.face_analyses.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(10)
        
        return {
            "session_id": session_id,
            "analyses": analyses,
            "count": len(analyses)
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analysis history")