/**
 * Optimized Health Aggregation Routes - PRODUCTION GRADE
 * Resolves 18+ second bottleneck with concurrent processing and circuit breakers
 */

import express from 'express';
import { httpClient, ServiceType } from '../utils/httpClient';
import { gatewayLogger } from '../utils/logger';
import { serviceConfigs, healthConfig } from '../config/settings';
import { AggregatedHealthResponse, HealthCheckResult } from '../types/services';
import { serviceCircuitBreakers } from '../middleware/circuitBreaker';

// Enhanced health cache with TTL and concurrent protection
interface CachedHealth {
  data: AggregatedHealthResponse;
  timestamp: number;
  isStale: boolean;
}

const healthCache = new Map<string, CachedHealth>();
const ongoingHealthChecks = new Map<string, Promise<HealthCheckResult>>();

/**
 * Setup optimized health routes - PRODUCTION VERSION
 */
export async function setupOptimizedHealthRoutes(app: express.Application): Promise<void> {
  
  /**
   * High-performance aggregated health endpoint
   * Concurrent processing with circuit breaker integration
   */
  app.get('/health', async (req: express.Request, res: express.Response) => {
    const correlationId = req.headers['x-correlation-id'] as string;
    const startTime = Date.now();
    
    try {
      // Check cache first - serve stale data under high load
      const cached = healthCache.get('aggregated');
      const cacheAge = cached ? Date.now() - cached.timestamp : Infinity;
      const isWithinTTL = cacheAge < healthConfig.cacheTtl;
      const isStale = cacheAge > (healthConfig.cacheTtl * 2); // Double TTL for stale check
      
      // Serve fresh cache immediately
      if (cached && isWithinTTL) {
        gatewayLogger.debug('Serving fresh cached health status', {
          correlationId,
          cacheAge,
          responseTime: Date.now() - startTime
        });
        
        const statusCode = cached.data.status === 'healthy' ? 200 : 503;
        return res.status(statusCode).json(cached.data);
      }
      
      // Serve stale cache for high-availability, refresh in background
      if (cached && !isStale) {
        gatewayLogger.debug('Serving stale cache, refreshing in background', {
          correlationId,
          cacheAge,
          staleness: 'acceptable'
        });
        
        // Background refresh (don't await)
        refreshHealthCache(correlationId).catch(error => 
          gatewayLogger.error('Background health refresh failed', error, { correlationId })
        );
        
        const statusCode = cached.data.status === 'healthy' ? 200 : 503;
        return res.status(statusCode).json({
          ...cached.data,
          cache_info: { served_from_cache: true, age_ms: cacheAge, freshness: 'stale' }
        });
      }
      
      // No cache or too stale - perform fresh check with timeout protection
      const healthData = await performConcurrentHealthCheck(correlationId);
      
      // Cache the result
      healthCache.set('aggregated', {
        data: healthData,
        timestamp: Date.now(),
        isStale: false
      });
      
      const statusCode = healthData.status === 'healthy' ? 200 : 503;
      const responseTime = Date.now() - startTime;
      
      gatewayLogger.analytics('Health check completed', {
        correlationId,
        responseTime,
        status: healthData.status,
        serviceStates: {
          coreData: healthData.services.coreData?.status,
          faceRecognition: healthData.services.faceRecognition?.status,
          cameraStream: healthData.services.cameraStream?.status
        }
      });
      
      res.status(statusCode).json({
        ...healthData,
        response_time_ms: responseTime,
        cache_info: { served_from_cache: false, freshness: 'live' }
      });
      
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      gatewayLogger.error('Health check failed', error, {
        correlationId,
        responseTime,
        fallbackStrategy: 'degraded_response'
      });
      
      // Return degraded health response
      res.status(503).json({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: 'Health check system failure',
        services: {},
        gateway: getGatewayHealth(),
        response_time_ms: responseTime
      });
    }
  });

  /**
   * Individual service health endpoints for debugging
   */
  app.get('/health/core-data', createIndividualHealthEndpoint(ServiceType.CORE_DATA));
  app.get('/health/face-recognition', createIndividualHealthEndpoint(ServiceType.FACE_RECOGNITION));
  app.get('/health/camera-stream', createIndividualHealthEndpoint(ServiceType.CAMERA_STREAM));

  /**
   * Circuit breaker status endpoint for monitoring
   */
  app.get('/health/circuit-breakers', (req: express.Request, res: express.Response) => {
    const stats = {
      timestamp: new Date().toISOString(),
      circuit_breakers: {
        'core-data': serviceCircuitBreakers[ServiceType.CORE_DATA].getStats(),
        'face-recognition': serviceCircuitBreakers[ServiceType.FACE_RECOGNITION].getStats(),
        'camera-stream': serviceCircuitBreakers[ServiceType.CAMERA_STREAM].getStats()
      }
    };
    
    res.json(stats);
  });

  gatewayLogger.config('Optimized health routes configured', {
    endpoints: ['/health', '/health/core-data', '/health/face-recognition', '/health/camera-stream', '/health/circuit-breakers'],
    cacheTtl: healthConfig.cacheTtl,
    concurrentChecks: true,
    circuitBreakerIntegration: true
  });
}

/**
 * Perform concurrent health checks with circuit breaker protection
 */
async function performConcurrentHealthCheck(correlationId: string): Promise<AggregatedHealthResponse> {
  const healthPromises = [
    checkServiceHealthWithCircuitBreaker(ServiceType.CORE_DATA, correlationId),
    checkServiceHealthWithCircuitBreaker(ServiceType.FACE_RECOGNITION, correlationId), 
    checkServiceHealthWithCircuitBreaker(ServiceType.CAMERA_STREAM, correlationId)
  ];
  
  // Use Promise.allSettled for fault tolerance
  const results = await Promise.allSettled(healthPromises);
  
  const coreDataHealth = results[0].status === 'fulfilled' ? results[0].value : createFailedHealth('Core Data Service', results[0].reason);
  const faceRecognitionHealth = results[1].status === 'fulfilled' ? results[1].value : createFailedHealth('Face Recognition Service', results[1].reason);
  const cameraStreamHealth = results[2].status === 'fulfilled' ? results[2].value : createFailedHealth('Camera Stream Service', results[2].reason);
  
  // Determine overall status
  const services = [coreDataHealth, faceRecognitionHealth, cameraStreamHealth];
  const healthyCount = services.filter(s => s.status === 'healthy').length;
  const totalCount = services.length;
  
  let overallStatus: 'healthy' | 'degraded' | 'unhealthy';
  if (healthyCount === totalCount) {
    overallStatus = 'healthy';
  } else if (healthyCount > 0) {
    overallStatus = 'degraded';
  } else {
    overallStatus = 'unhealthy';
  }
  
  return {
    status: overallStatus,
    timestamp: new Date().toISOString(),
    services: {
      coreData: coreDataHealth,
      faceRecognition: faceRecognitionHealth,
      cameraStream: cameraStreamHealth
    },
    gateway: getGatewayHealth()
  };
}

/**
 * Check service health with circuit breaker integration
 */
async function checkServiceHealthWithCircuitBreaker(serviceType: ServiceType, correlationId: string): Promise<HealthCheckResult> {
  const serviceName = getServiceName(serviceType);
  const cacheKey = `health_${serviceType}`;
  
  // Check if there's an ongoing health check for this service
  const ongoing = ongoingHealthChecks.get(cacheKey);
  if (ongoing) {
    gatewayLogger.debug(`Joining ongoing health check for ${serviceName}`, { correlationId });
    return ongoing;
  }
  
  const circuitBreaker = serviceCircuitBreakers[serviceType];
  const healthCheckPromise = circuitBreaker.execute(async () => {
    return performSingleHealthCheck(serviceType, correlationId);
  }).catch(error => {
    gatewayLogger.warn(`Circuit breaker blocked health check for ${serviceName}`, {
      correlationId,
      circuitState: circuitBreaker.getStats().state,
      error: error.message
    });
    
    return createFailedHealth(serviceName, error);
  });
  
  // Cache the ongoing promise to prevent duplicate requests
  ongoingHealthChecks.set(cacheKey, healthCheckPromise);
  
  // Clean up after completion
  healthCheckPromise.finally(() => {
    ongoingHealthChecks.delete(cacheKey);
  });
  
  return healthCheckPromise;
}

/**
 * Perform single service health check with timeout
 */
async function performSingleHealthCheck(serviceType: ServiceType, correlationId: string): Promise<HealthCheckResult> {
  const startTime = Date.now();
  const serviceName = getServiceName(serviceType);
  
  try {
    let healthUrl: string;
    let timeout: number;
    
    switch (serviceType) {
      case ServiceType.CORE_DATA:
        healthUrl = '/health/';
        timeout = serviceConfigs.coreData.timeout;
        break;
      case ServiceType.FACE_RECOGNITION:
        healthUrl = '/health/';
        timeout = serviceConfigs.faceRecognition.timeout;
        break;
      case ServiceType.CAMERA_STREAM:
        healthUrl = '/api/health/';
        timeout = serviceConfigs.cameraStream.timeout;
        break;
      default:
        throw new Error(`Unknown service type: ${serviceType}`);
    }
    
    const response = await httpClient.get(serviceType, healthUrl, { timeout });
    const responseTime = Date.now() - startTime;
    
    gatewayLogger.debug(`Health check successful for ${serviceName}`, {
      correlationId,
      responseTime,
      statusCode: response.status
    });
    
    return {
      service: serviceName,
      status: response.status === 200 ? 'healthy' : 'degraded',
      responseTime,
      timestamp: new Date().toISOString()
    };
    
  } catch (error: any) {
    const responseTime = Date.now() - startTime;
    
    gatewayLogger.warn(`Health check failed for ${serviceName}`, {
      correlationId,
      responseTime,
      error: error.message,
      statusCode: error.response?.status || 0
    });
    
    return createFailedHealth(serviceName, error, responseTime);
  }
}

/**
 * Background cache refresh without blocking requests
 */
async function refreshHealthCache(correlationId: string): Promise<void> {
  try {
    const healthData = await performConcurrentHealthCheck(correlationId);
    healthCache.set('aggregated', {
      data: healthData,
      timestamp: Date.now(),
      isStale: false
    });
    
    gatewayLogger.debug('Background health cache refresh completed', { correlationId });
  } catch (error) {
    gatewayLogger.error('Background health cache refresh failed', error, { correlationId });
  }
}

/**
 * Create individual service health endpoint
 */
function createIndividualHealthEndpoint(serviceType: ServiceType) {
  return async (req: express.Request, res: express.Response) => {
    const correlationId = req.headers['x-correlation-id'] as string;
    
    try {
      const result = await checkServiceHealthWithCircuitBreaker(serviceType, correlationId);
      const statusCode = result.status === 'healthy' ? 200 : 503;
      res.status(statusCode).json(result);
    } catch (error) {
      gatewayLogger.error(`Individual health check failed for ${getServiceName(serviceType)}`, error, { correlationId });
      res.status(503).json(createFailedHealth(getServiceName(serviceType), error));
    }
  };
}

/**
 * Helper functions
 */
function getServiceName(serviceType: ServiceType): string {
  switch (serviceType) {
    case ServiceType.CORE_DATA: return 'Core Data Service';
    case ServiceType.FACE_RECOGNITION: return 'Face Recognition Service';
    case ServiceType.CAMERA_STREAM: return 'Camera Stream Service';
    default: return 'Unknown Service';
  }
}

function createFailedHealth(serviceName: string, error: any, responseTime?: number): HealthCheckResult {
  return {
    service: serviceName,
    status: 'unhealthy',
    responseTime: responseTime || 0,
    timestamp: new Date().toISOString(),
    error: error?.message || 'Unknown error'
  };
}

function getGatewayHealth() {
  return {
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    version: '2.0.0',
    nodeVersion: process.version
  };
}