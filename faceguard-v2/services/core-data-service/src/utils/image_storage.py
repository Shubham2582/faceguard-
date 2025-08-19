"""
Image Storage Utilities for Person Sighting Tracking

Handles WebP compression, quality assessment, and file organization
for sighting images separate from enrollment images.

File Structure:
- F:/faceguard/data/known_faces/ (EXISTING - enrollment images)
- F:/faceguard/storage/persons/{person_id}/sightings/ (NEW - sighting images)
"""

import os
import cv2
import hashlib
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple
from PIL import Image, ImageEnhance
import numpy as np

class ImageStorageManager:
    """Manages storage and compression for person sighting images"""
    
    def __init__(self, base_storage_path: str = "F:/faceguard/storage"):
        self.base_path = Path(base_storage_path)
        self.ensure_storage_structure()
        
    def ensure_storage_structure(self) -> None:
        """Create necessary storage directories"""
        directories = [
            self.base_path / "persons",
            self.base_path / "temp", 
            self.base_path / "uploads"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_person_sighting_dir(self, person_id: str) -> Path:
        """Get person-specific sighting directory"""
        person_dir = self.base_path / "persons" / person_id / "sightings"
        person_dir.mkdir(parents=True, exist_ok=True)
        return person_dir
    
    def get_date_subdir(self, person_id: str, timestamp: datetime) -> Path:
        """Get date-organized subdirectory for sightings"""
        year_month = timestamp.strftime("%Y/%m")
        date_dir = self.get_person_sighting_dir(person_id) / year_month
        date_dir.mkdir(parents=True, exist_ok=True)
        return date_dir
    
    async def save_sighting_image(
        self, 
        image: np.ndarray,
        person_id: str,
        camera_id: str,
        source_type: str = "camera_stream",
        quality: float = 85.0,
        timestamp: Optional[datetime] = None
    ) -> Tuple[str, float, Dict]:
        """
        Save sighting image with WebP compression and quality assessment
        
        Returns:
            Tuple[file_path, quality_score, metadata]
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        try:
            # 1. Assess image quality first
            quality_score = await self.assess_image_quality(image)
            
            # 2. Get storage location
            date_dir = self.get_date_subdir(person_id, timestamp)
            
            # 3. Generate unique filename
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            image_hash = self.generate_image_hash(image)[:8]
            filename = f"{source_type}_{camera_id}_{timestamp_str}_{image_hash}.webp"
            file_path = date_dir / filename
            
            # 4. Compress and save as WebP
            await self.save_webp_compressed(image, file_path, quality)
            
            # 5. Generate metadata
            metadata = {
                "original_size": image.shape,
                "file_size_bytes": file_path.stat().st_size,
                "compression_quality": quality,
                "quality_score": quality_score,
                "timestamp": timestamp.isoformat(),
                "camera_id": camera_id,
                "source_type": source_type
            }
            
            return str(file_path), quality_score, metadata
            
        except Exception as e:
            raise Exception(f"Failed to save sighting image: {str(e)}")
    
    async def assess_image_quality(self, image: np.ndarray) -> float:
        """
        Assess face image quality for embedding update decisions
        
        Returns quality score 0.0-1.0 (higher = better)
        """
        try:
            # 1. Brightness assessment
            brightness = np.mean(image)
            brightness_score = min(1.0, max(0.0, 1.0 - abs(brightness - 127) / 127))
            
            # 2. Contrast assessment  
            contrast = np.std(image)
            contrast_score = min(1.0, contrast / 60.0)  # Normalize to 0-1
            
            # 3. Sharpness assessment (Laplacian variance)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 1000.0)
            
            # 4. Resolution assessment
            height, width = image.shape[:2]
            resolution_score = min(1.0, (height * width) / (200 * 200))  # Normalize for 200x200 minimum
            
            # 5. Weighted combination
            quality_score = (
                brightness_score * 0.2 +
                contrast_score * 0.3 +
                sharpness_score * 0.4 +
                resolution_score * 0.1
            )
            
            return round(quality_score, 3)
            
        except Exception as e:
            # Default to medium quality if assessment fails
            return 0.5
    
    async def save_webp_compressed(
        self, 
        image: np.ndarray, 
        file_path: Path, 
        quality: float = 85.0
    ) -> None:
        """Save image with WebP compression for space efficiency"""
        try:
            # Convert BGR to RGB for PIL
            if len(image.shape) == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
                
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_image)
            
            # Save as WebP with specified quality
            pil_image.save(
                file_path,
                "WEBP",
                quality=int(quality),
                method=6,  # Maximum compression effort
                lossless=False
            )
            
        except Exception as e:
            raise Exception(f"Failed to save WebP image: {str(e)}")
    
    def generate_image_hash(self, image: np.ndarray) -> str:
        """Generate hash for image deduplication"""
        # Use image content hash for deduplication
        image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
        return hashlib.md5(image_bytes).hexdigest()
    
    async def should_update_embeddings(
        self, 
        current_quality: float, 
        person_id: str,
        min_improvement: float = 0.1
    ) -> bool:
        """
        Determine if current image quality justifies embedding update
        
        Args:
            current_quality: Quality score of current image
            person_id: Person identifier
            min_improvement: Minimum quality improvement required (default 10%)
        """
        try:
            # This will be integrated with database to check best existing quality
            # For now, return True if quality is above threshold
            return current_quality > 0.8
            
        except Exception as e:
            # Conservative approach - don't update on errors
            return False
    
    async def cleanup_old_sightings(
        self, 
        person_id: str, 
        days_to_keep: int = 90
    ) -> Dict[str, int]:
        """
        Clean up old sighting images based on retention policy
        
        Returns:
            Dict with cleanup statistics
        """
        try:
            person_dir = self.get_person_sighting_dir(person_id)
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            deleted_files = 0
            deleted_bytes = 0
            
            for file_path in person_dir.rglob("*.webp"):
                if file_path.stat().st_mtime < cutoff_date:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files += 1
                    deleted_bytes += file_size
            
            return {
                "deleted_files": deleted_files,
                "deleted_bytes": deleted_bytes,
                "days_kept": days_to_keep
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_storage_stats(self) -> Dict:
        """Get storage usage statistics"""
        try:
            total_files = 0
            total_bytes = 0
            person_count = 0
            
            persons_dir = self.base_path / "persons"
            if persons_dir.exists():
                for person_dir in persons_dir.iterdir():
                    if person_dir.is_dir():
                        person_count += 1
                        for file_path in person_dir.rglob("*.webp"):
                            total_files += 1
                            total_bytes += file_path.stat().st_size
            
            return {
                "total_persons": person_count,
                "total_sighting_images": total_files,
                "total_storage_bytes": total_bytes,
                "total_storage_mb": round(total_bytes / (1024 * 1024), 2),
                "avg_bytes_per_image": round(total_bytes / max(1, total_files), 2)
            }
            
        except Exception as e:
            return {"error": str(e)}


# Initialize global storage manager
storage_manager = ImageStorageManager()