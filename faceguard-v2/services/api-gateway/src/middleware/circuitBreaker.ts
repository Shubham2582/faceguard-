/**
 * Circuit Breaker Implementation
 * Prevents cascading failures and provides fallback responses
 */

import { ServiceType } from '../utils/httpClient';
import { gatewayLogger } from '../utils/logger';
import { circuitBreakerConfig } from '../config/settings';

export enum CircuitState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half-open'
}

export interface CircuitBreakerStats {
  state: CircuitState;
  failureCount: number;
  successCount: number;
  lastFailureTime?: number;
  lastSuccessTime?: number;
  requestCount: number;
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount: number = 0;
  private successCount: number = 0;
  private lastFailureTime?: number;
  private lastSuccessTime?: number;
  private requestCount: number = 0;
  
  constructor(
    private readonly serviceName: string,
    private readonly serviceType: ServiceType,
    private readonly config = circuitBreakerConfig
  ) {}

  /**
   * Execute request through circuit breaker
   */
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    this.requestCount++;
    
    // Check if circuit should be opened
    if (this.state === CircuitState.OPEN) {
      if (this.shouldAttemptReset()) {
        this.state = CircuitState.HALF_OPEN;
        gatewayLogger.circuitBreaker(this.serviceName, 'half-open', {
          failureCount: this.failureCount,
          timeSinceLastFailure: Date.now() - (this.lastFailureTime || 0)
        });
      } else {
        throw new CircuitBreakerOpenError(this.serviceName);
      }
    }

    try {
      const result = await Promise.race([
        operation(),
        this.timeoutPromise()
      ]);
      
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * Record successful operation
   */
  private onSuccess(): void {
    this.failureCount = 0;
    this.successCount++;
    this.lastSuccessTime = Date.now();
    
    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.CLOSED;
      gatewayLogger.circuitBreaker(this.serviceName, 'closed', {
        successCount: this.successCount,
        message: 'Service recovered, circuit closed'
      });
    }
  }

  /**
   * Record failed operation
   */
  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    const failureRate = this.failureCount / Math.max(this.requestCount, 1) * 100;
    
    if (this.failureCount >= 5 && failureRate >= this.config.errorThreshold) {
      this.state = CircuitState.OPEN;
      gatewayLogger.circuitBreaker(this.serviceName, 'open', {
        failureCount: this.failureCount,
        failureRate: failureRate.toFixed(2),
        threshold: this.config.errorThreshold
      });
    }
  }

  /**
   * Check if circuit should attempt to reset
   */
  private shouldAttemptReset(): boolean {
    if (!this.lastFailureTime) return false;
    return (Date.now() - this.lastFailureTime) >= this.config.resetTimeout;
  }

  /**
   * Create timeout promise
   */
  private timeoutPromise(): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Operation timeout after ${this.config.timeout}ms`));
      }, this.config.timeout);
    });
  }

  /**
   * Get current circuit breaker statistics
   */
  getStats(): CircuitBreakerStats {
    return {
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      lastFailureTime: this.lastFailureTime,
      lastSuccessTime: this.lastSuccessTime,
      requestCount: this.requestCount
    };
  }

  /**
   * Reset circuit breaker
   */
  reset(): void {
    this.state = CircuitState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
    this.requestCount = 0;
    this.lastFailureTime = undefined;
    this.lastSuccessTime = undefined;
    
    gatewayLogger.circuitBreaker(this.serviceName, 'reset', {
      message: 'Circuit breaker manually reset'
    });
  }
}

/**
 * Circuit breaker open error
 */
export class CircuitBreakerOpenError extends Error {
  constructor(serviceName: string) {
    super(`Circuit breaker is open for ${serviceName}`);
    this.name = 'CircuitBreakerOpenError';
  }
}

/**
 * Service circuit breakers
 */
export const serviceCircuitBreakers = {
  [ServiceType.CORE_DATA]: new CircuitBreaker('Core Data Service', ServiceType.CORE_DATA),
  [ServiceType.FACE_RECOGNITION]: new CircuitBreaker('Face Recognition Service', ServiceType.FACE_RECOGNITION),
  [ServiceType.CAMERA_STREAM]: new CircuitBreaker('Camera Stream Service', ServiceType.CAMERA_STREAM)
};

/**
 * Fallback responses for when circuit is open
 */
export const fallbackResponses = {
  [ServiceType.CORE_DATA]: {
    persons: {
      error: 'Service Temporarily Unavailable',
      message: 'Core Data Service is currently down. Please try again later.',
      fallback: true,
      timestamp: new Date().toISOString(),
      statusCode: 503
    },
    health: {
      status: 'unhealthy',
      service: 'Core Data Service',
      message: 'Service circuit breaker is open',
      fallback: true,
      timestamp: new Date().toISOString()
    }
  },
  
  [ServiceType.FACE_RECOGNITION]: {
    recognition: {
      error: 'Recognition Service Unavailable', 
      message: 'Face Recognition Service is currently down. Cannot process images.',
      fallback: true,
      timestamp: new Date().toISOString(),
      statusCode: 503
    },
    health: {
      status: 'unhealthy',
      service: 'Face Recognition Service', 
      message: 'Service circuit breaker is open',
      fallback: true,
      timestamp: new Date().toISOString()
    }
  },
  
  [ServiceType.CAMERA_STREAM]: {
    cameras: {
      error: 'Camera Service Unavailable',
      message: 'Camera Stream Service is currently down. Live feeds unavailable.',
      fallback: true,
      timestamp: new Date().toISOString(),
      statusCode: 503
    },
    health: {
      status: 'unhealthy',
      service: 'Camera Stream Service',
      message: 'Service circuit breaker is open', 
      fallback: true,
      timestamp: new Date().toISOString()
    }
  }
};

/**
 * Get all circuit breaker statistics
 */
export function getAllCircuitBreakerStats(): Record<string, CircuitBreakerStats> {
  return {
    coreData: serviceCircuitBreakers[ServiceType.CORE_DATA].getStats(),
    faceRecognition: serviceCircuitBreakers[ServiceType.FACE_RECOGNITION].getStats(),
    cameraStream: serviceCircuitBreakers[ServiceType.CAMERA_STREAM].getStats()
  };
}