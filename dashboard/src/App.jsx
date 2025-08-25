import React, { useState } from 'react';
import { Sidebar } from '@/components/ui/Sidebar';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { Dashboard } from '@/components/sections/Dashboard';
import { PersonsPage } from '@/components/sections/PersonsPage';
import { CamerasPage } from '@/components/sections/CamerasPage';
import { AnalyticsPage } from '@/components/sections/AnalyticsPage';
import { MediaAnalysisPage } from '@/components/sections/MediaAnalysisPage';
import { AddPersonPage } from '@/components/sections/AddPersonPage';
import { NotificationsPage } from '@/components/sections/NotificationsPage';
import { MonitoringPage } from '@/components/sections/MonitoringPage';
import { SettingsPage } from '@/components/sections/SettingsPage';

const PlaceholderPage = ({ title, subtitle }) => (
  <div className="text-center py-20">
    <div className="inline-block bg-blue-600/10 border border-blue-600/20 text-blue-400 px-3 py-1.5 rounded-full text-xs font-medium mb-8 tracking-wider">
      COMING SOON
    </div>
    <h1 className="text-5xl lg:text-6xl font-normal mb-6 tracking-tight leading-tight">
      {title} <span className="italic text-zinc-600 font-light">{subtitle}</span>
    </h1>
    <p className="text-zinc-500 text-lg max-w-2xl mx-auto leading-relaxed">
      This feature is currently under development. Check back soon for updates.
    </p>
  </div>
);

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleNavigation = (page) => {
    setCurrentPage(page);
  };

  const renderCurrentPage = () => {
    switch(currentPage) {
      case 'dashboard':
        return <Dashboard onNavigate={handleNavigation} />;
      case 'persons':
        return <PersonsPage onNavigate={handleNavigation} />;
      case 'cameras':
        return <CamerasPage onNavigate={handleNavigation} />;
      case 'analytics':
        return <AnalyticsPage onNavigate={handleNavigation} />;
      case 'upload':
        return <MediaAnalysisPage onNavigate={handleNavigation} />;
      case 'enroll':
        return <AddPersonPage onNavigate={handleNavigation} />;
      case 'notifications':
        return <NotificationsPage onNavigate={handleNavigation} />;
      case 'monitoring':
        return <MonitoringPage onNavigate={handleNavigation} />;
      case 'settings':
        return <SettingsPage onNavigate={handleNavigation} />;
      default:
        return <Dashboard onNavigate={handleNavigation} />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Sidebar */}
      <Sidebar 
        currentPage={currentPage}
        onNavigate={handleNavigation}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content */}
      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="px-8 py-12">
          {renderCurrentPage()}
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
}

export default App;