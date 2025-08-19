"""
Recognition Integration Service
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md - Service B integration
Real API calls to Face Recognition Service - Zero Placeholder Code
"""
import asyncio
import aiohttp
import cv2
import time
import logging
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import base64

from ..config.settings import Settings
from ..domain.models import FrameMetadata

logger = logging.getLogger(__name__)


@dataclass
class RecognitionResult:
    """Recognition result from Service B"""
    success: bool
    persons_detected: List[Dict[str, Any]]
    processing_time_ms: float
    confidence_threshold: float
    frame_id: str
    timestamp: datetime
    error: Optional[str] = None


class RecognitionIntegrationService:
    """
    Service B (Face Recognition) Integration
    Real HTTP API calls - no placeholder code
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.service_b_url = settings.face_recognition_service_url
        self.timeout = settings.integration_timeout
        self.retry_attempts = settings.integration_retry_attempts
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_processing_time = 0.0
        self.last_success_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        
    async def initialize(self):
        """Initialize HTTP session for Service B communication"""
        logger.info("Initializing Recognition Integration Service")
        
        # Create persistent HTTP session (no Content-Type for multipart uploads)
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        
        # Test Service B connectivity
        await self._test_service_b_connectivity()
        
    async def shutdown(self):
        """Shutdown HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("Recognition Integration Service shutdown complete")
    
    async def _test_service_b_connectivity(self):
        """Test if Service B is accessible"""
        try:
            if not self.session:
                return False
                
            health_url = f"{self.service_b_url}/health"
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    logger.info(f"Service B connectivity confirmed: {self.service_b_url}")
                    return True
                else:
                    logger.warning(f"Service B health check failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Service B connectivity test failed: {str(e)}")
            self.last_error = f"Connectivity test failed: {str(e)}"
            return False
    
    def _encode_frame_for_api(self, frame: np.ndarray) -> bytes:
        """
        Encode frame for Service B API
        Real implementation - converts OpenCV frame to JPEG bytes for multipart upload
        """
        try:
            # Encode frame as JPEG bytes
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]  # Good quality/size balance
            success, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            if not success:
                raise Exception("Failed to encode frame as JPEG")
            
            # Return raw bytes for multipart upload
            return buffer.tobytes()
            
        except Exception as e:
            logger.error(f"Frame encoding error: {str(e)}")
            raise
    
    async def process_frame(
        self, 
        frame: np.ndarray, 
        metadata: FrameMetadata,
        confidence_threshold: float = 0.6
    ) -> RecognitionResult:
        """
        Send frame to Service B for recognition
        Real API integration - no placeholder code
        """
        start_time = time.time()
        self.total_requests += 1
        
        try:
            if not self.session:
                raise Exception("Recognition service not initialized")
            
            # Encode frame for API transmission
            frame_bytes = self._encode_frame_for_api(frame)
            
            # Prepare multipart/form-data (Service B expects file upload)
            form_data = aiohttp.FormData()
            form_data.add_field(
                'file', 
                frame_bytes, 
                filename=f'frame_{metadata.frame_id}.jpg',
                content_type='image/jpeg'
            )
            
            # Call Service B recognition endpoint
            recognition_url = f"{self.service_b_url}/process/image/"
            
            async with self.session.post(recognition_url, data=form_data) as response:
                processing_time = (time.time() - start_time) * 1000  # ms
                
                if response.status == 200:
                    # Success - process recognition results
                    result_data = await response.json()
                    
                    self.successful_requests += 1
                    self.total_processing_time += processing_time
                    self.last_success_time = datetime.utcnow()
                    
                    # Extract recognized faces (Service B API format)
                    persons_detected = result_data.get('recognized_faces', [])
                    
                    logger.debug(f"Recognition successful: {len(persons_detected)} persons detected "
                               f"in {processing_time:.2f}ms")
                    
                    return RecognitionResult(
                        success=True,
                        persons_detected=persons_detected,
                        processing_time_ms=processing_time,
                        confidence_threshold=confidence_threshold,
                        frame_id=metadata.frame_id,
                        timestamp=datetime.utcnow()
                    )
                    
                else:
                    # API error
                    error_text = await response.text()
                    error_msg = f"Service B API error: {response.status} - {error_text}"
                    
                    self.failed_requests += 1
                    self.last_error = error_msg
                    
                    logger.error(f"Recognition API failed: {error_msg}")
                    
                    return RecognitionResult(
                        success=False,
                        persons_detected=[],
                        processing_time_ms=processing_time,
                        confidence_threshold=confidence_threshold,
                        frame_id=metadata.frame_id,
                        timestamp=datetime.utcnow(),
                        error=error_msg
                    )
                    
        except asyncio.TimeoutError:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Recognition request timeout after {self.timeout}s"
            
            self.failed_requests += 1
            self.last_error = error_msg
            
            logger.error(error_msg)
            
            return RecognitionResult(
                success=False,
                persons_detected=[],
                processing_time_ms=processing_time,
                confidence_threshold=confidence_threshold,
                frame_id=metadata.frame_id,
                timestamp=datetime.utcnow(),
                error=error_msg
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Recognition integration error: {str(e)}"
            
            self.failed_requests += 1
            self.last_error = error_msg
            
            logger.error(f"Recognition processing failed: {error_msg}")
            
            return RecognitionResult(
                success=False,
                persons_detected=[],
                processing_time_ms=processing_time,
                confidence_threshold=confidence_threshold,
                frame_id=metadata.frame_id,
                timestamp=datetime.utcnow(),
                error=error_msg
            )
    
    async def process_frame_with_retry(
        self,
        frame: np.ndarray,
        metadata: FrameMetadata,
        confidence_threshold: float = 0.6
    ) -> RecognitionResult:
        """
        Process frame with retry logic for reliability
        """
        last_result = None
        
        for attempt in range(self.retry_attempts):
            result = await self.process_frame(frame, metadata, confidence_threshold)
            
            if result.success:
                return result
            
            last_result = result
            
            if attempt < self.retry_attempts - 1:  # Don't wait after last attempt
                wait_time = (attempt + 1) * 0.5  # Exponential backoff
                logger.debug(f"Recognition attempt {attempt + 1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
        
        # All attempts failed
        logger.error(f"Recognition failed after {self.retry_attempts} attempts")
        return last_result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get recognition integration performance statistics"""
        avg_processing_time = (
            self.total_processing_time / max(self.successful_requests, 1)
        )
        
        success_rate = (
            (self.successful_requests / max(self.total_requests, 1)) * 100
        )
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate_percent": round(success_rate, 2),
            "avg_processing_time_ms": round(avg_processing_time, 2),
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "last_error": self.last_error,
            "service_b_url": self.service_b_url
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for recognition integration"""
        try:
            connectivity_ok = await self._test_service_b_connectivity()
            
            stats = self.get_performance_stats()
            
            # Determine health status
            if not connectivity_ok:
                status = "unhealthy"
            elif stats["success_rate_percent"] < 50:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "connectivity": connectivity_ok,
                "performance": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }