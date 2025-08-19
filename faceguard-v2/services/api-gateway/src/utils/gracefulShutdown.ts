/**
 * Graceful Shutdown Utility
 * Handles proper cleanup of server resources and connections
 */

import { Server } from 'http';
import { gatewayLogger } from './logger';
import { cleanupWebSocketProxy } from '../routes/websocket';

let isShuttingDown = false;

/**
 * Setup graceful shutdown for the server
 */
export function gracefulShutdown(server: Server): void {
  // Handle shutdown signals
  const shutdownSignals = ['SIGTERM', 'SIGINT', 'SIGUSR2'];
  
  shutdownSignals.forEach((signal) => {
    process.on(signal, () => {
      if (isShuttingDown) {
        gatewayLogger.warn(`Received ${signal} during shutdown, forcing exit`);
        process.exit(1);
      }
      
      gatewayLogger.startup(`Received ${signal}, initiating graceful shutdown`);
      shutdown(server, signal);
    });
  });
  
  // Handle uncaught exceptions during shutdown
  process.on('uncaughtException', (error) => {
    gatewayLogger.error('Uncaught exception during shutdown', error);
    if (isShuttingDown) {
      process.exit(1);
    }
  });
  
  process.on('unhandledRejection', (reason, promise) => {
    gatewayLogger.error('Unhandled rejection during shutdown', reason, {
      promise: promise.toString()
    });
    if (isShuttingDown) {
      process.exit(1);
    }
  });
}

/**
 * Perform graceful shutdown
 */
async function shutdown(server: Server, signal: string): Promise<void> {
  isShuttingDown = true;
  
  const shutdownTimeout = 30000; // 30 seconds timeout
  const shutdownTimer = setTimeout(() => {
    gatewayLogger.error('Graceful shutdown timeout, forcing exit', new Error('Shutdown timeout'));
    process.exit(1);
  }, shutdownTimeout);
  
  try {
    gatewayLogger.startup('Starting graceful shutdown sequence', {
      signal,
      uptime: process.uptime(),
      memoryUsage: process.memoryUsage()
    });
    
    // Step 1: Stop accepting new connections
    gatewayLogger.startup('Stopping new connections');
    server.close();
    
    // Step 2: Close WebSocket connections and Redis clients
    gatewayLogger.startup('Cleaning up WebSocket and Redis connections');
    await cleanupWebSocketProxy();
    
    // Step 3: Wait for existing connections to finish
    gatewayLogger.startup('Waiting for existing connections to finish');
    await waitForConnectionsToClose(server);
    
    // Step 4: Cleanup other resources
    gatewayLogger.startup('Performing final cleanup');
    await performFinalCleanup();
    
    // Clear shutdown timeout
    clearTimeout(shutdownTimer);
    
    gatewayLogger.startup('Graceful shutdown completed successfully', {
      signal,
      shutdownDuration: process.uptime()
    });
    
    process.exit(0);
    
  } catch (error) {
    gatewayLogger.error('Error during graceful shutdown', error);
    clearTimeout(shutdownTimer);
    process.exit(1);
  }
}

/**
 * Wait for all connections to close
 */
function waitForConnectionsToClose(server: Server): Promise<void> {
  return new Promise((resolve) => {
    server.on('close', () => {
      gatewayLogger.startup('All connections closed');
      resolve();
    });
    
    // Check if server is already closed
    if (!server.listening) {
      resolve();
    }
  });
}

/**
 * Perform final cleanup tasks
 */
async function performFinalCleanup(): Promise<void> {
  try {
    // Log final statistics
    const finalStats = {
      uptime: process.uptime(),
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      pid: process.pid
    };
    
    gatewayLogger.startup('Final server statistics', finalStats);
    
    // Flush logs - simplified for now
    gatewayLogger.startup('Finalizing logs');
    
    // Small delay to ensure logs are written
    await new Promise(resolve => setTimeout(resolve, 100));
    
  } catch (error) {
    console.error('Error during final cleanup:', error);
  }
}

/**
 * Check if server is shutting down
 */
export function isServerShuttingDown(): boolean {
  return isShuttingDown;
}