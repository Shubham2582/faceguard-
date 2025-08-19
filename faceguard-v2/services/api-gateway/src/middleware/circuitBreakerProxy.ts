/**
 * Circuit Breaker Proxy Middleware
 * Integrates circuit breakers with http-proxy-middleware for enhanced reliability
 */

import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { ServiceType } from '../utils/httpClient';
import { gatewayLogger } from '../utils/logger';
import { serviceCircuitBreakers, fallbackResponses, CircuitBreakerOpenError } from './circuitBreaker';

/**
 * Create circuit breaker enhanced proxy middleware
 */
export function createCircuitBreakerProxy(
  serviceType: ServiceType,
  target: string,
  pathRewrite: Record<string, string>,
  timeout: number
) {
  const circuitBreaker = serviceCircuitBreakers[serviceType];
  const fallback = fallbackResponses[serviceType];
  
  // Create the base proxy middleware
  const baseProxy = createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite,
    timeout,
    proxyTimeout: timeout,
    
    onError: (err, req, res) => {
      // Log the error but let circuit breaker handle the response
      gatewayLogger.error(`${serviceType} proxy error`, err, {
        method: req.method,
        url: req.url,
        correlationId: req.headers['x-correlation-id']
      });
      
      // Don't send response here - let circuit breaker handle it
    },
    
    onProxyReq: (proxyReq, req) => {
      proxyReq.setHeader('X-Gateway-Service', 'api-gateway');
      proxyReq.setHeader('X-Target-Service', serviceType);
      
      gatewayLogger.serviceCall(getServiceName(serviceType), `${req.method} ${req.url}`, {
        correlationId: req.headers['x-correlation-id'],
        targetUrl: `${target}${proxyReq.path}`
      });
    },
    
    onProxyRes: (proxyRes, req, res) => {
      proxyRes.headers['X-Proxied-By'] = 'faceguard-api-gateway';
      proxyRes.headers['X-Source-Service'] = serviceType;
      proxyRes.headers['X-Circuit-State'] = circuitBreaker.getStats().state;
      
      gatewayLogger.serviceCall(getServiceName(serviceType), 'Response received', {
        correlationId: req.headers['x-correlation-id'],
        statusCode: proxyRes.statusCode,
        contentType: proxyRes.headers['content-type'],
        circuitState: circuitBreaker.getStats().state
      });
    }
  });
  
  // Return circuit breaker enhanced middleware
  return async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      // Execute proxy through circuit breaker
      await circuitBreaker.execute(async () => {
        return new Promise<void>((resolve, reject) => {
          // Override the proxy error handler to properly reject the promise
          const originalProxy = baseProxy as any;
          const enhancedProxy = (req: express.Request, res: express.Response, next: express.NextFunction) => {
            // Monitor response to determine success/failure
            const originalSend = res.send;
            const originalStatus = res.status;
            let statusCode = 200;
            
            res.status = function(code: number) {
              statusCode = code;
              return originalStatus.call(this, code);
            };
            
            res.send = function(body: any) {
              // Determine if this was a successful response
              if (statusCode >= 200 && statusCode < 400) {
                resolve();
              } else if (statusCode >= 500) {
                reject(new Error(`Service error: ${statusCode}`));
              } else {
                // Client errors (4xx) are not circuit breaker failures
                resolve();
              }
              
              return originalSend.call(this, body);
            };
            
            // Handle proxy errors
            const originalEnd = res.end;
            res.end = function(chunk?: any, encoding?: any) {
              if (!res.headersSent) {
                if (statusCode >= 500) {
                  reject(new Error(`Service error: ${statusCode}`));
                } else {
                  resolve();
                }
              }
              return originalEnd.call(this, chunk, encoding);
            };
            
            originalProxy(req, res, (error: any) => {
              if (error) {
                reject(error);
              } else {
                next();
              }
            });
          };
          
          enhancedProxy(req, res, next);
        });
      });
      
    } catch (error) {
      // Handle circuit breaker open state
      if (error instanceof CircuitBreakerOpenError) {
        gatewayLogger.circuitBreaker(getServiceName(serviceType), 'fallback_response', {
          correlationId: req.headers['x-correlation-id'],
          originalUrl: req.originalUrl,
          circuitState: 'open'
        });
        
        // Determine fallback response based on endpoint
        const fallbackKey = determineFallbackKey(req.path);
        const fallbackResponse = fallback[fallbackKey] || fallback.health;
        
        return res.status(fallbackResponse.statusCode || 503).json({
          ...fallbackResponse,
          timestamp: new Date().toISOString(),
          circuit_breaker: {
            state: 'open',
            service: serviceType,
            stats: circuitBreaker.getStats()
          }
        });
      }
      
      // Handle other errors
      gatewayLogger.error(`Circuit breaker execution failed for ${serviceType}`, error, {
        correlationId: req.headers['x-correlation-id'],
        originalUrl: req.originalUrl
      });
      
      return res.status(503).json({
        error: 'Service Temporarily Unavailable',
        message: `${getServiceName(serviceType)} is experiencing issues`,
        service: serviceType,
        timestamp: new Date().toISOString(),
        statusCode: 503
      });
    }
  };
}

/**
 * Get human-readable service name
 */
function getServiceName(serviceType: ServiceType): string {
  switch (serviceType) {
    case ServiceType.CORE_DATA:
      return 'Core Data Service';
    case ServiceType.FACE_RECOGNITION:
      return 'Face Recognition Service';
    case ServiceType.CAMERA_STREAM:
      return 'Camera Stream Service';
    default:
      return 'Unknown Service';
  }
}

/**
 * Determine fallback response key based on request path
 */
function determineFallbackKey(path: string): string {
  if (path.includes('/persons')) return 'persons';
  if (path.includes('/recognize') || path.includes('/process')) return 'recognition';
  if (path.includes('/cameras')) return 'cameras';
  return 'health';
}

/**
 * Middleware to add circuit breaker statistics to response headers
 */
export function circuitBreakerStatsMiddleware(req: express.Request, res: express.Response, next: express.NextFunction) {
  // Add circuit breaker statistics to response headers
  const stats = {
    'core-data': serviceCircuitBreakers[ServiceType.CORE_DATA].getStats(),
    'face-recognition': serviceCircuitBreakers[ServiceType.FACE_RECOGNITION].getStats(),
    'camera-stream': serviceCircuitBreakers[ServiceType.CAMERA_STREAM].getStats()
  };
  
  res.setHeader('X-Circuit-Breaker-Stats', JSON.stringify(stats));
  next();
}