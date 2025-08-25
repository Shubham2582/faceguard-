import React from 'react';
import {
  ChevronLeft,
  Eye,
  MapPin,
  Target,
  Camera,
  Mail,
  Phone,
  Building,
  Badge,
  Calendar,
  Clock
} from 'lucide-react';
import { MinimalCard, MinimalCardContent } from '@/components/ui/MinimalCard';
import { ImageCarousel } from '@/components/ui/ImageCarousel';
import { getRiskLevelColor } from '@/lib/utils';

export const PersonProfile = ({ person, onBack }) => {
  return (
    <>
      {/* Back Button */}
      <button 
        onClick={onBack}
        className="flex items-center gap-2 mb-8 text-zinc-400 hover:text-white transition-colors"
      >
        <ChevronLeft className="h-4 w-4" />
        Back to All Persons
      </button>

      {/* Person Profile Header */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {/* Profile Image & Basic Info */}
        <MinimalCard className="lg:col-span-1">
          <MinimalCardContent className="p-8 text-center">
            <ImageCarousel images={person.images} person={person.name} />
            <div className="mt-6">
              <h1 className="text-2xl font-bold text-white mb-2">{person.name}</h1>
              <p className="text-zinc-400 mb-1">{person.position}</p>
              <p className="text-zinc-500 text-sm">{person.department}</p>
              
              <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium mt-4 border ${getRiskLevelColor(person.riskLevel)}`}>
                {person.riskLevel.toUpperCase()} RISK
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>

        {/* Contact & Details */}
        <MinimalCard className="lg:col-span-2">
          <MinimalCardContent className="p-8">
            <h2 className="text-xl font-semibold text-white mb-6">Personal Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-blue-400" />
                  <div>
                    <div className="text-sm text-zinc-400">Email</div>
                    <div className="text-white">{person.email}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="h-5 w-5 text-emerald-400" />
                  <div>
                    <div className="text-sm text-zinc-400">Phone</div>
                    <div className="text-white">{person.phone}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Building className="h-5 w-5 text-purple-400" />
                  <div>
                    <div className="text-sm text-zinc-400">Department</div>
                    <div className="text-white">{person.department}</div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Badge className="h-5 w-5 text-orange-400" />
                  <div>
                    <div className="text-sm text-zinc-400">Employee ID</div>
                    <div className="text-white">{person.id}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Calendar className="h-5 w-5 text-cyan-400" />
                  <div>
                    <div className="text-sm text-zinc-400">Enrolled Date</div>
                    <div className="text-white">{person.enrolledDate}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-pink-400" />
                  <div>
                    <div className="text-sm text-zinc-400">Last Seen</div>
                    <div className="text-white">{person.lastSeen}</div>
                  </div>
                </div>
              </div>
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <MinimalCard className="hover:scale-105 transition-transform">
          <MinimalCardContent className="p-6 text-center">
            <div className="p-3 bg-blue-600/20 rounded-lg mb-4 w-fit mx-auto">
              <Eye className="h-6 w-6 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{person.totalDetections}</div>
            <div className="text-sm text-zinc-400">Total Detections</div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-105 transition-transform">
          <MinimalCardContent className="p-6 text-center">
            <div className="p-3 bg-emerald-600/20 rounded-lg mb-4 w-fit mx-auto">
              <MapPin className="h-6 w-6 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{person.locationsVisited}</div>
            <div className="text-sm text-zinc-400">Locations Visited</div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-105 transition-transform">
          <MinimalCardContent className="p-6 text-center">
            <div className="p-3 bg-purple-600/20 rounded-lg mb-4 w-fit mx-auto">
              <Target className="h-6 w-6 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{person.averageConfidence}</div>
            <div className="text-sm text-zinc-400">Avg Confidence</div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="hover:scale-105 transition-transform">
          <MinimalCardContent className="p-6 text-center">
            <div className="p-3 bg-orange-600/20 rounded-lg mb-4 w-fit mx-auto">
              <Camera className="h-6 w-6 text-orange-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{person.images.length}</div>
            <div className="text-sm text-zinc-400">Profile Images</div>
          </MinimalCardContent>
        </MinimalCard>
      </div>

      {/* Recent Activity & Location History */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Detections */}
        <MinimalCard>
          <MinimalCardContent className="p-8">
            <h2 className="text-xl font-semibold text-white mb-6">Recent Detections</h2>
            <div className="space-y-4">
              {person.recentDetections.map((detection, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-zinc-900/30 rounded-lg hover:bg-zinc-900/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-blue-600/20 rounded-lg">
                      <Camera className="h-4 w-4 text-blue-400" />
                    </div>
                    <div>
                      <div className="text-white font-medium">{detection.location}</div>
                      <div className="text-zinc-400 text-sm">{detection.camera} • {detection.time}</div>
                    </div>
                  </div>
                  <div className="text-emerald-400 font-medium">{detection.confidence}</div>
                </div>
              ))}
            </div>
          </MinimalCardContent>
        </MinimalCard>

        {/* Location History */}
        <MinimalCard>
          <MinimalCardContent className="p-8">
            <h2 className="text-xl font-semibold text-white mb-6">Location History</h2>
            <div className="space-y-4">
              {person.locationHistory.map((location, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-zinc-900/30 rounded-lg hover:bg-zinc-900/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-emerald-600/20 rounded-lg">
                      <MapPin className="h-4 w-4 text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-white font-medium">{location.location}</div>
                      <div className="text-zinc-400 text-sm">Last visit: {location.lastVisit}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-medium">{location.visits}</div>
                    <div className="text-zinc-400 text-xs">visits</div>
                  </div>
                </div>
              ))}
            </div>
          </MinimalCardContent>
        </MinimalCard>
      </div>
    </>
  );
};