import React, { useState } from 'react';
import {
  X,
  Camera,
  Plus,
  Settings,
  Wifi,
  MapPin,
  Monitor,
  Eye,
  CheckCircle,
  AlertTriangle,
  Loader,
  Play,
  TestTube2,
  Globe,
  Network,
  Video,
  Zap,
  Volume2
} from 'lucide-react';
import { MinimalCard, MinimalCardContent } from '@/components/ui/MinimalCard';
import { cn } from '@/lib/utils';

// Stream types and configurations
const streamTypes = [
  {
    id: 'rtsp',
    name: 'RTSP Stream',
    description: 'Real Time Streaming Protocol for IP cameras',
    icon: Video,
    urlFormat: 'rtsp://username:password@ip:port/stream',
    defaultPort: 554,
    examples: [
      'rtsp://admin:password@192.168.1.100:554/stream1',
      'rtsp://user:pass@camera.local/live/ch00_0'
    ]
  },
  {
    id: 'http',
    name: 'HTTP/MJPEG',
    description: 'Motion JPEG over HTTP',
    icon: Globe,
    urlFormat: 'http://ip:port/mjpeg',
    defaultPort: 80,
    examples: [
      'http://192.168.1.100:8080/video',
      'http://camera.local/mjpeg'
    ]
  },
  {
    id: 'onvif',
    name: 'ONVIF Camera',
    description: 'Open Network Video Interface Forum standard',
    icon: Network,
    urlFormat: 'Auto-discovery via ONVIF',
    defaultPort: 80,
    examples: [
      'Auto-detected from network scan',
      'Manual IP: 192.168.1.100'
    ]
  },
  {
    id: 'usb',
    name: 'USB Camera',
    description: 'Local USB connected camera',
    icon: Monitor,
    urlFormat: '/dev/video0 or Camera Index',
    defaultPort: null,
    examples: [
      '/dev/video0 (Linux)',
      '0 (Camera Index)'
    ]
  }
];

const resolutions = [
  { value: '1920x1080', label: '1080p (1920×1080)' },
  { value: '1280x720', label: '720p (1280×720)' },
  { value: '640x480', label: '480p (640×480)' },
  { value: '3840x2160', label: '4K (3840×2160)' }
];

const frameRates = [
  { value: 30, label: '30 FPS' },
  { value: 25, label: '25 FPS' },
  { value: 20, label: '20 FPS' },
  { value: 15, label: '15 FPS' },
  { value: 10, label: '10 FPS' }
];

export const AddCameraModal = ({ isOpen, onClose, onAddCamera }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedStreamType, setSelectedStreamType] = useState(null);
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    streamType: '',
    streamUrl: '',
    username: '',
    password: '',
    resolution: '1920x1080',
    frameRate: 30,
    enableAudio: false,
    enableNightVision: true,
    enableMotionDetection: true,
    enableRecording: true,
    description: ''
  });

  const steps = [
    { id: 1, title: 'Camera Type', description: 'Select stream source' },
    { id: 2, title: 'Connection', description: 'Configure stream settings' },
    { id: 3, title: 'Settings', description: 'Camera preferences' },
    { id: 4, title: 'Test & Save', description: 'Verify and add camera' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleStreamTypeSelect = (streamType) => {
    setSelectedStreamType(streamType);
    handleInputChange('streamType', streamType.id);
    setCurrentStep(2);
  };

  const testConnection = async () => {
    setIsTestingConnection(true);
    setConnectionStatus(null);

    try {
      // Simulate connection test - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock successful connection
      const success = Math.random() > 0.3; // 70% success rate for demo
      
      if (success) {
        setConnectionStatus({
          status: 'success',
          message: 'Connection successful! Stream is accessible.',
          details: {
            resolution: formData.resolution,
            frameRate: `${formData.frameRate} FPS`,
            codec: 'H.264',
            latency: '120ms'
          }
        });
      } else {
        setConnectionStatus({
          status: 'error',
          message: 'Connection failed. Please check your settings.',
          details: {
            error: 'Network timeout',
            suggestion: 'Verify IP address and credentials'
          }
        });
      }
    } catch (error) {
      setConnectionStatus({
        status: 'error',
        message: 'Connection test failed.',
        details: { error: error.message }
      });
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleAddCamera = () => {
    const newCamera = {
      id: `CAM-${Date.now()}`,
      name: formData.name,
      location: formData.location,
      status: 'active',
      resolution: formData.resolution,
      fps: formData.frameRate,
      stream: formData.streamUrl,
      streamType: formData.streamType,
      lastSeen: 'Just now',
      recognitions: [],
      uptime: '100%',
      alerts: 0,
      // Additional metadata
      manufacturer: 'Generic',
      model: selectedStreamType?.name || 'Unknown',
      enableAudio: formData.enableAudio,
      enableNightVision: formData.enableNightVision,
      enableMotionDetection: formData.enableMotionDetection,
      enableRecording: formData.enableRecording,
      description: formData.description
    };

    onAddCamera(newCamera);
    onClose();
    resetForm();
  };

  const resetForm = () => {
    setCurrentStep(1);
    setSelectedStreamType(null);
    setConnectionStatus(null);
    setFormData({
      name: '',
      location: '',
      streamType: '',
      streamUrl: '',
      username: '',
      password: '',
      resolution: '1920x1080',
      frameRate: 30,
      enableAudio: false,
      enableNightVision: true,
      enableMotionDetection: true,
      enableRecording: true,
      description: ''
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-950 border border-zinc-900 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-zinc-900 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-blue-600/20 rounded-lg">
              <Plus className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-medium text-white">Add New Camera</h2>
              <p className="text-sm text-zinc-500">Connect a new camera to your surveillance network</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Steps */}
        <div className="px-6 py-4 border-b border-zinc-900">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
                    currentStep >= step.id
                      ? "bg-blue-600 text-white"
                      : "bg-zinc-800 text-zinc-400"
                  )}>
                    {currentStep > step.id ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      step.id
                    )}
                  </div>
                  <div>
                    <div className={cn(
                      "text-sm font-medium",
                      currentStep >= step.id ? "text-white" : "text-zinc-400"
                    )}>
                      {step.title}
                    </div>
                    <div className="text-xs text-zinc-500">{step.description}</div>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className={cn(
                    "w-16 h-0.5 mx-4",
                    currentStep > step.id ? "bg-blue-600" : "bg-zinc-800"
                  )} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Step 1: Camera Type Selection */}
          {currentStep === 1 && (
            <div>
              <h3 className="text-lg font-medium text-white mb-6">Select Camera Stream Type</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {streamTypes.map((type) => {
                  const IconComponent = type.icon;
                  return (
                    <MinimalCard
                      key={type.id}
                      className="cursor-pointer hover:scale-[1.02] transition-all duration-300 group"
                      onClick={() => handleStreamTypeSelect(type)}
                    >
                      <MinimalCardContent className="p-6">
                        <div className="flex items-start gap-4">
                          <div className="p-3 bg-blue-600/20 rounded-lg group-hover:bg-blue-600/30 transition-colors">
                            <IconComponent className="h-6 w-6 text-blue-400" />
                          </div>
                          <div className="flex-1">
                            <h4 className="text-white font-medium mb-1 group-hover:text-blue-300 transition-colors">
                              {type.name}
                            </h4>
                            <p className="text-zinc-400 text-sm mb-3">{type.description}</p>
                            <div className="space-y-1">
                              <div className="text-xs text-zinc-500">Examples:</div>
                              {type.examples.map((example, index) => (
                                <div key={index} className="text-xs text-zinc-400 font-mono bg-zinc-900/50 px-2 py-1 rounded">
                                  {example}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </MinimalCardContent>
                    </MinimalCard>
                  );
                })}
              </div>
            </div>
          )}

          {/* Step 2: Connection Configuration */}
          {currentStep === 2 && selectedStreamType && (
            <div>
              <h3 className="text-lg font-medium text-white mb-6">Configure {selectedStreamType.name}</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">Camera Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder="e.g., Main Entrance Camera"
                      className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">Location</label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      placeholder="e.g., Building A - Floor 1"
                      className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">Stream URL</label>
                    <input
                      type="text"
                      value={formData.streamUrl}
                      onChange={(e) => handleInputChange('streamUrl', e.target.value)}
                      placeholder={selectedStreamType.urlFormat}
                      className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                  </div>

                  {selectedStreamType.id === 'rtsp' && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">Username</label>
                        <input
                          type="text"
                          value={formData.username}
                          onChange={(e) => handleInputChange('username', e.target.value)}
                          placeholder="admin"
                          className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">Password</label>
                        <input
                          type="password"
                          value={formData.password}
                          onChange={(e) => handleInputChange('password', e.target.value)}
                          placeholder="••••••••"
                          className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <MinimalCard>
                    <MinimalCardContent className="p-4">
                      <h4 className="text-white font-medium mb-3">Stream Information</h4>
                      <div className="space-y-3 text-sm">
                        <div className="flex items-center gap-2">
                          <Video className="h-4 w-4 text-blue-400" />
                          <span className="text-zinc-400">Type:</span>
                          <span className="text-white">{selectedStreamType.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Network className="h-4 w-4 text-blue-400" />
                          <span className="text-zinc-400">Default Port:</span>
                          <span className="text-white">{selectedStreamType.defaultPort || 'N/A'}</span>
                        </div>
                        <div className="border-t border-zinc-800 pt-3">
                          <h5 className="text-zinc-400 text-xs mb-2">EXAMPLE URLS:</h5>
                          {selectedStreamType.examples.map((example, index) => (
                            <div key={index} className="text-xs text-zinc-500 font-mono bg-zinc-900/50 px-2 py-1 rounded mb-1">
                              {example}
                            </div>
                          ))}
                        </div>
                      </div>
                    </MinimalCardContent>
                  </MinimalCard>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Camera Settings */}
          {currentStep === 3 && (
            <div>
              <h3 className="text-lg font-medium text-white mb-6">Camera Settings</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-zinc-400 mb-2">Resolution</label>
                      <select
                        value={formData.resolution}
                        onChange={(e) => handleInputChange('resolution', e.target.value)}
                        className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
                      >
                        {resolutions.map((res) => (
                          <option key={res.value} value={res.value}>{res.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-400 mb-2">Frame Rate</label>
                      <select
                        value={formData.frameRate}
                        onChange={(e) => handleInputChange('frameRate', parseInt(e.target.value))}
                        className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
                      >
                        {frameRates.map((rate) => (
                          <option key={rate.value} value={rate.value}>{rate.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">Description (Optional)</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      placeholder="Additional information about this camera..."
                      rows={3}
                      className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors resize-none"
                    />
                  </div>
                </div>

                <div>
                  <h4 className="text-white font-medium mb-4">Features</h4>
                  <div className="space-y-3">
                    {[
                      { key: 'enableAudio', label: 'Audio Recording', icon: Volume2 },
                      { key: 'enableNightVision', label: 'Night Vision', icon: Eye },
                      { key: 'enableMotionDetection', label: 'Motion Detection', icon: Zap },
                      { key: 'enableRecording', label: 'Video Recording', icon: Video }
                    ].map((feature) => {
                      const IconComponent = feature.icon;
                      return (
                        <div key={feature.key} className="flex items-center justify-between p-3 bg-zinc-900/50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <IconComponent className="h-4 w-4 text-blue-400" />
                            <span className="text-white text-sm">{feature.label}</span>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={formData[feature.key]}
                              onChange={(e) => handleInputChange(feature.key, e.target.checked)}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Test & Save */}
          {currentStep === 4 && (
            <div>
              <h3 className="text-lg font-medium text-white mb-6">Test Connection & Save</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <MinimalCard>
                    <MinimalCardContent className="p-6">
                      <h4 className="text-white font-medium mb-4">Camera Summary</h4>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-zinc-400">Name:</span>
                          <span className="text-white">{formData.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-400">Location:</span>
                          <span className="text-white">{formData.location}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-400">Stream Type:</span>
                          <span className="text-white">{selectedStreamType?.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-400">Resolution:</span>
                          <span className="text-white">{formData.resolution}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-400">Frame Rate:</span>
                          <span className="text-white">{formData.frameRate} FPS</span>
                        </div>
                      </div>
                    </MinimalCardContent>
                  </MinimalCard>
                </div>

                <div>
                  <MinimalCard>
                    <MinimalCardContent className="p-6">
                      <h4 className="text-white font-medium mb-4">Connection Test</h4>
                      
                      {!connectionStatus && !isTestingConnection && (
                        <div className="text-center py-8">
                          <TestTube2 className="h-12 w-12 text-zinc-600 mx-auto mb-4" />
                          <p className="text-zinc-500 mb-4">Test the camera connection before adding</p>
                          <button
                            onClick={testConnection}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-600/30 mx-auto hover:bg-blue-600/30 transition-colors"
                          >
                            <Play className="h-4 w-4" />
                            Test Connection
                          </button>
                        </div>
                      )}

                      {isTestingConnection && (
                        <div className="text-center py-8">
                          <Loader className="h-12 w-12 text-blue-400 mx-auto mb-4 animate-spin" />
                          <p className="text-white">Testing connection...</p>
                          <p className="text-zinc-500 text-sm">This may take a few seconds</p>
                        </div>
                      )}

                      {connectionStatus && (
                        <div className={`p-4 rounded-lg border ${
                          connectionStatus.status === 'success' 
                            ? 'bg-emerald-950/50 border-emerald-900' 
                            : 'bg-red-950/50 border-red-900'
                        }`}>
                          <div className="flex items-center gap-3 mb-3">
                            {connectionStatus.status === 'success' ? (
                              <CheckCircle className="h-5 w-5 text-emerald-400" />
                            ) : (
                              <AlertTriangle className="h-5 w-5 text-red-400" />
                            )}
                            <span className={`font-medium ${
                              connectionStatus.status === 'success' ? 'text-emerald-400' : 'text-red-400'
                            }`}>
                              {connectionStatus.message}
                            </span>
                          </div>
                          {connectionStatus.details && (
                            <div className="space-y-2 text-sm">
                              {Object.entries(connectionStatus.details).map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                  <span className="text-zinc-400 capitalize">{key}:</span>
                                  <span className="text-white">{value}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </MinimalCardContent>
                  </MinimalCard>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-zinc-900 flex items-center justify-between">
          <button
            onClick={() => currentStep > 1 ? setCurrentStep(currentStep - 1) : onClose()}
            className="px-4 py-2 text-zinc-400 hover:text-white transition-colors"
          >
            {currentStep > 1 ? 'Previous' : 'Cancel'}
          </button>
          
          <div className="flex gap-3">
            {currentStep < 4 ? (
              <button
                onClick={() => setCurrentStep(currentStep + 1)}
                disabled={
                  (currentStep === 1 && !selectedStreamType) ||
                  (currentStep === 2 && (!formData.name || !formData.location || !formData.streamUrl))
                }
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-lg transition-colors"
              >
                Next
              </button>
            ) : (
              <>
                <button
                  onClick={testConnection}
                  disabled={isTestingConnection}
                  className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors disabled:opacity-50"
                >
                  {isTestingConnection ? 'Testing...' : 'Test Again'}
                </button>
                <button
                  onClick={handleAddCamera}
                  disabled={!connectionStatus || connectionStatus.status !== 'success'}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-lg transition-colors"
                >
                  Add Camera
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};