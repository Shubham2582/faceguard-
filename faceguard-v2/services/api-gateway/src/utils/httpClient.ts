/**
 * HTTP Client Utility
 * Handles communication with all backend services with retry logic and error handling
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { serviceConfigs } from '../config/settings';
import { logger } from './logger';

/**
 * Service identification enum
 */
export enum ServiceType {
  CORE_DATA = 'coreData',
  FACE_RECOGNITION = 'faceRecognition',
  CAMERA_STREAM = 'cameraStream'
}

/**
 * HTTP client configuration for each service
 */
interface ServiceClientConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  serviceName: string;
}

/**
 * Request retry configuration
 */
interface RetryConfig {
  attempts: number;
  delay: number;
  maxDelay: number;
  backoffFactor: number;
}

/**
 * Create axios instance with service-specific configuration
 */
function createServiceClient(config: ServiceClientConfig): AxiosInstance {
  const client = axios.create({
    baseURL: config.baseURL,
    timeout: config.timeout,
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'FaceGuard-API-Gateway/2.0.0',
      'X-Service-Name': 'api-gateway'
    }
  });

  // Request interceptor for logging and correlation
  client.interceptors.request.use(
    (request) => {
      const correlationId = generateCorrelationId();
      request.headers['X-Correlation-ID'] = correlationId;
      
      logger.info('HTTP Request', {
        service: config.serviceName,
        method: request.method?.toUpperCase(),
        url: request.url,
        correlationId,
        timeout: config.timeout
      });
      
      return request;
    },
    (error) => {
      logger.error('HTTP Request Error', {
        service: config.serviceName,
        error: error.message
      });
      return Promise.reject(error);
    }
  );

  // Response interceptor for logging and error handling
  client.interceptors.response.use(
    (response) => {
      const correlationId = response.config.headers['X-Correlation-ID'];
      
      logger.info('HTTP Response', {
        service: config.serviceName,
        status: response.status,
        statusText: response.statusText,
        correlationId,
        responseTime: Date.now() - (response.config as any).requestStartTime
      });
      
      return response;
    },
    (error) => {
      const correlationId = error.config?.headers['X-Correlation-ID'];
      
      logger.error('HTTP Response Error', {
        service: config.serviceName,
        status: error.response?.status,
        statusText: error.response?.statusText,
        message: error.message,
        correlationId
      });
      
      return Promise.reject(error);
    }
  );

  return client;
}

/**
 * Service-specific HTTP clients
 * Based on analyzed service configurations
 */
export const serviceClients = {
  // Core Data Service (Port 8001) - 56 persons, real CRUD operations
  [ServiceType.CORE_DATA]: createServiceClient({
    baseURL: serviceConfigs.coreData.url,
    timeout: serviceConfigs.coreData.timeout,
    retries: serviceConfigs.coreData.retries,
    serviceName: 'Core Data Service'
  }),

  // Face Recognition Service (Port 8002) - 703x cache speedup, GPU acceleration
  [ServiceType.FACE_RECOGNITION]: createServiceClient({
    baseURL: serviceConfigs.faceRecognition.url,
    timeout: serviceConfigs.faceRecognition.timeout,
    retries: serviceConfigs.faceRecognition.retries,
    serviceName: 'Face Recognition Service'
  }),

  // Camera Stream Service (Port 8003) - Live validated, 1,258+ frames processed
  [ServiceType.CAMERA_STREAM]: createServiceClient({
    baseURL: serviceConfigs.cameraStream.url,
    timeout: serviceConfigs.cameraStream.timeout,
    retries: serviceConfigs.cameraStream.retries,
    serviceName: 'Camera Stream Service'
  })
};

/**
 * Generate correlation ID for request tracing
 */
function generateCorrelationId(): string {
  return `gw_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Retry logic with exponential backoff
 */
async function retryRequest<T>(
  fn: () => Promise<AxiosResponse<T>>,
  config: RetryConfig,
  serviceName: string
): Promise<AxiosResponse<T>> {
  let lastError: any;
  let delay = config.delay;

  for (let attempt = 1; attempt <= config.attempts; attempt++) {
    try {
      const result = await fn();
      
      if (attempt > 1) {
        logger.info('Request succeeded after retry', {
          service: serviceName,
          attempt,
          totalAttempts: config.attempts
        });
      }
      
      return result;
    } catch (error) {
      lastError = error;
      
      logger.warn('Request failed, will retry', {
        service: serviceName,
        attempt,
        totalAttempts: config.attempts,
        error: (error as any).message,
        retryDelay: delay
      });

      if (attempt < config.attempts) {
        await new Promise(resolve => setTimeout(resolve, delay));
        delay = Math.min(delay * config.backoffFactor, config.maxDelay);
      }
    }
  }

  logger.error('Request failed after all retries', {
    service: serviceName,
    totalAttempts: config.attempts,
    finalError: lastError.message
  });

  throw lastError;
}

/**
 * Make HTTP request with retry logic
 */
export async function makeRequest<T>(
  serviceType: ServiceType,
  config: AxiosRequestConfig
): Promise<AxiosResponse<T>> {
  const client = serviceClients[serviceType];
  const serviceConfig = Object.values(serviceConfigs).find(s => s.url === client.defaults.baseURL);
  
  if (!serviceConfig) {
    throw new Error(`Service configuration not found for ${serviceType}`);
  }

  const retryConfig: RetryConfig = {
    attempts: serviceConfig.retries,
    delay: 1000,
    maxDelay: 10000,
    backoffFactor: 2
  };

  // Add request start time for response time calculation
  (config as any).requestStartTime = Date.now();

  return retryRequest(
    () => client.request<T>(config),
    retryConfig,
    (client.defaults.headers as any)['X-Service-Name'] || serviceType
  );
}

/**
 * Specific methods for different request types
 */
export const httpClient = {
  /**
   * GET request with retry logic
   */
  async get<T>(serviceType: ServiceType, url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return makeRequest<T>(serviceType, {
      method: 'GET',
      url,
      ...config
    });
  },

  /**
   * POST request with retry logic
   */
  async post<T>(serviceType: ServiceType, url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return makeRequest<T>(serviceType, {
      method: 'POST',
      url,
      data,
      ...config
    });
  },

  /**
   * PUT request with retry logic
   */
  async put<T>(serviceType: ServiceType, url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return makeRequest<T>(serviceType, {
      method: 'PUT',
      url,
      data,
      ...config
    });
  },

  /**
   * DELETE request with retry logic
   */
  async delete<T>(serviceType: ServiceType, url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return makeRequest<T>(serviceType, {
      method: 'DELETE',
      url,
      ...config
    });
  },

  /**
   * Health check specific method
   */
  async healthCheck(serviceType: ServiceType): Promise<AxiosResponse> {
    const serviceConfig = serviceConfigs[serviceType];
    return makeRequest(serviceType, {
      method: 'GET',
      url: serviceConfig.healthPath,
      timeout: 5000 // Shorter timeout for health checks
    });
  }
};

/**
 * Check if error is retryable
 */
export function isRetryableError(error: any): boolean {
  // Network errors
  if (error.code === 'ECONNRESET' || error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
    return true;
  }

  // HTTP status codes that should be retried
  if (error.response?.status) {
    const status = error.response.status;
    return status >= 500 || status === 408 || status === 429;
  }

  return false;
}

/**
 * Extract error message from axios error
 */
export function extractErrorMessage(error: any): string {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'Unknown error occurred';
}