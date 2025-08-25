import React, { useState, useEffect } from 'react';
import {
  Bell,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  EyeOff,
  Filter,
  Search,
  Settings,
  User,
  Camera,
  MapPin,
  Mail,
  Phone,
  Smartphone,
  Volume2,
  VolumeX,
  Star,
  Shield,
  Activity,
  Trash2,
  Archive,
  MoreVertical,
  Calendar,
  Users,
  AlertCircle,
  XCircle,
  Zap,
  Info,
  ExternalLink,
  Download,
  RefreshCw
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardTitle } from '@/components/ui/MinimalCard';

export const NotificationsPage = ({ onNavigate }) => {
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNotifications, setSelectedNotifications] = useState([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState(null);

  // Mock notifications data
  const [notifications, setNotifications] = useState([
    {
      id: 'ALR-001',
      type: 'high_profile_detection',
      priority: 'critical',
      status: 'unread',
      timestamp: '2 minutes ago',
      title: 'High-Profile Person Detected',
      description: 'Shubham Kumar (VIP) detected at Main Entrance',
      location: 'Camera 1 - Main Entrance',
      personName: 'Shubham Kumar',
      personId: 'EMP-001',
      confidence: 96.8,
      image: '/api/placeholder/64/64',
      actions: ['email_sent', 'sms_sent', 'dashboard_alert'],
      cameraId: 'CAM-001',
      deliveryStatus: {
        email: 'sent',
        sms: 'sent',
        webhook: 'pending',
        dashboard: 'delivered'
      }
    },
    {
      id: 'ALR-002',
      type: 'unauthorized_access',
      priority: 'high',
      status: 'unread',
      timestamp: '15 minutes ago',
      title: 'Unauthorized Access Attempt',
      description: 'Unknown person detected in restricted area',
      location: 'Camera 5 - Server Room',
      confidence: 0,
      image: '/api/placeholder/64/64',
      actions: ['security_notified'],
      cameraId: 'CAM-005',
      deliveryStatus: {
        email: 'sent',
        sms: 'failed',
        dashboard: 'delivered'
      }
    },
    {
      id: 'ALR-003',
      type: 'system_alert',
      priority: 'medium',
      status: 'read',
      timestamp: '1 hour ago',
      title: 'Camera Connection Issue',
      description: 'Camera 3 experiencing connectivity problems',
      location: 'Camera 3 - Parking Lot',
      actions: ['maintenance_notified'],
      cameraId: 'CAM-003',
      deliveryStatus: {
        email: 'sent',
        dashboard: 'delivered'
      }
    },
    {
      id: 'ALR-004',
      type: 'recognition_alert',
      priority: 'low',
      status: 'read',
      timestamp: '2 hours ago',
      title: 'Low Confidence Detection',
      description: 'Person detection with confidence below threshold',
      location: 'Camera 2 - Reception',
      confidence: 45.2,
      image: '/api/placeholder/64/64',
      actions: ['review_required'],
      cameraId: 'CAM-002',
      deliveryStatus: {
        dashboard: 'delivered'
      }
    }
  ]);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'text-red-400 bg-red-950/50 border-red-600/30';
      case 'high': return 'text-orange-400 bg-orange-950/50 border-orange-600/30';
      case 'medium': return 'text-yellow-400 bg-yellow-950/50 border-yellow-600/30';
      case 'low': return 'text-blue-400 bg-blue-950/50 border-blue-600/30';
      default: return 'text-zinc-400 bg-zinc-950/50 border-zinc-600/30';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'high_profile_detection': return <Star className="h-4 w-4" />;
      case 'unauthorized_access': return <Shield className="h-4 w-4" />;
      case 'system_alert': return <AlertTriangle className="h-4 w-4" />;
      case 'recognition_alert': return <Eye className="h-4 w-4" />;
      default: return <Bell className="h-4 w-4" />;
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    const matchesSearch = notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         notification.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         notification.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || notification.status === filterStatus;
    const matchesPriority = filterPriority === 'all' || notification.priority === filterPriority;
    const matchesType = filterType === 'all' || notification.type === filterType;
    return matchesSearch && matchesStatus && matchesPriority && matchesType;
  });

  const markAsRead = (notificationId) => {
    setNotifications(prev => prev.map(notif => 
      notif.id === notificationId ? { ...notif, status: 'read' } : notif
    ));
  };

  const markAsArchived = (notificationId) => {
    setNotifications(prev => prev.map(notif => 
      notif.id === notificationId ? { ...notif, status: 'archived' } : notif
    ));
  };

  const deleteNotification = (notificationId) => {
    setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(notif => ({ ...notif, status: 'read' })));
  };

  const unreadCount = notifications.filter(n => n.status === 'unread').length;
  const criticalCount = notifications.filter(n => n.priority === 'critical' && n.status === 'unread').length;

  return (
    <>
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="inline-block bg-orange-600/10 border border-orange-600/20 text-orange-400 px-4 py-2 rounded-full text-xs font-medium mb-10 tracking-wider">
          NOTIFICATIONS
        </div>
        <h1 className="text-5xl lg:text-6xl font-normal mb-8 tracking-tight leading-tight">
          Alert <span className="italic text-zinc-600 font-light">Management</span>
        </h1>
        <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
          Monitor and manage security alerts from surveillance cameras with real-time notifications and automated response systems.
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-orange-600/20 rounded-lg">
                <Bell className="h-6 w-6 text-orange-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{unreadCount}</div>
                <div className="text-sm text-zinc-400">Unread Alerts</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-600/20 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-red-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{criticalCount}</div>
                <div className="text-sm text-zinc-400">Critical Alerts</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-emerald-600/20 rounded-lg">
                <CheckCircle className="h-6 w-6 text-emerald-400" />
              </div>
              <div>
                <div className="text-2xl font-bold text-white">
                  {notifications.filter(n => n.deliveryStatus?.email === 'sent').length}
                </div>
                <div className="text-sm text-zinc-400">Delivered</div>
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
                  {notifications.filter(n => n.type === 'high_profile_detection').length}
                </div>
                <div className="text-sm text-zinc-400">VIP Alerts</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Filters and Controls */}
      <div className="flex flex-col lg:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search notifications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-orange-500 transition-colors"
          />
        </div>
        
        <div className="flex gap-4">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-orange-500 transition-colors"
          >
            <option value="all">All Status</option>
            <option value="unread">Unread</option>
            <option value="read">Read</option>
            <option value="archived">Archived</option>
          </select>

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-orange-500 transition-colors"
          >
            <option value="all">All Priority</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-orange-500 transition-colors"
          >
            <option value="all">All Types</option>
            <option value="high_profile_detection">VIP Detection</option>
            <option value="unauthorized_access">Unauthorized Access</option>
            <option value="system_alert">System Alert</option>
            <option value="recognition_alert">Recognition Alert</option>
          </select>

          <button
            onClick={markAllAsRead}
            className="flex items-center gap-2 px-4 py-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 rounded-lg border border-emerald-600/30 transition-colors"
          >
            <CheckCircle className="h-4 w-4" />
            Mark All Read
          </button>

          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center gap-2 px-4 py-3 bg-zinc-800/50 hover:bg-zinc-800 text-zinc-400 rounded-lg border border-zinc-700 transition-colors"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <MinimalCard className="mb-8">
          <MinimalCardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Settings className="h-5 w-5 text-orange-400" />
              <h3 className="text-lg font-medium text-white">Notification Settings</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Sound Notifications</div>
                  <div className="text-sm text-zinc-400">Play sound for new alerts</div>
                </div>
                <button
                  onClick={() => setSoundEnabled(!soundEnabled)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    soundEnabled 
                      ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/30' 
                      : 'bg-zinc-800/50 text-zinc-400 border border-zinc-700'
                  }`}
                >
                  {soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
                  {soundEnabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-medium">Auto Refresh</div>
                  <div className="text-sm text-zinc-400">Automatically refresh notifications</div>
                </div>
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    autoRefresh 
                      ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/30' 
                      : 'bg-zinc-800/50 text-zinc-400 border border-zinc-700'
                  }`}
                >
                  <RefreshCw className="h-4 w-4" />
                  {autoRefresh ? 'Enabled' : 'Disabled'}
                </button>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      )}

      {/* Notifications List */}
      <div className="space-y-4">
        {filteredNotifications.length === 0 ? (
          <MinimalCard>
            <MinimalCardContent className="p-12 text-center">
              <div className="p-4 bg-zinc-800/50 rounded-lg mb-4 w-fit mx-auto">
                <Bell className="h-8 w-8 text-zinc-400" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">No Notifications</h3>
              <p className="text-zinc-400">No notifications match your current filters.</p>
            </MinimalCardContent>
          </MinimalCard>
        ) : (
          filteredNotifications.map((notification) => (
            <MinimalCard 
              key={notification.id} 
              className={`cursor-pointer transition-all duration-300 hover:scale-[1.01] ${
                notification.status === 'unread' ? 'ring-1 ring-orange-500/30 bg-orange-950/10' : ''
              }`}
              onClick={() => {
                setSelectedNotification(notification);
                if (notification.status === 'unread') markAsRead(notification.id);
              }}
            >
              <MinimalCardContent className="p-6">
                <div className="flex items-start gap-4">
                  {/* Notification Icon & Image */}
                  <div className="flex-shrink-0">
                    {notification.image ? (
                      <div className="relative">
                        <img
                          src={notification.image}
                          alt="Detection"
                          className="w-16 h-16 rounded-lg object-cover"
                        />
                        <div className="absolute -top-2 -right-2 p-1 bg-zinc-900 rounded-full">
                          {getTypeIcon(notification.type)}
                        </div>
                      </div>
                    ) : (
                      <div className={`p-4 rounded-lg ${
                        notification.priority === 'critical' ? 'bg-red-600/20' :
                        notification.priority === 'high' ? 'bg-orange-600/20' :
                        notification.priority === 'medium' ? 'bg-yellow-600/20' :
                        'bg-blue-600/20'
                      }`}>
                        {getTypeIcon(notification.type)}
                      </div>
                    )}
                  </div>

                  {/* Notification Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className="text-white font-medium mb-1">{notification.title}</h3>
                        <p className="text-zinc-400 text-sm mb-2">{notification.description}</p>
                        
                        <div className="flex items-center gap-4 text-xs text-zinc-500">
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {notification.location}
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {notification.timestamp}
                          </div>
                          {notification.confidence && (
                            <div className="flex items-center gap-1">
                              <Activity className="h-3 w-3" />
                              {notification.confidence}% confidence
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <div className={`px-2 py-1 rounded text-xs border ${getPriorityColor(notification.priority)}`}>
                          {notification.priority.toUpperCase()}
                        </div>
                        {notification.status === 'unread' && (
                          <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                        )}
                      </div>
                    </div>

                    {/* Delivery Status */}
                    {notification.deliveryStatus && (
                      <div className="flex items-center gap-3 mt-3 pt-3 border-t border-zinc-800">
                        <span className="text-xs text-zinc-500">Delivery:</span>
                        {Object.entries(notification.deliveryStatus).map(([channel, status]) => (
                          <div key={channel} className="flex items-center gap-1">
                            {channel === 'email' && <Mail className="h-3 w-3" />}
                            {channel === 'sms' && <Smartphone className="h-3 w-3" />}
                            {channel === 'webhook' && <ExternalLink className="h-3 w-3" />}
                            {channel === 'dashboard' && <Activity className="h-3 w-3" />}
                            <span className={`text-xs ${
                              status === 'sent' || status === 'delivered' ? 'text-emerald-400' :
                              status === 'failed' ? 'text-red-400' :
                              'text-yellow-400'
                            }`}>
                              {status}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Actions */}
                    {notification.actions && notification.actions.length > 0 && (
                      <div className="flex items-center gap-2 mt-3">
                        <span className="text-xs text-zinc-500">Actions:</span>
                        {notification.actions.map((action, index) => (
                          <span key={index} className="px-2 py-1 bg-zinc-800/50 text-zinc-300 rounded text-xs">
                            {action.replace(/_/g, ' ')}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Quick Actions */}
                  <div className="flex-shrink-0 flex items-center gap-2">
                    {notification.status === 'unread' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          markAsRead(notification.id);
                        }}
                        className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
                        title="Mark as read"
                      >
                        <Eye className="h-4 w-4 text-zinc-400" />
                      </button>
                    )}
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        markAsArchived(notification.id);
                      }}
                      className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
                      title="Archive"
                    >
                      <Archive className="h-4 w-4 text-zinc-400" />
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNotification(notification.id);
                      }}
                      className="p-2 hover:bg-red-600/20 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4 text-red-400" />
                    </button>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          ))
        )}
      </div>

      {/* Notification Detail Modal */}
      {selectedNotification && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <MinimalCard className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <MinimalCardContent className="p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-normal text-white mb-2">{selectedNotification.title}</h2>
                  <div className={`inline-block px-3 py-1 rounded text-sm border ${getPriorityColor(selectedNotification.priority)}`}>
                    {selectedNotification.priority.toUpperCase()} PRIORITY
                  </div>
                </div>
                <button
                  onClick={() => setSelectedNotification(null)}
                  className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
                >
                  <XCircle className="h-6 w-6 text-zinc-400" />
                </button>
              </div>

              {selectedNotification.image && (
                <div className="mb-6">
                  <img
                    src={selectedNotification.image}
                    alt="Detection"
                    className="w-full h-48 object-cover rounded-lg"
                  />
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <h3 className="text-white font-medium mb-2">Description</h3>
                  <p className="text-zinc-400">{selectedNotification.description}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-white font-medium mb-2">Location</h4>
                    <p className="text-zinc-400">{selectedNotification.location}</p>
                  </div>
                  <div>
                    <h4 className="text-white font-medium mb-2">Timestamp</h4>
                    <p className="text-zinc-400">{selectedNotification.timestamp}</p>
                  </div>
                  {selectedNotification.confidence && (
                    <div>
                      <h4 className="text-white font-medium mb-2">Confidence</h4>
                      <p className="text-zinc-400">{selectedNotification.confidence}%</p>
                    </div>
                  )}
                  {selectedNotification.personName && (
                    <div>
                      <h4 className="text-white font-medium mb-2">Person</h4>
                      <p className="text-zinc-400">{selectedNotification.personName}</p>
                    </div>
                  )}
                </div>

                {selectedNotification.deliveryStatus && (
                  <div>
                    <h4 className="text-white font-medium mb-2">Delivery Status</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(selectedNotification.deliveryStatus).map(([channel, status]) => (
                        <div key={channel} className="flex items-center justify-between p-3 bg-zinc-950/30 rounded-lg">
                          <span className="text-zinc-300 capitalize">{channel}</span>
                          <span className={`text-sm ${
                            status === 'sent' || status === 'delivered' ? 'text-emerald-400' :
                            status === 'failed' ? 'text-red-400' :
                            'text-yellow-400'
                          }`}>
                            {status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-4 mt-8 pt-6 border-t border-zinc-800">
                <button
                  onClick={() => {
                    if (selectedNotification.cameraId) {
                      onNavigate('cameras');
                    }
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors"
                >
                  <Camera className="h-4 w-4" />
                  View Camera
                </button>
                
                {selectedNotification.personId && (
                  <button
                    onClick={() => {
                      onNavigate('persons');
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 rounded-lg border border-emerald-600/30 transition-colors"
                  >
                    <User className="h-4 w-4" />
                    View Person
                  </button>
                )}
                
                <button
                  onClick={() => setSelectedNotification(null)}
                  className="flex items-center gap-2 px-4 py-2 bg-zinc-800/50 hover:bg-zinc-800 text-zinc-400 rounded-lg border border-zinc-700 transition-colors ml-auto"
                >
                  Close
                </button>
              </div>
            </MinimalCardContent>
          </MinimalCard>
        </div>
      )}
    </>
  );
};