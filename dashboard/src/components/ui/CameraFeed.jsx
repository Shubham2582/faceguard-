import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize2, Settings } from 'lucide-react';

export const CameraFeed = ({ 
  streamUrl, 
  cameraName, 
  status = 'active',
  resolution = '1920x1080',
  fps = 30,
  onRecognition,
  className = '' 
}) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (videoRef.current && streamUrl && status === 'active') {
      // In a real implementation, this would connect to the actual stream
      // For now, we'll simulate a live feed
      console.log(`Connecting to stream: ${streamUrl}`);
    }
  }, [streamUrl, status]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (!document.fullscreenElement) {
        videoRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  if (status !== 'active') {
    return (
      <div className={`relative bg-zinc-900 aspect-video rounded-lg overflow-hidden ${className}`}>
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center mb-4">
              <Settings className="h-8 w-8 text-zinc-600" />
            </div>
            <p className="text-zinc-500 text-sm">Camera Offline</p>
            <p className="text-zinc-600 text-xs">{cameraName}</p>
          </div>
        </div>
        <div className="absolute top-3 left-3 bg-red-600/90 text-white px-2 py-1 rounded-full text-xs font-medium">
          OFFLINE
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-zinc-900 aspect-video rounded-lg overflow-hidden group ${className}`}>
      {/* Video Element - In production, this would stream from the actual camera */}
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        muted={isMuted}
        autoPlay
        loop
        onLoadedData={() => setIsPlaying(true)}
      >
        {/* Placeholder video source - replace with actual stream */}
        <source src="/placeholder-stream.mp4" type="video/mp4" />
      </video>

      {/* Live Indicator */}
      <div className="absolute top-3 left-3 flex items-center gap-2 bg-red-600/90 text-white px-2 py-1 rounded-full text-xs font-medium">
        <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
        LIVE
      </div>

      {/* Camera Info */}
      <div className="absolute top-3 right-3 bg-black/50 text-white px-2 py-1 rounded text-xs">
        {resolution} • {fps}fps
      </div>

      {/* Controls Overlay */}
      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors">
        <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Left Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={togglePlay}
              className="p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
            >
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </button>
            <button
              onClick={toggleMute}
              className="p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
            >
              {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </button>
          </div>

          {/* Center - Camera Name */}
          <div className="bg-black/50 px-3 py-1 rounded-full text-white text-sm">
            {cameraName}
          </div>

          {/* Right Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleFullscreen}
              className="p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
            >
              <Maximize2 className="h-4 w-4" />
            </button>
            <button className="p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors">
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};