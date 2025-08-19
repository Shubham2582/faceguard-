/**
 * Service Type Definitions
 * Based on comprehensive analysis of implemented Services A, B, C
 */

// Service Health Response Types (analyzed from all 3 services)
export interface ServiceHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service?: string;
  version?: string;
  timestamp: string;
  components?: Record<string, ComponentHealth>;
  uptime_seconds?: number;
}

export interface ComponentHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  message?: string;
  response_time_ms?: number;
  [key: string]: any;
}

// Core Data Service Types (Port 8001)
export interface CoreDataServiceConfig {
  url: string;
  timeout: number;
  retries: number;
  healthPath: string;
}

export interface PersonResponse {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  department?: string;
  position?: string;
  access_level: 'visitor' | 'employee' | 'contractor' | 'admin' | 'security' | 'vip';
  id: string;
  person_id: string;
  status: 'active' | 'inactive' | 'blocked' | 'pending' | 'archived';
  is_vip: boolean;
  is_watchlist: boolean;
  is_verified: boolean;
  face_count: number;
  embedding_count: number;
  recognition_count: number;
  avg_confidence?: number;
  avg_face_quality?: number;
  best_face_quality?: number;
  first_seen?: string;
  last_seen?: string;
  created_at: string;
  updated_at: string;
}

export interface PersonListResponse {
  total: number;
  page: number;
  limit: number;
  persons: PersonResponse[];
}

// Face Recognition Service Types (Port 8002)
export interface FaceRecognitionServiceConfig {
  url: string;
  timeout: number;
  retries: number;
  healthPath: string;
}

export interface RecognitionResponse {
  processing_result: {
    success: boolean;
    faces: FaceDetection[];
    face_count: number;
    processing_time_ms: number;
    image_size: {
      width: number;
      height: number;
    };
    gpu_used: boolean;
    model_info: {
      name: string;
      detection: string;
      recognition: string;
      stage: string;
    };
  };
  recognized_faces: RecognizedFace[];
  summary: {
    faces_detected: number;
    faces_recognized: number;
    total_processing_time_ms: number;
    detection_time_ms: number;
    gpu_used: boolean;
    cache_hit: boolean;
    optimization_applied: boolean;
  };
}

export interface FaceDetection {
  face_id: number;
  bbox: [number, number, number, number];
  confidence: number;
  embedding: number[];
  age: number;
  gender: number;
}

export interface RecognizedFace extends FaceDetection {
  recognized: boolean;
  person_id?: string;
  recognition_confidence?: number;
  avg_confidence?: number;
  matching_embeddings?: number;
  total_embeddings?: number;
}

export interface CacheStatsResponse {
  cache_performance: {
    hit_ratio: number;
    total_requests: number;
    cache_hits: number;
    cache_misses: number;
    memory_usage_mb: number;
    entries_count: number;
  };
  optimization_impact: {
    speedup_factor: number;
    time_saved_ms: number;
    efficiency_percentage: number;
  };
}

export interface PerformanceDashboardResponse {
  service_metrics: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    average_response_time_ms: number;
    requests_per_second: number;
  };
  recognition_metrics: {
    faces_processed: number;
    persons_recognized: number;
    accuracy_percentage: number;
    processing_speed_fps: number;
  };
  system_metrics: {
    cpu_usage_percent: number;
    memory_usage_mb: number;
    gpu_utilization_percent: number;
    disk_usage_percent: number;
  };
}

// Camera Stream Service Types (Port 8003)
export interface CameraStreamServiceConfig {
  url: string;
  timeout: number;
  retries: number;
  healthPath: string;
}

export interface CameraInfo {
  camera_id: string;
  configuration: {
    name: string;
    source: string;
    camera_type: string;
    resolution_width: number;
    resolution_height: number;
    frame_rate: number;
    enabled: boolean;
    auto_reconnect: boolean;
    location?: string;
  };
  status: 'connected' | 'disconnected' | 'error';
  stream_status: 'stopped' | 'running' | 'paused';
  frames_processed: number;
  frames_recognized: number;
  errors_count: number;
  last_frame_time?: string;
  last_error?: string;
  uptime_seconds: number;
}

export interface CameraStatsResponse {
  service_name: string;
  version: string;
  start_time: string;
  cameras: Array<{
    camera_id: string;
    configuration: {
      name: string;
      source: string;
    };
    status: string;
    frames_processed: number;
    errors_count: number;
  }>;
  processing_stats: {
    total_frames_processed: number;
    total_errors: number;
    error_rate_percent: number;
    active_streams: number;
    frames_per_second: number;
  };
  event_stats: {
    events_published: number;
    events_pending: number;
    events_failed: number;
    subscribers_connected: number;
  };
  performance_metrics: {
    memory_usage_mb: number;
    cpu_usage_percent: number;
    uptime_seconds: number;
    cameras_connected: number;
    cameras_total: number;
  };
}

export interface RecognitionEvent {
  event_id: string;
  timestamp: string;
  camera_id: string;
  frame_id: string;
  persons_detected: Array<{
    person_id: string;
    confidence: number;
  }>;
  processing_time_ms: number;
  confidence_threshold: number;
  frame_metadata: {
    width: number;
    height: number;
    quality_score: number;
  };
  recognition_successful: boolean;
  event_type: string;
  service_version: string;
}

// Gateway Configuration Types
export interface GatewayConfig {
  host: string;
  port: number;
  version: string;
  name: string;
  nodeEnv: string;
}

export interface ServiceConfigs {
  coreData: CoreDataServiceConfig;
  faceRecognition: FaceRecognitionServiceConfig;
  cameraStream: CameraStreamServiceConfig;
}

export interface SecurityConfig {
  cors: {
    origins: string[];
    credentials: boolean;
    methods: string[];
    headers: string[];
  };
  rateLimit: {
    windowMs: number;
    maxRequests: number;
    skipSuccessful: boolean;
    endpoints: {
      recognition: number;
      persons: number;
      cameras: number;
      health: number;
    };
  };
}

export interface RedisConfig {
  host: string;
  port: number;
  password?: string | undefined;
  db: number;
  channels: string[];
}

export interface CircuitBreakerConfig {
  timeout: number;
  errorThreshold: number;
  resetTimeout: number;
}

// API Response Types
export interface ApiError {
  error: string;
  message: string;
  timestamp: string;
  path?: string;
  statusCode: number;
}

export interface HealthCheckResult {
  service: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  responseTime: number;
  timestamp?: string;
  error?: string | undefined;
}

export interface AggregatedHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    coreData: HealthCheckResult;
    faceRecognition: HealthCheckResult;
    cameraStream: HealthCheckResult;
  };
  gateway: {
    uptime: number;
    memory: NodeJS.MemoryUsage;
    version: string;
  };
}