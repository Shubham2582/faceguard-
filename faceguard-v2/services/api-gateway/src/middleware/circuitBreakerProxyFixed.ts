/**
 * Circuit Breaker Proxy Middleware - PRODUCTION FIXED
 * Race condition resolved with response guards and proper synchronization
 */

import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { ServiceType } from '../utils/httpClient';
import { gatewayLogger } from '../utils/logger';
import { serviceCircuitBreakers, fallbackResponses, CircuitBreakerOpenError } from './circuitBreaker';

/**
 * Response guard to prevent duplicate responses
 */
class ResponseGuard {
  private responseSent = false;
  private readonly req: express.Request;
  private readonly res: express.Response;

  constructor(req: express.Request, res: express.Response) {
    this.req = req;
    this.res = res;
  }

  sendOnce(statusCode: number, body: any): boolean {
    if (this.responseSent || this.res.headersSent) {
      gatewayLogger.debug('Response already sent, skipping duplicate', {
        correlationId: this.req.headers['x-correlation-id'],
        url: this.req.url,
        statusCode
      });
      return false;
    }

    this.responseSent = true;
    this.res.status(statusCode).json(body);
    return true;
  }

  isResponseSent(): boolean {
    return this.responseSent || this.res.headersSent;
  }
}

/**
 * Create circuit breaker enhanced proxy middleware - PRODUCTION VERSION
 */
export function createCircuitBreakerProxyFixed(
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
      gatewayLogger.error(`${serviceType} proxy error`, err, {
        method: req.method,
        url: req.url,
        correlationId: req.headers['x-correlation-id']
      });
      
      // Only send response if not already sent
      if (!res.headersSent) {
        res.status(503).json({
          error: 'Service Unavailable',
          message: `${getServiceName(serviceType)} is currently unavailable`,
          service: serviceType,
          timestamp: new Date().toISOString(),
          statusCode: 503
        });
      }
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
  
  // Return production-ready circuit breaker enhanced middleware
  return async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    const responseGuard = new ResponseGuard(req, res);
    const correlationId = req.headers['x-correlation-id'] as string;
    
    try {
      // Execute proxy through circuit breaker with proper error handling
      await circuitBreaker.execute(async () => {
        return new Promise<void>((resolve, reject) => {
          // Set a timeout for the entire operation
          const operationTimeout = setTimeout(() => {
            if (!responseGuard.isResponseSent()) {
              reject(new Error(`Operation timeout after ${timeout}ms`));
            }
          }, timeout);

          // Create a protected proxy call
          const protectedProxy = (req: express.Request, res: express.Response, next: express.NextFunction) => {
            // Monitor for successful completion
            const originalEnd = res.end;
            res.end = function(chunk?: any, encoding?: any) {
              clearTimeout(operationTimeout);
              resolve();
              return originalEnd.call(this, chunk, encoding);
            };

            // Call the actual proxy
            baseProxy(req, res, (error) => {
              clearTimeout(operationTimeout);
              if (error) {
                reject(error);
              } else {
                resolve();
              }
            });
          };

          protectedProxy(req, res, next);
        });
      });
      
    } catch (error) {
      // Handle circuit breaker open state
      if (error instanceof CircuitBreakerOpenError) {
        gatewayLogger.circuitBreaker(getServiceName(serviceType), 'fallback_response', {
          correlationId,
          originalUrl: req.originalUrl,
          circuitState: 'open'
        });
        
        const fallbackKey = determineFallbackKey(req.path);
        const fallbackResponse = fallback[fallbackKey] || fallback.health;
        
        responseGuard.sendOnce(fallbackResponse.statusCode || 503, {
          ...fallbackResponse,
          timestamp: new Date().toISOString(),
          circuit_breaker: {
            state: 'open',
            service: serviceType,
            stats: circuitBreaker.getStats()
          }
        });
        return;
      }
      
      // Handle other errors with response guard
      gatewayLogger.error(`Circuit breaker execution failed for ${serviceType}`, error, {
        correlationId,
        originalUrl: req.originalUrl
      });
      
      responseGuard.sendOnce(503, {
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
 * Production-ready middleware to add circuit breaker statistics
 */
export function circuitBreakerStatsMiddleware(req: express.Request, res: express.Response, next: express.NextFunction) {
  // Only add stats if response hasn't been sent
  if (!res.headersSent) {
    const stats = {
      'core-data': serviceCircuitBreakers[ServiceType.CORE_DATA].getStats(),
      'face-recognition': serviceCircuitBreakers[ServiceType.FACE_RECOGNITION].getStats(),
      'camera-stream': serviceCircuitBreakers[ServiceType.CAMERA_STREAM].getStats()
    };
    
    res.setHeader('X-Circuit-Breaker-Stats', JSON.stringify(stats));
  }
  next();
}