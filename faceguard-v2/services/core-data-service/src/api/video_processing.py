"""
FACEGUARD V2 CORE DATA SERVICE - VIDEO PROCESSING API
Rule 1: Incremental Completeness - Video processing endpoints built to 100% functionality
Rule 2: Zero Placeholder Code - Real video file handling and frame extraction
Rule 3: Error-First Development - Comprehensive video validation and error handling
Rule 4: End-to-End Before Features - Complete video processing workflow first
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime, timedelta
from uuid import uuid4, UUID
import os
import asyncio
import json
from pathlib import Path
import cv2
import numpy as np
from io import BytesIO
import tempfile

from storage.database import get_database_manager
from domain.video_schemas import VideoProcessingJobCreate, VideoProcessingJobResponse
from pydantic import BaseModel

router = APIRouter(prefix="/video-processing", tags=["video-processing"])
logger = structlog.get_logger(__name__)

# Video processing configuration
VIDEO_UPLOAD_DIR = Path("F:/faceguard/data/video_uploads")
VIDEO_FRAME_DIR = Path("F:/faceguard/data/video_frames")
SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
FRAME_EXTRACTION_INTERVAL = 1.0  # Extract frame every 1 second


class VideoUploadRequest(BaseModel):
    description: Optional[str] = None
    extract_faces: bool = True
    process_immediately: bool = True
    metadata: Dict[str, Any] = {}


class VideoProcessingStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress_percentage: float
    frames_extracted: int
    faces_detected: int
    processing_time_seconds: float
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class VideoFrameInfo(BaseModel):
    frame_id: str
    timestamp_seconds: float
    face_count: int
    frame_path: str
    faces_detected: List[Dict[str, Any]] = []


@router.post("/upload", response_model=Dict[str, Any], status_code=201)
async def upload_video_for_processing(
    video_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    request_data: Optional[str] = None  # JSON string for additional parameters
):
    """
    Upload video file for face detection processing
    Rule 2: Zero Placeholder Code - Real video file handling with validation
    """
    job_id = str(uuid4())
    start_time = datetime.utcnow()
    
    try:
        # Parse additional request data
        upload_request = VideoUploadRequest()
        if request_data:
            try:
                request_dict = json.loads(request_data)
                upload_request = VideoUploadRequest(**request_dict)
            except json.JSONDecodeError:
                await logger.awarn("Invalid JSON in request_data", job_id=job_id)
        
        await logger.ainfo(
            "Video upload started",
            job_id=job_id,
            filename=video_file.filename,
            content_type=video_file.content_type,
            extract_faces=upload_request.extract_faces
        )
        
        # Validate video file
        validation_result = await _validate_video_file(video_file, job_id)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "video_validation_failed",
                    "message": validation_result["error"],
                    "job_id": job_id
                }
            )
        
        # Create upload directories
        os.makedirs(VIDEO_UPLOAD_DIR, exist_ok=True)
        os.makedirs(VIDEO_FRAME_DIR, exist_ok=True)
        
        # Save video file
        file_extension = Path(video_file.filename).suffix.lower()
        video_filename = f"{job_id}{file_extension}"
        video_path = VIDEO_UPLOAD_DIR / video_filename
        
        # Write video file to disk
        video_content = await video_file.read()
        with open(video_path, "wb") as buffer:
            buffer.write(video_content)
        
        await logger.ainfo(
            "Video file saved successfully",
            job_id=job_id,
            video_path=str(video_path),
            file_size_mb=len(video_content) / (1024 * 1024)
        )
        
        # Create video processing job record in database
        job_record = await _create_video_processing_job(
            job_id=job_id,
            filename=video_file.filename,
            video_path=str(video_path),
            file_size=len(video_content),
            upload_request=upload_request
        )
        
        # Start background processing if requested
        if upload_request.process_immediately:
            background_tasks.add_task(
                _process_video_background,
                job_id,
                video_path,
                upload_request
            )
            
            await logger.ainfo(
                "Video processing queued for immediate execution",
                job_id=job_id
            )
        
        processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "job_id": job_id,
            "status": "pending" if upload_request.process_immediately else "uploaded",
            "message": "Video uploaded successfully and queued for processing",
            "filename": video_file.filename,
            "file_size_mb": round(len(video_content) / (1024 * 1024), 2),
            "processing_options": {
                "extract_faces": upload_request.extract_faces,
                "process_immediately": upload_request.process_immediately
            },
            "endpoints": {
                "status": f"/video-processing/jobs/{job_id}/status",
                "frames": f"/video-processing/jobs/{job_id}/frames",
                "results": f"/video-processing/jobs/{job_id}/results"
            },
            "processing_time_ms": processing_time_ms,
            "created_at": start_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror(
            "Video upload failed",
            job_id=job_id,
            error=str(e),
            filename=video_file.filename if video_file else "unknown"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "video_upload_failed",
                "message": "Failed to upload and process video file",
                "job_id": job_id,
                "details": {"reason": str(e)}
            }
        )


@router.get("/jobs/{job_id}/status", response_model=VideoProcessingStatus)
async def get_video_processing_status(job_id: str):
    """
    Get current status of video processing job
    Rule 2: Zero Placeholder Code - Real database query for job status
    """
    try:
        job_uuid = UUID(job_id)
        
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            # Query video processing job from database
            from sqlalchemy import text
            query = text("""
                SELECT 
                    job_id,
                    status,
                    progress_percentage,
                    frames_extracted,
                    faces_detected,
                    processing_time_seconds,
                    error_message,
                    created_at,
                    completed_at
                FROM video_processing_jobs 
                WHERE job_id = :job_id
            """)
            
            result = await session.execute(query, {"job_id": str(job_uuid)})
            job_row = result.fetchone()
            
            if not job_row:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "job_not_found",
                        "message": f"Video processing job {job_id} not found",
                        "job_id": job_id
                    }
                )
            
            return VideoProcessingStatus(
                job_id=str(job_row.job_id),
                status=job_row.status,
                progress_percentage=float(job_row.progress_percentage or 0),
                frames_extracted=int(job_row.frames_extracted or 0),
                faces_detected=int(job_row.faces_detected or 0),
                processing_time_seconds=float(job_row.processing_time_seconds or 0),
                error_message=job_row.error_message,
                created_at=job_row.created_at.isoformat(),
                completed_at=job_row.completed_at.isoformat() if job_row.completed_at else None
            )
            
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_job_id",
                "message": "Job ID must be a valid UUID",
                "job_id": job_id
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror(
            "Failed to get video processing status",
            job_id=job_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "status_query_failed",
                "message": "Failed to retrieve video processing status",
                "job_id": job_id
            }
        )


@router.get("/jobs/{job_id}/frames", response_model=List[VideoFrameInfo])
async def get_video_frames(job_id: str, limit: int = 50, offset: int = 0):
    """
    Get extracted frames from video processing job
    Rule 2: Zero Placeholder Code - Real frame data from database and filesystem
    """
    try:
        job_uuid = UUID(job_id)
        
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            # Verify job exists
            from sqlalchemy import text
            job_query = text("""
                SELECT status FROM video_processing_jobs 
                WHERE job_id = :job_id
            """)
            
            job_result = await session.execute(job_query, {"job_id": str(job_uuid)})
            job_row = job_result.fetchone()
            
            if not job_row:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "job_not_found",
                        "message": f"Video processing job {job_id} not found"
                    }
                )
            
            # Query video frames
            frames_query = text("""
                SELECT 
                    frame_id,
                    timestamp_seconds,
                    face_count,
                    frame_path,
                    faces_data
                FROM video_frames 
                WHERE job_id = :job_id
                ORDER BY timestamp_seconds ASC
                LIMIT :limit OFFSET :offset
            """)
            
            frames_result = await session.execute(
                frames_query, 
                {"job_id": str(job_uuid), "limit": limit, "offset": offset}
            )
            
            frames = []
            for row in frames_result.fetchall():
                faces_detected = []
                if row.faces_data:
                    try:
                        faces_detected = json.loads(row.faces_data)
                    except json.JSONDecodeError:
                        faces_detected = []
                
                frames.append(VideoFrameInfo(
                    frame_id=str(row.frame_id),
                    timestamp_seconds=float(row.timestamp_seconds),
                    face_count=int(row.face_count),
                    frame_path=row.frame_path,
                    faces_detected=faces_detected
                ))
            
            await logger.ainfo(
                "Video frames retrieved",
                job_id=job_id,
                frames_returned=len(frames),
                limit=limit,
                offset=offset
            )
            
            return frames
            
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_job_id",
                "message": "Job ID must be a valid UUID"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror(
            "Failed to get video frames",
            job_id=job_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "frames_query_failed",
                "message": "Failed to retrieve video frames"
            }
        )


async def _validate_video_file(video_file: UploadFile, job_id: str) -> Dict[str, Any]:
    """
    Validate uploaded video file
    Rule 3: Error-First Development - Comprehensive video validation
    """
    try:
        # Check file extension
        if not video_file.filename:
            return {"valid": False, "error": "No filename provided"}
        
        file_extension = Path(video_file.filename).suffix.lower()
        if file_extension not in SUPPORTED_VIDEO_FORMATS:
            return {
                "valid": False, 
                "error": f"Unsupported video format {file_extension}. Supported: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
            }
        
        # Check content type
        if video_file.content_type and not video_file.content_type.startswith("video/"):
            return {
                "valid": False, 
                "error": f"Invalid content type {video_file.content_type}. Expected video/* format"
            }
        
        # Check file size (read first chunk to get size estimate)
        video_file.file.seek(0, 2)  # Seek to end
        file_size = video_file.file.tell()
        video_file.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_VIDEO_SIZE:
            return {
                "valid": False, 
                "error": f"Video file too large ({file_size / (1024*1024):.1f}MB). Maximum allowed: {MAX_VIDEO_SIZE / (1024*1024):.0f}MB"
            }
        
        if file_size == 0:
            return {"valid": False, "error": "Video file is empty"}
        
        await logger.ainfo(
            "Video file validation passed",
            job_id=job_id,
            filename=video_file.filename,
            file_size_mb=file_size / (1024 * 1024),
            content_type=video_file.content_type
        )
        
        return {"valid": True, "file_size": file_size}
        
    except Exception as e:
        await logger.aerror(
            "Video file validation failed",
            job_id=job_id,
            error=str(e)
        )
        return {"valid": False, "error": f"Validation error: {str(e)}"}


async def _create_video_processing_job(
    job_id: str,
    filename: str,
    video_path: str,
    file_size: int,
    upload_request: VideoUploadRequest
) -> Dict[str, Any]:
    """
    Create video processing job record in database
    Rule 2: Zero Placeholder Code - Real database insertion
    """
    try:
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            from sqlalchemy import text
            
            # Insert video processing job
            insert_query = text("""
                INSERT INTO video_processing_jobs (
                    job_id, filename, video_path, file_size_bytes,
                    description, extract_faces, metadata,
                    status, progress_percentage, created_at
                ) VALUES (
                    :job_id, :filename, :video_path, :file_size_bytes,
                    :description, :extract_faces, :metadata,
                    'pending', 0.0, NOW()
                )
            """)
            
            await session.execute(insert_query, {
                "job_id": job_id,
                "filename": filename,
                "video_path": video_path,
                "file_size_bytes": file_size,
                "description": upload_request.description,
                "extract_faces": upload_request.extract_faces,
                "metadata": json.dumps(upload_request.metadata)
            })
            
            await session.commit()
            
            await logger.ainfo(
                "Video processing job created in database",
                job_id=job_id,
                filename=filename,
                file_size_mb=file_size / (1024 * 1024)
            )
            
            return {"job_id": job_id, "status": "created"}
            
    except Exception as e:
        await logger.aerror(
            "Failed to create video processing job in database",
            job_id=job_id,
            error=str(e)
        )
        raise


async def _process_video_background(
    job_id: str,
    video_path: Path,
    upload_request: VideoUploadRequest
):
    """
    Background video processing task
    Rule 4: End-to-End Before Features - Complete video processing workflow
    """
    start_time = datetime.utcnow()
    
    try:
        await logger.ainfo(
            "Starting background video processing",
            job_id=job_id,
            video_path=str(video_path)
        )
        
        # Update job status to processing
        await _update_job_status(job_id, "processing", 0.0)
        
        # Extract frames from video
        frames_extracted = await _extract_video_frames(job_id, video_path)
        
        # Update progress
        await _update_job_status(job_id, "processing", 50.0, frames_extracted=frames_extracted)
        
        # Extract faces from frames if requested
        total_faces = 0
        if upload_request.extract_faces:
            total_faces = await _extract_faces_from_frames(job_id)
        
        # Complete processing
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        await _update_job_status(
            job_id, 
            "completed", 
            100.0, 
            frames_extracted=frames_extracted,
            faces_detected=total_faces,
            processing_time=processing_time
        )
        
        await logger.ainfo(
            "Video processing completed successfully",
            job_id=job_id,
            frames_extracted=frames_extracted,
            faces_detected=total_faces,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        await logger.aerror(
            "Video processing failed",
            job_id=job_id,
            error=str(e)
        )
        
        # Update job status to failed
        await _update_job_status(
            job_id, 
            "failed", 
            0.0, 
            error_message=str(e)
        )


async def _extract_video_frames(job_id: str, video_path: Path) -> int:
    """
    Extract frames from video file using OpenCV
    Rule 2: Zero Placeholder Code - Real video frame extraction
    """
    try:
        # Create frame directory for this job
        job_frame_dir = VIDEO_FRAME_DIR / job_id
        os.makedirs(job_frame_dir, exist_ok=True)
        
        # Open video file
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        await logger.ainfo(
            "Video properties extracted",
            job_id=job_id,
            fps=fps,
            frame_count=frame_count,
            duration_seconds=duration
        )
        
        # Extract frames at specified interval
        frame_interval = int(fps * FRAME_EXTRACTION_INTERVAL) if fps > 0 else 30
        frames_extracted = 0
        current_frame = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extract frame at interval
            if current_frame % frame_interval == 0:
                timestamp = current_frame / fps if fps > 0 else current_frame
                frame_id = str(uuid4())
                frame_filename = f"frame_{frames_extracted:06d}_{frame_id}.jpg"
                frame_path = job_frame_dir / frame_filename
                
                # Save frame
                cv2.imwrite(str(frame_path), frame)
                
                # Store frame information in database
                await _store_frame_info(
                    job_id=job_id,
                    frame_id=frame_id,
                    timestamp_seconds=timestamp,
                    frame_path=str(frame_path)
                )
                
                frames_extracted += 1
            
            current_frame += 1
        
        cap.release()
        
        await logger.ainfo(
            "Frame extraction completed",
            job_id=job_id,
            frames_extracted=frames_extracted,
            video_duration=duration
        )
        
        return frames_extracted
        
    except Exception as e:
        await logger.aerror(
            "Frame extraction failed",
            job_id=job_id,
            error=str(e)
        )
        raise


async def _store_frame_info(job_id: str, frame_id: str, timestamp_seconds: float, frame_path: str):
    """
    Store frame information in database
    Rule 2: Zero Placeholder Code - Real database storage
    """
    try:
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            from sqlalchemy import text
            
            insert_query = text("""
                INSERT INTO video_frames (
                    frame_id, job_id, timestamp_seconds, frame_path,
                    face_count, faces_data, created_at
                ) VALUES (
                    :frame_id, :job_id, :timestamp_seconds, :frame_path,
                    0, '[]', NOW()
                )
            """)
            
            await session.execute(insert_query, {
                "frame_id": frame_id,
                "job_id": job_id,
                "timestamp_seconds": timestamp_seconds,
                "frame_path": frame_path
            })
            
            await session.commit()
            
    except Exception as e:
        await logger.aerror(
            "Failed to store frame info",
            job_id=job_id,
            frame_id=frame_id,
            error=str(e)
        )


async def _extract_faces_from_frames(job_id: str) -> int:
    """
    Extract faces from video frames using existing Face Recognition Service
    Rule 2: Zero Placeholder Code - Real integration with face-recognition-service on port 8002
    """
    try:
        import aiohttp
        import aiofiles
        import json
        
        # Get all frames for this job
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            from sqlalchemy import text
            
            frames_query = text("""
                SELECT frame_id, frame_path, timestamp_seconds
                FROM video_frames 
                WHERE job_id = :job_id
                ORDER BY timestamp_seconds ASC
            """)
            
            frames_result = await session.execute(frames_query, {"job_id": job_id})
            frames = frames_result.fetchall()
            
            if not frames:
                await logger.awarn("No frames found for face extraction", job_id=job_id)
                return 0
            
            total_faces_detected = 0
            processed_frames = 0
            
            # Process each frame through face recognition service
            async with aiohttp.ClientSession() as http_session:
                for frame_row in frames:
                    frame_id = str(frame_row.frame_id)
                    frame_path = frame_row.frame_path
                    timestamp = float(frame_row.timestamp_seconds)
                    
                    try:
                        # Check if frame file exists
                        if not os.path.exists(frame_path):
                            await logger.awarn(
                                "Frame file not found, skipping",
                                job_id=job_id,
                                frame_id=frame_id,
                                frame_path=frame_path
                            )
                            continue
                        
                        # Read frame file
                        async with aiofiles.open(frame_path, 'rb') as frame_file:
                            frame_data = await frame_file.read()
                        
                        # Create form data for face recognition service
                        data = aiohttp.FormData()
                        data.add_field(
                            'file', 
                            frame_data, 
                            filename=f'frame_{frame_id}.jpg',
                            content_type='image/jpeg'
                        )
                        
                        # Call face recognition service
                        async with http_session.post(
                            'http://localhost:8002/process/image/',
                            data=data,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            
                            if response.status == 200:
                                result = await response.json()
                                
                                # Extract face information
                                faces_detected = result.get('summary', {}).get('faces_detected', 0)
                                faces_recognized = result.get('summary', {}).get('faces_recognized', 0)
                                
                                recognized_faces = result.get('recognized_faces', [])
                                
                                # Prepare faces data for storage
                                faces_data = []
                                for face in recognized_faces:
                                    face_info = {
                                        "face_id": face.get("face_id"),
                                        "bbox": face.get("bbox"),
                                        "confidence": face.get("confidence"),
                                        "age": face.get("age"),
                                        "gender": face.get("gender"),
                                        "recognized": face.get("recognized", False),
                                        "person_id": face.get("person_id"),
                                        "recognition_confidence": face.get("recognition_confidence", 0.0)
                                    }
                                    faces_data.append(face_info)
                                
                                # Update frame with face information
                                await _update_frame_face_data(
                                    frame_id=frame_id,
                                    face_count=faces_detected,
                                    faces_data=faces_data
                                )
                                
                                total_faces_detected += faces_detected
                                processed_frames += 1
                                
                                await logger.ainfo(
                                    "Frame processed successfully",
                                    job_id=job_id,
                                    frame_id=frame_id,
                                    timestamp_seconds=timestamp,
                                    faces_detected=faces_detected,
                                    faces_recognized=faces_recognized
                                )
                                
                            else:
                                await logger.aerror(
                                    "Face recognition service error",
                                    job_id=job_id,
                                    frame_id=frame_id,
                                    status_code=response.status,
                                    error_text=await response.text()
                                )
                    
                    except Exception as frame_error:
                        await logger.aerror(
                            "Failed to process frame for face detection",
                            job_id=job_id,
                            frame_id=frame_id,
                            error=str(frame_error)
                        )
                        continue
            
            await logger.ainfo(
                "Face extraction from frames completed",
                job_id=job_id,
                processed_frames=processed_frames,
                total_frames=len(frames),
                total_faces_detected=total_faces_detected
            )
            
            return total_faces_detected
            
    except Exception as e:
        await logger.aerror(
            "Face extraction from frames failed",
            job_id=job_id,
            error=str(e)
        )
        return 0


async def _update_frame_face_data(frame_id: str, face_count: int, faces_data: list):
    """
    Update frame with face detection results
    Rule 2: Zero Placeholder Code - Real database update with face information
    """
    try:
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            from sqlalchemy import text
            
            update_query = text("""
                UPDATE video_frames 
                SET face_count = :face_count,
                    faces_data = :faces_data,
                    updated_at = NOW()
                WHERE frame_id = :frame_id
            """)
            
            await session.execute(update_query, {
                "frame_id": frame_id,
                "face_count": face_count,
                "faces_data": json.dumps(faces_data)
            })
            
            await session.commit()
            
    except Exception as e:
        await logger.aerror(
            "Failed to update frame face data",
            frame_id=frame_id,
            error=str(e)
        )


async def _update_job_status(
    job_id: str, 
    status: str, 
    progress: float, 
    frames_extracted: int = None,
    faces_detected: int = None,
    processing_time: float = None,
    error_message: str = None
):
    """
    Update video processing job status in database
    Rule 2: Zero Placeholder Code - Real database updates
    """
    try:
        db_manager = await get_database_manager()
        async with db_manager.get_session() as session:
            from sqlalchemy import text
            
            update_fields = [
                "status = :status",
                "progress_percentage = :progress",
                "updated_at = NOW()"
            ]
            
            params = {
                "job_id": job_id,
                "status": status,
                "progress": progress
            }
            
            if frames_extracted is not None:
                update_fields.append("frames_extracted = :frames_extracted")
                params["frames_extracted"] = frames_extracted
            
            if faces_detected is not None:
                update_fields.append("faces_detected = :faces_detected")
                params["faces_detected"] = faces_detected
            
            if processing_time is not None:
                update_fields.append("processing_time_seconds = :processing_time")
                params["processing_time"] = processing_time
            
            if error_message is not None:
                update_fields.append("error_message = :error_message")
                params["error_message"] = error_message
            
            if status == "completed":
                update_fields.append("completed_at = NOW()")
            
            update_query = text(f"""
                UPDATE video_processing_jobs 
                SET {', '.join(update_fields)}
                WHERE job_id = :job_id
            """)
            
            await session.execute(update_query, params)
            await session.commit()
            
    except Exception as e:
        await logger.aerror(
            "Failed to update job status",
            job_id=job_id,
            status=status,
            error=str(e)
        )