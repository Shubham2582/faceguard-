import React, { useState } from 'react';
import {
  Settings, User, Shield, Bell, Camera, Monitor, Save, RotateCcw, CheckCircle,
  AlertTriangle, Info, Timer, Lock, Mail, Smartphone, Volume2, VolumeX,
  RefreshCw, BarChart3, HardDrive, Network, Globe, Key, Eye, EyeOff
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardTitle } from '@/components/ui/MinimalCard';

export const SettingsPage = ({ onNavigate }) => {
  const [activeSection, setActiveSection] = useState('general');
  const [settings, setSettings] = useState({
    general: {
      systemName: 'FaceGuard Security System',
      timezone: 'UTC-05:00',
      language: 'en',
      dateFormat: 'MM/DD/YYYY'
    },
    security: {
      sessionTimeout: 30,
      requireMFA: false,
      loginAttempts: 5,
      autoLockout: true
    },
    notifications: {
      emailEnabled: true,
      smsEnabled: false,
      soundEnabled: true,
      quietHours: { enabled: false, start: '22:00', end: '08:00' }
    },
    cameras: {
      defaultQuality: 'high',
      recordingEnabled: true,
      faceDetectionThreshold: 0.75,
      maxStreams: 10
    },
    system: {
      autoUpdates: true,
      debugMode: false,
      logLevel: 'info',
      storageLimit: 500
    }
  });

  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  const settingSections = [
    { id: 'general', label: 'General', icon: Settings, color: 'blue' },
    { id: 'security', label: 'Security', icon: Shield, color: 'red' },
    { id: 'notifications', label: 'Notifications', icon: Bell, color: 'orange' },
    { id: 'cameras', label: 'Cameras', icon: Camera, color: 'purple' },
    { id: 'system', label: 'System', icon: Monitor, color: 'zinc' }
  ];

  const updateSetting = (section, key, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
    setUnsavedChanges(true);
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaveStatus('success');
      setUnsavedChanges(false);
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const ToggleSwitch = ({ enabled, onChange, label, description }) => (
    <div className="flex items-center justify-between">
      <div>
        <div className="text-white font-medium">{label}</div>
        {description && <div className="text-sm text-zinc-400">{description}</div>}
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          enabled ? 'bg-blue-600' : 'bg-zinc-700'
        }`}
      >
        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`} />
      </button>
    </div>
  );

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">System Name</label>
          <input
            type="text"
            value={settings.general.systemName}
            onChange={(e) => updateSetting('general', 'systemName', e.target.value)}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Timezone</label>
          <select
            value={settings.general.timezone}
            onChange={(e) => updateSetting('general', 'timezone', e.target.value)}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="UTC-05:00">UTC-05:00 (Eastern)</option>
            <option value="UTC-06:00">UTC-06:00 (Central)</option>
            <option value="UTC-07:00">UTC-07:00 (Mountain)</option>
            <option value="UTC-08:00">UTC-08:00 (Pacific)</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Language</label>
          <select
            value={settings.general.language}
            onChange={(e) => updateSetting('general', 'language', e.target.value)}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Date Format</label>
          <select
            value={settings.general.dateFormat}
            onChange={(e) => updateSetting('general', 'dateFormat', e.target.value)}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">
            <Timer className="inline h-4 w-4 mr-1" />
            Session Timeout (minutes)
          </label>
          <input
            type="number"
            value={settings.security.sessionTimeout}
            onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-red-500 transition-colors"
            min="5" max="120"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">
            <Lock className="inline h-4 w-4 mr-1" />
            Failed Login Attempts
          </label>
          <input
            type="number"
            value={settings.security.loginAttempts}
            onChange={(e) => updateSetting('security', 'loginAttempts', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-red-500 transition-colors"
            min="3" max="10"
          />
        </div>
      </div>
      <div className="space-y-4">
        <ToggleSwitch
          enabled={settings.security.requireMFA}
          onChange={(value) => updateSetting('security', 'requireMFA', value)}
          label="Multi-Factor Authentication"
          description="Require additional verification for login"
        />
        <ToggleSwitch
          enabled={settings.security.autoLockout}
          onChange={(value) => updateSetting('security', 'autoLockout', value)}
          label="Auto Account Lockout"
          description="Lock accounts after failed attempts"
        />
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <ToggleSwitch
          enabled={settings.notifications.emailEnabled}
          onChange={(value) => updateSetting('notifications', 'emailEnabled', value)}
          label="Email Notifications"
          description="Receive alerts via email"
        />
        <ToggleSwitch
          enabled={settings.notifications.smsEnabled}
          onChange={(value) => updateSetting('notifications', 'smsEnabled', value)}
          label="SMS Notifications"
          description="Critical alerts via SMS"
        />
        <ToggleSwitch
          enabled={settings.notifications.soundEnabled}
          onChange={(value) => updateSetting('notifications', 'soundEnabled', value)}
          label="Sound Alerts"
          description="Play sound for notifications"
        />
      </div>
      <div className="space-y-4">
        <ToggleSwitch
          enabled={settings.notifications.quietHours.enabled}
          onChange={(value) => updateSetting('notifications', 'quietHours', { 
            ...settings.notifications.quietHours, enabled: value 
          })}
          label="Quiet Hours"
          description="Disable non-critical notifications"
        />
        {settings.notifications.quietHours.enabled && (
          <div className="grid grid-cols-2 gap-4 ml-6">
            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">Start</label>
              <input
                type="time"
                value={settings.notifications.quietHours.start}
                onChange={(e) => updateSetting('notifications', 'quietHours', {
                  ...settings.notifications.quietHours, start: e.target.value
                })}
                className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-orange-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">End</label>
              <input
                type="time"
                value={settings.notifications.quietHours.end}
                onChange={(e) => updateSetting('notifications', 'quietHours', {
                  ...settings.notifications.quietHours, end: e.target.value
                })}
                className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-orange-500 transition-colors"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderCameraSettings = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Default Quality</label>
          <select
            value={settings.cameras.defaultQuality}
            onChange={(e) => updateSetting('cameras', 'defaultQuality', e.target.value)}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-purple-500 transition-colors"
          >
            <option value="low">Low (480p)</option>
            <option value="medium">Medium (720p)</option>
            <option value="high">High (1080p)</option>
            <option value="ultra">Ultra (4K)</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Max Concurrent Streams</label>
          <input
            type="number"
            value={settings.cameras.maxStreams}
            onChange={(e) => updateSetting('cameras', 'maxStreams', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-purple-500 transition-colors"
            min="1" max="50"
          />
        </div>
      </div>
      <div className="space-y-4">
        <ToggleSwitch
          enabled={settings.cameras.recordingEnabled}
          onChange={(value) => updateSetting('cameras', 'recordingEnabled', value)}
          label="Recording Enabled"
          description="Automatically record from all cameras"
        />
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">
            Detection Threshold: {(settings.cameras.faceDetectionThreshold * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            min="0.5" max="0.95" step="0.05"
            value={settings.cameras.faceDetectionThreshold}
            onChange={(e) => updateSetting('cameras', 'faceDetectionThreshold', parseFloat(e.target.value))}
            className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-zinc-500 mt-1">
            <span>Less Strict</span>
            <span>More Strict</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSystemSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <ToggleSwitch
          enabled={settings.system.autoUpdates}
          onChange={(value) => updateSetting('system', 'autoUpdates', value)}
          label="Automatic Updates"
          description="Install updates automatically"
        />
        <ToggleSwitch
          enabled={settings.system.debugMode}
          onChange={(value) => updateSetting('system', 'debugMode', value)}
          label="Debug Mode"
          description="Enable detailed logging"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Storage Limit (GB)</label>
          <input
            type="number"
            value={settings.system.storageLimit}
            onChange={(e) => updateSetting('system', 'storageLimit', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-zinc-500 transition-colors"
            min="100" max="5000"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-2">Log Level</label>
          <select
            value={settings.system.logLevel}
            onChange={(e) => updateSetting('system', 'logLevel', e.target.value)}
            className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-zinc-500 transition-colors"
          >
            <option value="error">Error Only</option>
            <option value="warn">Warning & Error</option>
            <option value="info">Info & Above</option>
            <option value="debug">All (Debug)</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'general': return renderGeneralSettings();
      case 'security': return renderSecuritySettings();
      case 'notifications': return renderNotificationSettings();
      case 'cameras': return renderCameraSettings();
      case 'system': return renderSystemSettings();
      default: return renderGeneralSettings();
    }
  };

  return (
    <>
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="inline-block bg-zinc-600/10 border border-zinc-600/20 text-zinc-400 px-4 py-2 rounded-full text-xs font-medium mb-10 tracking-wider">
          SETTINGS
        </div>
        <h1 className="text-5xl lg:text-6xl font-normal mb-8 tracking-tight leading-tight">
          System <span className="italic text-zinc-600 font-light">Configuration</span>
        </h1>
        <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
          Configure system preferences, security settings, and operational parameters to customize your FaceGuard experience.
        </p>
      </div>

      {/* Status Bar */}
      {(unsavedChanges || saveStatus) && (
        <div className="mb-8">
          <MinimalCard className={`border-${saveStatus === 'success' ? 'emerald' : saveStatus === 'error' ? 'red' : 'yellow'}-900/50 bg-${saveStatus === 'success' ? 'emerald' : saveStatus === 'error' ? 'red' : 'yellow'}-950/20`}>
            <MinimalCardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {saveStatus === 'success' && <CheckCircle className="h-5 w-5 text-emerald-400" />}
                  {saveStatus === 'error' && <AlertTriangle className="h-5 w-5 text-red-400" />}
                  {unsavedChanges && !saveStatus && <Info className="h-5 w-5 text-yellow-400" />}
                  <span className={`text-${saveStatus === 'success' ? 'emerald' : saveStatus === 'error' ? 'red' : 'yellow'}-400`}>
                    {saveStatus === 'success' && 'Settings saved successfully'}
                    {saveStatus === 'error' && 'Failed to save settings'}
                    {unsavedChanges && !saveStatus && 'You have unsaved changes'}
                  </span>
                </div>
                {unsavedChanges && !saveStatus && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setUnsavedChanges(false)}
                      className="px-3 py-1 text-sm text-zinc-400 hover:text-white transition-colors"
                    >
                      Reset
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={isLoading}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors disabled:opacity-50"
                    >
                      {isLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                      {isLoading ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                )}
              </div>
            </MinimalCardContent>
          </MinimalCard>
        </div>
      )}

      {/* Settings Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <MinimalCard>
            <MinimalCardContent className="p-6">
              <h3 className="text-lg font-medium text-white mb-6">Categories</h3>
              <nav className="space-y-2">
                {settingSections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                        activeSection === section.id
                          ? `bg-${section.color}-600/20 text-${section.color}-400 border border-${section.color}-600/30`
                          : 'text-zinc-400 hover:text-white hover:bg-zinc-950/50'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="font-medium">{section.label}</span>
                    </button>
                  );
                })}
              </nav>
            </MinimalCardContent>
          </MinimalCard>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          <MinimalCard>
            <MinimalCardContent className="p-8">
              <div className="flex items-center gap-3 mb-8">
                {settingSections.find(s => s.id === activeSection) && (
                  <>
                    <div className={`p-2 bg-${settingSections.find(s => s.id === activeSection).color}-600/20 rounded-lg`}>
                      {React.createElement(settingSections.find(s => s.id === activeSection).icon, {
                        className: `h-5 w-5 text-${settingSections.find(s => s.id === activeSection).color}-400`
                      })}
                    </div>
                    <h2 className="text-2xl font-normal text-white">
                      {settingSections.find(s => s.id === activeSection).label} Settings
                    </h2>
                  </>
                )}
              </div>
              {renderActiveSection()}
            </MinimalCardContent>
          </MinimalCard>
        </div>
      </div>
    </>
  );
};