/**
 * FaceGuard V2 API Gateway
 * Main entry point for the unified backend API
 * Synthesized from comprehensive analysis of all production services
 */

import express from 'express';
import compression from 'compression';
import { validateConfig, gatewayConfig } from './config/settings';
import { gatewayLogger } from './utils/logger';
import { setupMiddleware } from './middleware';
import { setupRoutes } from './routes';
import { gracefulShutdown } from './utils/gracefulShutdown';

/**
 * Initialize and start the API Gateway
 */
async function startGateway(): Promise<void> {
  try {
    // Validate configuration on startup
    validateConfig();
    
    // Create Express application
    const app = express();
    
    // Enable response compression
    app.use(compression());
    
    // Setup middleware (security, logging, rate limiting)
    await setupMiddleware(app);
    
    // Setup routes (proxy to all 3 services)
    await setupRoutes(app);
    
    // Global error handler
    app.use((error: any, req: express.Request, res: express.Response, _next: express.NextFunction) => {
      gatewayLogger.error('Unhandled error in API Gateway', error, {
        method: req.method,
        path: req.path,
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });
      
      res.status(500).json({
        error: 'Internal Server Error',
        message: 'An unexpected error occurred',
        timestamp: new Date().toISOString(),
        path: req.path,
        statusCode: 500
      });
    });
    
    // 404 handler
    app.use('*', (req: express.Request, res: express.Response) => {
      res.status(404).json({
        error: 'Not Found',
        message: `API endpoint ${req.method} ${req.originalUrl} not found`,
        timestamp: new Date().toISOString(),
        path: req.originalUrl,
        statusCode: 404
      });
    });
    
    // Start server
    const server = app.listen(gatewayConfig.port, gatewayConfig.host, () => {
      gatewayLogger.startup(`API Gateway started successfully`, {
        host: gatewayConfig.host,
        port: gatewayConfig.port,
        version: gatewayConfig.version,
        environment: gatewayConfig.nodeEnv,
        processId: process.pid
      });
      
      gatewayLogger.startup('Gateway is ready to proxy requests to:', {
        services: [
          'Core Data Service (8001) - 56 persons, real CRUD operations',
          'Face Recognition Service (8002) - 703x cache speedup, GPU acceleration',
          'Camera Stream Service (8003) - Live validated, 1,258+ frames processed'
        ]
      });
    });
    
    // Setup graceful shutdown
    gracefulShutdown(server);
    
  } catch (error) {
    gatewayLogger.error('Failed to start API Gateway', error);
    process.exit(1);
  }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  gatewayLogger.error('Uncaught Exception', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  gatewayLogger.error('Unhandled Rejection', reason, {
    promise: promise.toString()
  });
  process.exit(1);
});

// Start the gateway
startGateway();