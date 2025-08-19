/**
 * WebSocket Proxy for Real-Time Events
 * Proxies Redis events from Camera Stream Service to frontend clients
 */

import express from 'express';
import WebSocket from 'ws';
import { createClient } from 'redis';
import { redisConfig, websocketConfig } from '../config/settings';
import { gatewayLogger } from '../utils/logger';

let wss: WebSocket.Server;
let redisClient: any;
let redisSubscriber: any;

/**
 * Setup WebSocket proxy for real-time events
 */
export async function setupWebSocketProxy(app: express.Application): Promise<void> {
  try {
    // Create WebSocket server
    wss = new WebSocket.Server({ 
      port: websocketConfig.port,
      path: websocketConfig.path
    });
    
    // Create Redis clients
    redisClient = createClient({
      url: `redis://${redisConfig.host}:${redisConfig.port}`,
      password: redisConfig.password,
      database: redisConfig.db
    });
    
    redisSubscriber = createClient({
      url: `redis://${redisConfig.host}:${redisConfig.port}`,
      password: redisConfig.password,
      database: redisConfig.db
    });
    
    // Connect to Redis
    await redisClient.connect();
    await redisSubscriber.connect();
    
    // Subscribe to face recognition events
    for (const channel of redisConfig.channels) {
      await redisSubscriber.subscribe(channel, (message: string) => {
        handleRedisMessage(channel, message);
      });
      
      gatewayLogger.config(`Subscribed to Redis channel: ${channel}`, {
        redisHost: redisConfig.host,
        redisPort: redisConfig.port
      });
    }
    
    // Handle WebSocket connections
    wss.on('connection', (ws: WebSocket, request) => {
      const clientIp = request.socket.remoteAddress;
      const userAgent = request.headers['user-agent'];
      
      gatewayLogger.analytics('WebSocket client connected', {
        clientIp,
        userAgent,
        totalClients: wss.clients.size
      });
      
      // Send welcome message
      ws.send(JSON.stringify({
        type: 'connection_established',
        message: 'Connected to FaceGuard V2 real-time events',
        timestamp: new Date().toISOString(),
        available_channels: redisConfig.channels
      }));
      
      // Handle client messages
      ws.on('message', (message: string) => {
        try {
          const data = JSON.parse(message);
          handleClientMessage(ws, data, clientIp);
        } catch (error) {
          gatewayLogger.error('Invalid WebSocket message from client', error, {
            clientIp,
            message: message.toString()
          });
          
          ws.send(JSON.stringify({
            type: 'error',
            message: 'Invalid message format',
            timestamp: new Date().toISOString()
          }));
        }
      });
      
      // Handle client disconnect
      ws.on('close', () => {
        gatewayLogger.analytics('WebSocket client disconnected', {
          clientIp,
          remainingClients: wss.clients.size - 1
        });
      });
      
      // Handle client errors
      ws.on('error', (error) => {
        gatewayLogger.error('WebSocket client error', error, { clientIp });
      });
    });
    
    // Handle WebSocket server errors
    wss.on('error', (error) => {
      gatewayLogger.error('WebSocket server error', error);
    });
    
    // Add WebSocket status endpoint
    app.get('/api/websocket/status', (req: express.Request, res: express.Response) => {
      res.json({
        status: 'operational',
        server: {
          port: websocketConfig.port,
          path: websocketConfig.path,
          connected_clients: wss.clients.size
        },
        redis: {
          host: redisConfig.host,
          port: redisConfig.port,
          subscribed_channels: redisConfig.channels
        },
        timestamp: new Date().toISOString()
      });
    });
    
    gatewayLogger.config('WebSocket proxy configured', {
      port: websocketConfig.port,
      path: websocketConfig.path,
      redisChannels: redisConfig.channels,
      redisHost: redisConfig.host
    });
    
  } catch (error) {
    gatewayLogger.error('Failed to setup WebSocket proxy', error);
    throw error;
  }
}

/**
 * Handle Redis messages and forward to WebSocket clients
 */
function handleRedisMessage(channel: string, message: string): void {
  try {
    // Parse Redis message
    const eventData = JSON.parse(message);
    
    // Create WebSocket message
    const wsMessage = {
      type: 'recognition_event',
      channel,
      data: eventData,
      timestamp: new Date().toISOString(),
      source: 'camera-stream-service'
    };
    
    // Broadcast to all connected clients
    const messageStr = JSON.stringify(wsMessage);
    let sentCount = 0;
    
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(messageStr);
        sentCount++;
      }
    });
    
    gatewayLogger.analytics('Redis event forwarded to WebSocket clients', {
      channel,
      eventType: eventData.event_type || 'unknown',
      clientsSent: sentCount,
      totalClients: wss.clients.size,
      eventId: eventData.event_id || 'unknown'
    });
    
  } catch (error) {
    gatewayLogger.error('Failed to process Redis message', error, {
      channel,
      messageLength: message.length
    });
  }
}

/**
 * Handle messages from WebSocket clients
 */
function handleClientMessage(ws: WebSocket, data: any, clientIp?: string): void {
  switch (data.type) {
    case 'ping':
      ws.send(JSON.stringify({
        type: 'pong',
        timestamp: new Date().toISOString()
      }));
      break;
      
    case 'subscribe':
      // Note: In this implementation, clients are automatically subscribed to all channels
      // In a more advanced version, we could implement selective subscription
      ws.send(JSON.stringify({
        type: 'subscription_info',
        subscribed_channels: redisConfig.channels,
        timestamp: new Date().toISOString()
      }));
      break;
      
    case 'get_status':
      ws.send(JSON.stringify({
        type: 'status',
        server_status: 'operational',
        connected_clients: wss.clients.size,
        redis_channels: redisConfig.channels,
        timestamp: new Date().toISOString()
      }));
      break;
      
    default:
      gatewayLogger.warn('Unknown WebSocket message type', {
        type: data.type,
        clientIp
      });
      
      ws.send(JSON.stringify({
        type: 'error',
        message: `Unknown message type: ${data.type}`,
        available_types: ['ping', 'subscribe', 'get_status'],
        timestamp: new Date().toISOString()
      }));
  }
}

/**
 * Cleanup WebSocket connections and Redis clients
 */
export async function cleanupWebSocketProxy(): Promise<void> {
  try {
    if (wss) {
      wss.clients.forEach((client) => {
        client.close(1000, 'Server shutting down');
      });
      wss.close();
      gatewayLogger.startup('WebSocket server closed');
    }
    
    if (redisSubscriber) {
      await redisSubscriber.quit();
      gatewayLogger.startup('Redis subscriber disconnected');
    }
    
    if (redisClient) {
      await redisClient.quit();
      gatewayLogger.startup('Redis client disconnected');
    }
    
  } catch (error) {
    gatewayLogger.error('Error during WebSocket cleanup', error);
  }
}