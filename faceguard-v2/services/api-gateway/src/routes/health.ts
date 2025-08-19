/**
 * Health Aggregation Routes
 * Compiles health status from all 3 backend services
 */

import express from 'express';
import { httpClient, ServiceType } from '../utils/httpClient';
import { gatewayLogger } from '../utils/logger';
import { serviceConfigs, healthConfig } from '../config/settings';
import { AggregatedHealthResponse, HealthCheckResult } from '../types/services';

// Health cache to avoid overwhelming backend services
const healthCache = new Map<string, { data: AggregatedHealthResponse; timestamp: number }>();

/**
 * Setup health routes
 */
export async function setupHealthRoutes(app: express.Application): Promise<void> {
  
  /**
   * Aggregated health endpoint
   * Compiles health from Core Data, Face Recognition, and Camera Stream services
   */
  app.get('/health', async (req: express.Request, res: express.Response) => {
    const correlationId = req.headers['x-correlation-id'] as string;
    
    try {
      // Check cache first
      const cached = healthCache.get('aggregated');
      if (cached && (Date.now() - cached.timestamp) < healthConfig.cacheTtl) {
        gatewayLogger.debug('Returning cached health status', {
          correlationId,
          cacheAge: Date.now() - cached.timestamp
        });
        
        const statusCode = cached.data.status === 'healthy' ? 200 : 503;
        return res.status(statusCode).json(cached.data);
      }
      
      // Perform health checks on all services
      const healthPromises = [
        checkServiceHealth(ServiceType.CORE_DATA, 'Core Data Service', correlationId),
        checkServiceHealth(ServiceType.FACE_RECOGNITION, 'Face Recognition Service', correlationId),
        checkServiceHealth(ServiceType.CAMERA_STREAM, 'Camera Stream Service', correlationId)
      ];
      
      const healthResults = await Promise.allSettled(healthPromises);
      
      // Process results
      const coreDataHealth = healthResults[0].status === 'fulfilled' ? healthResults[0].value : createFailedHealth('Core Data Service', healthResults[0].reason);
      const recognitionHealth = healthResults[1].status === 'fulfilled' ? healthResults[1].value : createFailedHealth('Face Recognition Service', healthResults[1].reason);
      const cameraHealth = healthResults[2].status === 'fulfilled' ? healthResults[2].value : createFailedHealth('Camera Stream Service', healthResults[2].reason);
      
      // Calculate overall status
      const allHealthy = [coreDataHealth, recognitionHealth, cameraHealth].every(h => h.status === 'healthy');
      const anyHealthy = [coreDataHealth, recognitionHealth, cameraHealth].some(h => h.status === 'healthy');
      
      let overallStatus: 'healthy' | 'degraded' | 'unhealthy';
      if (allHealthy) {
        overallStatus = 'healthy';
      } else if (anyHealthy) {
        overallStatus = 'degraded';
      } else {
        overallStatus = 'unhealthy';
      }
      
      // Compile aggregated response
      const aggregatedHealth: AggregatedHealthResponse = {
        status: overallStatus,
        timestamp: new Date().toISOString(),
        services: {
          coreData: coreDataHealth,
          faceRecognition: recognitionHealth,
          cameraStream: cameraHealth
        },
        gateway: {
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          version: '2.0.0'
        }
      };
      
      // Cache the result
      healthCache.set('aggregated', {
        data: aggregatedHealth,
        timestamp: Date.now()
      });
      
      // Log health status
      gatewayLogger.healthCheck('Gateway Aggregated', overallStatus, Date.now(), {
        correlationId,
        serviceStates: {
          coreData: coreDataHealth.status,
          recognition: recognitionHealth.status,
          camera: cameraHealth.status
        }
      });
      
      const statusCode = overallStatus === 'healthy' ? 200 : 503;
      res.status(statusCode).json(aggregatedHealth);
      
    } catch (error) {
      gatewayLogger.error('Health aggregation failed', error, { correlationId });
      
      res.status(500).json({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: 'Health check aggregation failed',
        message: 'Unable to determine system health',
        statusCode: 500
      });
    }
  });
  
  /**
   * Individual service health endpoints for debugging
   */
  app.get('/health/core-data', async (req: express.Request, res: express.Response) => {
    const correlationId = req.headers['x-correlation-id'] as string;
    
    try {
      const health = await checkServiceHealth(ServiceType.CORE_DATA, 'Core Data Service', correlationId);
      const statusCode = health.status === 'healthy' ? 200 : 503;
      res.status(statusCode).json(health);
    } catch (error) {
      res.status(503).json(createFailedHealth('Core Data Service', error));
    }
  });
  
  app.get('/health/face-recognition', async (req: express.Request, res: express.Response) => {
    const correlationId = req.headers['x-correlation-id'] as string;
    
    try {
      const health = await checkServiceHealth(ServiceType.FACE_RECOGNITION, 'Face Recognition Service', correlationId);
      const statusCode = health.status === 'healthy' ? 200 : 503;
      res.status(statusCode).json(health);
    } catch (error) {
      res.status(503).json(createFailedHealth('Face Recognition Service', error));
    }
  });
  
  app.get('/health/camera-stream', async (req: express.Request, res: express.Response) => {
    const correlationId = req.headers['x-correlation-id'] as string;
    
    try {
      const health = await checkServiceHealth(ServiceType.CAMERA_STREAM, 'Camera Stream Service', correlationId);
      const statusCode = health.status === 'healthy' ? 200 : 503;
      res.status(statusCode).json(health);
    } catch (error) {
      res.status(503).json(createFailedHealth('Camera Stream Service', error));
    }
  });
  
  gatewayLogger.config('Health routes configured', {
    aggregatedEndpoint: '/health',
    individualEndpoints: ['/health/core-data', '/health/face-recognition', '/health/camera-stream'],
    cacheTtl: healthConfig.cacheTtl
  });
}

/**
 * Check health of a specific service
 */
async function checkServiceHealth(
  serviceType: ServiceType,
  serviceName: string,
  correlationId: string
): Promise<HealthCheckResult> {
  const startTime = Date.now();
  
  try {
    const response = await httpClient.healthCheck(serviceType);
    const responseTime = Date.now() - startTime;
    
    // Parse service health response
    const healthData = response.data;
    let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    
    if (healthData.status) {
      status = healthData.status;
    } else if (response.status >= 200 && response.status < 300) {
      status = 'healthy';
    } else {
      status = 'unhealthy';
    }
    
    gatewayLogger.healthCheck(serviceName, status, responseTime, {
      correlationId,
      statusCode: response.status,
      components: healthData.components ? Object.keys(healthData.components).length : 0
    });
    
    return {
      service: serviceName,
      status,
      responseTime,
      error: undefined
    };
    
  } catch (error: any) {
    const responseTime = Date.now() - startTime;
    
    gatewayLogger.healthCheck(serviceName, 'unhealthy', responseTime, {
      correlationId,
      error: error.message,
      statusCode: error.response?.status || 0
    });
    
    return {
      service: serviceName,
      status: 'unhealthy',
      responseTime,
      error: error.message || 'Health check failed'
    };
  }
}

/**
 * Create a failed health result
 */
function createFailedHealth(serviceName: string, error: any): HealthCheckResult {
  return {
    service: serviceName,
    status: 'unhealthy',
    responseTime: 0,
    error: error?.message || 'Service unavailable'
  };
}