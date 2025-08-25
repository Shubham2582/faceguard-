import React, { useState, useEffect } from 'react';
import { User, Clock, MapPin, Zap } from 'lucide-react';

export const LiveRecognitionOverlay = ({ 
  recognitions = [], 
  cameraLocation,
  className = '' 
}) => {
  const [animatedRecognitions, setAnimatedRecognitions] = useState([]);

  useEffect(() => {
    // Animate recognition entries
    const newRecognitions = recognitions.map((recognition, index) => ({
      ...recognition,
      id: `${recognition.person}-${recognition.timestamp}-${index}`,
      isNew: true
    }));

    setAnimatedRecognitions(newRecognitions);

    // Remove the "new" flag after animation
    const timer = setTimeout(() => {
      setAnimatedRecognitions(prev => 
        prev.map(rec => ({ ...rec, isNew: false }))
      );
    }, 1000);

    return () => clearTimeout(timer);
  }, [recognitions]);

  if (animatedRecognitions.length === 0) {
    return (
      <div className={`bg-zinc-950/30 border border-zinc-900 rounded-lg p-4 ${className}`}>
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-zinc-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="h-8 w-8 text-zinc-600" />
          </div>
          <p className="text-zinc-500 text-sm">No active detections</p>
          <p className="text-zinc-600 text-xs">Monitoring for recognized persons...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-zinc-950/30 border border-zinc-900 rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-zinc-900">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <h3 className="text-sm font-medium text-white">Live Recognition</h3>
          </div>
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <MapPin className="h-3 w-3" />
            {cameraLocation}
          </div>
        </div>
      </div>

      {/* Recognition List */}
      <div className="max-h-64 overflow-y-auto">
        {animatedRecognitions.map((recognition) => (
          <div
            key={recognition.id}
            className={`px-4 py-3 border-b border-zinc-900/50 transition-all duration-1000 ${
              recognition.isNew 
                ? 'bg-emerald-600/20 border-emerald-600/30 animate-pulse' 
                : 'hover:bg-zinc-900/30'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {/* Avatar */}
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="h-5 w-5 text-white" />
                </div>
                
                {/* Person Info */}
                <div>
                  <div className="text-sm font-medium text-white">
                    {recognition.person}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-zinc-500">
                    <Clock className="h-3 w-3" />
                    {recognition.timestamp}
                  </div>
                </div>
              </div>

              {/* Confidence Badge */}
              <div className="flex flex-col items-end gap-1">
                <div className={`px-2 py-1 rounded-full text-xs border ${
                  parseFloat(recognition.confidence) >= 95 
                    ? 'bg-emerald-950/50 text-emerald-400 border-emerald-900'
                    : parseFloat(recognition.confidence) >= 85
                    ? 'bg-yellow-950/50 text-yellow-400 border-yellow-900'
                    : 'bg-orange-950/50 text-orange-400 border-orange-900'
                }`}>
                  {recognition.confidence}
                </div>
                {recognition.isNew && (
                  <div className="flex items-center gap-1 text-xs text-emerald-400">
                    <Zap className="h-3 w-3" />
                    NEW
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Stats */}
      <div className="px-4 py-3 bg-zinc-900/30 border-t border-zinc-900">
        <div className="flex items-center justify-between text-xs">
          <div className="text-zinc-500">
            Total: {animatedRecognitions.length} detections
          </div>
          <div className="text-zinc-500">
            Avg Confidence: {
              animatedRecognitions.length > 0 
                ? (animatedRecognitions.reduce((sum, rec) => 
                    sum + parseFloat(rec.confidence), 0
                  ) / animatedRecognitions.length).toFixed(1)
                : 0
            }%
          </div>
        </div>
      </div>
    </div>
  );
};