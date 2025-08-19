/**
 * Gateway Configuration Management
 * Synthesized from all service configurations with environment-based validation
 */

import dotenv from 'dotenv';
import { 
  GatewayConfig, 
  ServiceConfigs, 
  SecurityConfig, 
  RedisConfig, 
  CircuitBreakerConfig 
} from '../types/services';

// Load environment variables
dotenv.config();

/**
 * Validate required environment variable
 */
function requireEnv(key: string, defaultValue?: string): string {
  const value = process.env[key] || defaultValue;
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

/**
 * Parse number from environment with validation
 */
function parseNumber(key: string, defaultValue: number): number {
  const value = process.env[key];
  if (!value) return defaultValue;
  
  const parsed = parseInt(value, 10);
  if (isNaN(parsed)) {
    throw new Error(`Invalid number for environment variable ${key}: ${value}`);
  }
  return parsed;
}

/**
 * Parse boolean from environment
 */
function parseBoolean(key: string, defaultValue: boolean): boolean {
  const value = process.env[key];
  if (!value) return defaultValue;
  return value.toLowerCase() === 'true';
}

/**
 * Parse comma-separated array from environment
 */
function parseArray(key: string, defaultValue: string[] = []): string[] {
  const value = process.env[key];
  if (!value) return defaultValue;
  return value.split(',').map(item => item.trim()).filter(Boolean);
}

/**
 * Gateway service configuration
 */
export const gatewayConfig: GatewayConfig = {
  host: requireEnv('GATEWAY_HOST', '0.0.0.0'),
  port: parseNumber('GATEWAY_PORT', 3000),
  version: requireEnv('GATEWAY_VERSION', '2.0.0'),
  name: requireEnv('GATEWAY_NAME', 'api-gateway'),
  nodeEnv: requireEnv('NODE_ENV', 'development')
};

/**
 * Backend service configurations
 * Based on comprehensive analysis of Services A, B, C
 */
export const serviceConfigs: ServiceConfigs = {
  // Core Data Service (Port 8001) - 56 persons, real CRUD operations
  coreData: {
    url: requireEnv('CORE_DATA_SERVICE_URL', 'http://localhost:8001'),
    timeout: parseNumber('CORE_DATA_TIMEOUT', 5000),
    retries: parseNumber('CORE_DATA_RETRIES', 3),
    healthPath: requireEnv('CORE_DATA_HEALTH_PATH', '/health/')
  },
  
  // Face Recognition Service (Port 8002) - 703x cache speedup, GPU acceleration
  faceRecognition: {
    url: requireEnv('FACE_RECOGNITION_SERVICE_URL', 'http://localhost:8002'),
    timeout: parseNumber('FACE_RECOGNITION_TIMEOUT', 30000), // Higher for GPU processing
    retries: parseNumber('FACE_RECOGNITION_RETRIES', 2),
    healthPath: requireEnv('FACE_RECOGNITION_HEALTH_PATH', '/health/')
  },
  
  // Camera Stream Service (Port 8003) - Live validated, 1,258+ frames processed
  cameraStream: {
    url: requireEnv('CAMERA_STREAM_SERVICE_URL', 'http://localhost:8003'),
    timeout: parseNumber('CAMERA_STREAM_TIMEOUT', 10000),
    retries: parseNumber('CAMERA_STREAM_RETRIES', 3),
    healthPath: requireEnv('CAMERA_STREAM_HEALTH_PATH', '/api/health/')
  }
};

/**
 * Security configuration
 */
export const securityConfig: SecurityConfig = {
  cors: {
    origins: parseArray('CORS_ORIGINS', [
      'http://localhost:3000',
      'http://localhost:8000',
      'http://localhost:8001',
      'http://localhost:8002',
      'http://localhost:8003'
    ]),
    credentials: parseBoolean('CORS_CREDENTIALS', true),
    methods: parseArray('CORS_METHODS', ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']),
    headers: parseArray('CORS_HEADERS', [
      'Content-Type',
      'Authorization',
      'X-Requested-With',
      'Accept',
      'Origin',
      'Access-Control-Request-Method',
      'Access-Control-Request-Headers'
    ])
  },
  rateLimit: {
    windowMs: parseNumber('RATE_LIMIT_WINDOW_MS', 60000),
    maxRequests: parseNumber('RATE_LIMIT_MAX_REQUESTS', 1000),
    skipSuccessful: parseBoolean('RATE_LIMIT_SKIP_SUCCESSFUL', true),
    endpoints: {
      recognition: parseNumber('RATE_LIMIT_RECOGNITION_MAX', 10), // Heavy processing
      persons: parseNumber('RATE_LIMIT_PERSONS_MAX', 100),       // CRUD operations
      cameras: parseNumber('RATE_LIMIT_CAMERAS_MAX', 50),        // Stream operations  
      health: parseNumber('RATE_LIMIT_HEALTH_MAX', 200)          // Monitoring
    }
  }
};

/**
 * Redis configuration for event streaming
 */
export const redisConfig: RedisConfig = {
  host: requireEnv('REDIS_HOST', 'localhost'),
  port: parseNumber('REDIS_PORT', 6379),
  password: process.env['REDIS_PASSWORD'],
  db: parseNumber('REDIS_DB', 0),
  channels: parseArray('REDIS_CHANNELS', ['face_recognition_events'])
};

/**
 * Circuit breaker configuration
 */
export const circuitBreakerConfig: CircuitBreakerConfig = {
  timeout: parseNumber('CIRCUIT_BREAKER_TIMEOUT', 5000),
  errorThreshold: parseNumber('CIRCUIT_BREAKER_ERROR_THRESHOLD', 50),
  resetTimeout: parseNumber('CIRCUIT_BREAKER_RESET_TIMEOUT', 30000)
};

/**
 * WebSocket configuration
 */
export const websocketConfig = {
  port: parseNumber('WEBSOCKET_PORT', 3001),
  path: requireEnv('WEBSOCKET_PATH', '/ws')
};

/**
 * Logging configuration
 */
export const loggingConfig = {
  level: requireEnv('LOG_LEVEL', 'info'),
  format: requireEnv('LOG_FORMAT', 'json'),
  file: requireEnv('LOG_FILE', 'logs/gateway.log')
};

/**
 * Health check configuration
 */
export const healthConfig = {
  interval: parseNumber('HEALTH_CHECK_INTERVAL', 30000),
  timeout: parseNumber('HEALTH_CHECK_TIMEOUT', 5000),
  cacheTtl: parseNumber('HEALTH_CACHE_TTL', 10000)
};

/**
 * Performance configuration
 */
export const performanceConfig = {
  compressionEnabled: parseBoolean('COMPRESSION_ENABLED', true),
  cacheTtl: parseNumber('CACHE_TTL', 300000),
  requestTimeout: parseNumber('REQUEST_TIMEOUT', 30000),
  keepAliveTimeout: parseNumber('KEEP_ALIVE_TIMEOUT', 5000)
};

/**
 * Security headers configuration
 */
export const securityHeaders = {
  hstsMaxAge: parseNumber('SECURITY_HSTS_MAX_AGE', 31536000),
  cspEnabled: parseBoolean('SECURITY_CSP_ENABLED', true),
  frameOptions: requireEnv('SECURITY_FRAME_OPTIONS', 'DENY'),
  contentTypeOptions: requireEnv('SECURITY_CONTENT_TYPE_OPTIONS', 'nosniff')
};

/**
 * Validate all configurations on startup
 */
export function validateConfig(): void {
  console.log('🔧 Validating Gateway Configuration...');
  
  // Validate gateway config
  if (gatewayConfig.port < 1024 || gatewayConfig.port > 65535) {
    throw new Error(`Invalid gateway port: ${gatewayConfig.port}`);
  }
  
  // Validate service URLs
  const urlPattern = /^https?:\/\/.+/;
  if (!urlPattern.test(serviceConfigs.coreData.url)) {
    throw new Error(`Invalid Core Data Service URL: ${serviceConfigs.coreData.url}`);
  }
  if (!urlPattern.test(serviceConfigs.faceRecognition.url)) {
    throw new Error(`Invalid Face Recognition Service URL: ${serviceConfigs.faceRecognition.url}`);
  }
  if (!urlPattern.test(serviceConfigs.cameraStream.url)) {
    throw new Error(`Invalid Camera Stream Service URL: ${serviceConfigs.cameraStream.url}`);
  }
  
  // Validate timeouts
  if (serviceConfigs.faceRecognition.timeout < 10000) {
    console.warn('⚠️  Face Recognition timeout is low for GPU processing');
  }
  
  // Validate Redis config
  if (redisConfig.port < 1 || redisConfig.port > 65535) {
    throw new Error(`Invalid Redis port: ${redisConfig.port}`);
  }
  
  console.log('✅ Gateway Configuration validated successfully');
  console.log(`🚀 Gateway will start on ${gatewayConfig.host}:${gatewayConfig.port}`);
  console.log(`📊 Services: Core Data (${serviceConfigs.coreData.url}), Recognition (${serviceConfigs.faceRecognition.url}), Camera Stream (${serviceConfigs.cameraStream.url})`);
}