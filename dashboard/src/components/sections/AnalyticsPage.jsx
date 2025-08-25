import React, { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Users,
  Camera,
  Eye,
  AlertTriangle,
  Activity,
  BarChart3,
  PieChart,
  LineChart,
  Calendar,
  Clock,
  MapPin,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardTitle } from '@/components/ui/MinimalCard';
import { useRealTimeAnalytics } from '@/hooks/useAnalytics';

export const AnalyticsPage = ({ onNavigate }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('detections');
  
  // Use the analytics hook to fetch data with real-time updates
  const {
    data: analyticsData,
    loading,
    error,
    lastUpdated,
    refresh,
    isUsingMockData,
    autoRefresh,
    setAutoRefresh
  } = useRealTimeAnalytics(selectedTimeRange, 60000); // Refresh every minute

  // Show loading state
  if (loading && !analyticsData) {
    return (
      <div className="pt-24 pb-16">
        <div className="text-center">
          <div className="inline-block bg-purple-600/10 border border-purple-600/20 text-purple-400 px-4 py-2 rounded-full text-xs font-medium mb-10 tracking-wider">
            LOADING ANALYTICS
          </div>
          <h1 className="text-5xl lg:text-6xl font-normal mb-8 tracking-tight leading-tight">
            Loading <span className="italic text-zinc-600 font-light">Data</span>
          </h1>
          <div className="flex justify-center">
            <div className="w-8 h-8 border-2 border-purple-600/20 border-t-purple-600 rounded-full animate-spin"></div>
          </div>
        </div>
      </div>
    );
  }

  // Handle error state
  if (error && !analyticsData) {
    return (
      <div className="pt-24 pb-16">
        <div className="text-center">
          <div className="inline-block bg-red-600/10 border border-red-600/20 text-red-400 px-4 py-2 rounded-full text-xs font-medium mb-10 tracking-wider">
            ERROR
          </div>
          <h1 className="text-5xl lg:text-6xl font-normal mb-8 tracking-tight leading-tight">
            Data <span className="italic text-zinc-600 font-light">Unavailable</span>
          </h1>
          <p className="text-zinc-500 text-lg max-w-2xl mx-auto mb-8">
            Unable to load analytics data. Please check your connection and try again.
          </p>
          <button 
            onClick={refresh}
            className="px-6 py-3 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded-lg border border-purple-600/30 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const MetricCard = ({ title, value, trend, icon: Icon, color, subtitle }) => (
    <MinimalCard className="hover:scale-[1.03] hover:shadow-2xl hover:shadow-purple-500/5 transition-all duration-500 group border-zinc-800/50 backdrop-blur-sm">
      <MinimalCardContent className="p-8 relative overflow-hidden">
        {/* Background gradient effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-zinc-900/20 via-transparent to-zinc-800/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        <div className="flex items-start justify-between mb-8 relative z-10">
          <div className={`p-4 bg-gradient-to-br ${color} rounded-xl shadow-lg group-hover:shadow-xl transition-all duration-300 relative overflow-hidden`}>
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <Icon className="h-7 w-7 text-white relative z-10 group-hover:scale-110 transition-transform duration-300" />
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium backdrop-blur-sm border transition-all duration-300 ${
            trend.type === 'increase' 
              ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20 hover:bg-emerald-400/20' 
              : 'text-red-400 bg-red-400/10 border-red-400/20 hover:bg-red-400/20'
          }`}>
            {trend.type === 'increase' ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            {trend.value}%
          </div>
        </div>
        
        <div className="relative z-10">
          <h3 className="text-4xl font-light mb-3 text-white group-hover:text-zinc-100 transition-colors duration-300 tracking-tight">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </h3>
          <p className="text-zinc-400 text-base font-medium">{title}</p>
          {subtitle && <p className="text-zinc-600 text-sm mt-2 group-hover:text-zinc-500 transition-colors duration-300">{subtitle}</p>}
        </div>
      </MinimalCardContent>
    </MinimalCard>
  );

  const ChartContainer = ({ title, children, actions }) => (
    <MinimalCard className="h-full hover:shadow-xl hover:shadow-purple-500/5 transition-all duration-500 border-zinc-800/50 backdrop-blur-sm group">
      <MinimalCardContent className="p-8 relative overflow-hidden">
        {/* Subtle background pattern */}
        <div className="absolute inset-0 bg-gradient-to-br from-zinc-900/10 via-transparent to-zinc-800/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        <div className="flex items-center justify-between mb-10 relative z-10">
          <div>
            <MinimalCardTitle className="text-2xl text-white font-light tracking-tight group-hover:text-zinc-100 transition-colors duration-300">{title}</MinimalCardTitle>
            <div className="w-12 h-1 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full mt-2 opacity-60 group-hover:opacity-100 transition-opacity duration-300" />
          </div>
          {actions && <div className="flex gap-3">{actions}</div>}
        </div>
        
        <div className="relative z-10">
          {children}
        </div>
      </MinimalCardContent>
    </MinimalCard>
  );

  return (
    <>
      {/* Hero Section */}
      <div className="pt-4 pb-12">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-600/10 to-blue-600/10 border border-purple-600/20 text-purple-400 px-6 py-3 rounded-full text-sm font-medium mb-8 tracking-wider backdrop-blur-sm hover:bg-purple-600/20 transition-colors duration-300">
            <Activity className="h-4 w-4" />
            ANALYTICS DASHBOARD
          </div>
          <h1 className="text-6xl lg:text-7xl font-extralight mb-6 tracking-tighter leading-tight">
            Recognition <span className="italic text-transparent bg-gradient-to-r from-zinc-400 to-zinc-600 bg-clip-text font-thin">Analytics</span>
          </h1>
          <p className="text-zinc-400 text-xl max-w-5xl mx-auto leading-relaxed font-light">
            Comprehensive insights into facial recognition performance, detection patterns, and system utilization with advanced analytics and visualization.
          </p>
          
          {/* Decorative elements */}
          <div className="flex justify-center mt-8 space-x-1">
            <div className="w-2 h-2 bg-purple-500/40 rounded-full animate-pulse" />
            <div className="w-2 h-2 bg-blue-500/40 rounded-full animate-pulse" style={{animationDelay: '0.2s'}} />
            <div className="w-2 h-2 bg-emerald-500/40 rounded-full animate-pulse" style={{animationDelay: '0.4s'}} />
          </div>
        </div>

        {/* Data Status & Controls */}
        <div className="flex justify-between items-center mb-16">
          <div className="flex items-center gap-6">
            {/* Data Source Indicator */}
            <div className={`inline-flex items-center gap-3 px-4 py-2.5 rounded-full text-sm font-medium backdrop-blur-sm transition-all duration-300 hover:scale-105 ${
              isUsingMockData 
                ? 'bg-gradient-to-r from-yellow-600/10 to-orange-600/10 text-yellow-400 border border-yellow-600/20 hover:border-yellow-500/30'
                : 'bg-gradient-to-r from-emerald-600/10 to-green-600/10 text-emerald-400 border border-emerald-600/20 hover:border-emerald-500/30'
            }`}>
              <div className={`w-2.5 h-2.5 rounded-full ${
                isUsingMockData ? 'bg-yellow-400' : 'bg-emerald-400 animate-pulse'
              }`} />
              {isUsingMockData ? 'DEMO DATA' : 'LIVE DATA'}
            </div>

            {/* Last Updated */}
            {lastUpdated && (
              <div className="flex items-center gap-2 text-zinc-400 text-sm bg-zinc-900/30 px-3 py-1.5 rounded-lg border border-zinc-800/50">
                <Clock className="h-3 w-3" />
                Updated {lastUpdated.toLocaleTimeString()}
              </div>
            )}

            {/* Auto-refresh Toggle */}
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center gap-2 text-sm px-4 py-2.5 rounded-full transition-all duration-300 hover:scale-105 backdrop-blur-sm ${
                autoRefresh
                  ? 'bg-gradient-to-r from-blue-600/10 to-cyan-600/10 text-blue-400 border border-blue-600/20 hover:border-blue-500/30'
                  : 'bg-zinc-900/50 text-zinc-400 border border-zinc-700/50 hover:border-zinc-600/50 hover:text-zinc-300'
              }`}
            >
              <RefreshCw className={`h-3 w-3 ${autoRefresh ? 'animate-spin' : ''}`} />
              Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* Time Range Selector & Refresh */}
          <div className="flex items-center gap-6">
            <div className="flex bg-zinc-950/70 border border-zinc-800/50 rounded-xl p-1.5 backdrop-blur-sm">
              {[
                { key: '24h', label: '24h' },
                { key: '7d', label: '7d' },
                { key: '30d', label: '30d' },
                { key: '90d', label: '90d' }
              ].map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setSelectedTimeRange(key)}
                  className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                    selectedTimeRange === key
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg shadow-purple-500/25'
                      : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <button
              onClick={refresh}
              disabled={loading}
              className="p-3 bg-zinc-800/50 hover:bg-zinc-700/50 text-zinc-400 hover:text-white rounded-xl border border-zinc-700/50 transition-all duration-300 disabled:opacity-50 hover:scale-105 backdrop-blur-sm"
            >
              <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
        <MetricCard
          title="Total Detections"
          value={analyticsData.overview.totalDetections}
          trend={analyticsData.overview.trends.detections}
          icon={Eye}
          color="from-blue-500 to-blue-600"
          subtitle="Past 30 days"
        />
        <MetricCard
          title="Unique Persons"
          value={analyticsData.overview.uniquePersons}
          trend={analyticsData.overview.trends.persons}
          icon={Users}
          color="from-emerald-500 to-emerald-600"
          subtitle="Active recognitions"
        />
        <MetricCard
          title="Avg Confidence"
          value={`${analyticsData.overview.averageConfidence}%`}
          trend={analyticsData.overview.trends.confidence}
          icon={Activity}
          color="from-purple-500 to-purple-600"
          subtitle="Recognition accuracy"
        />
        <MetricCard
          title="Alerts Triggered"
          value={analyticsData.overview.alertsTriggered}
          trend={analyticsData.overview.trends.alerts}
          icon={AlertTriangle}
          color="from-orange-500 to-orange-600"
          subtitle="Security events"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mb-20">
        {/* Weekly Detection Pattern */}
        <ChartContainer 
          title="Weekly Detection Pattern"
          actions={[
            <button key="refresh" className="p-2 text-zinc-400 hover:text-white transition-colors">
              <RefreshCw className="h-4 w-4" />
            </button>
          ]}
        >
          <div className="space-y-4">
            {analyticsData.timeAnalytics.weeklyPattern.map((day, index) => (
              <div key={day.day} className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-zinc-400 w-8 text-sm">{day.day}</span>
                  <div className="flex-1 bg-zinc-800 rounded-full h-2 w-48">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${(day.detections / 1300) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-white text-sm font-medium">{day.detections}</div>
                  <div className="text-zinc-500 text-xs">{day.confidence}%</div>
                </div>
              </div>
            ))}
          </div>
        </ChartContainer>

        {/* Confidence Distribution */}
        <ChartContainer 
          title="Confidence Score Distribution"
          actions={[
            <button key="download" className="p-2 text-zinc-400 hover:text-white transition-colors">
              <Download className="h-4 w-4" />
            </button>
          ]}
        >
          <div className="space-y-6">
            {analyticsData.confidenceDistribution.map((range, index) => (
              <div key={range.range} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-zinc-400">{range.range}</span>
                  <span className="text-white font-medium">{range.count.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-zinc-800 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-1000 ${
                        index === 0 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                        index === 1 ? 'bg-gradient-to-r from-emerald-500 to-green-500' :
                        'bg-gradient-to-r from-blue-500 to-purple-500'
                      }`}
                      style={{ width: `${range.percentage}%` }}
                    />
                  </div>
                  <span className="text-zinc-300 text-sm w-12">{range.percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </ChartContainer>
      </div>

      {/* Location Analytics */}
      <div className="mb-20">
        <div className="flex items-center justify-between mb-12">
          <div>
            <h2 className="text-4xl font-light text-white mb-4 tracking-tight">Location Analytics</h2>
            <p className="text-zinc-400 text-xl font-light">Detection activity across different camera locations</p>
            <div className="w-16 h-1 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full mt-3 opacity-60" />
          </div>
          <button className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-600/20 to-blue-600/20 hover:from-purple-600/30 hover:to-blue-600/30 text-purple-400 rounded-xl border border-purple-600/30 transition-all duration-300 hover:scale-105 backdrop-blur-sm">
            <Filter className="h-5 w-5" />
            Filter Locations
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {analyticsData.locationAnalytics.map((location, index) => (
            <MinimalCard key={location.location} className="hover:scale-[1.02] hover:shadow-xl hover:shadow-purple-500/5 transition-all duration-500 border-zinc-800/50 backdrop-blur-sm group">
              <MinimalCardContent className="p-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-zinc-900/20 via-transparent to-zinc-800/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="grid grid-cols-12 gap-8 items-center relative z-10">
                  <div className="col-span-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-600/20 rounded-lg">
                        <MapPin className="h-4 w-4 text-blue-400" />
                      </div>
                      <div>
                        <h3 className="text-white font-medium">{location.location}</h3>
                        <p className="text-zinc-500 text-sm">Camera Location</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="col-span-2 text-center">
                    <div className="text-2xl font-normal text-white">{location.detections.toLocaleString()}</div>
                    <div className="text-zinc-500 text-sm">Total Detections</div>
                  </div>
                  
                  <div className="col-span-2 text-center">
                    <div className="text-xl font-normal text-emerald-400">{location.uniquePersons}</div>
                    <div className="text-zinc-500 text-sm">Unique Persons</div>
                  </div>
                  
                  <div className="col-span-2 text-center">
                    <div className="text-xl font-normal text-purple-400">{location.avgConfidence}%</div>
                    <div className="text-zinc-500 text-sm">Avg Confidence</div>
                  </div>
                  
                  <div className="col-span-2 text-center">
                    <div className={`text-xl font-normal ${location.alerts > 0 ? 'text-red-400' : 'text-zinc-600'}`}>
                      {location.alerts}
                    </div>
                    <div className="text-zinc-500 text-sm">Alerts</div>
                  </div>
                  
                  <div className="col-span-1">
                    <div className="w-full bg-zinc-800 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-1000"
                        style={{ width: `${Math.min((location.detections / 3000) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          ))}
        </div>
      </div>

      {/* Person Activity Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 mb-20">
        {/* Top Active Persons */}
        <div className="lg:col-span-2">
          <MinimalCard>
            <MinimalCardContent className="p-8">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <MinimalCardTitle className="text-xl text-white mb-2">Most Active Persons</MinimalCardTitle>
                  <p className="text-zinc-500 text-sm">Based on detection frequency and location coverage</p>
                </div>
                <button 
                  onClick={() => onNavigate('persons')}
                  className="text-purple-400 hover:text-purple-300 text-sm font-medium"
                >
                  View All Persons
                </button>
              </div>
              
              <div className="space-y-4">
                {analyticsData.personActivity.map((person, index) => (
                  <div key={person.name} className="flex items-center justify-between p-6 rounded-xl bg-gradient-to-r from-zinc-900/20 to-zinc-800/20 hover:from-zinc-900/40 hover:to-zinc-800/40 transition-all duration-300 border border-zinc-800/30 hover:border-zinc-700/50 backdrop-blur-sm group">
                    <div className="flex items-center gap-6">
                      <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-xl border border-purple-600/20 group-hover:border-purple-500/30 transition-colors">
                        <span className="text-purple-400 text-sm font-medium">#{index + 1}</span>
                      </div>
                      <div>
                        <div className="text-white font-medium text-lg">{person.name}</div>
                        <div className="text-zinc-400 text-sm">Last seen {person.lastSeen}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-10">
                      <div className="text-center">
                        <div className="text-blue-400 font-semibold text-lg">{person.detections}</div>
                        <div className="text-zinc-500 text-xs font-medium">Detections</div>
                      </div>
                      <div className="text-center">
                        <div className="text-emerald-400 font-semibold text-lg">{person.locations}</div>
                        <div className="text-zinc-500 text-xs font-medium">Locations</div>
                      </div>
                      <div className="text-center">
                        <div className="text-purple-400 font-semibold text-lg">{person.avgConfidence}%</div>
                        <div className="text-zinc-500 text-xs font-medium">Confidence</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </MinimalCardContent>
          </MinimalCard>
        </div>

        {/* Peak Hours */}
        <MinimalCard>
          <MinimalCardContent className="p-8">
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2 bg-orange-600/20 rounded-lg">
                <Clock className="h-5 w-5 text-orange-400" />
              </div>
              <div>
                <MinimalCardTitle className="text-xl text-white">Peak Hours</MinimalCardTitle>
                <p className="text-zinc-500 text-sm">Highest activity periods</p>
              </div>
            </div>
            
            <div className="space-y-6">
              {analyticsData.timeAnalytics.peakHours.map((hour, index) => (
                <div key={hour.hour} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-zinc-400 text-sm">{hour.hour}</span>
                    <span className="text-white font-medium">{hour.detections}</span>
                  </div>
                  <div className="w-full bg-zinc-800 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${(hour.detections / 250) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-8 p-4 bg-zinc-900/30 rounded-lg">
              <div className="text-center">
                <div className="text-orange-400 text-lg font-medium">17:00</div>
                <div className="text-zinc-500 text-sm">Peak Activity Hour</div>
                <div className="text-zinc-400 text-xs mt-1">234 detections</div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Action Bar */}
      <div className="flex justify-center">
        <div className="flex gap-6">
          <button 
            onClick={() => onNavigate('persons')}
            className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-emerald-600/20 to-green-600/20 hover:from-emerald-600/30 hover:to-green-600/30 text-emerald-400 rounded-xl border border-emerald-600/30 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105 backdrop-blur-sm font-medium"
          >
            <Users className="h-5 w-5" />
            View Persons
          </button>
          <button 
            onClick={() => onNavigate('cameras')}
            className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600/20 to-cyan-600/20 hover:from-blue-600/30 hover:to-cyan-600/30 text-blue-400 rounded-xl border border-blue-600/30 hover:border-blue-500/40 transition-all duration-300 hover:scale-105 backdrop-blur-sm font-medium"
          >
            <Camera className="h-5 w-5" />
            Manage Cameras
          </button>
          <button className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-600/20 to-violet-600/20 hover:from-purple-600/30 hover:to-violet-600/30 text-purple-400 rounded-xl border border-purple-600/30 hover:border-purple-500/40 transition-all duration-300 hover:scale-105 backdrop-blur-sm font-medium">
            <Download className="h-5 w-5" />
            Export Report
          </button>
        </div>
      </div>
    </>
  );
};