import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  HardDrive,
  MemoryStick,
  Monitor,
  NetworkIcon as Network,
  RefreshCw,
  Settings,
  Shield,
  TrendingUp,
  TrendingDown,
  Wifi,
  Zap,
  Server,
  Camera,
  Users,
  Eye,
  AlertCircle,
  XCircle,
  Pause,
  Play,
  BarChart3,
  PieChart,
  LineChart,
  Info,
  Bell,
  Download
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardTitle } from '@/components/ui/MinimalCard';
import { monitoringAPI, analyticsAPI } from '@/services/api';

export const MonitoringPage = ({ onNavigate }) => {
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [serviceStatus, setServiceStatus] = useState(null);
  const [dashboardAnalytics, setDashboardAnalytics] = useState(null);
  const [circuitBreakerStatus, setCircuitBreakerStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5); // seconds
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [alerts, setAlerts] = useState([]);
  const intervalRef = useRef(null);

  // Mock data for demonstration - in real app, this would come from APIs
  const [mockData] = useState({
    systemHealth: {
      overall_status: 'healthy',
      services: {
        'core-data': { status: 'healthy', uptime: '99.8%', response_time: 23.5 },
        'face-recognition': { status: 'healthy', uptime: '99.9%', response_time: 45.2 },
        'camera-stream': { status: 'degraded', uptime: '97.3%', response_time: 120.8 },
        'notification': { status: 'healthy', uptime: '99.7%', response_time: 18.1 },
        'api-gateway': { status: 'healthy', uptime: '99.9%', response_time: 12.5 }
      }
    },
    resourceMetrics: {
      cpu_usage: 45.2,
      memory_usage: 67.8,
      disk_usage: 34.5,
      network_io: { in: 125.4, out: 89.2 },
      gpu_usage: 78.3
    },
    performanceMetrics: {
      face_recognition: {
        avg_response_time: 245,
        requests_per_minute: 42,
        success_rate: 98.7,
        queue_length: 3
      },
      database: {
        active_connections: 12,
        max_connections: 100,
        avg_query_time: 23.5,
        slow_queries: 2
      }
    }
  });

  const fetchMonitoringData = async () => {
    try {
      setIsLoading(true);
      
      // In a real implementation, these would be actual API calls
      // For now, we'll use mock data with some simulated variation
      const variation = () => Math.random() * 10 - 5; // ±5% variation
      
      setSystemMetrics({
        ...mockData.resourceMetrics,
        cpu_usage: Math.max(0, Math.min(100, mockData.resourceMetrics.cpu_usage + variation())),
        memory_usage: Math.max(0, Math.min(100, mockData.resourceMetrics.memory_usage + variation())),
        disk_usage: Math.max(0, Math.min(100, mockData.resourceMetrics.disk_usage + variation())),
      });

      setServiceStatus(mockData.systemHealth);
      
      // Generate some alerts based on thresholds
      const newAlerts = [];
      if (mockData.resourceMetrics.cpu_usage > 80) {
        newAlerts.push({
          id: 'cpu-high',
          level: 'warning',
          message: 'High CPU usage detected',
          value: mockData.resourceMetrics.cpu_usage,
          threshold: 80
        });
      }
      if (mockData.resourceMetrics.memory_usage > 90) {
        newAlerts.push({
          id: 'memory-critical',
          level: 'critical',
          message: 'Critical memory usage',
          value: mockData.resourceMetrics.memory_usage,
          threshold: 90
        });
      }
      setAlerts(newAlerts);
      
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch monitoring data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMonitoringData();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchMonitoringData, refreshInterval * 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-emerald-400 bg-emerald-950/50 border-emerald-600/30';
      case 'degraded': return 'text-yellow-400 bg-yellow-950/50 border-yellow-600/30';
      case 'unhealthy': return 'text-red-400 bg-red-950/50 border-red-600/30';
      default: return 'text-zinc-400 bg-zinc-950/50 border-zinc-600/30';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-4 w-4" />;
      case 'degraded': return <AlertTriangle className="h-4 w-4" />;
      case 'unhealthy': return <XCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-emerald-500';
  };

  return (
    <>
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="inline-block bg-blue-600/10 border border-blue-600/20 text-blue-400 px-4 py-2 rounded-full text-xs font-medium mb-10 tracking-wider">
          MONITORING
        </div>
        <h1 className="text-5xl lg:text-6xl font-normal mb-8 tracking-tight leading-tight">
          System <span className="italic text-zinc-600 font-light">Health</span>
        </h1>
        <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
          Real-time monitoring of system performance, operational health, and service status with comprehensive analytics and alerting.
        </p>
      </div>

      {/* Control Panel */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <button
            onClick={fetchMonitoringData}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
              autoRefresh 
                ? 'bg-emerald-600/20 text-emerald-400 border-emerald-600/30' 
                : 'bg-zinc-800/50 text-zinc-400 border-zinc-700'
            }`}
          >
            {autoRefresh ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            Auto Refresh
          </button>

          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="px-3 py-2 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value={5}>5s</option>
            <option value={10}>10s</option>
            <option value={30}>30s</option>
            <option value={60}>1m</option>
          </select>
        </div>

        <div className="text-sm text-zinc-500">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      </div>

      {/* System Alerts */}
      {alerts.length > 0 && (
        <div className="mb-8">
          <MinimalCard className="border-red-900/50 bg-red-950/20">
            <MinimalCardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                <h3 className="text-red-400 font-medium">System Alerts</h3>
              </div>
              <div className="space-y-2">
                {alerts.map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between p-3 bg-red-950/30 rounded-lg">
                    <span className="text-zinc-300">{alert.message}</span>
                    <div className="text-sm text-red-400">
                      {alert.value?.toFixed(1)}% (threshold: {alert.threshold}%)
                    </div>
                  </div>
                ))}
              </div>
            </MinimalCardContent>
          </MinimalCard>
        </div>
      )}

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-emerald-600/20 rounded-lg">
                <CheckCircle className="h-6 w-6 text-emerald-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-white">
                  {serviceStatus ? Object.values(serviceStatus.services).filter(s => s.status === 'healthy').length : 0}
                </div>
                <div className="text-sm text-zinc-400">Healthy Services</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-600/20 rounded-lg">
                <Activity className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-white">
                  {systemMetrics ? systemMetrics.cpu_usage.toFixed(1) : 0}%
                </div>
                <div className="text-sm text-zinc-400">CPU Usage</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-600/20 rounded-lg">
                <MemoryStick className="h-6 w-6 text-purple-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-white">
                  {systemMetrics ? systemMetrics.memory_usage.toFixed(1) : 0}%
                </div>
                <div className="text-sm text-zinc-400">Memory Usage</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-orange-600/20 rounded-lg">
                <HardDrive className="h-6 w-6 text-orange-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-white">
                  {systemMetrics ? systemMetrics.disk_usage.toFixed(1) : 0}%
                </div>
                <div className="text-sm text-zinc-400">Disk Usage</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Detailed Monitoring Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* Service Status */}
        <MinimalCard>
          <MinimalCardContent className="p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-emerald-600/20 rounded-lg">
                <Server className="h-5 w-5 text-emerald-400" />
              </div>
              <h2 className="text-xl font-normal text-white">Service Status</h2>
            </div>

            <div className="space-y-4">
              {serviceStatus && Object.entries(serviceStatus.services).map(([serviceName, service]) => (
                <div key={serviceName} className="flex items-center justify-between p-4 bg-zinc-950/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`flex items-center gap-2 px-2 py-1 rounded text-xs border ${getStatusColor(service.status)}`}>
                      {getStatusIcon(service.status)}
                      {service.status}
                    </div>
                    <span className="text-white font-medium capitalize">
                      {serviceName.replace(/-/g, ' ')}
                    </span>
                  </div>
                  <div className="text-sm text-zinc-400">
                    <div>Uptime: {service.uptime}</div>
                    <div>Response: {service.response_time}ms</div>
                  </div>
                </div>
              ))}
            </div>
          </MinimalCardContent>
        </MinimalCard>

        {/* Resource Utilization */}
        <MinimalCard>
          <MinimalCardContent className="p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-600/20 rounded-lg">
                <Monitor className="h-5 w-5 text-blue-400" />
              </div>
              <h2 className="text-xl font-normal text-white">Resource Utilization</h2>
            </div>

            <div className="space-y-6">
              {systemMetrics && [
                { name: 'CPU Usage', value: systemMetrics.cpu_usage, icon: Cpu, color: 'blue' },
                { name: 'Memory Usage', value: systemMetrics.memory_usage, icon: MemoryStick, color: 'purple' },
                { name: 'Disk Usage', value: systemMetrics.disk_usage, icon: HardDrive, color: 'orange' },
                { name: 'GPU Usage', value: systemMetrics.gpu_usage || 78.3, icon: Zap, color: 'emerald' }
              ].map(({ name, value, icon: Icon, color }) => (
                <div key={name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Icon className={`h-4 w-4 text-${color}-400`} />
                      <span className="text-zinc-300">{name}</span>
                    </div>
                    <span className="text-white font-medium">{value.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-zinc-800 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${getUsageColor(value)}`}
                      style={{ width: `${value}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {/* Face Recognition Performance */}
        <MinimalCard>
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-600/20 rounded-lg">
                <Eye className="h-5 w-5 text-purple-400" />
              </div>
              <h3 className="text-lg font-medium text-white">Face Recognition</h3>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Avg Response Time</span>
                <span className="text-white font-medium">245ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Requests/min</span>
                <span className="text-white font-medium">42</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Success Rate</span>
                <span className="text-emerald-400 font-medium">98.7%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Queue Length</span>
                <span className="text-white font-medium">3</span>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        {/* Database Performance */}
        <MinimalCard>
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-emerald-600/20 rounded-lg">
                <Database className="h-5 w-5 text-emerald-400" />
              </div>
              <h3 className="text-lg font-medium text-white">Database</h3>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Active Connections</span>
                <span className="text-white font-medium">12/100</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Avg Query Time</span>
                <span className="text-white font-medium">23.5ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Slow Queries</span>
                <span className="text-yellow-400 font-medium">2</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Connection Pool</span>
                <span className="text-emerald-400 font-medium">12%</span>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        {/* Network Performance */}
        <MinimalCard>
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-600/20 rounded-lg">
                <Network className="h-5 w-5 text-blue-400" />
              </div>
              <h3 className="text-lg font-medium text-white">Network I/O</h3>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Inbound</span>
                <span className="text-white font-medium">125.4 MB/s</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Outbound</span>
                <span className="text-white font-medium">89.2 MB/s</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Latency</span>
                <span className="text-emerald-400 font-medium">12ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Packet Loss</span>
                <span className="text-emerald-400 font-medium">0.01%</span>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* System Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* System Info */}
        <MinimalCard>
          <MinimalCardContent className="p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-zinc-600/20 rounded-lg">
                <Info className="h-5 w-5 text-zinc-400" />
              </div>
              <h2 className="text-xl font-normal text-white">System Information</h2>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-zinc-400 mb-1">Version</div>
                  <div className="text-white font-medium">FaceGuard v2.1.0</div>
                </div>
                <div>
                  <div className="text-sm text-zinc-400 mb-1">Uptime</div>
                  <div className="text-white font-medium">7d 14h 23m</div>
                </div>
                <div>
                  <div className="text-sm text-zinc-400 mb-1">Environment</div>
                  <div className="text-white font-medium">Production</div>
                </div>
                <div>
                  <div className="text-sm text-zinc-400 mb-1">Node Version</div>
                  <div className="text-white font-medium">18.17.0</div>
                </div>
              </div>

              <div className="pt-4 border-t border-zinc-800">
                <div className="text-sm text-zinc-400 mb-2">Active Components</div>
                <div className="flex flex-wrap gap-2">
                  {['Core Data', 'Face Recognition', 'Camera Stream', 'Notifications', 'API Gateway'].map((component) => (
                    <span key={component} className="px-2 py-1 bg-emerald-950/50 text-emerald-400 rounded text-xs border border-emerald-600/30">
                      {component}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        {/* Quick Actions */}
        <MinimalCard>
          <MinimalCardContent className="p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-orange-600/20 rounded-lg">
                <Settings className="h-5 w-5 text-orange-400" />
              </div>
              <h2 className="text-xl font-normal text-white">Quick Actions</h2>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => onNavigate('cameras')}
                className="w-full flex items-center gap-3 p-3 bg-zinc-950/30 hover:bg-zinc-900/50 rounded-lg transition-colors text-left"
              >
                <Camera className="h-4 w-4 text-blue-400" />
                <span className="text-white">View Camera Status</span>
              </button>
              
              <button
                onClick={() => onNavigate('notifications')}
                className="w-full flex items-center gap-3 p-3 bg-zinc-950/30 hover:bg-zinc-900/50 rounded-lg transition-colors text-left"
              >
                <Bell className="h-4 w-4 text-orange-400" />
                <span className="text-white">Check Notifications</span>
              </button>
              
              <button
                onClick={() => onNavigate('analytics')}
                className="w-full flex items-center gap-3 p-3 bg-zinc-950/30 hover:bg-zinc-900/50 rounded-lg transition-colors text-left"
              >
                <BarChart3 className="h-4 w-4 text-emerald-400" />
                <span className="text-white">View Analytics</span>
              </button>
              
              <button
                className="w-full flex items-center gap-3 p-3 bg-zinc-950/30 hover:bg-zinc-900/50 rounded-lg transition-colors text-left"
              >
                <Download className="h-4 w-4 text-purple-400" />
                <span className="text-white">Export System Logs</span>
              </button>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>
    </>
  );
};