"""
Quality Control Framework - Face Recognition Service
Prevention Rules Implementation:
- Rule 2: Zero Placeholder Code - All real implementations
- Rule 3: Error-First Development - Comprehensive validation
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any
import time
import logging
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    """Face recognition quality metrics"""
    detection_confidence: float
    recognition_confidence: float
    image_quality_score: float
    processing_time_ms: float
    gpu_used: bool
    face_count: int
    embedding_quality_score: float

@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    overall_score: float
    passed: bool
    issues: List[str]
    recommendations: List[str]
    metrics: QualityMetrics
    timestamp: float

class ImageQualityAnalyzer:
    """Analyze image quality for face recognition"""
    
    def __init__(self):
        self.min_resolution = (112, 112)  # Minimum for ArcFace
        self.max_resolution = (2048, 2048)  # Maximum practical resolution
        self.min_brightness = 50
        self.max_brightness = 200
        
    def analyze_image_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive image quality analysis
        Returns quality score and specific metrics
        """
        try:
            quality_factors = {}
            
            # Resolution check
            height, width = image.shape[:2]
            quality_factors['resolution'] = self._score_resolution(width, height)
            
            # Brightness analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            quality_factors['brightness'] = self._score_brightness(brightness)
            
            # Contrast analysis
            contrast = np.std(gray)
            quality_factors['contrast'] = self._score_contrast(contrast)
            
            # Blur detection using Laplacian variance
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_factors['sharpness'] = self._score_sharpness(blur_score)
            
            # Noise analysis
            noise_score = self._estimate_noise(gray)
            quality_factors['noise'] = self._score_noise(noise_score)
            
            # Overall quality score (weighted average)
            weights = {
                'resolution': 0.2,
                'brightness': 0.2,
                'contrast': 0.2,
                'sharpness': 0.25,
                'noise': 0.15
            }
            
            overall_score = sum(
                quality_factors[factor] * weights[factor] 
                for factor in weights
            )
            
            return {
                'overall_score': round(overall_score, 3),
                'factors': quality_factors,
                'image_stats': {
                    'width': width,
                    'height': height,
                    'brightness': round(brightness, 2),
                    'contrast': round(contrast, 2),
                    'sharpness': round(blur_score, 2),
                    'noise': round(noise_score, 4)
                }
            }
            
        except Exception as e:
            return {
                'overall_score': 0.0,
                'error': str(e),
                'factors': {},
                'image_stats': {}
            }
    
    def _score_resolution(self, width: int, height: int) -> float:
        """Score image resolution (0.0 to 1.0)"""
        min_area = self.min_resolution[0] * self.min_resolution[1]
        current_area = width * height
        
        if current_area < min_area:
            return 0.0
        elif current_area > 640 * 640:  # Optimal range
            return 1.0
        else:
            return current_area / (640 * 640)
    
    def _score_brightness(self, brightness: float) -> float:
        """Score image brightness (0.0 to 1.0)"""
        if brightness < self.min_brightness or brightness > self.max_brightness:
            return max(0.0, 1.0 - abs(brightness - 127.5) / 127.5)
        else:
            # Optimal range: 80-175
            if 80 <= brightness <= 175:
                return 1.0
            else:
                return 0.8
    
    def _score_contrast(self, contrast: float) -> float:
        """Score image contrast (0.0 to 1.0)"""
        if contrast < 20:
            return 0.3  # Very low contrast
        elif contrast > 80:
            return 1.0  # Good contrast
        else:
            return 0.3 + (contrast - 20) / 60 * 0.7
    
    def _score_sharpness(self, blur_score: float) -> float:
        """Score image sharpness using Laplacian variance (0.0 to 1.0)"""
        if blur_score < 100:
            return 0.2  # Very blurry
        elif blur_score > 500:
            return 1.0  # Sharp
        else:
            return 0.2 + (blur_score - 100) / 400 * 0.8
    
    def _score_noise(self, noise_score: float) -> float:
        """Score image noise level (0.0 to 1.0)"""
        if noise_score < 0.01:
            return 1.0  # Low noise
        elif noise_score > 0.05:
            return 0.3  # High noise
        else:
            return 1.0 - (noise_score - 0.01) / 0.04 * 0.7
    
    def _estimate_noise(self, gray_image: np.ndarray) -> float:
        """Estimate noise level in grayscale image"""
        try:
            # Use Laplacian to estimate noise
            laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
            noise_estimate = np.var(laplacian) / (gray_image.shape[0] * gray_image.shape[1])
            return noise_estimate
        except:
            return 0.0

class FaceQualityAnalyzer:
    """Analyze face detection and recognition quality"""
    
    def __init__(self):
        self.min_face_size = 50  # Minimum face size in pixels
        self.min_detection_confidence = 0.5
        self.min_recognition_confidence = 0.6
        
    def analyze_face_quality(self, face_data: Dict) -> Dict[str, Any]:
        """
        Analyze quality of a detected/recognized face
        """
        try:
            quality_factors = {}
            
            # Face size analysis
            bbox = face_data.get('bbox', [])
            if len(bbox) >= 4:
                face_width = bbox[2] - bbox[0]
                face_height = bbox[3] - bbox[1]
                face_area = face_width * face_height
                quality_factors['size'] = self._score_face_size(face_width, face_height)
            else:
                quality_factors['size'] = 0.0
                face_area = 0
            
            # Detection confidence
            detection_conf = face_data.get('confidence', 0.0)
            quality_factors['detection'] = self._score_detection_confidence(detection_conf)
            
            # Recognition confidence (if available)
            recognition_conf = face_data.get('recognition_confidence', 0.0)
            quality_factors['recognition'] = self._score_recognition_confidence(recognition_conf)
            
            # Embedding quality (based on norm)
            embedding = face_data.get('embedding', [])
            if embedding:
                embedding_norm = np.linalg.norm(embedding)
                quality_factors['embedding'] = self._score_embedding_quality(embedding_norm)
            else:
                quality_factors['embedding'] = 0.0
            
            # Age/gender confidence (if available)
            age = face_data.get('age')
            gender = face_data.get('gender')
            quality_factors['attributes'] = self._score_attributes_quality(age, gender)
            
            # Overall face quality score
            weights = {
                'size': 0.2,
                'detection': 0.25,
                'recognition': 0.25,
                'embedding': 0.2,
                'attributes': 0.1
            }
            
            overall_score = sum(
                quality_factors[factor] * weights[factor] 
                for factor in weights
            )
            
            return {
                'overall_score': round(overall_score, 3),
                'factors': quality_factors,
                'face_stats': {
                    'face_area': face_area,
                    'detection_confidence': detection_conf,
                    'recognition_confidence': recognition_conf,
                    'embedding_norm': np.linalg.norm(embedding) if embedding else 0.0,
                    'has_age': age is not None,
                    'has_gender': gender is not None
                }
            }
            
        except Exception as e:
            return {
                'overall_score': 0.0,
                'error': str(e),
                'factors': {},
                'face_stats': {}
            }
    
    def _score_face_size(self, width: float, height: float) -> float:
        """Score face size (0.0 to 1.0)"""
        min_dim = min(width, height)
        if min_dim < self.min_face_size:
            return 0.2
        elif min_dim > 200:
            return 1.0
        else:
            return 0.2 + (min_dim - self.min_face_size) / 150 * 0.8
    
    def _score_detection_confidence(self, confidence: float) -> float:
        """Score detection confidence (0.0 to 1.0)"""
        if confidence < self.min_detection_confidence:
            return confidence / self.min_detection_confidence * 0.5
        else:
            return 0.5 + (confidence - self.min_detection_confidence) / 0.5 * 0.5
    
    def _score_recognition_confidence(self, confidence: float) -> float:
        """Score recognition confidence (0.0 to 1.0)"""
        if confidence == 0.0:
            return 0.0  # No recognition
        elif confidence < self.min_recognition_confidence:
            return confidence / self.min_recognition_confidence * 0.5
        else:
            return 0.5 + (confidence - self.min_recognition_confidence) / 0.4 * 0.5
    
    def _score_embedding_quality(self, embedding_norm: float) -> float:
        """Score embedding quality based on norm (0.0 to 1.0)"""
        # Good embeddings typically have norms between 20-30
        if 20 <= embedding_norm <= 30:
            return 1.0
        elif embedding_norm < 10 or embedding_norm > 50:
            return 0.3
        else:
            return 0.7
    
    def _score_attributes_quality(self, age: Optional[int], gender: Optional[str]) -> float:
        """Score age/gender attributes quality (0.0 to 1.0)"""
        score = 0.0
        if age is not None and 0 <= age <= 120:
            score += 0.5
        if gender is not None:
            score += 0.5
        return score

class QualityController:
    """Main quality control orchestrator"""
    
    def __init__(self):
        self.image_analyzer = ImageQualityAnalyzer()
        self.face_analyzer = FaceQualityAnalyzer()
        self.quality_thresholds = {
            'image_min_score': 0.4,
            'face_min_score': 0.3,
            'overall_min_score': 0.5
        }
        
    def assess_recognition_quality(
        self,
        image: np.ndarray,
        faces: List[Dict],
        processing_time_ms: float,
        gpu_used: bool
    ) -> QualityReport:
        """
        Comprehensive quality assessment for face recognition results
        """
        try:
            start_time = time.time()
            issues = []
            recommendations = []
            
            # Analyze image quality
            image_quality = self.image_analyzer.analyze_image_quality(image)
            image_score = image_quality.get('overall_score', 0.0)
            
            # Check image quality issues
            if image_score < self.quality_thresholds['image_min_score']:
                issues.append(f"Low image quality: {image_score:.2f}")
                recommendations.append("Improve lighting and image resolution")
            
            # Analyze face qualities
            face_scores = []
            recognition_confidences = []
            
            for face in faces:
                face_quality = self.face_analyzer.analyze_face_quality(face)
                face_score = face_quality.get('overall_score', 0.0)
                face_scores.append(face_score)
                
                # Check face-specific issues
                if face_score < self.quality_thresholds['face_min_score']:
                    issues.append(f"Low quality face detected: {face_score:.2f}")
                
                # Track recognition confidence
                if face.get('recognized', False):
                    recognition_confidences.append(face.get('recognition_confidence', 0.0))
            
            # Calculate overall metrics
            avg_face_score = np.mean(face_scores) if face_scores else 0.0
            max_recognition_conf = max(recognition_confidences) if recognition_confidences else 0.0
            embedding_quality = np.mean([
                self.face_analyzer._score_embedding_quality(
                    np.linalg.norm(face.get('embedding', []))
                ) for face in faces if face.get('embedding')
            ]) if faces else 0.0
            
            # Overall quality score
            overall_score = (
                image_score * 0.3 +
                avg_face_score * 0.4 +
                (max_recognition_conf if recognition_confidences else 0.5) * 0.3
            )
            
            # Check performance issues
            if processing_time_ms > 1000:
                issues.append(f"Slow processing: {processing_time_ms:.1f}ms")
                recommendations.append("Consider image resizing or GPU optimization")
            
            if not gpu_used:
                recommendations.append("Enable GPU acceleration for better performance")
            
            # Check recognition issues
            recognized_count = sum(1 for f in faces if f.get('recognized', False))
            if len(faces) > 0 and recognized_count == 0:
                issues.append("No faces recognized from detected faces")
                recommendations.append("Check if faces are enrolled in database")
            
            # Final assessment
            passed = (
                overall_score >= self.quality_thresholds['overall_min_score'] and
                len([i for i in issues if 'Low' in i]) <= 1
            )
            
            metrics = QualityMetrics(
                detection_confidence=np.mean([f.get('confidence', 0) for f in faces]) if faces else 0.0,
                recognition_confidence=max_recognition_conf,
                image_quality_score=image_score,
                processing_time_ms=processing_time_ms,
                gpu_used=gpu_used,
                face_count=len(faces),
                embedding_quality_score=embedding_quality
            )
            
            assessment_time = (time.time() - start_time) * 1000
            
            return QualityReport(
                overall_score=round(overall_score, 3),
                passed=passed,
                issues=issues,
                recommendations=recommendations,
                metrics=metrics,
                timestamp=time.time()
            )
            
        except Exception as e:
            return QualityReport(
                overall_score=0.0,
                passed=False,
                issues=[f"Quality assessment error: {str(e)}"],
                recommendations=["Retry with different image"],
                metrics=QualityMetrics(0, 0, 0, processing_time_ms, gpu_used, 0, 0),
                timestamp=time.time()
            )
    
    def generate_quality_summary(self, report: QualityReport) -> Dict[str, Any]:
        """Generate human-readable quality summary"""
        status = "PASS" if report.passed else "FAIL"
        
        return {
            'status': status,
            'overall_score': report.overall_score,
            'grade': self._score_to_grade(report.overall_score),
            'assessment_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.timestamp)),
            'metrics': {
                'detection_confidence': f"{report.metrics.detection_confidence:.2f}",
                'recognition_confidence': f"{report.metrics.recognition_confidence:.2f}",
                'image_quality': f"{report.metrics.image_quality_score:.2f}",
                'processing_time_ms': f"{report.metrics.processing_time_ms:.1f}",
                'face_count': report.metrics.face_count,
                'gpu_acceleration': report.metrics.gpu_used
            },
            'issues': report.issues,
            'recommendations': report.recommendations,
            'details': {
                'quality_thresholds': self.quality_thresholds,
                'embedding_quality': f"{report.metrics.embedding_quality_score:.2f}"
            }
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "D"
        else:
            return "F"

# Global quality controller instance
quality_controller = QualityController()