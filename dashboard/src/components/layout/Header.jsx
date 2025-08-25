import React from 'react';
import { Bell, User } from 'lucide-react';

export const Header = () => {
  return (
    <header className="border-b border-zinc-900/50 px-6 py-2 backdrop-blur-sm bg-black/50">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-xs text-zinc-500">Welcome back</div>
            <div className="text-sm font-medium text-zinc-300">Security Admin</div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* System Status */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1 bg-emerald-950/30 border border-emerald-900/50 rounded-full">
            <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
            <span className="text-xs text-emerald-400 font-medium">Online</span>
          </div>
          
          {/* Notifications */}
          <button className="relative p-2 hover:bg-zinc-800/50 rounded-lg transition-colors group">
            <Bell className="h-4 w-4 text-zinc-400 group-hover:text-zinc-300" />
            <span className="absolute top-1 right-1 h-1.5 w-1.5 bg-red-500 rounded-full animate-pulse"></span>
          </button>
          
          {/* User Menu */}
          <button className="p-2 hover:bg-zinc-800/50 rounded-lg transition-colors group">
            <User className="h-4 w-4 text-zinc-400 group-hover:text-zinc-300" />
          </button>
          
          {/* Contact Button */}
          <button className="bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 hover:text-blue-300 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 border border-blue-600/30 hover:border-blue-600/50">
            Contact
          </button>
        </div>
      </div>
    </header>
  );
};