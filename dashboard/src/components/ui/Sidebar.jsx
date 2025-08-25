import React from 'react';
import {
  Home,
  Camera,
  Users,
  BarChart3,
  Upload,
  UserPlus,
  Bell,
  Monitor,
  Settings,
  Shield,
  User,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export const Sidebar = ({ currentPage, onNavigate, isCollapsed, onToggleCollapse }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, badge: null },
    { id: 'cameras', label: 'Live Cameras', icon: Camera, badge: '24' },
    { id: 'persons', label: 'Enrolled Persons', icon: Users, badge: '1,247' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, badge: null },
    { id: 'upload', label: 'Media Analysis', icon: Upload, badge: null },
    { id: 'enroll', label: 'Add Person', icon: UserPlus, badge: null },
    { id: 'notifications', label: 'Notifications', icon: Bell, badge: '3' },
    { id: 'monitoring', label: 'System Monitor', icon: Monitor, badge: null },
    { id: 'settings', label: 'Settings', icon: Settings, badge: null }
  ];

  return (
    <div className={`fixed left-0 top-0 h-full bg-zinc-950/80 border-r border-zinc-900/50 backdrop-blur-sm transition-all duration-300 z-40 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Logo */}
      <div className="p-6 border-b border-zinc-900/50">
        <div className="flex items-center gap-3">
          <Shield className="h-8 w-8 text-blue-500 flex-shrink-0" />
          {!isCollapsed && <span className="text-xl font-medium text-white">FaceGuard</span>}
        </div>
      </div>

      {/* Toggle Button */}
      <button
        onClick={onToggleCollapse}
        className="absolute -right-3 top-20 w-6 h-6 bg-zinc-800 border border-zinc-700 rounded-full flex items-center justify-center hover:bg-zinc-700 transition-colors"
      >
        {isCollapsed ? (
          <ChevronRight className="h-3 w-3 text-zinc-400" />
        ) : (
          <ChevronLeft className="h-3 w-3 text-zinc-400" />
        )}
      </button>

      {/* Menu Items */}
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const IconComponent = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 ${
                isActive 
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-600/30' 
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
              }`}
              title={isCollapsed ? item.label : undefined}
            >
              <IconComponent className="h-5 w-5 flex-shrink-0" />
              {!isCollapsed && (
                <>
                  <span className="text-sm font-medium flex-1 text-left">{item.label}</span>
                  {item.badge && (
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      isActive 
                        ? 'bg-blue-500/20 text-blue-300' 
                        : 'bg-zinc-800 text-zinc-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </button>
          );
        })}
      </nav>

      {/* User Profile */}
      {!isCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-zinc-900/50">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900/30">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white truncate">Admin User</div>
              <div className="text-xs text-zinc-400 truncate">Security Admin</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};