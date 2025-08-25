import React, { useState } from 'react';
import {
  Search,
  Plus,
  Eye,
  Users,
  CheckCircle,
  Activity,
  TrendingUp
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardImage, MinimalCardTitle } from '@/components/ui/MinimalCard';
import { PersonProfile } from './PersonProfile';
import { enrolledPersons } from '@/data/mockData';
import { getStatusColor, getRiskLevelColor } from '@/lib/utils';

export const PersonsPage = ({ onNavigate }) => {
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredPersons = enrolledPersons.filter(person => {
    const matchesSearch = person.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         person.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         person.department.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || person.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  if (selectedPerson) {
    return (
      <PersonProfile 
        person={selectedPerson} 
        onBack={() => setSelectedPerson(null)} 
      />
    );
  }

  return (
    <>
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="inline-block bg-blue-600/10 border border-blue-600/20 text-blue-400 px-3 py-1.5 rounded-full text-xs font-medium mb-8 tracking-wider">
          ENROLLED PERSONS
        </div>
        <h1 className="text-5xl lg:text-6xl font-normal mb-6 tracking-tight leading-tight">
          Person <span className="italic text-zinc-600 font-light">Profiles</span>
        </h1>
        <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
          Comprehensive profiles and tracking data for all enrolled individuals in the surveillance system.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-12">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search by name, email, or department..."
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
            <option value="inactive">Inactive</option>
          </select>
          <button 
            onClick={() => onNavigate('enroll')}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add Person
          </button>
        </div>
      </div>

      {/* Person Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-16">
        {filteredPersons.map((person) => (
          <MinimalCard 
            key={person.id} 
            className="group hover:scale-[1.02] transition-all duration-300 cursor-pointer"
            onClick={() => setSelectedPerson(person)}
          >
            <MinimalCardImage 
              src={person.images[0]}
              alt={person.name}
              className="h-40"
            />
            <MinimalCardContent className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <MinimalCardTitle className="text-base mb-1">{person.name}</MinimalCardTitle>
                  <div className="text-xs text-zinc-500">{person.position}</div>
                  <div className="text-xs text-zinc-600">{person.department}</div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(person.status)}`}>
                  {person.status}
                </div>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">Detections</span>
                  <span className="text-white font-medium">{person.totalDetections}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">Confidence</span>
                  <span className="text-emerald-400 font-medium">{person.averageConfidence}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">Last Seen</span>
                  <span className="text-zinc-300">{person.lastSeen}</span>
                </div>
              </div>
              
              <div className="pt-4 border-t border-zinc-800">
                <div className="flex items-center justify-between">
                  <div className={`px-2 py-1 rounded text-xs border ${getRiskLevelColor(person.riskLevel)}`}>
                    {person.riskLevel.toUpperCase()} RISK
                  </div>
                  <button className="text-zinc-500 hover:text-white transition-colors group-hover:text-blue-400">
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </MinimalCardContent>
          </MinimalCard>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MinimalCard className="text-center">
          <MinimalCardContent className="p-6">
            <div className="p-3 bg-blue-600/20 rounded-lg mb-4 w-fit mx-auto">
              <Users className="h-6 w-6 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{enrolledPersons.length}</div>
            <div className="text-sm text-zinc-400">Total Enrolled</div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="text-center">
          <MinimalCardContent className="p-6">
            <div className="p-3 bg-emerald-600/20 rounded-lg mb-4 w-fit mx-auto">
              <CheckCircle className="h-6 w-6 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{enrolledPersons.filter(p => p.status === 'active').length}</div>
            <div className="text-sm text-zinc-400">Active Persons</div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="text-center">
          <MinimalCardContent className="p-6">
            <div className="p-3 bg-purple-600/20 rounded-lg mb-4 w-fit mx-auto">
              <Activity className="h-6 w-6 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{enrolledPersons.reduce((sum, p) => sum + p.totalDetections, 0)}</div>
            <div className="text-sm text-zinc-400">Total Detections</div>
          </MinimalCardContent>
        </MinimalCard>

        <MinimalCard className="text-center">
          <MinimalCardContent className="p-6">
            <div className="p-3 bg-orange-600/20 rounded-lg mb-4 w-fit mx-auto">
              <TrendingUp className="h-6 w-6 text-orange-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">96.2%</div>
            <div className="text-sm text-zinc-400">Avg Accuracy</div>
          </MinimalCardContent>
        </MinimalCard>
      </div>
    </>
  );
};