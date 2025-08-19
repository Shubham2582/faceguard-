"""
Performance Monitoring & Metrics Collection - Day 5 Implementation
Real-time performance tracking and optimization recommendations
Rule 2: Zero Placeholder Code - All real implementations
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import numpy as np
import json
from datetime import datetime, timedelta

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    timestamp: float
    operation: str
    duration_ms: float
    success: bool
    metadata: Dict[str, Any]

@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    gpu_memory_mb: Optional[float]
    gpu_utilization: Optional[float]

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    timeframe_minutes: int
    total_operations: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    success_rate: float
    throughput_ops_per_second: float
    system_health: Dict[str, Any]
    bottlenecks: List[str]
    recommendations: List[str]

class MetricsCollector:
    """Collects and aggregates performance metrics"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.system_metrics: deque = deque(maxlen=1000)  # Store system metrics for last ~16 minutes
        self.operation_stats = defaultdict(list)
        self._lock = threading.RLock()
        
        # Performance thresholds
        self.thresholds = {
            'response_time_warning_ms': 500,
            'response_time_critical_ms': 2000,
            'memory_warning_percent': 80,
            'memory_critical_percent': 90,
            'cpu_warning_percent': 80,
            'success_rate_warning': 0.95,
            'success_rate_critical': 0.90
        }
    
    def record_operation(self, operation: str, duration_ms: float, success: bool = True, **metadata):
        """Record a performance metric for an operation"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata
        )
        
        with self._lock:
            self.metrics.append(metric)
            self.operation_stats[operation].append(metric)
    
    def record_system_metrics(self):
        """Record current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            
            # GPU metrics (if available)
            gpu_memory_mb = None
            gpu_utilization = None
            
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use first GPU
                    gpu_memory_mb = gpu.memoryUsed
                    gpu_utilization = gpu.load * 100
            except (ImportError, Exception):
                pass  # GPU monitoring not available
            
            system_metric = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory.percent,
                gpu_memory_mb=gpu_memory_mb,
                gpu_utilization=gpu_utilization
            )
            
            with self._lock:
                self.system_metrics.append(system_metric)
                
        except Exception as e:
            print(f"Error recording system metrics: {e}")
    
    def get_metrics_in_timeframe(self, minutes: int) -> List[PerformanceMetric]:
        """Get metrics from the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            return [metric for metric in self.metrics if metric.timestamp >= cutoff_time]
    
    def get_system_metrics_in_timeframe(self, minutes: int) -> List[SystemMetrics]:
        """Get system metrics from the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            return [metric for metric in self.system_metrics if metric.timestamp >= cutoff_time]
    
    def calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        return np.percentile(values, percentile)
    
    def generate_performance_report(self, timeframe_minutes: int = 60) -> PerformanceReport:
        """Generate comprehensive performance report"""
        metrics = self.get_metrics_in_timeframe(timeframe_minutes)
        system_metrics = self.get_system_metrics_in_timeframe(timeframe_minutes)
        
        if not metrics:
            return PerformanceReport(
                timeframe_minutes=timeframe_minutes,
                total_operations=0,
                avg_response_time_ms=0.0,
                p95_response_time_ms=0.0,
                p99_response_time_ms=0.0,
                success_rate=1.0,
                throughput_ops_per_second=0.0,
                system_health={},
                bottlenecks=[],
                recommendations=[]
            )
        
        # Calculate performance metrics
        durations = [m.duration_ms for m in metrics]
        successes = [m.success for m in metrics]
        
        total_operations = len(metrics)
        avg_response_time = np.mean(durations)
        p95_response_time = self.calculate_percentile(durations, 95)
        p99_response_time = self.calculate_percentile(durations, 99)
        success_rate = sum(successes) / len(successes)
        
        # Calculate throughput
        time_span = timeframe_minutes * 60
        throughput = total_operations / time_span if time_span > 0 else 0
        
        # System health analysis
        system_health = self._analyze_system_health(system_metrics)
        
        # Identify bottlenecks and recommendations
        bottlenecks, recommendations = self._analyze_bottlenecks(metrics, system_metrics)
        
        return PerformanceReport(
            timeframe_minutes=timeframe_minutes,
            total_operations=total_operations,
            avg_response_time_ms=round(avg_response_time, 2),
            p95_response_time_ms=round(p95_response_time, 2),
            p99_response_time_ms=round(p99_response_time, 2),
            success_rate=round(success_rate, 3),
            throughput_ops_per_second=round(throughput, 2),
            system_health=system_health,
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )
    
    def _analyze_system_health(self, system_metrics: List[SystemMetrics]) -> Dict[str, Any]:
        """Analyze system health from metrics"""
        if not system_metrics:
            return {}
        
        # Calculate averages
        avg_cpu = np.mean([m.cpu_percent for m in system_metrics])
        avg_memory_percent = np.mean([m.memory_percent for m in system_metrics])
        avg_memory_mb = np.mean([m.memory_mb for m in system_metrics])
        
        # GPU metrics if available
        gpu_metrics = [m for m in system_metrics if m.gpu_memory_mb is not None]
        avg_gpu_memory = np.mean([m.gpu_memory_mb for m in gpu_metrics]) if gpu_metrics else None
        avg_gpu_utilization = np.mean([m.gpu_utilization for m in gpu_metrics]) if gpu_metrics else None
        
        health_status = "healthy"
        if avg_cpu > self.thresholds['cpu_warning_percent'] or avg_memory_percent > self.thresholds['memory_warning_percent']:
            health_status = "warning"
        if avg_memory_percent > self.thresholds['memory_critical_percent']:
            health_status = "critical"
        
        return {
            'status': health_status,
            'cpu_percent': round(avg_cpu, 1),
            'memory_percent': round(avg_memory_percent, 1),
            'memory_mb': round(avg_memory_mb, 1),
            'gpu_memory_mb': round(avg_gpu_memory, 1) if avg_gpu_memory else None,
            'gpu_utilization_percent': round(avg_gpu_utilization, 1) if avg_gpu_utilization else None,
            'metrics_count': len(system_metrics)
        }
    
    def _analyze_bottlenecks(self, metrics: List[PerformanceMetric], system_metrics: List[SystemMetrics]) -> tuple[List[str], List[str]]:
        """Analyze performance bottlenecks and generate recommendations"""
        bottlenecks = []
        recommendations = []
        
        if not metrics:
            return bottlenecks, recommendations
        
        # Analyze response times
        durations = [m.duration_ms for m in metrics]
        avg_duration = np.mean(durations)
        p95_duration = self.calculate_percentile(durations, 95)
        
        if avg_duration > self.thresholds['response_time_warning_ms']:
            bottlenecks.append(f"High average response time: {avg_duration:.1f}ms")
            recommendations.append("Consider image preprocessing optimization")
            recommendations.append("Enable result caching for frequently processed images")
        
        if p95_duration > self.thresholds['response_time_critical_ms']:
            bottlenecks.append(f"Very high P95 response time: {p95_duration:.1f}ms")
            recommendations.append("Investigate slow operations and optimize GPU utilization")
        
        # Analyze success rate
        success_rate = sum(m.success for m in metrics) / len(metrics)
        if success_rate < self.thresholds['success_rate_warning']:
            bottlenecks.append(f"Low success rate: {success_rate:.1%}")
            recommendations.append("Review error handling and input validation")
        
        # Analyze operation types
        operation_performance = defaultdict(list)
        for metric in metrics:
            operation_performance[metric.operation].append(metric.duration_ms)
        
        for operation, durations in operation_performance.items():
            avg_op_duration = np.mean(durations)
            if avg_op_duration > self.thresholds['response_time_warning_ms']:
                bottlenecks.append(f"Slow operation '{operation}': {avg_op_duration:.1f}ms average")
                
                if operation == 'face_detection':
                    recommendations.append("Optimize face detection model or reduce image resolution")
                elif operation == 'face_recognition':
                    recommendations.append("Implement embedding caching for known faces")
                elif operation == 'image_processing':
                    recommendations.append("Preprocess images to optimal size before detection")
        
        # Analyze system metrics
        if system_metrics:
            avg_memory = np.mean([m.memory_percent for m in system_metrics])
            avg_cpu = np.mean([m.cpu_percent for m in system_metrics])
            
            if avg_memory > self.thresholds['memory_warning_percent']:
                bottlenecks.append(f"High memory usage: {avg_memory:.1f}%")
                recommendations.append("Implement more aggressive cache cleanup")
                recommendations.append("Reduce batch sizes for processing")
            
            if avg_cpu > self.thresholds['cpu_warning_percent']:
                bottlenecks.append(f"High CPU usage: {avg_cpu:.1f}%")
                recommendations.append("Ensure GPU acceleration is properly utilized")
        
        return bottlenecks, recommendations
    
    def get_operation_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary statistics for each operation type"""
        summary = {}
        
        with self._lock:
            for operation, metrics in self.operation_stats.items():
                if not metrics:
                    continue
                
                # Filter to last hour
                cutoff_time = time.time() - 3600
                recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
                
                if not recent_metrics:
                    continue
                
                durations = [m.duration_ms for m in recent_metrics]
                successes = [m.success for m in recent_metrics]
                
                summary[operation] = {
                    'count': len(recent_metrics),
                    'avg_duration_ms': round(np.mean(durations), 2),
                    'p95_duration_ms': round(self.calculate_percentile(durations, 95), 2),
                    'success_rate': round(sum(successes) / len(successes), 3),
                    'min_duration_ms': round(min(durations), 2),
                    'max_duration_ms': round(max(durations), 2)
                }
        
        return summary

class PerformanceMonitor:
    """Main performance monitoring coordinator"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.monitoring_active = False
        self.monitoring_thread = None
        self._stop_event = threading.Event()
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self._stop_event.clear()
        
        def monitor_loop():
            while not self._stop_event.is_set():
                self.metrics_collector.record_system_metrics()
                self._stop_event.wait(interval_seconds)
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self._stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
    
    def record_operation(self, operation: str, duration_ms: float, success: bool = True, **metadata):
        """Record operation performance"""
        self.metrics_collector.record_operation(operation, duration_ms, success, **metadata)
    
    def get_performance_dashboard(self, timeframe_minutes: int = 60) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        report = self.metrics_collector.generate_performance_report(timeframe_minutes)
        operation_summary = self.metrics_collector.get_operation_summary()
        
        return {
            'report': asdict(report),
            'operations': operation_summary,
            'monitoring_status': {
                'active': self.monitoring_active,
                'metrics_collected': len(self.metrics_collector.metrics),
                'system_metrics_collected': len(self.metrics_collector.system_metrics)
            },
            'thresholds': self.metrics_collector.thresholds,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics"""
        # Last 5 minutes for real-time view
        metrics = self.metrics_collector.get_metrics_in_timeframe(5)
        system_metrics = self.metrics_collector.get_system_metrics_in_timeframe(5)
        
        current_system = None
        if system_metrics:
            latest = system_metrics[-1]
            current_system = {
                'cpu_percent': latest.cpu_percent,
                'memory_percent': latest.memory_percent,
                'memory_mb': round(latest.memory_mb, 1),
                'gpu_memory_mb': latest.gpu_memory_mb,
                'gpu_utilization': latest.gpu_utilization,
                'timestamp': latest.timestamp
            }
        
        recent_operations = len(metrics)
        avg_response_time = np.mean([m.duration_ms for m in metrics]) if metrics else 0
        
        return {
            'current_system': current_system,
            'last_5_minutes': {
                'operations': recent_operations,
                'avg_response_time_ms': round(avg_response_time, 2),
                'throughput_ops_per_minute': recent_operations,
                'success_rate': sum(m.success for m in metrics) / len(metrics) if metrics else 1.0
            },
            'status': 'healthy' if avg_response_time < 1000 and recent_operations > 0 else 'idle'
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()