/**
 * Middleware Setup
 * Configures all middleware for security, logging, rate limiting, and CORS
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import { securityConfig, securityHeaders } from '../config/settings';
import { gatewayLogger, createCorrelationId } from '../utils/logger';
import { setupRateLimiting } from './rateLimiting';

/**
 * Setup all middleware for the API Gateway
 */
export async function setupMiddleware(app: express.Application): Promise<void> {
  // Trust proxy for accurate IP addresses
  app.set('trust proxy', 1);
  
  // Correlation ID middleware
  app.use((req: express.Request, res: express.Response, next: express.NextFunction) => {
    const correlationId = req.headers['x-correlation-id'] as string || createCorrelationId();
    req.headers['x-correlation-id'] = correlationId;
    res.setHeader('X-Correlation-ID', correlationId);
    next();
  });
  
  // Security headers
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "blob:"],
        connectSrc: ["'self'", "ws:", "wss:"]
      }
    },
    hsts: {
      maxAge: securityHeaders.hstsMaxAge,
      includeSubDomains: true,
      preload: true
    },
    frameguard: { action: securityHeaders.frameOptions.toLowerCase() as any },
    noSniff: securityHeaders.contentTypeOptions === 'nosniff'
  }));
  
  // CORS configuration
  app.use(cors({
    origin: securityConfig.cors.origins,
    credentials: securityConfig.cors.credentials,
    methods: securityConfig.cors.methods,
    allowedHeaders: securityConfig.cors.headers,
    optionsSuccessStatus: 200
  }));
  
  // Request parsing middleware
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true, limit: '10mb' }));
  
  // Structured logging middleware
  const logFormat = ':method :url :status :response-time ms - :res[content-length] bytes';
  app.use(morgan(logFormat, {
    stream: {
      write: (message: string) => {
        const parts = message.trim().split(' ');
        if (parts.length >= 8) {
          gatewayLogger.proxyRequest(
            parts[0] || 'UNKNOWN', // method
            parts[1] || '/', // url
            `Gateway processed in ${parts[3] || '0'}ms`, // processing info
            {
              statusCode: parseInt(parts[2] || '0'),
              responseTime: parseFloat(parts[3] || '0'),
              contentLength: parts[7] !== '-' ? parseInt(parts[7] || '0') : 0
            }
          );
        }
      }
    }
  }));
  
  // Global rate limiting
  const globalLimiter = rateLimit({
    windowMs: securityConfig.rateLimit.windowMs,
    max: securityConfig.rateLimit.maxRequests,
    skipSuccessfulRequests: securityConfig.rateLimit.skipSuccessful,
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      error: 'Too Many Requests',
      message: 'Too many requests from this IP, please try again later',
      retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
      timestamp: new Date().toISOString(),
      statusCode: 429
    },
    handler: (req: express.Request, res: express.Response) => {
      gatewayLogger.rateLimit(
        req.ip || 'unknown',
        req.originalUrl,
        {
          userAgent: req.get('User-Agent'),
          correlationId: req.headers['x-correlation-id']
        }
      );
      
      res.status(429).json({
        error: 'Too Many Requests',
        message: 'Too many requests from this IP, please try again later',
        retryAfter: Math.ceil(securityConfig.rateLimit.windowMs / 1000),
        timestamp: new Date().toISOString(),
        statusCode: 429
      });
    }
  });
  
  app.use(globalLimiter);
  
  // Setup endpoint-specific rate limiting
  await setupRateLimiting(app);
  
  gatewayLogger.config('Middleware setup completed', {
    corsOrigins: securityConfig.cors.origins.length,
    rateLimitWindow: securityConfig.rateLimit.windowMs,
    globalRateLimit: securityConfig.rateLimit.maxRequests,
    securityHeaders: Object.keys(securityHeaders).length
  });
}