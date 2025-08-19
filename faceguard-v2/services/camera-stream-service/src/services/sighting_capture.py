"""
Camera Stream Service - Async Sighting Capture Integration
Rule 2: Zero Placeholder Code - Real async sighting recording
Rule 3: Error-First Development - Non-blocking with proper error handling
Performance: Async background capture that NEVER blocks recognition pipeline
"""
import asyncio
import aiohttp
import cv2
import numpy as np
import base64
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class SightingData:
    """Sighting data for async capture"""
    person_id: str
    camera_id: str
    confidence_score: float
    face_crop: np.ndarray
    face_bbox: List[float]
    timestamp: datetime
    frame_metadata: Dict[str, Any]


class AsyncSightingCapture:
    """
    Async sighting capture service - COMPLETELY NON-BLOCKING
    Rule 1: Recognition pipeline speed is NEVER impacted
    Rule 2: All sighting operations are background async tasks
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.core_data_service_url = settings.core_data_service_url  # http://localhost:8001
        self.notification_service_url = getattr(settings, 'notification_service_url', 'http://localhost:8002')  # Notification service
        self.session: Optional[aiohttp.ClientSession] = None
        self.sighting_queue = asyncio.Queue(maxsize=1000)  # Buffer for high-traffic scenarios
        self.is_running = False
        
        # Performance metrics
        self.total_sightings_captured = 0
        self.successful_uploads = 0
        self.failed_uploads = 0
        self.queue_full_drops = 0
        self.alert_evaluations_triggered = 0
        self.alert_evaluation_failures = 0
        
    async def initialize(self):
        """Initialize async sighting capture service"""
        logger.info("Initializing Async Sighting Capture Service")
        
        # Create HTTP session for Core Data Service
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)  # 30s timeout for sighting uploads
        )
        
        # Start background sighting processor
        self.is_running = True
        asyncio.create_task(self._process_sighting_queue())
        
        logger.info("Async Sighting Capture Service initialized successfully")
        
    async def shutdown(self):
        """Shutdown sighting capture service"""
        self.is_running = False
        
        if self.session:
            await self.session.close()
            
        logger.info("Async Sighting Capture Service shutdown complete")
        
    async def capture_sightings_async(
        self, 
        recognition_result: Any, 
        camera_id: str, 
        original_frame: np.ndarray,
        frame_metadata: Dict[str, Any]
    ) -> None:
        """
        CRITICAL: Async sighting capture - NEVER blocks recognition pipeline
        This method returns immediately, all processing happens in background
        """
        if not recognition_result.success or not recognition_result.persons_detected:
            return  # No persons detected, nothing to capture
            
        # Queue sightings for background processing (NON-BLOCKING)
        try:
            for person_data in recognition_result.persons_detected:
                # Extract face crop from bbox
                face_crop = self._extract_face_crop(original_frame, person_data.get('bbox', []))
                
                if face_crop is not None:
                    sighting = SightingData(
                        person_id=person_data.get('person_id', 'unknown'),
                        camera_id=camera_id,
                        confidence_score=person_data.get('confidence', 0.0),
                        face_crop=face_crop,
                        face_bbox=person_data.get('bbox', []),
                        timestamp=datetime.now(),
                        frame_metadata=frame_metadata
                    )
                    
                    # Non-blocking queue operation
                    self.sighting_queue.put_nowait(sighting)
                    self.total_sightings_captured += 1
                    
        except asyncio.QueueFull:
            # Queue is full - drop oldest sightings (graceful degradation)
            self.queue_full_drops += 1
            logger.warning(f"Sighting queue full, dropping sighting for camera {camera_id}")
        except Exception as e:
            # Never let sighting capture errors affect recognition
            logger.error(f"Sighting capture error (non-blocking): {str(e)}")
            
        # Method returns immediately - recognition pipeline continues unaffected
        
    def _extract_face_crop(self, frame: np.ndarray, bbox: List[float]) -> Optional[np.ndarray]:
        """Extract face crop from frame using bounding box"""
        try:
            if not bbox or len(bbox) != 4:
                return None
                
            h, w = frame.shape[:2]
            x1, y1, x2, y2 = bbox
            
            # Ensure coordinates are within frame bounds
            x1 = max(0, min(int(x1), w-1))
            y1 = max(0, min(int(y1), h-1))
            x2 = max(x1+1, min(int(x2), w))
            y2 = max(y1+1, min(int(y2), h))
            
            # Extract face crop
            face_crop = frame[y1:y2, x1:x2]
            
            # Minimum size check
            if face_crop.shape[0] < 50 or face_crop.shape[1] < 50:
                return None
                
            return face_crop
            
        except Exception as e:
            logger.error(f"Face crop extraction error: {str(e)}")
            return None
            
    async def _process_sighting_queue(self):
        """Background queue processor - processes sightings asynchronously"""
        logger.info("Background sighting processor started")
        
        while self.is_running:
            try:
                # Wait for sighting data (with timeout to allow shutdown)
                sighting = await asyncio.wait_for(
                    self.sighting_queue.get(), 
                    timeout=1.0
                )
                
                # Process sighting in background (upload to Core Data Service)
                asyncio.create_task(self._upload_sighting_to_core_data(sighting))
                
            except asyncio.TimeoutError:
                # Normal timeout - continue processing
                continue
            except Exception as e:
                logger.error(f"Sighting queue processing error: {str(e)}")
                await asyncio.sleep(1)  # Brief pause on error
                
    async def _upload_sighting_to_core_data(self, sighting: SightingData):
        """Upload sighting with image to Core Data Service"""
        try:
            if not self.session:
                return
                
            # Encode face crop as JPEG for upload
            success, buffer = cv2.imencode('.jpg', sighting.face_crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
            if not success:
                logger.error("Failed to encode face crop for upload")
                self.failed_uploads += 1
                return
                
            # Prepare multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field('person_id', sighting.person_id)
            form_data.add_field('camera_id', sighting.camera_id)
            form_data.add_field('confidence_score', str(sighting.confidence_score))
            form_data.add_field('source_type', 'camera_stream')
            form_data.add_field('face_bbox', str(sighting.face_bbox))
            form_data.add_field(
                'image', 
                buffer.tobytes(), 
                filename=f'sighting_{int(time.time())}.jpg',
                content_type='image/jpeg'
            )
            
            # Upload to Core Data Service /sightings/with-image endpoint
            upload_url = f"{self.core_data_service_url}/sightings/with-image"
            
            async with self.session.post(upload_url, data=form_data) as response:
                if response.status == 201:
                    self.successful_uploads += 1
                    logger.debug(f"Sighting uploaded successfully for person {sighting.person_id}")
                    
                    # INTEGRATION: Trigger real-time alert evaluation after successful sighting upload
                    asyncio.create_task(self._evaluate_alerts_for_sighting(sighting, response))
                    
                else:
                    self.failed_uploads += 1
                    error_text = await response.text()
                    logger.error(f"Sighting upload failed (HTTP {response.status}): {error_text}")
                    
        except Exception as e:
            self.failed_uploads += 1
            logger.error(f"Sighting upload error: {str(e)}")
            
    async def _evaluate_alerts_for_sighting(self, sighting: SightingData, upload_response: aiohttp.ClientResponse):
        """
        Trigger real-time alert evaluation for the sighting
        CRITICAL: Non-blocking background task - never affects sighting capture performance
        """
        try:
            # Extract sighting ID from upload response if available
            sighting_response = await upload_response.json()
            sighting_id = sighting_response.get('id', 'unknown')
            
            # Prepare alert evaluation payload
            alert_payload = {
                "sighting_id": sighting_id,
                "person_id": sighting.person_id,
                "camera_id": sighting.camera_id,
                "confidence_score": sighting.confidence_score,
                "timestamp": sighting.timestamp.isoformat(),
                "source_type": "camera_stream",
                "face_bbox": sighting.face_bbox,
                "frame_metadata": sighting.frame_metadata
            }
            
            # Call notification service alert evaluation endpoint
            alert_url = f"{self.notification_service_url}/alert-evaluation/evaluate-sighting"
            
            async with self.session.post(
                alert_url, 
                json=alert_payload,
                headers={'Content-Type': 'application/json'}
            ) as alert_response:
                if alert_response.status == 200:
                    self.alert_evaluations_triggered += 1
                    alert_result = await alert_response.json()
                    
                    # Log any triggered alerts
                    if alert_result.get('alerts_triggered', 0) > 0:
                        logger.info(
                            f"ALERT TRIGGERED: {alert_result['alerts_triggered']} alerts for person {sighting.person_id} "
                            f"at camera {sighting.camera_id} (confidence: {sighting.confidence_score:.2f})"
                        )
                    else:
                        logger.debug(f"Alert evaluation completed - no alerts triggered for sighting {sighting_id}")
                        
                elif alert_response.status == 404:
                    # Notification service not available - graceful degradation
                    logger.debug(f"Notification service unavailable for alert evaluation (sighting {sighting_id})")
                    
                else:
                    self.alert_evaluation_failures += 1
                    error_text = await alert_response.text()
                    logger.warning(f"Alert evaluation failed (HTTP {alert_response.status}): {error_text}")
                    
        except Exception as e:
            self.alert_evaluation_failures += 1
            logger.warning(f"Alert evaluation error (non-blocking): {str(e)}")
            # Never let alert evaluation errors affect sighting capture
            
    def get_capture_statistics(self) -> Dict[str, Any]:
        """Get sighting capture performance statistics"""
        success_rate = (self.successful_uploads / max(1, self.total_sightings_captured)) * 100
        
        alert_success_rate = (self.alert_evaluations_triggered / max(1, self.successful_uploads)) * 100
        
        return {
            "total_sightings_captured": self.total_sightings_captured,
            "successful_uploads": self.successful_uploads,
            "failed_uploads": self.failed_uploads,
            "success_rate_percent": round(success_rate, 2),
            "queue_full_drops": self.queue_full_drops,
            "queue_size": self.sighting_queue.qsize(),
            "is_running": self.is_running,
            # Alert evaluation metrics
            "alert_evaluations_triggered": self.alert_evaluations_triggered,
            "alert_evaluation_failures": self.alert_evaluation_failures,
            "alert_success_rate_percent": round(alert_success_rate, 2)
        }