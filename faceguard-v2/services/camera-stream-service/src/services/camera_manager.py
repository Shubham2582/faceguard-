"""
Camera Management Service
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md - REAL camera operations (no placeholders)
"""
import asyncio
import time
import logging
import threading

import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
import uuid

from ..domain.models import (
    CameraConfiguration, CameraInfo, CameraStatus, CameraType, 
    StreamStatus, FrameMetadata, FrameQuality
)
from ..config.settings import Settings
from .recognition_integration import RecognitionIntegrationService
from .event_publisher import EventPublisher
from .sighting_capture import AsyncSightingCapture

logger = logging.getLogger(__name__)


class CameraConnection:
    """Manages individual camera connection and frame extraction"""
    
    def __init__(self, config: CameraConfiguration):
        self.config = config
        self.cap: Optional[cv2.VideoCapture] = None
        self.status = CameraStatus.DISCONNECTED
        self.last_frame_time: Optional[datetime] = None
        self.frames_processed = 0
        self.errors_count = 0
        self.last_error: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.reconnect_attempts = 0
        self.is_running = False
        self._lock = threading.Lock()
    
    def detect_camera_type(self, source: str) -> CameraType:
        """Detect camera type from source string"""
        if source.isdigit():
            return CameraType.USB
        elif source.startswith(('rtsp://', 'rtmp://')):
            return CameraType.RTSP
        elif source.startswith(('http://', 'https://')):
            return CameraType.IP
        elif source.startswith(('file://', '/')) or source.endswith(('.mp4', '.avi', '.mov')):
            return CameraType.FILE
        else:
            return CameraType.USB  # Default fallback
    
    def connect(self) -> bool:
        """Establish camera connection"""
        try:
            with self._lock:
                if self.cap is not None:
                    self.cap.release()
                
                # Create VideoCapture based on source type
                if self.config.source.isdigit():
                    # USB camera
                    camera_index = int(self.config.source)
                    self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # DirectShow for Windows
                else:
                    # IP/RTSP camera or file
                    self.cap = cv2.VideoCapture(self.config.source)
                
                if not self.cap.isOpened():
                    raise Exception(f"Failed to open camera source: {self.config.source}")
                
                # Configure camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resolution_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resolution_height)
                self.cap.set(cv2.CAP_PROP_FPS, self.config.frame_rate)
                
                # Test frame capture
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    raise Exception("Failed to capture test frame")
                
                self.status = CameraStatus.CONNECTED
                self.reconnect_attempts = 0
                self.last_error = None
                
                logger.info(f"Camera {self.config.camera_id} connected successfully")
                return True
                
        except Exception as e:
            error_msg = f"Camera connection failed: {str(e)}"
            self.last_error = error_msg
            self.status = CameraStatus.ERROR
            self.errors_count += 1
            logger.error(f"Camera {self.config.camera_id}: {error_msg}")
            
            if self.cap:
                self.cap.release()
                self.cap = None
            
            return False
    
    def disconnect(self):
        """Disconnect camera"""
        with self._lock:
            if self.cap:
                self.cap.release()
                self.cap = None
            self.status = CameraStatus.DISCONNECTED
            self.is_running = False
        
        logger.info(f"Camera {self.config.camera_id} disconnected")
    
    def capture_frame(self) -> Optional[Tuple[np.ndarray, FrameMetadata]]:
        """Capture single frame with metadata"""
        try:
            with self._lock:
                if not self.cap or not self.cap.isOpened():
                    return None
                
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.status = CameraStatus.ERROR
                    self.last_error = "Failed to capture frame"
                    return None
                
                # Create frame metadata
                frame_id = str(uuid.uuid4())
                timestamp = datetime.utcnow()
                height, width, channels = frame.shape
                file_size = frame.nbytes
                
                metadata = FrameMetadata(
                    frame_id=frame_id,
                    camera_id=self.config.camera_id,
                    timestamp=timestamp,
                    frame_number=self.frames_processed,
                    width=width,
                    height=height,
                    channels=channels,
                    file_size=file_size
                )
                
                self.frames_processed += 1
                self.last_frame_time = timestamp
                self.status = CameraStatus.CONNECTED
                
                return frame, metadata
                
        except Exception as e:
            error_msg = f"Frame capture error: {str(e)}"
            self.last_error = error_msg
            self.status = CameraStatus.ERROR
            self.errors_count += 1
            logger.error(f"Camera {self.config.camera_id}: {error_msg}")
            return None
    
    def assess_frame_quality(self, frame: np.ndarray) -> Tuple[float, FrameQuality]:
        """Assess frame quality using computer vision metrics"""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Blur detection using Laplacian variance
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_normalized = min(blur_score / 1000.0, 1.0)  # Normalize to 0-1
            
            # Brightness assessment
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Optimal around 0.5
            
            # Contrast assessment
            contrast = np.std(gray) / 255.0
            contrast_score = min(contrast * 2.0, 1.0)  # Higher contrast is better
            
            # Overall quality score (weighted average)
            quality_score = (
                blur_normalized * 0.4 +      # 40% weight on sharpness
                brightness_score * 0.3 +     # 30% weight on brightness
                contrast_score * 0.3         # 30% weight on contrast
            )
            
            # Determine quality grade
            if quality_score >= 0.8:
                grade = FrameQuality.EXCELLENT
            elif quality_score >= 0.6:
                grade = FrameQuality.GOOD
            elif quality_score >= 0.4:
                grade = FrameQuality.FAIR
            elif quality_score >= 0.2:
                grade = FrameQuality.POOR
            else:
                grade = FrameQuality.UNUSABLE
            
            return quality_score, grade
            
        except Exception as e:
            logger.error(f"Quality assessment error: {str(e)}")
            return 0.0, FrameQuality.UNUSABLE
    
    def get_info(self) -> CameraInfo:
        """Get current camera information"""
        uptime = int((datetime.utcnow() - self.created_at).total_seconds())
        
        return CameraInfo(
            camera_id=self.config.camera_id,
            configuration=self.config,
            status=self.status,
            stream_status=StreamStatus.ACTIVE if self.is_running else StreamStatus.STOPPED,
            last_frame_time=self.last_frame_time,
            frames_processed=self.frames_processed,
            frames_recognized=0,  # Will be updated by recognition service
            errors_count=self.errors_count,
            last_error=self.last_error,
            uptime_seconds=uptime,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )


class CameraManager:
    """Manages multiple cameras and frame processing"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.cameras: Dict[str, CameraConnection] = {}
        self.frame_queues: Dict[str, asyncio.Queue] = {}
        self.running_streams: Dict[str, bool] = {}
        self.executor = ThreadPoolExecutor(max_workers=settings.max_concurrent_cameras)
        self.health_check_task: Optional[asyncio.Task] = None
        self.start_time = datetime.utcnow()
        self.total_frames_processed = 0
        self.total_errors = 0
        self.recognition_service: Optional[RecognitionIntegrationService] = None
        self.event_publisher: Optional[EventPublisher] = None
        self.sighting_capture: Optional[AsyncSightingCapture] = None
    
    async def initialize(self):
        """Initialize camera manager and auto-discover cameras"""
        logger.info("Initializing Camera Manager...")
        
        # Create cameras from configuration
        for i, source in enumerate(self.settings.camera_sources):
            camera_id = f"camera_{i}"
            await self.add_camera(
                source=source,
                name=f"Camera {i+1}",
                camera_id=camera_id
            )
        
        # Initialize recognition service integration if enabled
        if self.settings.face_recognition_service_url:
            logger.info("Initializing Recognition Integration Service...")
            self.recognition_service = RecognitionIntegrationService(self.settings)
            await self.recognition_service.initialize()
        
        # Initialize event publishing system if enabled
        if self.settings.enable_event_publishing:
            logger.info("Initializing Event Publishing Service...")
            self.event_publisher = EventPublisher(self.settings)
            await self.event_publisher.initialize()
        
        # Initialize async sighting capture service
        logger.info("Initializing Async Sighting Capture Service...")
        self.sighting_capture = AsyncSightingCapture(self.settings)
        await self.sighting_capture.initialize()
        
        # Start health monitoring
        if self.settings.enable_health_monitoring:
            self.health_check_task = asyncio.create_task(self._health_monitor_loop())
        
        logger.info(f"Camera Manager initialized with {len(self.cameras)} cameras")
    
    async def add_camera(self, source: str, name: str, camera_id: Optional[str] = None, 
                        location: Optional[str] = None) -> str:
        """Add new camera configuration"""
        if camera_id is None:
            camera_id = f"camera_{len(self.cameras)}"
        
        # Detect camera type
        temp_conn = CameraConnection(CameraConfiguration(
            camera_id="temp", source="0", camera_type=CameraType.USB, name="temp"
        ))
        camera_type = temp_conn.detect_camera_type(source)
        
        # Create camera configuration
        config = CameraConfiguration(
            camera_id=camera_id,
            source=source,
            camera_type=camera_type,
            name=name,
            location=location,
            resolution_width=self.settings.camera_resolution_width,
            resolution_height=self.settings.camera_resolution_height,
            frame_rate=self.settings.camera_frame_rate,
            enabled=True,
            auto_reconnect=True,
            reconnect_attempts=self.settings.camera_reconnect_attempts,
            reconnect_delay=self.settings.camera_reconnect_delay
        )
        
        # Create camera connection
        camera = CameraConnection(config)
        self.cameras[camera_id] = camera
        self.frame_queues[camera_id] = asyncio.Queue(maxsize=self.settings.frame_buffer_size)
        self.running_streams[camera_id] = False
        
        logger.info(f"Added camera {camera_id}: {name} ({source})")
        return camera_id
    
    async def connect_camera(self, camera_id: str) -> bool:
        """Connect specific camera"""
        if camera_id not in self.cameras:
            logger.error(f"Camera {camera_id} not found")
            return False
        
        camera = self.cameras[camera_id]
        success = await asyncio.get_event_loop().run_in_executor(
            self.executor, camera.connect
        )
        
        return success
    
    async def disconnect_camera(self, camera_id: str):
        """Disconnect specific camera"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            await asyncio.get_event_loop().run_in_executor(
                self.executor, camera.disconnect
            )
    
    async def start_stream(self, camera_id: str) -> bool:
        """Start camera stream processing"""
        if camera_id not in self.cameras:
            logger.error(f"Camera {camera_id} not found")
            return False
        
        if self.running_streams.get(camera_id, False):
            logger.warning(f"Camera {camera_id} stream already running")
            return True
        
        camera = self.cameras[camera_id]
        
        # Ensure camera is connected
        if camera.status != CameraStatus.CONNECTED:
            if not await self.connect_camera(camera_id):
                return False
        
        # Start stream processing
        self.running_streams[camera_id] = True
        asyncio.create_task(self._stream_processing_loop(camera_id))
        
        logger.info(f"Started stream for camera {camera_id}")
        return True
    
    async def stop_stream(self, camera_id: str):
        """Stop camera stream processing"""
        if camera_id in self.running_streams:
            self.running_streams[camera_id] = False
            logger.info(f"Stopped stream for camera {camera_id}")
    
    async def start_all_streams(self):
        """Start all enabled camera streams"""
        for camera_id, camera in self.cameras.items():
            if camera.config.enabled:
                await self.start_stream(camera_id)
    
    async def stop_all_streams(self):
        """Stop all camera streams"""
        for camera_id in self.cameras:
            await self.stop_stream(camera_id)
    
    async def _stream_processing_loop(self, camera_id: str):
        """Main stream processing loop for a camera"""
        camera = self.cameras[camera_id]
        frame_interval = 1.0 / camera.config.frame_rate
        
        logger.info(f"Starting stream processing loop for camera {camera_id}")
        
        while self.running_streams.get(camera_id, False):
            try:
                start_time = time.time()
                
                # Capture frame
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, camera.capture_frame
                )
                
                if result is None:
                    # Handle connection issues
                    if camera.config.auto_reconnect and camera.reconnect_attempts < camera.config.reconnect_attempts:
                        logger.warning(f"Attempting to reconnect camera {camera_id}")
                        camera.reconnect_attempts += 1
                        await asyncio.sleep(camera.config.reconnect_delay)
                        await self.connect_camera(camera_id)
                        continue
                    else:
                        logger.error(f"Camera {camera_id} failed, stopping stream")
                        break
                
                frame, metadata = result
                
                # Assess frame quality if enabled
                if self.settings.enable_frame_quality_assessment:
                    quality_score, quality_grade = await asyncio.get_event_loop().run_in_executor(
                        self.executor, camera.assess_frame_quality, frame
                    )
                    metadata.quality_score = quality_score
                    metadata.quality_grade = quality_grade
                    
                    # Skip low quality frames
                    if quality_score < self.settings.frame_quality_threshold:
                        continue
                
                # Process frame through recognition service if enabled
                recognition_result = None
                if self.recognition_service:
                    try:
                        # Send frame to Service B for face recognition
                        recognition_result = await self.recognition_service.process_frame_with_retry(
                            frame, metadata, confidence_threshold=0.6
                        )
                        
                        # Update camera recognition stats
                        if recognition_result.success:
                            # Update frames_recognized count (we'll enhance CameraInfo later)
                            logger.debug(f"Recognition successful for camera {camera_id}: "
                                       f"{len(recognition_result.persons_detected)} persons detected")
                            
                            # ASYNC SIGHTING CAPTURE - NON-BLOCKING
                            if self.sighting_capture and recognition_result.persons_detected:
                                await self.sighting_capture.capture_sightings_async(
                                    recognition_result=recognition_result,
                                    camera_id=camera_id,
                                    original_frame=frame,
                                    frame_metadata=metadata.__dict__
                                )
                        
                        # Publish recognition event if event publisher is enabled
                        if self.event_publisher and recognition_result:
                            try:
                                await self.event_publisher.publish_recognition_event(
                                    camera_id=camera_id,
                                    frame_id=metadata.frame_id,
                                    persons_detected=recognition_result.persons_detected,
                                    processing_time_ms=recognition_result.processing_time_ms,
                                    confidence_threshold=recognition_result.confidence_threshold,
                                    frame_metadata=metadata,
                                    recognition_successful=recognition_result.success
                                )
                                logger.debug(f"Recognition event published for camera {camera_id}")
                            except Exception as e:
                                logger.error(f"Event publishing error for camera {camera_id}: {str(e)}")
                        
                    except Exception as e:
                        logger.error(f"Recognition processing error for camera {camera_id}: {str(e)}")
                        # Continue processing even if recognition fails
                
                # Add frame to processing queue
                try:
                    queue = self.frame_queues[camera_id]
                    queue.put_nowait((frame, metadata))
                    self.total_frames_processed += 1
                except asyncio.QueueFull:
                    logger.warning(f"Frame queue full for camera {camera_id}, dropping frame")
                
                # Maintain frame rate
                processing_time = time.time() - start_time
                sleep_time = max(0, frame_interval - processing_time)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                error_msg = f"Stream processing error: {str(e)}"
                camera.last_error = error_msg
                camera.errors_count += 1
                self.total_errors += 1
                logger.error(f"Camera {camera_id}: {error_msg}")
                await asyncio.sleep(1)  # Brief pause before retry
        
        logger.info(f"Stream processing loop ended for camera {camera_id}")
    
    async def get_frame(self, camera_id: str, timeout: float = 1.0) -> Optional[Tuple[np.ndarray, FrameMetadata]]:
        """Get next frame from camera queue"""
        if camera_id not in self.frame_queues:
            return None
        
        try:
            queue = self.frame_queues[camera_id]
            return await asyncio.wait_for(queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    async def _health_monitor_loop(self):
        """Monitor camera health and attempt reconnections"""
        logger.info("Starting health monitor loop")
        
        while True:
            try:
                for camera_id, camera in self.cameras.items():
                    # Check if camera needs reconnection
                    if (camera.status == CameraStatus.ERROR and 
                        camera.config.auto_reconnect and 
                        camera.reconnect_attempts < camera.config.reconnect_attempts):
                        
                        logger.info(f"Health monitor: attempting reconnection for camera {camera_id}")
                        await self.connect_camera(camera_id)
                    
                    # Check for stale frames
                    if (camera.last_frame_time and 
                        datetime.utcnow() - camera.last_frame_time > timedelta(seconds=30)):
                        logger.warning(f"Camera {camera_id}: no frames for 30 seconds")
                        camera.status = CameraStatus.ERROR
                        camera.last_error = "Frame timeout"
                
                await asyncio.sleep(self.settings.camera_health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitor error: {str(e)}")
                await asyncio.sleep(5)
    
    def get_camera_info(self, camera_id: str) -> Optional[CameraInfo]:
        """Get information for specific camera"""
        if camera_id not in self.cameras:
            return None
        return self.cameras[camera_id].get_info()
    
    def get_all_cameras_info(self) -> List[CameraInfo]:
        """Get information for all cameras"""
        return [camera.get_info() for camera in self.cameras.values()]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_cameras = len(self.cameras)
        connected_cameras = sum(1 for cam in self.cameras.values() if cam.status == CameraStatus.CONNECTED)
        active_streams = sum(1 for active in self.running_streams.values() if active)
        
        uptime = int((datetime.utcnow() - self.start_time).total_seconds())
        
        return {
            "total_cameras": total_cameras,
            "connected_cameras": connected_cameras,
            "active_streams": active_streams,
            "total_frames_processed": self.total_frames_processed,
            "total_errors": self.total_errors,
            "uptime_seconds": uptime,
            "status": "healthy" if connected_cameras > 0 else "degraded"
        }
    
    async def shutdown(self):
        """Shutdown camera manager"""
        logger.info("Shutting down Camera Manager...")
        
        # Stop all streams
        await self.stop_all_streams()
        
        # Stop health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
        
        # Shutdown recognition service
        if self.recognition_service:
            await self.recognition_service.shutdown()
        
        # Shutdown event publisher
        if self.event_publisher:
            await self.event_publisher.shutdown()
        
        # Shutdown sighting capture service
        if self.sighting_capture:
            await self.sighting_capture.shutdown()
        
        # Disconnect all cameras
        for camera_id in list(self.cameras.keys()):
            await self.disconnect_camera(camera_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Camera Manager shutdown complete")