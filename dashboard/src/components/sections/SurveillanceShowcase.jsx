import React, { useState, useEffect } from 'react';
import {
  Camera,
  User,
  Target,
  Activity,
  MapPin,
  Wifi
} from 'lucide-react';

export const SurveillanceShowcase = () => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % 4);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  const steps = [
    { id: '1', name: 'Detection' },
    { id: '2', name: 'Recognition' },
    { id: '3', name: 'Tracking' },
    { id: '4', name: 'Analytics' }
  ];

  return (
    <div className="relative bg-zinc-950/40 border border-zinc-900 rounded-2xl p-8 overflow-hidden">
      <div className="relative z-10">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Left Content */}
          <div className="md:w-2/5 space-y-6">
            <div>
              <h2 className="text-3xl font-normal text-white mb-4">
                Advanced Recognition Pipeline
              </h2>
              <p className="text-zinc-500 leading-relaxed">
                Experience the complete facial recognition workflow from detection to analytics with our sophisticated AI-powered surveillance system.
              </p>
            </div>

            {/* Step Indicators */}
            <div className="flex gap-3">
              {steps.map((stepItem, index) => (
                <div
                  key={stepItem.id}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                    step === index 
                      ? 'bg-blue-600/20 border border-blue-600/30' 
                      : 'bg-zinc-900/50 border border-zinc-800'
                  }`}
                >
                  <div
                    className={`w-2 h-2 rounded-full transition-colors duration-300 ${
                      step === index ? 'bg-blue-400' : 'bg-zinc-600'
                    }`}
                  />
                  <span
                    className={`text-sm font-medium transition-colors duration-300 ${
                      step === index ? 'text-blue-400' : 'text-zinc-500'
                    }`}
                  >
                    {stepItem.name}
                  </span>
                </div>
              ))}
            </div>

            {/* Step Content */}
            <div className="space-y-4">
              {step === 0 && (
                <div className="space-y-3">
                  <h3 className="text-xl font-medium text-white">Live Detection</h3>
                  <p className="text-zinc-400 text-sm">Real-time face detection across all connected cameras with instant frame analysis.</p>
                  <div className="flex items-center gap-2 text-emerald-400 text-sm">
                    <Wifi className="h-4 w-4" />
                    <span>24 cameras active</span>
                  </div>
                </div>
              )}
              {step === 1 && (
                <div className="space-y-3">
                  <h3 className="text-xl font-medium text-white">Face Recognition</h3>
                  <p className="text-zinc-400 text-sm">Advanced AI matching against enrolled database with confidence scoring.</p>
                  <div className="flex items-center gap-2 text-blue-400 text-sm">
                    <Target className="h-4 w-4" />
                    <span>96.5% accuracy rate</span>
                  </div>
                </div>
              )}
              {step === 2 && (
                <div className="space-y-3">
                  <h3 className="text-xl font-medium text-white">Location Tracking</h3>
                  <p className="text-zinc-400 text-sm">Cross-camera tracking with comprehensive location history and movement patterns.</p>
                  <div className="flex items-center gap-2 text-purple-400 text-sm">
                    <MapPin className="h-4 w-4" />
                    <span>Real-time positioning</span>
                  </div>
                </div>
              )}
              {step === 3 && (
                <div className="space-y-3">
                  <h3 className="text-xl font-medium text-white">Smart Analytics</h3>
                  <p className="text-zinc-400 text-sm">Comprehensive reporting, alerts, and insights from surveillance data.</p>
                  <div className="flex items-center gap-2 text-orange-400 text-sm">
                    <Activity className="h-4 w-4" />
                    <span>Advanced insights</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Visual Area */}
          <div className="md:w-3/5 relative h-80 md:h-96">
            {/* Step 1: Camera Grid */}
            <div
              className={`absolute inset-0 transition-all duration-500 ${
                step === 0 ? 'opacity-100 translate-x-0' : step > 0 ? 'opacity-0 -translate-x-8' : 'opacity-0 translate-x-8'
              }`}
            >
              <div className="grid grid-cols-2 gap-3 h-full">
                {[1, 2, 3, 4].map((cam) => (
                  <div key={cam} className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 relative overflow-hidden">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs text-zinc-400">Camera {cam}</span>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                        <span className="text-xs text-red-400">LIVE</span>
                      </div>
                    </div>
                    <div className="bg-zinc-800/50 h-20 rounded flex items-center justify-center">
                      <Camera className="h-6 w-6 text-zinc-600" />
                    </div>
                    {cam === 1 && (
                      <div className="absolute top-12 left-4 w-8 h-8 border-2 border-red-400 rounded animate-pulse" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Step 2: Recognition Interface */}
            <div
              className={`absolute inset-0 transition-all duration-500 ${
                step === 1 ? 'opacity-100 translate-x-0' : step < 1 ? 'opacity-0 translate-x-8' : 'opacity-0 -translate-x-8'
              }`}
            >
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6 h-full">
                <div className="flex items-center gap-3 mb-4">
                  <Target className="h-5 w-5 text-blue-400" />
                  <span className="text-white font-medium">Face Recognition Analysis</span>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-3 bg-zinc-800/50 rounded-lg">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                      <User className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-white">Shubham Kumar</div>
                      <div className="text-sm text-zinc-400">Employee ID: EMP001</div>
                    </div>
                    <div className="text-emerald-400 font-medium">96.5%</div>
                  </div>
                  <div className="flex items-center gap-4 p-3 bg-zinc-800/30 rounded-lg">
                    <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full flex items-center justify-center">
                      <User className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-white">Priya Singh</div>
                      <div className="text-sm text-zinc-400">Employee ID: EMP002</div>
                    </div>
                    <div className="text-emerald-400 font-medium">94.2%</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 3: Location Tracking */}
            <div
              className={`absolute inset-0 transition-all duration-500 ${
                step === 2 ? 'opacity-100 translate-x-0' : step < 2 ? 'opacity-0 translate-x-8' : 'opacity-0 -translate-x-8'
              }`}
            >
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6 h-full">
                <div className="flex items-center gap-3 mb-4">
                  <MapPin className="h-5 w-5 text-purple-400" />
                  <span className="text-white font-medium">Location Tracking</span>
                </div>
                <div className="space-y-3">
                  {[
                    { location: 'Main Entrance', time: '09:15 AM', status: 'current' },
                    { location: 'Lobby', time: '09:12 AM', status: 'previous' },
                    { location: 'Parking Area', time: '09:10 AM', status: 'previous' }
                  ].map((entry, index) => (
                    <div key={index} className={`flex items-center gap-3 p-3 rounded-lg ${
                      entry.status === 'current' ? 'bg-purple-600/20 border border-purple-600/30' : 'bg-zinc-800/30'
                    }`}>
                      <div className={`w-3 h-3 rounded-full ${
                        entry.status === 'current' ? 'bg-purple-400 animate-pulse' : 'bg-zinc-600'
                      }`} />
                      <div className="flex-1">
                        <div className="text-white text-sm font-medium">{entry.location}</div>
                        <div className="text-zinc-400 text-xs">{entry.time}</div>
                      </div>
                      {entry.status === 'current' && (
                        <span className="text-xs text-purple-400 font-medium">CURRENT</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Step 4: Analytics Dashboard */}
            <div
              className={`absolute inset-0 transition-all duration-500 ${
                step === 3 ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'
              }`}
            >
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6 h-full">
                <div className="flex items-center gap-3 mb-4">
                  <Activity className="h-5 w-5 text-orange-400" />
                  <span className="text-white font-medium">Analytics Overview</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="text-center p-3 bg-zinc-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-white">342</div>
                      <div className="text-xs text-zinc-400">Today's Detections</div>
                    </div>
                    <div className="text-center p-3 bg-zinc-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-white">1,247</div>
                      <div className="text-xs text-zinc-400">Enrolled Persons</div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="text-center p-3 bg-red-600/20 border border-red-600/30 rounded-lg">
                      <div className="text-2xl font-bold text-red-400">3</div>
                      <div className="text-xs text-red-300">Active Alerts</div>
                    </div>
                    <div className="text-center p-3 bg-emerald-600/20 border border-emerald-600/30 rounded-lg">
                      <div className="text-2xl font-bold text-emerald-400">99.2%</div>
                      <div className="text-xs text-emerald-300">System Uptime</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Click overlay to advance steps */}
      <div 
        className="absolute inset-0 z-20 cursor-pointer"
        onClick={() => setStep((prev) => (prev + 1) % 4)}
      />
    </div>
  );
};