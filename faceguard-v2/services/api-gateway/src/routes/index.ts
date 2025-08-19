/**
 * Routes Setup
 * Intelligent routing and proxy configuration for all backend services
 */

import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { serviceConfigs } from '../config/settings';
import { gatewayLogger } from '../utils/logger';
import { ServiceType } from '../utils/httpClient';
import { setupOptimizedHealthRoutes } from './healthOptimized';
import { setupAnalyticsRoutes } from './analytics';
import { setupWebSocketProxy } from './websocket';
import { createCircuitBreakerProxyFixed as createCircuitBreakerProxy, circuitBreakerStatsMiddleware } from '../middleware/circuitBreakerProxyFixed';
import { serviceCircuitBreakers } from '../middleware/circuitBreaker';

/**
 * Setup all routes and proxies
 */
export async function setupRoutes(app: express.Application): Promise<void> {
  // Add request logging middleware for proxy routes
  const logProxyRequest = (serviceName: string) => {
    return (req: express.Request, res: express.Response, next: express.NextFunction) => {
      gatewayLogger.proxyRequest(
        req.method,
        req.originalUrl,
        `Proxying to ${serviceName}`,
        {
          correlationId: req.headers['x-correlation-id'],
          userAgent: req.get('User-Agent'),
          contentType: req.get('Content-Type'),
          contentLength: req.get('Content-Length')
        }
      );
      next();
    };
  };
  
  // Core Data Service Proxy with Circuit Breaker (Port 8001)
  // Routes: /api/persons/* → http://localhost:8001/persons/*
  const coreDataProxy = createCircuitBreakerProxy(
    ServiceType.CORE_DATA,
    serviceConfigs.coreData.url,
    {
      '^/api/persons': '/persons',
      '^/api/persons/': '/persons/'
    },
    serviceConfigs.coreData.timeout
  );
  
  // Face Recognition Service Proxy with Circuit Breaker (Port 8002)
  // Routes: /api/recognize/* → http://localhost:8002/*
  const recognitionProxy = createCircuitBreakerProxy(
    ServiceType.FACE_RECOGNITION,
    serviceConfigs.faceRecognition.url,
    {
      '^/api/recognize': '',
      '^/api/recognize/': '/'
    },
    serviceConfigs.faceRecognition.timeout
  );
  
  // Camera Stream Service Proxy with Circuit Breaker (Port 8003)
  // Routes: /api/cameras/* → http://localhost:8003/api/cameras/*
  const cameraProxy = createCircuitBreakerProxy(
    ServiceType.CAMERA_STREAM,
    serviceConfigs.cameraStream.url,
    {}, // No path rewrite needed
    serviceConfigs.cameraStream.timeout
  );
  
  // Add circuit breaker stats to all responses
  app.use(circuitBreakerStatsMiddleware);
  
  // Apply route-specific logging middleware and circuit breaker enhanced proxies
  app.use('/api/persons', logProxyRequest('Core Data Service'), coreDataProxy);
  app.use('/api/recognize', logProxyRequest('Face Recognition Service'), recognitionProxy);
  app.use('/api/cameras', logProxyRequest('Camera Stream Service'), cameraProxy);
  
  // Setup optimized health aggregation routes
  await setupOptimizedHealthRoutes(app);
  
  // Setup real-time analytics routes
  await setupAnalyticsRoutes(app);
  
  // Setup WebSocket proxy for real-time events
  await setupWebSocketProxy(app);
  
  // Circuit breaker status endpoint
  app.get('/circuit-breaker/status', (req: express.Request, res: express.Response) => {
    const stats = {
      timestamp: new Date().toISOString(),
      services: {
        'core-data': serviceCircuitBreakers[ServiceType.CORE_DATA].getStats(),
        'face-recognition': serviceCircuitBreakers[ServiceType.FACE_RECOGNITION].getStats(),
        'camera-stream': serviceCircuitBreakers[ServiceType.CAMERA_STREAM].getStats()
      },
      fallback_available: true,
      circuit_breaker_enabled: true
    };
    
    gatewayLogger.analytics('Circuit breaker status requested', {
      correlationId: req.headers['x-correlation-id'],
      requestedBy: req.ip
    });
    
    res.json(stats);
  });
  
  // Gateway info endpoint
  app.get('/', (req: express.Request, res: express.Response) => {
    res.json({
      service: 'FaceGuard V2 API Gateway',
      version: '2.0.0',
      status: 'operational',
      timestamp: new Date().toISOString(),
      endpoints: {
        health: '/health',
        analytics: '/api/dashboard/analytics',
        circuit_breaker: '/circuit-breaker/status',
        services: {
          persons: '/api/persons/*',
          recognition: '/api/recognize/*',
          cameras: '/api/cameras/*'
        }
      },
      backend_services: {
        'core-data': {
          url: serviceConfigs.coreData.url,
          description: '56 persons, real CRUD operations'
        },
        'face-recognition': {
          url: serviceConfigs.faceRecognition.url,
          description: '703x cache speedup, GPU acceleration'
        },
        'camera-stream': {
          url: serviceConfigs.cameraStream.url,
          description: 'Live validated, 1,258+ frames processed'
        }
      }
    });
  });
  
  gatewayLogger.config('Routes configured successfully', {
    proxyRoutes: [
      `/api/persons → ${serviceConfigs.coreData.url}`,
      `/api/recognize → ${serviceConfigs.faceRecognition.url}`,
      `/api/cameras → ${serviceConfigs.cameraStream.url}`
    ],
    healthEndpoint: '/health',
    analyticsEndpoint: '/api/dashboard/analytics',
    websocketSupport: true
  });
}