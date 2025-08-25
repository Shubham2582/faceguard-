import React, { useState, useEffect } from 'react';
import {
  Camera,
  Plus,
  Play,
  Pause,
  Settings,
  MapPin,
  Clock,
  Users,
  Activity,
  AlertTriangle,
  Eye,
  Signal,
  Wifi,
  WifiOff,
  MoreVertical,
  Grid,
  List,
  Search,
  Filter,
  Monitor,
  Video,
  Zap
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardImage, MinimalCardTitle } from '@/components/ui/MinimalCard';
import { CameraFeed } from '@/components/ui/CameraFeed';
import { LiveRecognitionOverlay } from '@/components/ui/LiveRecognitionOverlay';
import { CameraDetailModal } from '@/components/ui/CameraDetailModal';
import { AddCameraModal } from '@/components/ui/AddCameraModal';
import { cn } from '@/lib/utils';

// Mock camera data - will be replaced with real API data
const mockCameras = [
  {
    id: 'CAM-001',
    name: 'Main Entrance',
    location: 'Building A - Floor 1',
    status: 'active',
    resolution: '1920x1080',
    fps: 30,
    lastSeen: '2 seconds ago',
    recognitions: [
      { person: 'Shubham Kumar', confidence: '96.8%', timestamp: '2 min ago', x: 120, y: 80 },
      { person: 'Priya Singh', confidence: '94.2%', timestamp: '5 min ago', x: 300, y: 150 }
    ],
    stream: 'rtsp://camera1.local/stream',
    uptime: '99.8%',
    alerts: 2
  },
  {
    id: 'CAM-002',
    name: 'Reception Area',
    location: 'Building A - Ground Floor',
    status: 'active',
    resolution: '1920x1080',
    fps: 25,
    lastSeen: '1 second ago',
    recognitions: [
      { person: 'Rajesh Patel', confidence: '98.1%', timestamp: '1 min ago', x: 200, y: 120 }
    ],
    stream: 'rtsp://camera2.local/stream',
    uptime: '98.5%',
    alerts: 0
  },
  {
    id: 'CAM-003',
    name: 'Parking Area',
    location: 'Building A - Outdoor',
    status: 'warning',
    resolution: '1280x720',
    fps: 20,
    lastSeen: '30 seconds ago',
    recognitions: [],
    stream: 'rtsp://camera3.local/stream',
    uptime: '95.2%',
    alerts: 1
  },
  {
    id: 'CAM-004',
    name: 'Server Room',
    location: 'Building B - Floor 2',
    status: 'offline',
    resolution: '1920x1080',
    fps: 0,
    lastSeen: '2 hours ago',
    recognitions: [],
    stream: null,
    uptime: '87.3%',
    alerts: 5
  },
  {
    id: 'CAM-005',
    name: 'Cafeteria',
    location: 'Building A - Floor 2',
    status: 'active',
    resolution: '1920x1080',
    fps: 30,
    lastSeen: '1 second ago',
    recognitions: [
      { person: 'Sarah Johnson', confidence: '92.4%', timestamp: '3 min ago', x: 150, y: 200 },
      { person: 'Mike Chen', confidence: '89.7%', timestamp: '7 min ago', x: 400, y: 100 }
    ],
    stream: 'rtsp://camera5.local/stream',
    uptime: '99.1%',
    alerts: 0
  },
  {
    id: 'CAM-006',
    name: 'Loading Dock',
    location: 'Building C - Ground Floor',
    status: 'active',
    resolution: '1920x1080',
    fps: 15,
    lastSeen: '5 seconds ago',
    recognitions: [],
    stream: 'rtsp://camera6.local/stream',
    uptime: '96.7%',
    alerts: 0
  }
];

const getStatusColor = (status) => {
  switch (status) {
    case 'active':
      return 'bg-emerald-950/50 text-emerald-400 border-emerald-900';
    case 'warning':
      return 'bg-yellow-950/50 text-yellow-400 border-yellow-900';
    case 'offline':
      return 'bg-red-950/50 text-red-400 border-red-900';
    default:
      return 'bg-zinc-950/50 text-zinc-400 border-zinc-900';
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case 'active':
      return <Wifi className="h-4 w-4 text-emerald-400" />;
    case 'warning':
      return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
    case 'offline':
      return <WifiOff className="h-4 w-4 text-red-400" />;
    default:
      return <Signal className="h-4 w-4 text-zinc-400" />;
  }
};

export const CamerasPage = ({ onNavigate }) => {
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [cameras, setCameras] = useState(mockCameras);

  const handleCameraClick = (camera) => {
    setSelectedCamera(camera);
    setDetailModalOpen(true);
  };

  const handleAddCamera = (newCamera) => {
    setCameras(prev => [...prev, newCamera]);
    setShowAddModal(false);
  };

  const filteredCameras = cameras.filter(camera => {
    const matchesSearch = camera.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         camera.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || camera.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const activeCameras = cameras.filter(cam => cam.status === 'active').length;
  const totalRecognitions = cameras.reduce((sum, cam) => sum + cam.recognitions.length, 0);
  const totalAlerts = cameras.reduce((sum, cam) => sum + cam.alerts, 0);

  return (
    <>
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="inline-block bg-blue-600/10 border border-blue-600/20 text-blue-400 px-3 py-1.5 rounded-full text-xs font-medium mb-8 tracking-wider">
          LIVE MONITORING
        </div>
        <h1 className="text-5xl lg:text-6xl font-normal mb-6 tracking-tight leading-tight">
          Camera <span className="italic text-zinc-600 font-light">Network</span>
        </h1>
        <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
          Real-time surveillance monitoring with advanced facial recognition capabilities across all connected camera feeds.
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <MinimalCard className="group hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-emerald-600 to-emerald-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Camera className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium px-3 py-1.5 rounded-full text-emerald-400 bg-emerald-400/10">
                +{activeCameras}
              </span>
            </div>
            <div>
              <h3 className="text-3xl font-normal mb-2 text-white group-hover:text-white/90 transition-colors">
                {activeCameras}
              </h3>
              <p className="text-zinc-500 group-hover:text-zinc-400 transition-colors">
                Active Cameras
              </p>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="group hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-blue-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Eye className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium px-3 py-1.5 rounded-full text-blue-400 bg-blue-400/10">
                Live
              </span>
            </div>
            <div>
              <h3 className="text-3xl font-normal mb-2 text-white group-hover:text-white/90 transition-colors">
                {totalRecognitions}
              </h3>
              <p className="text-zinc-500 group-hover:text-zinc-400 transition-colors">
                Active Detections
              </p>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="group hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-purple-600 to-purple-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium px-3 py-1.5 rounded-full text-purple-400 bg-purple-400/10">
                99.2%
              </span>
            </div>
            <div>
              <h3 className="text-3xl font-normal mb-2 text-white group-hover:text-white/90 transition-colors">
                98.5%
              </h3>
              <p className="text-zinc-500 group-hover:text-zinc-400 transition-colors">
                Network Uptime
              </p>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="group hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-orange-600 to-orange-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                <AlertTriangle className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium px-3 py-1.5 rounded-full text-orange-400 bg-orange-400/10">
                {totalAlerts > 0 ? `+${totalAlerts}` : '0'}
              </span>
            </div>
            <div>
              <h3 className="text-3xl font-normal mb-2 text-white group-hover:text-white/90 transition-colors">
                {totalAlerts}
              </h3>
              <p className="text-zinc-500 group-hover:text-zinc-400 transition-colors">
                Active Alerts
              </p>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Controls */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search cameras by name or location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>
        <div className="flex gap-4">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="warning">Warning</option>
            <option value="offline">Offline</option>
          </select>
          
          <div className="flex bg-zinc-950/50 border border-zinc-900 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                "p-2 rounded transition-colors",
                viewMode === 'grid' 
                  ? 'bg-blue-600/20 text-blue-400' 
                  : 'text-zinc-400 hover:text-white'
              )}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                "p-2 rounded transition-colors",
                viewMode === 'list' 
                  ? 'bg-blue-600/20 text-blue-400' 
                  : 'text-zinc-400 hover:text-white'
              )}
            >
              <List className="h-4 w-4" />
            </button>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add Camera
          </button>
        </div>
      </div>

      {/* Camera Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-16">
          {filteredCameras.map((camera) => (
            <MinimalCard 
              key={camera.id} 
              className="group hover:scale-[1.02] transition-all duration-300 overflow-hidden cursor-pointer transform hover:shadow-2xl hover:shadow-blue-500/10"
              onClick={() => handleCameraClick(camera)}
            >
              {/* Live Feed Area */}
              <div className="relative bg-zinc-900 aspect-video">
                {camera.status === 'active' ? (
                  <>
                    {/* Placeholder for video stream */}
                    <div className="w-full h-full bg-gradient-to-br from-zinc-800 to-zinc-900 flex items-center justify-center">
                      <div className="text-center">
                        <Video className="h-12 w-12 text-zinc-600 mx-auto mb-2" />
                        <p className="text-zinc-500 text-sm">Live Stream</p>
                        <p className="text-zinc-600 text-xs">{camera.resolution} • {camera.fps}fps</p>
                      </div>
                    </div>
                    
                    {/* Recognition Overlays */}
                    {camera.recognitions.map((recognition, index) => (
                      <div
                        key={index}
                        className="absolute"
                        style={{ left: recognition.x, top: recognition.y }}
                      >
                        <div className="bg-emerald-600/90 text-white px-2 py-1 rounded text-xs font-medium shadow-lg">
                          {recognition.person} ({recognition.confidence})
                        </div>
                      </div>
                    ))}

                    {/* Live Indicator */}
                    <div className="absolute top-3 left-3 flex items-center gap-2 bg-red-600/90 text-white px-2 py-1 rounded-full text-xs font-medium">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                      LIVE
                    </div>
                  </>
                ) : (
                  <div className="w-full h-full bg-zinc-900/50 flex items-center justify-center">
                    <div className="text-center">
                      {getStatusIcon(camera.status)}
                      <p className="text-zinc-500 text-sm mt-2">
                        {camera.status === 'offline' ? 'Camera Offline' : 'Limited Feed'}
                      </p>
                    </div>
                  </div>
                )}

                {/* Camera Controls */}
                <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors">
                    <Settings className="h-4 w-4" />
                  </button>
                  <button className="p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors">
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <MinimalCardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <MinimalCardTitle className="text-lg mb-1">{camera.name}</MinimalCardTitle>
                    <div className="flex items-center gap-2 text-sm text-zinc-500">
                      <MapPin className="h-3 w-3" />
                      {camera.location}
                    </div>
                  </div>
                  <div className={`px-3 py-1.5 rounded-full text-xs border ${getStatusColor(camera.status)}`}>
                    {camera.status.toUpperCase()}
                  </div>
                </div>

                {/* Recognition List */}
                {camera.recognitions.length > 0 && (
                  <div className="space-y-2 mb-4">
                    <h4 className="text-sm font-medium text-zinc-400">Recent Detections</h4>
                    {camera.recognitions.slice(0, 2).map((recognition, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-zinc-900/30 rounded">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                          <span className="text-sm text-white">{recognition.person}</span>
                        </div>
                        <div className="text-xs text-zinc-500">{recognition.timestamp}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Camera Stats */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-zinc-800">
                  <div className="text-center">
                    <div className="text-sm font-medium text-white">{camera.uptime}</div>
                    <div className="text-xs text-zinc-500">Uptime</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-medium text-white">{camera.recognitions.length}</div>
                    <div className="text-xs text-zinc-500">Active</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-medium text-white">{camera.alerts}</div>
                    <div className="text-xs text-zinc-500">Alerts</div>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          ))}
        </div>
      ) : (
        /* List View */
        <div className="space-y-4 mb-16">
          {filteredCameras.map((camera) => (
            <MinimalCard key={camera.id} className="group hover:scale-[1.01] transition-all duration-300">
              <MinimalCardContent className="p-6">
                <div className="flex items-center gap-6">
                  {/* Camera Thumbnail */}
                  <div className="relative w-32 h-20 bg-zinc-900 rounded-lg overflow-hidden flex-shrink-0">
                    {camera.status === 'active' ? (
                      <>
                        <div className="w-full h-full bg-gradient-to-br from-zinc-800 to-zinc-900 flex items-center justify-center">
                          <Video className="h-6 w-6 text-zinc-600" />
                        </div>
                        <div className="absolute top-1 left-1 flex items-center gap-1 bg-red-600/90 text-white px-1.5 py-0.5 rounded text-xs">
                          <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                          LIVE
                        </div>
                      </>
                    ) : (
                      <div className="w-full h-full bg-zinc-900/50 flex items-center justify-center">
                        {getStatusIcon(camera.status)}
                      </div>
                    )}
                  </div>

                  {/* Camera Info */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-medium text-white">{camera.name}</h3>
                        <div className="flex items-center gap-2 text-sm text-zinc-500">
                          <MapPin className="h-3 w-3" />
                          {camera.location}
                        </div>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs border ${getStatusColor(camera.status)}`}>
                        {camera.status.toUpperCase()}
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-zinc-400">Resolution</div>
                        <div className="text-white">{camera.resolution}</div>
                      </div>
                      <div>
                        <div className="text-zinc-400">FPS</div>
                        <div className="text-white">{camera.fps}</div>
                      </div>
                      <div>
                        <div className="text-zinc-400">Uptime</div>
                        <div className="text-white">{camera.uptime}</div>
                      </div>
                      <div>
                        <div className="text-zinc-400">Last Seen</div>
                        <div className="text-white">{camera.lastSeen}</div>
                      </div>
                    </div>
                  </div>

                  {/* Recognition Count */}
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">{camera.recognitions.length}</div>
                    <div className="text-xs text-zinc-500">Active Detections</div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-400 hover:text-white transition-colors">
                      <Settings className="h-4 w-4" />
                    </button>
                    <button className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-400 hover:text-white transition-colors">
                      <MoreVertical className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          ))}
        </div>
      )}
      
      {/* Camera Detail Modal */}
      <CameraDetailModal
        cameraId={selectedCamera?.id}
        isOpen={detailModalOpen}
        onClose={() => {
          setDetailModalOpen(false);
          setSelectedCamera(null);
        }}
      />

      {/* Network Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <MinimalCard>
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-600/20 rounded-lg">
                <Monitor className="h-5 w-5 text-blue-400" />
              </div>
              <h2 className="text-xl font-normal text-white">Network Performance</h2>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Total Bandwidth Usage</span>
                <span className="text-white font-medium">2.4 GB/hr</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Average Latency</span>
                <span className="text-white font-medium">12ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Packet Loss</span>
                <span className="text-emerald-400 font-medium">0.01%</span>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard>
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-emerald-600/20 rounded-lg">
                <Zap className="h-5 w-5 text-emerald-400" />
              </div>
              <h2 className="text-xl font-normal text-white">System Performance</h2>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Recognition Processing</span>
                <span className="text-emerald-400 font-medium">157ms avg</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">GPU Utilization</span>
                <span className="text-white font-medium">67%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Memory Usage</span>
                <span className="text-white font-medium">4.2GB / 8GB</span>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Camera Detail Modal */}
      <CameraDetailModal
        cameraId={selectedCamera?.id}
        isOpen={detailModalOpen}
        onClose={() => {
          setDetailModalOpen(false);
          setSelectedCamera(null);
        }}
      />

      {/* Add Camera Modal */}
      <AddCameraModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAddCamera={handleAddCamera}
      />
    </>
  );
};                                                