import React from 'react';
import {
  Camera,
  Users,
  AlertTriangle,
  Eye,
  Settings,
  Activity,
  MapPin,
  Clock,
  Calendar,
  Search,
  Monitor,
  Upload
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardImage, MinimalCardTitle } from '@/components/ui/MinimalCard';
import { SurveillanceShowcase } from './SurveillanceShowcase';
import { statsCards, systemHealth, topCameras, recentDetections } from '@/data/mockData';
import { generateAvatar } from '@/lib/utils';

export const Dashboard = ({ onNavigate }) => {
  return (
    <>
      {/* Hero Section with improved spacing */}
      <div className="pt-4 pb-12">
        <div className="text-center mb-10">
          <div className="inline-block bg-blue-600/10 border border-blue-600/20 text-blue-400 px-4 py-2 rounded-full text-xs font-medium mb-6 tracking-wider">
            SURVEILLANCE
          </div>
          <h1 className="text-5xl lg:text-6xl font-normal mb-5 tracking-tight leading-tight">
            Surveillance Dashboard <span className="italic text-zinc-600 font-light">Overview</span>
          </h1>
          <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
            Real-time monitoring and analytics for your security infrastructure with advanced facial recognition capabilities and comprehensive surveillance management.
          </p>
        </div>

        {/* Interactive Process Showcase with more spacing */}
        <div className="max-w-6xl mx-auto mb-12">
          <SurveillanceShowcase />
        </div>
      </div>

      {/* Stats Cards Grid with improved spacing */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-24">
        {statsCards.map((card, index) => {
          const IconComponent = card.title === "Active Cameras" ? Camera :
                               card.title === "Enrolled Persons" ? Users :
                               card.title === "Today's Detections" ? Eye : AlertTriangle;
          return (
            <MinimalCard key={index} className="hover:scale-[1.02] transition-all duration-300 cursor-pointer group">
              <MinimalCardContent className="p-8">
                <div className="flex items-start justify-between mb-8">
                  <div className={`p-4 bg-gradient-to-r ${card.color} rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <IconComponent className="h-6 w-6 text-white" />
                  </div>
                  <span className={`text-sm font-medium px-3 py-1.5 rounded-full ${
                    card.changeType === 'positive' 
                      ? 'text-emerald-400 bg-emerald-400/10' 
                      : 'text-red-400 bg-red-400/10'
                  }`}>
                    {card.change}
                  </span>
                </div>
                <div>
                  <h3 className="text-4xl font-normal mb-3 text-white group-hover:text-white/90 transition-colors">
                    {card.value}
                  </h3>
                  <p className="text-zinc-500 group-hover:text-zinc-400 transition-colors">
                    {card.title}
                  </p>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          );
        })}
      </div>

      {/* Bento Grid - Management & Detection Table with improved spacing */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-16 mb-24">
        {/* Left Content - Management Info */}
        <div className="lg:col-span-2 space-y-16">
          <div>
            <h2 className="text-3xl font-normal mb-6">Recognition Management</h2>
            <p className="text-zinc-500 leading-relaxed mb-8 text-lg">
              FaceGuard boasts a sophisticated facial recognition system that streamlines and enhances the entire surveillance process, from detection to identification and tracking.
            </p>
            <button className="text-blue-400 hover:text-blue-300 text-sm font-medium tracking-wider">
              LEARN MORE
            </button>
          </div>

          <div>
            <h2 className="text-3xl font-normal mb-6 text-zinc-600">Real-time Tracking</h2>
            <p className="text-zinc-500 leading-relaxed mb-8 text-lg">
              The platform automates the logging of person movements across camera locations, enabling comprehensive tracking and location history for all enrolled individuals.
            </p>
            <button className="text-blue-400 hover:text-blue-300 text-sm font-medium tracking-wider">
              LEARN MORE
            </button>
          </div>

          <div>
            <h2 className="text-3xl font-normal text-zinc-600">Alert Automation</h2>
          </div>
        </div>

        {/* Right Content - Detection Table */}
        <div className="lg:col-span-3">
          <div className="bg-zinc-950/30 border border-zinc-900 rounded-lg overflow-hidden">
            {/* Table Header */}
            <div className="px-8 py-6 border-b border-zinc-900">
              <div className="grid grid-cols-12 gap-6 text-zinc-500 text-xs font-medium">
                <div className="col-span-2 flex items-center space-x-1">
                  <span>Detection ID</span>
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="col-span-4 flex items-center space-x-1">
                  <span>Person</span>
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="col-span-2">Location</div>
                <div className="col-span-2">Date</div>
                <div className="col-span-2 flex items-center space-x-1">
                  <span>Confidence</span>
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Table Body with improved spacing */}
            <div className="divide-y divide-zinc-900">
              {recentDetections.map((detection, index) => (
                <div key={index} className="px-8 py-5 hover:bg-zinc-950/30 transition-colors">
                  <div className="grid grid-cols-12 gap-6 items-center">
                    <div className="col-span-2 text-white text-sm font-medium">{detection.id}</div>
                    <div className="col-span-4">
                      <div className="text-white text-sm font-medium">{detection.personName}</div>
                      <div className="text-zinc-600 text-xs mt-1">{detection.email}</div>
                    </div>
                    <div className="col-span-2">
                      <div className="text-zinc-400 text-sm">{detection.location}</div>
                    </div>
                    <div className="col-span-2 flex items-center space-x-2">
                      <Calendar className="h-3 w-3 text-zinc-600" />
                      <span className="text-zinc-500 text-sm">{detection.timestamp}</span>
                    </div>
                    <div className="col-span-2 text-white text-sm font-medium">{detection.confidence}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

            {/* Bottom Bento Grid - Enhanced with MinimalCards */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
                    {/* System Health - Enhanced MinimalCard */}
                    <MinimalCard className="group hover:scale-[1.02] transition-all duration-300">
                    <MinimalCardContent className="p-8">
                        <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-emerald-600/20 rounded-lg">
                            <Activity className="h-5 w-5 text-emerald-400" />
                        </div>
                        <h2 className="text-xl font-normal text-white">System Health</h2>
                        </div>
                        <div className="space-y-4">
                        {systemHealth.map((system, index) => (
                            <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-zinc-900/30 hover:bg-zinc-900/50 transition-colors group-hover:bg-zinc-900/40">
                            <div className="flex items-center gap-3">
                                <div className={`w-2 h-2 rounded-full ${
                                system.status === 'Active' ? 'bg-emerald-400 animate-pulse' : 'bg-yellow-400'
                                }`} />
                                <div>
                                <div className="text-white text-sm font-medium">{system.name}</div>
                                <div className="text-zinc-600 text-xs">Uptime: {system.uptime}</div>
                                </div>
                            </div>
                            <div className={`px-2 py-1 rounded text-xs border ${
                                system.status === 'Active' 
                                ? 'bg-emerald-950/50 text-emerald-400 border-emerald-900' 
                                : 'bg-yellow-950/50 text-yellow-400 border-yellow-900'
                            }`}>
                                {system.status}
                            </div>
                            </div>
                        ))}
                        </div>
                    </MinimalCardContent>
                    </MinimalCard>

                    {/* Top Camera Locations - Enhanced MinimalCard */}
                    <MinimalCard className="group hover:scale-[1.02] transition-all duration-300">
                    <MinimalCardContent className="p-8">
                        <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-blue-600/20 rounded-lg">
                            <Camera className="h-5 w-5 text-blue-400" />
                        </div>
                        <h2 className="text-xl font-normal text-white">Top Camera Locations</h2>
                        </div>
                        <div className="space-y-4">
                        {topCameras.map((camera, index) => (
                            <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-zinc-900/30 hover:bg-zinc-900/50 transition-colors group-hover:bg-zinc-900/40">
                            <div className="flex items-center gap-3">
                                <span className="text-zinc-500 text-sm w-4">{index + 1}</span>
                                <div>
                                <div className="text-white text-sm font-medium">{camera.location}</div>
                                <div className="text-zinc-600 text-xs">{camera.detections} detections today</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {camera.alerts > 0 && (
                                <div className="px-2 py-1 bg-red-950/50 text-red-400 border border-red-900 rounded text-xs">
                                    {camera.alerts} alerts
                                </div>
                                )}
                                <div className="w-12 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                <div 
                                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-1000"
                                    style={{ width: `${Math.min((camera.detections / 150) * 100, 100)}%` }}
                                />
                                </div>
                            </div>
                            </div>
                        ))}
                        </div>
                    </MinimalCardContent>
                    </MinimalCard>

                    {/* Quick Actions - Creative MinimalCard Grid */}
                    <MinimalCard className="group hover:scale-[1.02] transition-all duration-300">
                    <MinimalCardContent className="p-8">
                        <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-purple-600/20 rounded-lg">
                            <Settings className="h-5 w-5 text-purple-400" />
                        </div>
                        <h2 className="text-xl font-normal text-white">Quick Actions</h2>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                        {[
                            { icon: Camera, label: 'Add Camera', color: 'blue', description: 'Connect new device', action: 'cameras' },
                            { icon: Users, label: 'View Persons', color: 'emerald', description: 'Browse enrolled', action: 'persons' },
                            { icon: Upload, label: 'Upload Media', color: 'purple', description: 'Analyze content', action: 'upload' },
                            { icon: Monitor, label: 'System Monitor', color: 'orange', description: 'View performance', action: 'monitoring' }
                        ].map((action, index) => {
                            const IconComponent = action.icon;
                            return (
                            <button 
                                key={index}
                                onClick={() => onNavigate(action.action)}
                                className="p-4 bg-zinc-900/30 hover:bg-zinc-900/50 rounded-lg transition-all duration-300 text-left group-hover:bg-zinc-900/40 hover:scale-105 border border-zinc-800/50 hover:border-zinc-700"
                            >
                                <div className={`p-2 bg-${action.color}-600/20 rounded-lg mb-3 w-fit`}>
                                <IconComponent className={`h-4 w-4 text-${action.color}-400`} />
                                </div>
                                <div className="text-sm font-medium text-white mb-1">{action.label}</div>
                                <div className="text-xs text-zinc-500">{action.description}</div>
                            </button>
                            );
                        })}
                        </div>
                    </MinimalCardContent>
                    </MinimalCard>
                </div>


      {/* Recent Detections - Card Gallery with improved spacing */}
      <div className="mb-24">
        <div className="flex items-center justify-between mb-12">
          <div>
            <h2 className="text-3xl font-normal text-white mb-3">Recent Detections</h2>
            <p className="text-zinc-500 text-lg">Latest facial recognition events across all cameras</p>
          </div>
          <button 
            onClick={() => onNavigate('persons')}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors"
          >
            <Eye className="h-4 w-4" />
            View All
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {recentDetections.slice(0, 4).map((detection, index) => (
            <MinimalCard key={index} className="group hover:scale-[1.02] transition-all duration-300 cursor-pointer">
              <MinimalCardImage 
                src={generateAvatar(detection.personName)}
                alt={detection.personName}
                className="h-36"
              />
              <MinimalCardContent className="p-8">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <MinimalCardTitle className="text-base mb-2">{detection.personName}</MinimalCardTitle>
                    <div className="text-xs text-zinc-500">{detection.email}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-emerald-400 text-sm font-medium">{detection.confidence}</div>
                    <div className="text-xs text-zinc-500 mt-1">confidence</div>
                  </div>
                </div>
                
                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <MapPin className="h-3 w-3" />
                    <span>{detection.location}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <Clock className="h-3 w-3" />
                    <span>{detection.timestamp}</span>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-zinc-800">
                  <div className="flex items-center justify-between">
                    <span className="px-3 py-1.5 bg-emerald-950/50 text-emerald-400 border border-emerald-900 rounded text-xs">
                      Verified
                    </span>
                    <button 
                      onClick={() => onNavigate('persons')}
                      className="text-zinc-500 hover:text-white transition-colors"
                    >
                      <Search className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          ))}
        </div>
      </div>
    </>
  );
};