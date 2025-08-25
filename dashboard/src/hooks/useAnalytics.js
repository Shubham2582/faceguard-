import { useState, useEffect, useCallback } from 'react';
import { analyticsAPI } from '@/services/api';
import { analyticsData as mockAnalyticsData } from '@/data/mockData';

// Custom hook for analytics data management
export const useAnalytics = (timeRange = '7d') => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch analytics data from API with fallback to mock data
  const fetchAnalyticsData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Try to fetch from real API
      const [
        overview,
        detectionTrends,
        locationStats,
        confidenceDistribution,
        personActivity,
        systemMetrics,
        peakHours,
        alertStats
      ] = await Promise.all([
        analyticsAPI.getOverview(timeRange).catch(() => null),
        analyticsAPI.getDetectionTrends(timeRange).catch(() => null),
        analyticsAPI.getLocationStats(timeRange).catch(() => null),
        analyticsAPI.getConfidenceDistribution(timeRange).catch(() => null),
        analyticsAPI.getPersonActivity(timeRange, 10).catch(() => null),
        analyticsAPI.getSystemMetrics().catch(() => null),
        analyticsAPI.getPeakHours(timeRange).catch(() => null),
        analyticsAPI.getAlertStats(timeRange).catch(() => null)
      ]);

      // If we have real data, use it
      if (overview) {
        setData({
          overview,
          detectionTrends,
          locationStats,
          confidenceDistribution,
          personActivity,
          systemMetrics,
          peakHours,
          alertStats,
          source: 'api'
        });
      } else {
        // Fallback to mock data
        console.warn('Analytics API not available, using mock data');
        setData({
          ...mockAnalyticsData,
          source: 'mock'
        });
      }

      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch analytics data:', err);
      
      // Use mock data as fallback
      setData({
        ...mockAnalyticsData,
        source: 'mock'
      });
      
      setError('Using offline data - API unavailable');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  // Initial data fetch
  useEffect(() => {
    fetchAnalyticsData();
  }, [fetchAnalyticsData]);

  // Refresh data manually
  const refresh = useCallback(() => {
    fetchAnalyticsData();
  }, [fetchAnalyticsData]);

  return {
    data,
    loading,
    error,
    lastUpdated,
    refresh,
    isUsingMockData: data?.source === 'mock'
  };
};

// Hook for real-time analytics updates
export const useRealTimeAnalytics = (timeRange = '7d', refreshInterval = 60000) => {
  const analyticsData = useAnalytics(timeRange);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Auto-refresh data
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      analyticsData.refresh();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, analyticsData.refresh]);

  return {
    ...analyticsData,
    autoRefresh,
    setAutoRefresh,
    refreshInterval
  };
};

// Hook for specific analytics metrics
export const useAnalyticsMetric = (metricType, timeRange = '7d') => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetric = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      let result;
      switch (metricType) {
        case 'overview':
          result = await analyticsAPI.getOverview(timeRange);
          break;
        case 'trends':
          result = await analyticsAPI.getDetectionTrends(timeRange);
          break;
        case 'locations':
          result = await analyticsAPI.getLocationStats(timeRange);
          break;
        case 'confidence':
          result = await analyticsAPI.getConfidenceDistribution(timeRange);
          break;
        case 'persons':
          result = await analyticsAPI.getPersonActivity(timeRange);
          break;
        case 'system':
          result = await analyticsAPI.getSystemMetrics();
          break;
        case 'peaks':
          result = await analyticsAPI.getPeakHours(timeRange);
          break;
        case 'alerts':
          result = await analyticsAPI.getAlertStats(timeRange);
          break;
        default:
          throw new Error(`Unknown metric type: ${metricType}`);
      }

      setData(result);
    } catch (err) {
      console.error(`Failed to fetch ${metricType} metric:`, err);
      
      // Fallback to mock data for specific metric
      const mockData = mockAnalyticsData[metricType] || mockAnalyticsData.overview;
      setData(mockData);
      setError(`Using offline data for ${metricType}`);
    } finally {
      setLoading(false);
    }
  }, [metricType, timeRange]);

  useEffect(() => {
    fetchMetric();
  }, [fetchMetric]);

  return { data, loading, error, refresh: fetchMetric };
};

// Analytics data transformation utilities
export const transformAnalyticsData = {
  // Convert confidence distribution to chart format
  confidenceToChartData: (distribution) => {
    return distribution?.map(item => ({
      name: item.range,
      value: item.count,
      percentage: item.percentage,
      color: getConfidenceColor(item.range)
    })) || [];
  },

  // Convert weekly pattern to chart format
  weeklyToChartData: (weeklyPattern) => {
    return weeklyPattern?.map(day => ({
      day: day.day,
      detections: day.detections,
      confidence: day.confidence,
      fill: getWeekdayColor(day.day)
    })) || [];
  },

  // Convert location analytics to sorted list
  locationToSortedData: (locations, sortBy = 'detections') => {
    return locations?.sort((a, b) => b[sortBy] - a[sortBy]) || [];
  },

  // Calculate percentage changes
  calculateTrend: (current, previous) => {
    if (!previous || previous === 0) return { value: 0, type: 'stable' };
    
    const change = ((current - previous) / previous) * 100;
    return {
      value: Math.abs(change).toFixed(1),
      type: change > 0 ? 'increase' : change < 0 ? 'decrease' : 'stable'
    };
  }
};

// Helper functions for data visualization
const getConfidenceColor = (range) => {
  if (range.includes('90-95')) return '#fbbf24'; // yellow
  if (range.includes('95-98')) return '#10b981'; // emerald
  if (range.includes('98-100')) return '#3b82f6'; // blue
  return '#6b7280'; // gray
};

const getWeekdayColor = (day) => {
  const colors = {
    'Mon': '#3b82f6',
    'Tue': '#8b5cf6',
    'Wed': '#10b981',
    'Thu': '#f59e0b',
    'Fri': '#ef4444',
    'Sat': '#06b6d4',
    'Sun': '#f97316'
  };
  return colors[day] || '#6b7280';
};

export default useAnalytics;