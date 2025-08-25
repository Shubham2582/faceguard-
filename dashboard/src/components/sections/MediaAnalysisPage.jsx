import React, { useState, useRef } from 'react';
import {
  Upload,
  Image,
  Video,
  Camera,
  Users,
  Eye,
  Clock,
  MapPin,
  CheckCircle,
  RotateCcw,
  Download,
  X,
  Loader2,
  FileImage,
  FileVideo,
  Activity,
  Brain
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardTitle } from '@/components/ui/MinimalCard';

export const MediaAnalysisPage = ({ onNavigate }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisHistory, setAnalysisHistory] = useState([
    {
      id: 'ANL-001',
      fileName: 'security_cam_footage.mp4',
      type: 'video',
      uploadTime: '2 hours ago',
      detectedPersons: 3,
      totalDuration: '00:02:45',
      status: 'completed',
      confidence: 94.2,
      processingTime: '2.4s',
      results: [
        { name: 'Shubham Kumar', confidence: 94.2, timestamp: '00:00:15', location: 'Main Entrance', enrolledId: 'EMP-001' },
        { name: 'Mayank Sharma', confidence: 87.6, timestamp: '00:01:23', location: 'Main Entrance', enrolledId: 'EMP-002' },
        { name: 'Unknown Person', confidence: 0, timestamp: '00:02:10', location: 'Main Entrance', enrolledId: null }
      ]
    },
    {
      id: 'ANL-002',
      fileName: 'conference_meeting.jpg',
      type: 'image',
      uploadTime: '5 hours ago',
      detectedPersons: 4,
      status: 'completed',
      confidence: 89.3,
      processingTime: '1.8s',
      results: [
        { name: 'Vipin Singh', confidence: 91.8, location: 'Conference Room', enrolledId: 'EMP-003' },
        { name: 'Pratham Gupta', confidence: 89.3, location: 'Conference Room', enrolledId: 'EMP-004' },
        { name: 'Sarah Wilson', confidence: 85.7, location: 'Conference Room', enrolledId: 'EMP-005' },
        { name: 'Unknown Person', confidence: 0, location: 'Conference Room', enrolledId: null }
      ]
    },
    {
      id: 'ANL-003',
      fileName: 'lobby_surveillance.mp4',
      type: 'video',
      uploadTime: '1 day ago',
      detectedPersons: 7,
      totalDuration: '00:05:12',
      status: 'completed',
      confidence: 92.1,
      processingTime: '4.2s',
      results: []
    }
  ]);
  
  const fileInputRef = useRef(null);

  const handleFileSelect = (files) => {
    const file = files[0];
    if (file && (file.type.startsWith('image/') || file.type.startsWith('video/'))) {
      setSelectedFile(file);
      setAnalysisResults(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFileSelect(files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const simulateAnalysis = () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    
    // Animate progress
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + Math.random() * 15 + 5;
      });
    }, 200);
    
    // Simulate analysis process with realistic stages
    setTimeout(() => {
      const mockResults = {
        fileName: selectedFile.name,
        fileType: selectedFile.type,
        fileSize: selectedFile.size,
        analysisTime: new Date().toLocaleString(),
        processingTime: `${(Math.random() * 2 + 1).toFixed(1)}s`,
        detectedPersons: selectedFile.type.startsWith('image/') ? Math.floor(Math.random() * 4) + 1 : Math.floor(Math.random() * 6) + 2,
        totalDuration: selectedFile.type.startsWith('video/') ? `00:0${Math.floor(Math.random() * 3) + 1}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}` : null,
        averageConfidence: Math.floor(Math.random() * 20) + 80,
        aiModel: 'InsightFace Buffalo_L + RetinaFace',
        processingNodes: Math.floor(Math.random() * 3) + 2,
        results: selectedFile.type.startsWith('image/') ? [
          {
            name: 'Shubham Kumar',
            confidence: 94.2 + Math.random() * 4,
            boundingBox: { x: 120, y: 80, width: 150, height: 200 },
            enrolledId: 'EMP-001',
            lastSeen: '2 days ago',
            location: 'Analysis Upload',
            age: 28,
            gender: 'Male',
            emotion: 'Neutral',
            quality: 'High'
          },
          {
            name: 'Sarah Wilson',
            confidence: 89.7 + Math.random() * 4,
            boundingBox: { x: 300, y: 90, width: 140, height: 180 },
            enrolledId: 'EMP-005',
            lastSeen: '1 week ago',
            location: 'Analysis Upload',
            age: 32,
            gender: 'Female',
            emotion: 'Happy',
            quality: 'High'
          },
          {
            name: 'Unknown Person',
            confidence: 0,
            boundingBox: { x: 480, y: 100, width: 135, height: 175 },
            enrolledId: null,
            location: 'Analysis Upload',
            age: 25,
            gender: 'Male',
            emotion: 'Neutral',
            quality: 'Medium'
          }
        ] : [
          {
            name: 'Shubham Kumar',
            confidence: 94.2 + Math.random() * 4,
            timestamp: '00:00:15',
            enrolledId: 'EMP-001',
            lastSeen: '2 days ago',
            location: 'Analysis Upload',
            age: 28,
            gender: 'Male',
            emotion: 'Neutral',
            appearances: 3
          },
          {
            name: 'Mayank Sharma',
            confidence: 87.6 + Math.random() * 4,
            timestamp: '00:00:45',
            enrolledId: 'EMP-002',
            lastSeen: '1 week ago',
            location: 'Analysis Upload',
            age: 30,
            gender: 'Male',
            emotion: 'Happy',
            appearances: 2
          },
          {
            name: 'Vipin Singh',
            confidence: 91.8 + Math.random() * 4,
            timestamp: '00:01:20',
            enrolledId: 'EMP-003',
            lastSeen: '3 days ago',
            location: 'Analysis Upload',
            age: 35,
            gender: 'Male',
            emotion: 'Serious',
            appearances: 1
          },
          {
            name: 'Unknown Person',
            confidence: 0,
            timestamp: '00:01:45',
            enrolledId: null,
            location: 'Analysis Upload',
            age: 27,
            gender: 'Female',
            emotion: 'Neutral',
            appearances: 2
          }
        ]
      };
      
      clearInterval(progressInterval);
      setAnalysisProgress(100);
      setTimeout(() => {
        setAnalysisResults(mockResults);
        setIsAnalyzing(false);
        setAnalysisProgress(0);
      }, 500);
    }, 3500);
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setAnalysisResults(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <>
      {/* Hero Section */}
      <div className="pt-4 pb-12">
        <div className="text-center mb-10">
          <div className="inline-block bg-purple-600/10 border border-purple-600/20 text-purple-400 px-4 py-2 rounded-full text-xs font-medium mb-6 tracking-wider">
            MEDIA ANALYSIS
          </div>
          <h1 className="text-5xl lg:text-6xl font-normal mb-5 tracking-tight leading-tight">
            Upload & Analyze <span className="italic text-zinc-600 font-light">Media</span>
          </h1>
          <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
            Upload images or videos to identify enrolled persons with AI-powered facial recognition technology. Get detailed analysis reports with confidence scores and timestamps.
          </p>
        </div>
      </div>

      {/* Enhanced Full-Viewport Upload Interface */}
      <div className="mb-24">
        {!analysisResults ? (
          /* Main Upload Card - Full Viewport */
          <div className="min-h-[70vh] flex items-center justify-center">
            <div className="w-full max-w-4xl">
              <MinimalCard className="hover:scale-[1.01] transition-all duration-500 group border-zinc-800/50 bg-gradient-to-br from-zinc-950/80 to-zinc-900/50 backdrop-blur-sm">
                <MinimalCardContent className="p-16 relative overflow-hidden">
                  {/* Subtle Background Pattern */}
                  <div className="absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity duration-500">
                    <div className="w-full h-full" style={{
                      backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(139,92,246,0.1) 1px, transparent 1px), radial-gradient(circle at 75% 75%, rgba(59,130,246,0.1) 1px, transparent 1px)',
                      backgroundSize: '50px 50px'
                    }} />
                  </div>
                  
                  {/* Header Section */}
                  <div className="text-center mb-12 relative z-10">
                    <div className="flex items-center justify-center gap-4 mb-8">
                      <div className="relative">
                        <div className="p-6 bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-purple-600/20 rounded-2xl border border-purple-500/30 shadow-xl group-hover:shadow-2xl transition-shadow duration-500">
                          <Upload className="h-10 w-10 text-purple-400 group-hover:scale-110 transition-transform duration-300" />
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-50 transition-opacity duration-500" />
                      </div>
                    </div>
                    <h2 className="text-4xl font-light text-white mb-4 tracking-tight group-hover:text-white/90 transition-colors duration-300">
                      Upload & Analyze Media
                    </h2>
                    <p className="text-zinc-400 text-lg leading-relaxed max-w-2xl mx-auto">
                      Drop your images or videos here to identify enrolled persons with advanced AI-powered facial recognition
                    </p>
                  </div>

                  {/* Enhanced Drop Zone */}
                  <div
                    className={`relative border-2 border-dashed rounded-2xl p-20 text-center transition-all duration-500 cursor-pointer group/drop ${
                      dragOver
                        ? 'border-purple-400/60 bg-gradient-to-br from-purple-500/10 to-blue-500/10 scale-[1.02] shadow-2xl shadow-purple-500/20'
                        : selectedFile
                        ? 'border-emerald-400/60 bg-gradient-to-br from-emerald-500/10 to-green-500/10 shadow-xl shadow-emerald-500/20'
                        : 'border-zinc-600/40 hover:border-zinc-500/60 hover:bg-gradient-to-br hover:from-zinc-800/20 hover:to-zinc-700/20 hover:scale-[1.01]'
                    }`}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onClick={() => !selectedFile && fileInputRef.current?.click()}
                  >
                    {/* Floating Elements for Visual Interest */}
                    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
                      {Array.from({ length: 6 }).map((_, i) => (
                        <div
                          key={i}
                          className={`absolute w-1 h-1 rounded-full animate-pulse ${
                            dragOver ? 'bg-purple-400' : selectedFile ? 'bg-emerald-400' : 'bg-zinc-500'
                          }`}
                          style={{
                            left: `${20 + (i * 15)}%`,
                            top: `${10 + (i * 10)}%`,
                            animationDelay: `${i * 0.5}s`
                          }}
                        />
                      ))}
                    </div>

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*,video/*"
                      onChange={(e) => handleFileSelect(e.target.files)}
                      className="hidden"
                    />

                    <div className="relative z-10">
                      {selectedFile ? (
                        <div className="space-y-8 animate-in slide-in-from-bottom duration-500">
                          <div className="flex justify-center">
                            <div className="relative">
                              <div className="p-8 bg-gradient-to-br from-emerald-600/20 to-green-600/20 rounded-2xl border border-emerald-400/30 shadow-2xl">
                                {selectedFile.type.startsWith('image/') ? (
                                  <FileImage className="h-16 w-16 text-emerald-400" />
                                ) : (
                                  <FileVideo className="h-16 w-16 text-emerald-400" />
                                )}
                              </div>
                              <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/20 to-green-600/20 rounded-2xl blur-2xl opacity-50 animate-pulse" />
                            </div>
                          </div>
                          
                          <div className="space-y-4">
                            <h4 className="text-white font-medium text-2xl tracking-tight">{selectedFile.name}</h4>
                            <div className="flex items-center justify-center gap-6 text-zinc-400">
                              <div className="flex items-center gap-2 px-4 py-2 bg-zinc-800/50 rounded-xl border border-zinc-700/50">
                                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                                <span className="text-sm font-medium">{selectedFile.type.startsWith('image/') ? 'Image File' : 'Video File'}</span>
                              </div>
                              <div className="flex items-center gap-2 px-4 py-2 bg-zinc-800/50 rounded-xl border border-zinc-700/50">
                                <span className="text-sm font-medium">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                              </div>
                            </div>
                          </div>
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              clearSelection();
                            }}
                            className="inline-flex items-center gap-3 px-6 py-3 text-zinc-400 hover:text-white bg-zinc-800/50 hover:bg-zinc-700/50 rounded-xl transition-all duration-300 hover:scale-105 border border-zinc-700/50 hover:border-zinc-600/50"
                          >
                            <X className="h-5 w-5" />
                            <span className="font-medium">Remove File</span>
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-10 animate-in fade-in duration-700">
                          <div className="flex justify-center space-x-8">
                            <div className="relative group/icon">
                              <div className="p-6 bg-gradient-to-br from-blue-600/20 to-cyan-600/20 rounded-2xl border border-blue-400/30 shadow-lg group-hover/icon:scale-110 transition-all duration-300">
                                <Image className="h-12 w-12 text-blue-400" />
                              </div>
                              <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-cyan-600/20 rounded-2xl blur-xl opacity-0 group-hover/icon:opacity-70 transition-opacity duration-300" />
                            </div>
                            <div className="relative group/icon">
                              <div className="p-6 bg-gradient-to-br from-purple-600/20 to-violet-600/20 rounded-2xl border border-purple-400/30 shadow-lg group-hover/icon:scale-110 transition-all duration-300">
                                <Video className="h-12 w-12 text-purple-400" />
                              </div>
                              <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-violet-600/20 rounded-2xl blur-xl opacity-0 group-hover/icon:opacity-70 transition-opacity duration-300" />
                            </div>
                          </div>
                          
                          <div className="space-y-6">
                            <h3 className="text-white text-3xl font-light tracking-tight group/drop-hover:text-white/90 transition-colors duration-300">
                              Drop files here or click to browse
                            </h3>
                            <p className="text-zinc-400 text-lg leading-relaxed max-w-xl mx-auto">
                              Supports <span className="text-blue-400 font-medium">JPG, PNG</span> images and <span className="text-purple-400 font-medium">MP4, AVI, MOV</span> videos up to 100MB
                            </p>
                            
                            {/* Decorative Elements */}
                            <div className="flex justify-center space-x-3 mt-8">
                              {[0, 1, 2, 3, 4].map((i) => (
                                <div
                                  key={i}
                                  className="w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse"
                                  style={{animationDelay: `${i * 0.3}s`}}
                                />
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  {selectedFile && (
                    <div className="flex gap-6 mt-12 relative z-10">
                      <button
                        onClick={simulateAnalysis}
                        disabled={isAnalyzing}
                        className="flex-1 relative overflow-hidden group/btn"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur-xl opacity-50 group-hover/btn:opacity-100 transition-opacity duration-300" />
                        <div className="relative flex items-center justify-center gap-4 px-10 py-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-2xl font-medium transition-all duration-300 hover:scale-105 disabled:opacity-60 disabled:hover:scale-100 shadow-2xl">
                          {isAnalyzing ? (
                            <>
                              <div className="relative">
                                <Loader2 className="h-6 w-6 animate-spin" />
                                <div className="absolute inset-0 bg-white rounded-full blur-sm opacity-50 animate-pulse" />
                              </div>
                              <span className="text-lg">Analyzing Media...</span>
                              {analysisProgress > 0 && (
                                <span className="text-sm opacity-90 bg-white/20 px-3 py-1 rounded-full">({Math.round(analysisProgress)}%)</span>
                              )}
                            </>
                          ) : (
                            <>
                              <Brain className="h-6 w-6 group-hover/btn:animate-pulse" />
                              <span className="text-lg">Start AI Analysis</span>
                              <div className="flex space-x-1">
                                {[0, 1, 2].map((i) => (
                                  <div key={i} className="w-1 h-1 bg-white/50 rounded-full animate-pulse" style={{animationDelay: `${i * 0.2}s`}} />
                                ))}
                              </div>
                            </>
                          )}
                        </div>
                      </button>
                      
                      <button
                        onClick={clearSelection}
                        className="px-8 py-6 bg-gradient-to-br from-zinc-800/80 to-zinc-700/80 hover:from-zinc-700/80 hover:to-zinc-600/80 text-zinc-300 hover:text-white rounded-2xl transition-all duration-300 hover:scale-105 backdrop-blur-sm border border-zinc-600/50 hover:border-zinc-500/50 shadow-xl"
                      >
                        <RotateCcw className="h-6 w-6" />
                      </button>
                    </div>
                  )}
                  
                  {/* Enhanced Progress Bar */}
                  {isAnalyzing && analysisProgress > 0 && (
                    <div className="mt-8 relative z-10">
                      <div className="w-full bg-zinc-800/50 rounded-full h-4 overflow-hidden border border-zinc-700/50 shadow-inner">
                        <div 
                          className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-emerald-500 rounded-full transition-all duration-500 relative overflow-hidden shadow-lg"
                          style={{ width: `${Math.min(analysisProgress, 100)}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
                        </div>
                      </div>
                      <div className="text-center mt-3">
                        <span className="text-sm text-zinc-400">Processing with AI recognition models...</span>
                      </div>
                    </div>
                  )}
                </MinimalCardContent>
              </MinimalCard>
            </div>
          </div>
        ) : (
          /* Results Grid Layout */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Compact Upload Interface */}
            <MinimalCard className="hover:scale-[1.02] transition-all duration-300 group">
              <MinimalCardContent className="p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-purple-600/20 rounded-lg">
                    <Upload className="h-5 w-5 text-purple-400" />
                  </div>
                  <h2 className="text-xl font-normal text-white">Upload New Media</h2>
                </div>

                <div
                  className="border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 border-zinc-600/40 hover:border-zinc-500/60 cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="space-y-4">
                    <div className="flex justify-center space-x-3">
                      <div className="p-2 bg-blue-600/20 rounded-lg">
                        <Image className="h-5 w-5 text-blue-400" />
                      </div>
                      <div className="p-2 bg-purple-600/20 rounded-lg">
                        <Video className="h-5 w-5 text-purple-400" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-white font-medium mb-2">Upload Another File</h3>
                      <p className="text-zinc-400 text-sm">Click to browse for images or videos</p>
                    </div>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>

            {/* Analysis Results */}
            {analysisResults && (
              <MinimalCard className="hover:scale-[1.02] transition-all duration-300">
                <MinimalCardContent className="p-8">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-emerald-600/20 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-emerald-400" />
                    </div>
                    <h2 className="text-xl font-normal text-white">Analysis Complete</h2>
                  </div>

                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="p-4 bg-zinc-900/30 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Users className="h-4 w-4 text-blue-400" />
                        <span className="text-blue-400 text-xs uppercase tracking-wider">Detected</span>
                      </div>
                      <div className="text-2xl font-normal text-white">{analysisResults.detectedPersons}</div>
                      <div className="text-zinc-500 text-sm">Persons Found</div>
                    </div>
                    
                    <div className="p-4 bg-zinc-900/30 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Activity className="h-4 w-4 text-purple-400" />
                        <span className="text-purple-400 text-xs uppercase tracking-wider">Confidence</span>
                      </div>
                      <div className="text-2xl font-normal text-white">{analysisResults.averageConfidence}%</div>
                      <div className="text-zinc-500 text-sm">Average Score</div>
                    </div>
                  </div>

                  {/* Person Results */}
                  <div className="space-y-3 mb-6">
                    <h4 className="text-lg font-normal text-white mb-4">Detected Persons</h4>
                    {analysisResults.results.map((person, index) => (
                      <div key={index} className="p-4 bg-zinc-900/30 rounded-lg hover:bg-zinc-900/50 transition-colors">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${
                              person.confidence > 80 ? 'bg-emerald-600/20' :
                              person.confidence > 60 ? 'bg-yellow-600/20' :
                              person.confidence > 0 ? 'bg-orange-600/20' : 'bg-red-600/20'
                            }`}>
                              <Users className={`h-4 w-4 ${
                                person.confidence > 80 ? 'text-emerald-400' :
                                person.confidence > 60 ? 'text-yellow-400' :
                                person.confidence > 0 ? 'text-orange-400' : 'text-red-400'
                              }`} />
                            </div>
                            <div>
                              <h5 className="text-white font-medium">{person.name}</h5>
                              {person.enrolledId && (
                                <span className="text-xs text-blue-400 bg-blue-600/20 px-2 py-1 rounded">
                                  {person.enrolledId}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`text-lg font-normal ${
                              person.confidence > 80 ? 'text-emerald-400' :
                              person.confidence > 60 ? 'text-yellow-400' :
                              person.confidence > 0 ? 'text-orange-400' : 'text-red-400'
                            }`}>
                              {person.confidence > 0 ? `${person.confidence.toFixed(1)}%` : 'Unknown'}
                            </div>
                            <div className="text-zinc-500 text-xs">Confidence</div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm text-zinc-400">
                          {person.timestamp && (
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {person.timestamp}
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {person.location}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors">
                    <Download className="h-4 w-4" />
                    Export Report
                  </button>
                </MinimalCardContent>
              </MinimalCard>
            )}
          </div>
        )}
      </div>

      {/* Analysis History */}
      <div className="mb-24">
        <div className="flex items-center justify-between mb-12">
          <div>
            <h2 className="text-3xl font-normal text-white mb-3">Analysis History</h2>
            <p className="text-zinc-500 text-lg">Previous media analysis sessions</p>
          </div>
          <button className="flex items-center gap-2 px-6 py-3 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded-lg border border-purple-600/30 transition-colors">
            <Activity className="h-4 w-4" />
            View All
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {analysisHistory.map((analysis, index) => (
            <MinimalCard key={analysis.id} className="hover:scale-[1.02] transition-all duration-300 group">
              <MinimalCardContent className="p-8">
                <div className="grid grid-cols-12 gap-6 items-center">
                  {/* File Info */}
                  <div className="col-span-12 lg:col-span-4">
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-lg ${
                        analysis.type === 'image' 
                          ? 'bg-blue-600/20' 
                          : 'bg-purple-600/20'
                      }`}>
                        {analysis.type === 'image' ? (
                          <FileImage className="h-5 w-5 text-blue-400" />
                        ) : (
                          <FileVideo className="h-5 w-5 text-purple-400" />
                        )}
                      </div>
                      <div>
                        <h3 className="text-white font-medium">{analysis.fileName}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`px-2 py-1 rounded text-xs ${
                            analysis.type === 'image'
                              ? 'bg-blue-600/20 text-blue-400'
                              : 'bg-purple-600/20 text-purple-400'
                          }`}>
                            {analysis.id}
                          </span>
                          <span className="text-zinc-500 text-sm">{analysis.uploadTime}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Stats */}
                  <div className="col-span-12 lg:col-span-6">
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center p-3 bg-zinc-900/30 rounded-lg">
                        <div className="text-emerald-400 text-lg font-normal">{analysis.detectedPersons}</div>
                        <div className="text-zinc-500 text-xs">Persons</div>
                      </div>
                      <div className="text-center p-3 bg-zinc-900/30 rounded-lg">
                        <div className="text-blue-400 text-sm">
                          {analysis.totalDuration || analysis.processingTime}
                        </div>
                        <div className="text-zinc-500 text-xs">{analysis.totalDuration ? 'Duration' : 'Time'}</div>
                      </div>
                      <div className="text-center p-3 bg-zinc-900/30 rounded-lg">
                        <div className="text-purple-400 text-sm">{analysis.confidence}%</div>
                        <div className="text-zinc-500 text-xs">Confidence</div>
                      </div>
                      <div className="text-center p-3 bg-zinc-900/30 rounded-lg">
                        <div className="text-emerald-400 text-sm capitalize">{analysis.status}</div>
                        <div className="text-zinc-500 text-xs">Status</div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Actions */}
                  <div className="col-span-12 lg:col-span-2 flex justify-end">
                    <div className="flex gap-2">
                      <button className="p-2 text-zinc-400 hover:text-white transition-colors hover:bg-zinc-800/50 rounded-lg">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-zinc-400 hover:text-white transition-colors hover:bg-zinc-800/50 rounded-lg">
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex justify-center mb-16">
        <div className="flex gap-6">
          <button 
            onClick={() => onNavigate('persons')}
            className="flex items-center gap-2 px-6 py-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 rounded-lg border border-emerald-600/30 transition-colors"
          >
            <Users className="h-4 w-4" />
            View Enrolled Persons
          </button>
          
          <button 
            onClick={() => onNavigate('cameras')}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors"
          >
            <Camera className="h-4 w-4" />
            Live Camera Feeds
          </button>
        </div>
      </div>
    </>
  );
};