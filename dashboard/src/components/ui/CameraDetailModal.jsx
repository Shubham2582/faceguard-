import React, { useState, useEffect } from 'react';
import {
  X,
  Camera,
  MapPin,
  Clock,
  Signal,
  Settings,
  Activity,
  Users,
  Eye,
  AlertTriangle,
  Monitor,
  Download,
  Play
} from 'lucide-react';
import { MinimalCard, MinimalCardContent } from '@/components/ui/MinimalCard';
import { CameraFeed } from '@/components/ui/CameraFeed';
import { cn } from '@/lib/utils';

// Mock detailed camera data
const getCameraDetails = (cameraId) => ({
  id: cameraId,
  name: 'Main Entrance',
  location: 'Building A - Floor 1',
  status: 'active',
  resolution: '1920x1080',
  fps: 30,
  manufacturer: 'Hikvision',
  model: 'DS-2CD2185FWD-I',
  ipAddress: '192.168.1.101',
  uptime: '99.8%',
  recognitionHistory: [
    { id: 1, person: 'Shubham Kumar', confidence: '96.8%', timestamp: '2024-01-24 14:23:15', activity: 'Entry' },
    { id: 2, person: 'Priya Singh', confidence: '94.2%', timestamp: '2024-01-24 13:45:32', activity: 'Exit' },
    { id: 3, person: 'Rajesh Patel', confidence: '98.1%', timestamp: '2024-01-24 12:15:48', activity: 'Entry' },
    { id: 4, person: 'Sarah Johnson', confidence: '92.4%', timestamp: '2024-01-24 11:30:22', activity: 'Entry' },
    { id: 5, person: 'Mike Chen', confidence: '89.7%', timestamp: '2024-01-24 10:45:15', activity: 'Exit' }
  ],
  performanceStats: {
    totalRecognitions: 1247,
    successRate: '96.8%',
    averageConfidence: '93.2%',
    responseTime: '180ms'
  },
  alertHistory: [
    { id: 1, type: 'High Priority Person', message: 'Rajesh Patel detected', severity: 'high', timestamp: '2024-01-24 14:15:30' },
    { id: 2, type: 'Motion Detection', message: 'Unusual activity after hours', severity: 'medium', timestamp: '2024-01-24 01:45:22' }
  ]
});

export const CameraDetailModal = ({ cameraId, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [camera, setCamera] = useState(null);

  useEffect(() => {
    if (isOpen && cameraId) {
      setCamera(getCameraDetails(cameraId));
    }
  }, [isOpen, cameraId]);

  if (!isOpen || !camera) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Monitor },
    { id: 'recognition', label: 'Recognition History', icon: Users },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    { id: 'performance', label: 'Performance', icon: Activity }
  ];

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-950 border border-zinc-900 rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-zinc-900 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-blue-600/20 rounded-lg">
              <Camera className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-medium text-white">{camera.name}</h2>
              <div className="flex items-center gap-2 text-sm text-zinc-500">
                <MapPin className="h-3 w-3" />
                {camera.location}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 py-3 border-b border-zinc-900">
          <div className="flex gap-1">
            {tabs.map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    activeTab === tab.id
                      ? "bg-blue-600/20 text-blue-400 border border-blue-600/30"
                      : "text-zinc-400 hover:text-white hover:bg-zinc-900/50"
                  )}
                >
                  <IconComponent className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <h3 className="text-lg font-medium text-white mb-4">Live Feed</h3>
                <CameraFeed
                  streamUrl={camera.stream}
                  cameraName={camera.name}
                  status={camera.status}
                  resolution={camera.resolution}
                  fps={camera.fps}
                />
                
                <div className="grid grid-cols-4 gap-4 mt-6">
                  {[
                    { label: 'Total', value: camera.performanceStats.totalRecognitions, color: 'emerald' },
                    { label: 'Success', value: camera.performanceStats.successRate, color: 'blue' },
                    { label: 'Response', value: camera.performanceStats.responseTime, color: 'purple' },
                    { label: 'Uptime', value: camera.uptime, color: 'orange' }
                  ].map((stat, index) => (
                    <MinimalCard key={index}>
                      <MinimalCardContent className="p-4 text-center">
                        <div className={`text-2xl font-bold text-${stat.color}-400`}>{stat.value}</div>
                        <div className="text-xs text-zinc-500">{stat.label}</div>
                      </MinimalCardContent>
                    </MinimalCard>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-white mb-4">Camera Information</h3>
                <MinimalCard>
                  <MinimalCardContent className="p-4 space-y-3">
                    {[
                      { label: 'Manufacturer', value: camera.manufacturer },
                      { label: 'Model', value: camera.model },
                      { label: 'IP Address', value: camera.ipAddress },
                      { label: 'Resolution', value: camera.resolution },
                      { label: 'Frame Rate', value: `${camera.fps} fps` }
                    ].map((info, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span className="text-zinc-500">{info.label}</span>
                        <span className="text-white">{info.value}</span>
                      </div>
                    ))}
                  </MinimalCardContent>
                </MinimalCard>
              </div>
            </div>
          )}

          {activeTab === 'recognition' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-medium text-white">Recognition History</h3>
                <button className="flex items-center gap-2 px-3 py-1.5 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-600/30 text-sm">
                  <Download className="h-4 w-4" />
                  Export
                </button>
              </div>

              <div className="space-y-3">
                {camera.recognitionHistory.map((recognition) => (
                  <MinimalCard key={recognition.id} className="hover:bg-zinc-900/30 transition-colors">
                    <MinimalCardContent className="p-4">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                          <Users className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="text-white font-medium">{recognition.person}</h4>
                            <div className="px-2 py-1 rounded text-xs border bg-emerald-950/50 text-emerald-400 border-emerald-900">
                              {recognition.confidence}
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-zinc-500">
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {recognition.timestamp}
                            </div>
                            <div className="flex items-center gap-1">
                              <Eye className="h-3 w-3" />
                              {recognition.activity}
                            </div>
                          </div>
                        </div>
                        <button className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-400 hover:text-white transition-colors">
                          <Play className="h-4 w-4" />
                        </button>
                      </div>
                    </MinimalCardContent>
                  </MinimalCard>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div>
              <h3 className="text-lg font-medium text-white mb-6">Alert History</h3>
              <div className="space-y-3">
                {camera.alertHistory.map((alert) => (
                  <MinimalCard key={alert.id}>
                    <MinimalCardContent className="p-4">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-red-600/20 rounded-lg">
                          <AlertTriangle className="h-5 w-5 text-red-400" />
                        </div>
                        <div className="flex-1">
                          <h4 className="text-white font-medium">{alert.type}</h4>
                          <p className="text-zinc-400 text-sm">{alert.message}</p>
                          <div className="text-xs text-zinc-500 mt-1">{alert.timestamp}</div>
                        </div>
                      </div>
                    </MinimalCardContent>
                  </MinimalCard>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div>
              <h3 className="text-lg font-medium text-white mb-6">Performance Metrics</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {[
                  { title: 'Recognition Performance', metrics: [
                    { label: 'Success Rate', value: camera.performanceStats.successRate },
                    { label: 'Avg Confidence', value: camera.performanceStats.averageConfidence },
                    { label: 'Response Time', value: camera.performanceStats.responseTime }
                  ]},
                  { title: 'System Performance', metrics: [
                    { label: 'CPU Usage', value: '23%' },
                    { label: 'Memory Usage', value: '512 MB' },
                    { label: 'Temperature', value: '42°C' }
                  ]}
                ].map((section, index) => (
                  <MinimalCard key={index}>
                    <MinimalCardContent className="p-6">
                      <h4 className="text-white font-medium mb-4">{section.title}</h4>
                      <div className="space-y-3">
                        {section.metrics.map((metric, idx) => (
                          <div key={idx} className="flex justify-between">
                            <span className="text-zinc-400">{metric.label}</span>
                            <span className="text-white">{metric.value}</span>
                          </div>
                        ))}
                      </div>
                    </MinimalCardContent>
                  </MinimalCard>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};