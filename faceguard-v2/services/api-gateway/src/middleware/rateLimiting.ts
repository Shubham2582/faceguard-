/**
 * Advanced Rate Limiting
 * Different rate limits for different endpoint types based on resource usage
 */

import express from 'express';
import rateLimit from 'express-rate-limit';
import { securityConfig } from '../config/settings';
import { gatewayLogger } from '../utils/logger';

/**
 * Setup endpoint-specific rate limiting
 */
export async function setupRateLimiting(app: express.Application): Promise<void> {
  // Recognition endpoint limiter - Heavy processing (GPU operations)
  const recognitionLimiter = rateLimit({
    windowMs: securityConfig.rateLimit.windowMs,
    max: securityConfig.rateLimit.endpoints.recognition,
    skipSuccessfulRequests: false, // Count all recognition attempts
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      error: 'Recognition Rate Limit Exceeded',
      message: 'Too many recognition requests. GPU processing requires rate limiting.',
      retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
      timestamp: new Date().toISOString(),
      statusCode: 429
    },
    handler: (req: express.Request, res: express.Response) => {
      gatewayLogger.rateLimit(
        req.ip || 'unknown',
        'Recognition endpoint',
        {
          endpoint: req.originalUrl,
          userAgent: req.get('User-Agent'),
          correlationId: req.headers['x-correlation-id'],
          limitType: 'recognition'
        }
      );
      
      res.status(429).json({
        error: 'Recognition Rate Limit Exceeded',
        message: 'Too many recognition requests. GPU processing requires rate limiting.',
        retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
        timestamp: new Date().toISOString(),
        statusCode: 429
      });
    }
  });
  
  // Persons endpoint limiter - CRUD operations
  const personsLimiter = rateLimit({
    windowMs: securityConfig.rateLimit.windowMs,
    max: securityConfig.rateLimit.endpoints.persons,
    skipSuccessfulRequests: true,
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      error: 'Persons API Rate Limit Exceeded',
      message: 'Too many person management requests. Please try again later.',
      retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
      timestamp: new Date().toISOString(),
      statusCode: 429
    },
    handler: (req: express.Request, res: express.Response) => {
      gatewayLogger.rateLimit(
        req.ip || 'unknown',
        'Persons endpoint',
        {
          endpoint: req.originalUrl,
          method: req.method,
          correlationId: req.headers['x-correlation-id'],
          limitType: 'persons'
        }
      );
      
      res.status(429).json({
        error: 'Persons API Rate Limit Exceeded',
        message: 'Too many person management requests. Please try again later.',
        retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
        timestamp: new Date().toISOString(),
        statusCode: 429
      });
    }
  });
  
  // Cameras endpoint limiter - Stream operations
  const camerasLimiter = rateLimit({
    windowMs: securityConfig.rateLimit.windowMs,
    max: securityConfig.rateLimit.endpoints.cameras,
    skipSuccessfulRequests: true,
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      error: 'Cameras API Rate Limit Exceeded',
      message: 'Too many camera stream requests. Please try again later.',
      retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
      timestamp: new Date().toISOString(),
      statusCode: 429
    },
    handler: (req: express.Request, res: express.Response) => {
      gatewayLogger.rateLimit(
        req.ip || 'unknown',
        'Cameras endpoint',
        {
          endpoint: req.originalUrl,
          method: req.method,
          correlationId: req.headers['x-correlation-id'],
          limitType: 'cameras'
        }
      );
      
      res.status(429).json({
        error: 'Cameras API Rate Limit Exceeded',
        message: 'Too many camera stream requests. Please try again later.',
        retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
        timestamp: new Date().toISOString(),
        statusCode: 429
      });
    }
  });
  
  // Health endpoint limiter - Monitoring operations (more lenient)
  const healthLimiter = rateLimit({
    windowMs: securityConfig.rateLimit.windowMs,
    max: securityConfig.rateLimit.endpoints.health,
    skipSuccessfulRequests: true,
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      error: 'Health Check Rate Limit Exceeded',
      message: 'Too many health check requests. Please try again later.',
      retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
      timestamp: new Date().toISOString(),
      statusCode: 429
    },
    handler: (req: express.Request, res: express.Response) => {
      gatewayLogger.rateLimit(
        req.ip || 'unknown',
        'Health endpoint',
        {
          endpoint: req.originalUrl,
          correlationId: req.headers['x-correlation-id'],
          limitType: 'health'
        }
      );
      
      res.status(429).json({
        error: 'Health Check Rate Limit Exceeded',
        message: 'Too many health check requests. Please try again later.',
        retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
        timestamp: new Date().toISOString(),
        statusCode: 429
      });
    }
  });
  
  // Apply rate limiters to specific routes
  app.use('/api/recognize', recognitionLimiter);
  app.use('/api/persons', personsLimiter);
  app.use('/api/cameras', camerasLimiter);
  app.use('/health', healthLimiter);
  app.use('/api/health', healthLimiter);
  
  gatewayLogger.config('Rate limiting configured', {
    recognition: securityConfig.rateLimit.endpoints.recognition,
    persons: securityConfig.rateLimit.endpoints.persons,
    cameras: securityConfig.rateLimit.endpoints.cameras,
    health: securityConfig.rateLimit.endpoints.health,
    windowMs: securityConfig.rateLimit.windowMs
  });
}