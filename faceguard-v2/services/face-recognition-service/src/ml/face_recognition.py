"""
InsightFace Buffalo_L Integration - Day 4 Implementation
Single-stage face recognition (RetinaFace + ArcFace together)
Rule 2: Zero Placeholder Code - All real implementations
"""

import numpy as np
import cv2
import time
from typing import List, Dict, Tuple, Optional, Union
import logging
from pathlib import Path

# Import InsightFace
try:
    import insightface
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("WARNING: InsightFace not available - face recognition will be disabled")

from config.settings import settings


class FaceRecognitionEngine:
    """
    GPU-enabled face recognition using InsightFace buffalo_l models
    Single-stage processing: Detection + Recognition in one pass
    """
    
    def __init__(self):
        self.app = None
        self.model_loaded = False
        self.gpu_available = False
        self.detection_threshold = settings.detection_confidence
        self.processing_stats = {
            'total_processed': 0,
            'total_faces_detected': 0,
            'total_processing_time_ms': 0,
            'gpu_usage_count': 0
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """
        Initialize InsightFace buffalo_l models with GPU support
        Real model loading, no placeholders
        """
        if not INSIGHTFACE_AVAILABLE:
            print("InsightFace not available - skipping model initialization")
            return
        
        try:
            print("Initializing InsightFace buffalo_l models...")
            
            # Determine providers (GPU first, CPU fallback)
            providers = ['CPUExecutionProvider']
            if settings.gpu_enabled:
                try:
                    # Check if CUDA is available
                    import onnxruntime as ort
                    available_providers = ort.get_available_providers()
                    if 'CUDAExecutionProvider' in available_providers:
                        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                        self.gpu_available = True
                        print("GPU (CUDA) provider available")
                    else:
                        print("CUDA provider not available, using CPU")
                except Exception as e:
                    print(f"GPU check failed: {e}, using CPU")
            
            # Initialize FaceAnalysis with buffalo_l models
            self.app = FaceAnalysis(
                providers=providers,
                allowed_modules=['detection', 'recognition', 'genderage']
            )
            
            # Prepare the models
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            
            self.model_loaded = True
            print(f"InsightFace models loaded successfully")
            print(f"Providers: {providers}")
            print(f"GPU enabled: {self.gpu_available}")
            
        except Exception as e:
            print(f"Error initializing InsightFace models: {e}")
            self.model_loaded = False
            self.gpu_available = False
    
    def is_ready(self) -> bool:
        """Check if face recognition is ready"""
        return INSIGHTFACE_AVAILABLE and self.model_loaded and self.app is not None
    
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces in image using RetinaFace (part of buffalo_l)
        Returns face detection results with bounding boxes
        """
        if not self.is_ready():
            return []
        
        try:
            start_time = time.time()
            
            # Get faces from InsightFace (includes detection + recognition)
            faces = self.app.get(image)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update stats
            self.processing_stats['total_processed'] += 1
            self.processing_stats['total_faces_detected'] += len(faces)
            self.processing_stats['total_processing_time_ms'] += processing_time
            if self.gpu_available:
                self.processing_stats['gpu_usage_count'] += 1
            
            # Convert to our format
            detected_faces = []
            for i, face in enumerate(faces):
                face_data = {
                    'face_id': i,
                    'bbox': face.bbox.tolist(),  # [x1, y1, x2, y2]
                    'confidence': float(face.det_score),
                    'embedding': face.embedding.tolist(),  # 512D vector
                    'age': int(face.age) if hasattr(face, 'age') and face.age is not None else None,
                    'gender': face.sex if hasattr(face, 'sex') else None,  # Keep as original value
                    'pose': face.pose.tolist() if hasattr(face, 'pose') and face.pose is not None else None
                }
                
                # Only include faces above detection threshold
                if face_data['confidence'] >= self.detection_threshold:
                    detected_faces.append(face_data)
            
            return detected_faces
            
        except Exception as e:
            print(f"Error in face detection: {e}")
            return []
    
    def extract_embedding(self, image: np.ndarray, bbox: Optional[List[float]] = None) -> Optional[List[float]]:
        """
        Extract face embedding from image
        If bbox provided, crop to that region first
        """
        if not self.is_ready():
            return None
        
        try:
            # If bbox provided, crop the image
            if bbox:
                x1, y1, x2, y2 = [int(coord) for coord in bbox]
                cropped_image = image[y1:y2, x1:x2]
                faces = self.app.get(cropped_image)
            else:
                faces = self.app.get(image)
            
            if len(faces) > 0:
                # Return embedding of the first (highest confidence) face
                return faces[0].embedding.tolist()
            
            return None
            
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            return None
    
    def process_image_single_stage(self, image: Union[np.ndarray, str]) -> Dict:
        """
        Single-stage face processing: Detection + Recognition together
        This is the main method implementing the strategic requirement
        """
        if not self.is_ready():
            return {
                'success': False,
                'error': 'Face recognition engine not ready',
                'faces': [],
                'processing_time_ms': 0
            }
        
        try:
            start_time = time.time()
            
            # Load image if path provided
            if isinstance(image, str):
                img = cv2.imread(image)
                if img is None:
                    return {
                        'success': False,
                        'error': 'Could not load image',
                        'faces': [],
                        'processing_time_ms': 0
                    }
            else:
                img = image
            
            # Validate image
            if img is None or img.size == 0:
                return {
                    'success': False,
                    'error': 'Invalid image data',
                    'faces': [],
                    'processing_time_ms': 0
                }
            
            # Single-stage processing: Detection + Recognition
            faces = self.detect_faces(img)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'faces': faces,
                'face_count': len(faces),
                'processing_time_ms': round(processing_time, 2),
                'image_size': {
                    'width': img.shape[1],
                    'height': img.shape[0]
                },
                'gpu_used': self.gpu_available,
                'model_info': {
                    'name': 'buffalo_l',
                    'detection': 'RetinaFace',
                    'recognition': 'ArcFace',
                    'stage': 'single'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'faces': [],
                'processing_time_ms': 0
            }
    
    def recognize_faces_with_database(self, faces: List[Dict], faiss_service) -> List[Dict]:
        """
        Recognize detected faces against database using FAISS
        Tests ALL embeddings per person (not LIMIT 1)
        """
        if not faiss_service:
            return []
        
        recognized_faces = []
        
        for face in faces:
            try:
                # Get embedding from detected face
                embedding = face.get('embedding')
                if not embedding:
                    continue
                
                # Search for person in FAISS
                person_result = faiss_service.search_person(
                    query_vector=embedding,
                    threshold=settings.recognition_threshold
                )
                
                if person_result:
                    recognized_face = {
                        **face,  # Include original detection data
                        'recognized': True,
                        'person_id': person_result['person_id'],
                        'recognition_confidence': person_result['max_similarity'],
                        'avg_confidence': person_result['avg_similarity'],
                        'matching_embeddings': person_result['matching_embeddings'],
                        'total_embeddings': person_result['total_embeddings']
                    }
                else:
                    recognized_face = {
                        **face,
                        'recognized': False,
                        'person_id': None,
                        'recognition_confidence': 0.0
                    }
                
                recognized_faces.append(recognized_face)
                
            except Exception as e:
                print(f"Error recognizing face: {e}")
                # Include face without recognition info
                recognized_faces.append({
                    **face,
                    'recognized': False,
                    'error': str(e)
                })
        
        return recognized_faces
    
    def get_model_info(self) -> Dict:
        """Get model information and status"""
        return {
            'available': INSIGHTFACE_AVAILABLE,
            'loaded': self.model_loaded,
            'gpu_available': self.gpu_available,
            'gpu_enabled': settings.gpu_enabled,
            'model_name': 'buffalo_l',
            'detection_model': 'RetinaFace',
            'recognition_model': 'ArcFace',
            'processing_mode': 'single_stage',
            'detection_threshold': self.detection_threshold,
            'recognition_threshold': settings.recognition_threshold
        }
    
    def get_performance_stats(self) -> Dict:
        """Get real performance statistics"""
        if self.processing_stats['total_processed'] == 0:
            return {
                'total_processed': 0,
                'avg_processing_time_ms': 0,
                'total_faces_detected': 0,
                'avg_faces_per_image': 0,
                'gpu_usage_percentage': 0
            }
        
        return {
            'total_processed': self.processing_stats['total_processed'],
            'avg_processing_time_ms': round(
                self.processing_stats['total_processing_time_ms'] / self.processing_stats['total_processed'], 2
            ),
            'total_faces_detected': self.processing_stats['total_faces_detected'],
            'avg_faces_per_image': round(
                self.processing_stats['total_faces_detected'] / self.processing_stats['total_processed'], 2
            ),
            'gpu_usage_percentage': round(
                (self.processing_stats['gpu_usage_count'] / self.processing_stats['total_processed']) * 100, 1
            ) if self.processing_stats['total_processed'] > 0 else 0
        }


# Global face recognition engine instance
face_engine = FaceRecognitionEngine()