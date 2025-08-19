/**
 * Structured Logging Utility
 * Production-grade logging with correlation IDs and JSON formatting
 */

import winston, { format, transports } from 'winston';
import { loggingConfig, gatewayConfig } from '../config/settings';

/**
 * Custom log levels for gateway operations
 */
const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

/**
 * Color scheme for console output
 */
const logColors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'cyan',
  debug: 'blue'
};

winston.addColors(logColors);

/**
 * Custom format for structured logging
 */
const logFormat = format.combine(
  format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss.SSS'
  }),
  format.errors({ stack: true }),
  format.metadata({
    fillExcept: ['timestamp', 'level', 'message']
  }),
  format.json()
);

/**
 * Console format for development
 */
const consoleFormat = format.combine(
  format.colorize({ all: true }),
  format.timestamp({
    format: 'HH:mm:ss.SSS'
  }),
  format.printf(({ timestamp, level, message, metadata, stack }) => {
    let log = `[${timestamp}] ${level}: ${message}`;
    
    if (metadata && Object.keys(metadata).length > 0) {
      log += ` ${JSON.stringify(metadata, null, 2)}`;
    }
    
    if (stack) {
      log += `\n${stack}`;
    }
    
    return log;
  })
);

/**
 * Create logger transports based on environment
 */
const createTransports = (): winston.transport[] => {
  const transportList: winston.transport[] = [];

  // Console transport for development
  if (gatewayConfig.nodeEnv === 'development') {
    transportList.push(
      new transports.Console({
        level: loggingConfig.level,
        format: consoleFormat
      })
    );
  }

  // File transport for production
  if (gatewayConfig.nodeEnv === 'production') {
    transportList.push(
      new transports.File({
        filename: loggingConfig.file,
        level: loggingConfig.level,
        format: logFormat,
        maxsize: 10 * 1024 * 1024, // 10MB
        maxFiles: 5,
        tailable: true
      })
    );
    
    // Error-specific file
    transportList.push(
      new transports.File({
        filename: loggingConfig.file.replace('.log', '-error.log'),
        level: 'error',
        format: logFormat,
        maxsize: 10 * 1024 * 1024,
        maxFiles: 5,
        tailable: true
      })
    );
  }

  // Always add console in production for immediate visibility
  if (gatewayConfig.nodeEnv === 'production') {
    transportList.push(
      new transports.Console({
        level: 'warn',
        format: format.combine(
          format.colorize(),
          format.simple()
        )
      })
    );
  }

  return transportList;
};

/**
 * Create winston logger instance
 */
export const logger = winston.createLogger({
  levels: logLevels,
  level: loggingConfig.level,
  format: logFormat,
  transports: createTransports(),
  exitOnError: false,
  silent: process.env.NODE_ENV === 'test'
});

/**
 * Enhanced logging methods with context
 */
export const gatewayLogger = {
  /**
   * Log gateway startup information
   */
  startup(message: string, metadata?: Record<string, any>) {
    logger.info(`🚀 ${message}`, {
      component: 'startup',
      service: 'api-gateway',
      version: gatewayConfig.version,
      ...metadata
    });
  },

  /**
   * Log service communication
   */
  serviceCall(serviceName: string, operation: string, metadata?: Record<string, any>) {
    logger.info(`📡 Service Call: ${serviceName} - ${operation}`, {
      component: 'service-communication',
      service: serviceName,
      operation,
      ...metadata
    });
  },

  /**
   * Log health check results
   */
  healthCheck(serviceName: string, status: string, responseTime: number, metadata?: Record<string, any>) {
    const logLevel = status === 'healthy' ? 'info' : status === 'degraded' ? 'warn' : 'error';
    const emoji = status === 'healthy' ? '✅' : status === 'degraded' ? '⚠️' : '❌';
    
    logger[logLevel](`${emoji} Health Check: ${serviceName} - ${status}`, {
      component: 'health-monitoring',
      service: serviceName,
      status,
      responseTime,
      ...metadata
    });
  },

  /**
   * Log proxy requests
   */
  proxyRequest(method: string, originalPath: string, targetUrl: string, metadata?: Record<string, any>) {
    logger.http(`🔄 Proxy Request: ${method} ${originalPath} → ${targetUrl}`, {
      component: 'proxy',
      method,
      originalPath,
      targetUrl,
      ...metadata
    });
  },

  /**
   * Log security events
   */
  security(event: string, metadata?: Record<string, any>) {
    logger.warn(`🔒 Security Event: ${event}`, {
      component: 'security',
      event,
      ...metadata
    });
  },

  /**
   * Log rate limiting events
   */
  rateLimit(clientIp: string, endpoint: string, metadata?: Record<string, any>) {
    logger.warn(`🚦 Rate Limit: ${clientIp} exceeded limit for ${endpoint}`, {
      component: 'rate-limiting',
      clientIp,
      endpoint,
      ...metadata
    });
  },

  /**
   * Log analytics compilation
   */
  analytics(operation: string, metadata?: Record<string, any>) {
    logger.info(`📊 Analytics: ${operation}`, {
      component: 'analytics',
      operation,
      ...metadata
    });
  },

  /**
   * Log circuit breaker events
   */
  circuitBreaker(service: string, state: string, metadata?: Record<string, any>) {
    const logLevel = state === 'closed' ? 'info' : 'warn';
    const emoji = state === 'closed' ? '✅' : state === 'half-open' ? '⚠️' : '🔴';
    
    logger[logLevel](`${emoji} Circuit Breaker: ${service} - ${state}`, {
      component: 'circuit-breaker',
      service,
      state,
      ...metadata
    });
  },

  /**
   * Log performance metrics
   */
  performance(operation: string, duration: number, metadata?: Record<string, any>) {
    logger.info(`⚡ Performance: ${operation} completed in ${duration}ms`, {
      component: 'performance',
      operation,
      duration,
      ...metadata
    });
  },

  /**
   * Log configuration validation
   */
  config(message: string, metadata?: Record<string, any>) {
    logger.info(`⚙️ Config: ${message}`, {
      component: 'configuration',
      ...metadata
    });
  },

  /**
   * Log error with full context
   */
  error(message: string, error: any, metadata?: Record<string, any>) {
    logger.error(`❌ ${message}`, {
      error: {
        message: error.message,
        stack: error.stack,
        code: error.code,
        statusCode: error.statusCode || error.status
      },
      ...metadata
    });
  },

  /**
   * Log warning with context
   */
  warn(message: string, metadata?: Record<string, any>) {
    logger.warn(`⚠️ ${message}`, metadata);
  },

  /**
   * Log debug information
   */
  debug(message: string, metadata?: Record<string, any>) {
    logger.debug(`🔍 ${message}`, metadata);
  }
};

/**
 * Create correlation ID for request tracing
 */
export function createCorrelationId(): string {
  return `gw_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Add correlation ID to logger context
 */
export function withCorrelation(correlationId: string) {
  return {
    info: (message: string, metadata?: Record<string, any>) => 
      logger.info(message, { correlationId, ...metadata }),
    warn: (message: string, metadata?: Record<string, any>) => 
      logger.warn(message, { correlationId, ...metadata }),
    error: (message: string, metadata?: Record<string, any>) => 
      logger.error(message, { correlationId, ...metadata }),
    debug: (message: string, metadata?: Record<string, any>) => 
      logger.debug(message, { correlationId, ...metadata })
  };
}

/**
 * Log unhandled errors
 */
process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
  gatewayLogger.error('Unhandled Promise Rejection', reason, {
    promise: promise.toString()
  });
});

process.on('uncaughtException', (error: Error) => {
  gatewayLogger.error('Uncaught Exception', error);
  process.exit(1);
});

/**
 * Log process signals
 */
process.on('SIGTERM', () => {
  gatewayLogger.startup('Received SIGTERM, shutting down gracefully');
});

process.on('SIGINT', () => {
  gatewayLogger.startup('Received SIGINT, shutting down gracefully');
});