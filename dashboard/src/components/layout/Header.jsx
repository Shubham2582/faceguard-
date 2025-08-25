import React from 'react';
import { Bell, User } from 'lucide-react';

export const Header = () => {
  return (
    <header className="border-b border-zinc-900 px-8 py-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-zinc-400">Welcome back</div>
            <div className="text-lg font-medium">Security Admin</div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="relative p-2">
            <Bell className="h-5 w-5 text-zinc-500" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
          </button>
          <button className="p-2">
            <User className="h-5 w-5 text-zinc-500" />
          </button>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
            Contact
          </button>
        </div>
      </div>
    </header>
  );
};