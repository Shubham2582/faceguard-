"""
Performance Optimization & Caching Manager - Day 5 Implementation
High-performance caching for face recognition operations
Rule 2: Zero Placeholder Code - All real implementations
"""

import hashlib
import time
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import OrderedDict
import asyncio
import threading
from functools import wraps
import cv2

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: float
    hit_count: int
    size_bytes: int
    ttl: float

@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_hits: int
    total_misses: int
    total_size_bytes: int
    avg_response_time_ms: float
    cache_entries: int
    hit_ratio: float

class LRUCache:
    """High-performance LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'total_size': 0,
            'response_times': []
        }
        self._lock = threading.RLock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate consistent cache key from arguments"""
        key_data = {
            'args': [str(arg) if not isinstance(arg, (list, np.ndarray)) else hashlib.md5(str(arg).encode()).hexdigest()[:16] for arg in args],
            'kwargs': {k: (str(v) if not isinstance(v, (list, np.ndarray)) else hashlib.md5(str(v).encode()).hexdigest()[:16]) for k, v in sorted(kwargs.items())}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _estimate_size(self, data: Any) -> int:
        """Estimate memory size of cached data"""
        if isinstance(data, np.ndarray):
            return data.nbytes
        elif isinstance(data, (list, tuple)):
            return sum(self._estimate_size(item) for item in data)
        elif isinstance(data, dict):
            return sum(self._estimate_size(k) + self._estimate_size(v) for k, v in data.items())
        elif isinstance(data, str):
            return len(data.encode('utf-8'))
        else:
            return len(str(data).encode('utf-8'))
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        return time.time() - entry.timestamp > entry.ttl
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            expired_keys = [key for key, entry in self.cache.items() if self._is_expired(entry)]
            for key in expired_keys:
                entry = self.cache.pop(key)
                self.stats['total_size'] -= entry.size_bytes
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        start_time = time.time()
        
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if self._is_expired(entry):
                    self.cache.pop(key)
                    self.stats['total_size'] -= entry.size_bytes
                    self.stats['misses'] += 1
                    return None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                entry.hit_count += 1
                self.stats['hits'] += 1
                
                response_time = (time.time() - start_time) * 1000
                self.stats['response_times'].append(response_time)
                
                return entry.data
            else:
                self.stats['misses'] += 1
                return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Put value in cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        size = self._estimate_size(value)
        
        with self._lock:
            # Remove oldest entries if needed
            while len(self.cache) >= self.max_size:
                oldest_key, oldest_entry = self.cache.popitem(last=False)
                self.stats['total_size'] -= oldest_entry.size_bytes
            
            # Create cache entry
            entry = CacheEntry(
                data=value,
                timestamp=time.time(),
                hit_count=0,
                size_bytes=size,
                ttl=ttl
            )
            
            self.cache[key] = entry
            self.stats['total_size'] += size
            
            return True
    
    def get_stats(self) -> CacheStats:
        """Get cache performance statistics"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_ratio = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
            avg_response_time = np.mean(self.stats['response_times']) if self.stats['response_times'] else 0.0
            
            return CacheStats(
                total_hits=self.stats['hits'],
                total_misses=self.stats['misses'],
                total_size_bytes=self.stats['total_size'],
                avg_response_time_ms=round(avg_response_time, 2),
                cache_entries=len(self.cache),
                hit_ratio=round(hit_ratio, 3)
            )
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'total_size': 0,
                'response_times': []
            }

class ImageCache(LRUCache):
    """Specialized cache for processed images"""
    
    def __init__(self, max_size: int = 100, default_ttl: float = 1800):  # 30 minutes
        super().__init__(max_size, default_ttl)
    
    def cache_processed_image(self, image_hash: str, processed_result: Dict) -> bool:
        """Cache processed image results"""
        return self.put(f"image:{image_hash}", processed_result, self.default_ttl)
    
    def get_processed_image(self, image_hash: str) -> Optional[Dict]:
        """Get cached processed image results"""
        return self.get(f"image:{image_hash}")

class EmbeddingCache(LRUCache):
    """Specialized cache for face embeddings and recognition results"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 7200):  # 2 hours
        super().__init__(max_size, default_ttl)
    
    def cache_face_embedding(self, face_hash: str, embedding: np.ndarray, metadata: Dict) -> bool:
        """Cache face embedding with metadata"""
        cache_data = {
            'embedding': embedding.tolist(),
            'metadata': metadata,
            'timestamp': time.time()
        }
        return self.put(f"embedding:{face_hash}", cache_data, self.default_ttl)
    
    def get_face_embedding(self, face_hash: str) -> Optional[Tuple[np.ndarray, Dict]]:
        """Get cached face embedding"""
        cached = self.get(f"embedding:{face_hash}")
        if cached:
            embedding = np.array(cached['embedding'])
            metadata = cached['metadata']
            return embedding, metadata
        return None
    
    def cache_recognition_result(self, embedding_hash: str, recognition_result: Dict) -> bool:
        """Cache recognition result"""
        return self.put(f"recognition:{embedding_hash}", recognition_result, self.default_ttl)
    
    def get_recognition_result(self, embedding_hash: str) -> Optional[Dict]:
        """Get cached recognition result"""
        return self.get(f"recognition:{embedding_hash}")

class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    @staticmethod
    def hash_image(image: np.ndarray) -> str:
        """Generate consistent hash for image"""
        # Resize to standard size for consistent hashing
        resized = cv2.resize(image, (64, 64))
        return hashlib.md5(resized.tobytes()).hexdigest()
    
    @staticmethod
    def hash_face_region(image: np.ndarray, bbox: List[float]) -> str:
        """Generate hash for face region"""
        x1, y1, x2, y2 = [int(coord) for coord in bbox]
        face_region = image[y1:y2, x1:x2]
        if face_region.size > 0:
            resized = cv2.resize(face_region, (64, 64))
            return hashlib.md5(resized.tobytes()).hexdigest()
        return hashlib.md5(b'empty_face').hexdigest()
    
    @staticmethod
    def hash_embedding(embedding: np.ndarray) -> str:
        """Generate hash for embedding vector"""
        # Quantize embedding to reduce precision for consistent hashing
        quantized = np.round(embedding, 4)
        return hashlib.md5(quantized.tobytes()).hexdigest()
    
    @staticmethod
    def optimize_image_for_processing(image: np.ndarray, max_dimension: int = 1024) -> Tuple[np.ndarray, float]:
        """Optimize image size for faster processing"""
        height, width = image.shape[:2]
        scale_factor = 1.0
        
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            optimized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return optimized, scale_factor
        
        return image, scale_factor
    
    @staticmethod
    def batch_embeddings(embeddings: List[np.ndarray], batch_size: int = 32) -> List[List[np.ndarray]]:
        """Batch embeddings for efficient processing"""
        batches = []
        for i in range(0, len(embeddings), batch_size):
            batch = embeddings[i:i + batch_size]
            batches.append(batch)
        return batches

class CacheManager:
    """Main cache manager coordinating all caching operations"""
    
    def __init__(self):
        self.image_cache = ImageCache(max_size=100, default_ttl=1800)  # 30 min
        self.embedding_cache = EmbeddingCache(max_size=1000, default_ttl=7200)  # 2 hours
        self.recognition_cache = LRUCache(max_size=500, default_ttl=3600)  # 1 hour
        self.performance_optimizer = PerformanceOptimizer()
        
        # Performance tracking
        self.performance_stats = {
            'cache_hits_saved_ms': 0,
            'total_operations': 0,
            'optimization_enabled': True
        }
    
    def cache_image_processing_result(self, image: np.ndarray, result: Dict) -> bool:
        """Cache complete image processing result"""
        try:
            image_hash = self.performance_optimizer.hash_image(image)
            
            # Add performance metadata
            cache_result = {
                **result,
                'cached_at': time.time(),
                'image_hash': image_hash
            }
            
            return self.image_cache.cache_processed_image(image_hash, cache_result)
        except Exception as e:
            print(f"Error caching image result: {e}")
            return False
    
    def get_cached_image_result(self, image: np.ndarray) -> Optional[Dict]:
        """Get cached image processing result"""
        try:
            image_hash = self.performance_optimizer.hash_image(image)
            cached = self.image_cache.get_processed_image(image_hash)
            
            if cached:
                # Update performance stats
                self.performance_stats['cache_hits_saved_ms'] += cached.get('processing_time_ms', 0)
                return cached
            
            return None
        except Exception as e:
            print(f"Error retrieving cached image result: {e}")
            return None
    
    def cache_face_recognition(self, face_data: Dict, recognition_result: Dict) -> bool:
        """Cache face recognition result"""
        try:
            if 'embedding' in face_data:
                embedding = np.array(face_data['embedding'])
                embedding_hash = self.performance_optimizer.hash_embedding(embedding)
                return self.embedding_cache.cache_recognition_result(embedding_hash, recognition_result)
            return False
        except Exception as e:
            print(f"Error caching recognition result: {e}")
            return False
    
    def get_cached_recognition(self, embedding: np.ndarray) -> Optional[Dict]:
        """Get cached recognition result"""
        try:
            embedding_hash = self.performance_optimizer.hash_embedding(embedding)
            return self.embedding_cache.get_recognition_result(embedding_hash)
        except Exception as e:
            print(f"Error retrieving cached recognition: {e}")
            return None
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        image_stats = self.image_cache.get_stats()
        embedding_stats = self.embedding_cache.get_stats()
        recognition_stats = self.recognition_cache.get_stats()
        
        total_hits = image_stats.total_hits + embedding_stats.total_hits + recognition_stats.total_hits
        total_misses = image_stats.total_misses + embedding_stats.total_misses + recognition_stats.total_misses
        total_requests = total_hits + total_misses
        
        overall_hit_ratio = total_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'overall': {
                'total_hits': total_hits,
                'total_misses': total_misses,
                'hit_ratio': round(overall_hit_ratio, 3),
                'total_size_mb': round((image_stats.total_size_bytes + embedding_stats.total_size_bytes + recognition_stats.total_size_bytes) / 1024 / 1024, 2),
                'cache_hits_saved_ms': self.performance_stats['cache_hits_saved_ms'],
                'total_operations': self.performance_stats['total_operations']
            },
            'image_cache': asdict(image_stats),
            'embedding_cache': asdict(embedding_stats),
            'recognition_cache': asdict(recognition_stats),
            'performance': {
                'optimization_enabled': self.performance_stats['optimization_enabled'],
                'avg_speedup_ratio': round(self.performance_stats['cache_hits_saved_ms'] / max(self.performance_stats['total_operations'], 1), 2)
            }
        }
    
    def clear_all_caches(self):
        """Clear all caches"""
        self.image_cache.clear()
        self.embedding_cache.clear()
        self.recognition_cache.clear()
        self.performance_stats = {
            'cache_hits_saved_ms': 0,
            'total_operations': 0,
            'optimization_enabled': True
        }

def cached_operation(cache_manager: CacheManager, cache_type: str = 'general', ttl: Optional[float] = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager.recognition_cache._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.recognition_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            # Cache the result
            cache_manager.recognition_cache.put(cache_key, result, ttl)
            cache_manager.performance_stats['total_operations'] += 1
            
            return result
        
        return wrapper
    return decorator

# Global cache manager instance
cache_manager = CacheManager()