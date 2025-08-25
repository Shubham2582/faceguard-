import React from 'react';
import { Shield } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="border-t border-zinc-900 px-8 py-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="h-6 w-6 text-blue-500" />
          <span className="text-lg font-medium">FaceGuard</span>
        </div>
        <div className="hidden lg:flex items-center space-x-8">
          <a href="#" className="text-zinc-500 hover:text-white text-sm transition-colors">About</a>
          <a href="#" className="text-zinc-500 hover:text-white text-sm transition-colors">Features</a>
          <a href="#" className="text-zinc-500 hover:text-white text-sm transition-colors">Advantages</a>
          <a href="#" className="text-zinc-500 hover:text-white text-sm transition-colors">Pricing</a>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
            Contact
          </button>
        </div>
      </div>
    </footer>
  );
};