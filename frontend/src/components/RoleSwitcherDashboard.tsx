import React, { useState } from 'react';
import { BoltIcon, CpuChipIcon, UserGroupIcon, ChartBarIcon, GlobeAltIcon, BeakerIcon } from '@heroicons/react/24/outline';

const prosumerWidgets = [
  { icon: BoltIcon, title: 'Energy Production', value: '85.2 kWh', desc: 'Today', color: 'bg-blue-100 text-blue-700' },
  { icon: CpuChipIcon, title: 'Smart Trading', value: '12 trades', desc: 'This week', color: 'bg-purple-100 text-purple-700' },
  { icon: UserGroupIcon, title: 'Communities', value: '3 joined', desc: 'Active', color: 'bg-green-100 text-green-700' },
  { icon: ChartBarIcon, title: 'Analytics', value: '4.8', desc: 'Reputation', color: 'bg-yellow-100 text-yellow-700' },
  { icon: GlobeAltIcon, title: 'Beckn Protocol', value: 'Enabled', desc: 'Cross-network', color: 'bg-orange-100 text-orange-700' },
  { icon: BeakerIcon, title: 'IoT Devices', value: '4', desc: 'Connected', color: 'bg-indigo-100 text-indigo-700' },
];

const consumerWidgets = [
  { icon: BoltIcon, title: 'Energy Requests', value: '2 open', desc: 'Active', color: 'bg-blue-100 text-blue-700' },
  { icon: CpuChipIcon, title: 'Personalized Offers', value: '5 offers', desc: 'Available', color: 'bg-purple-100 text-purple-700' },
  { icon: UserGroupIcon, title: 'Communities', value: '2 joined', desc: 'Active', color: 'bg-green-100 text-green-700' },
  { icon: ChartBarIcon, title: 'Analytics', value: '1.2 MWh', desc: 'Consumed', color: 'bg-yellow-100 text-yellow-700' },
  { icon: GlobeAltIcon, title: 'Beckn Protocol', value: 'Enabled', desc: 'Cross-network', color: 'bg-orange-100 text-orange-700' },
  { icon: BeakerIcon, title: 'IoT Devices', value: '2', desc: 'Connected', color: 'bg-indigo-100 text-indigo-700' },
];

const quickActions = {
  prosumer: [
    { label: 'Optimize My Bid', action: () => alert('Bid optimization launched!') },
    { label: 'View Trading Opportunities', action: () => alert('Trading opportunities shown!') },
    { label: 'Forecast Alerts', action: () => alert('Forecast alerts shown!') },
    { label: 'Community Insights', action: () => alert('Community insights shown!') },
    { label: 'Cross-Network Trading (Beckn)', action: () => alert('Beckn protocol demo!') },
  ],
  consumer: [
    { label: 'Find Best Offers', action: () => alert('Best offers shown!') },
    { label: 'Personalized Recommendations', action: () => alert('Personalized recommendations!') },
    { label: 'Forecast Alerts', action: () => alert('Forecast alerts shown!') },
    { label: 'Join Community', action: () => alert('Community join flow!') },
    { label: 'Cross-Network Discovery (Beckn)', action: () => alert('Beckn protocol demo!') },
  ]
};

const RoleSwitcherDashboard: React.FC = () => {
  const [role, setRole] = useState<'prosumer' | 'consumer'>('prosumer');

  const widgets = role === 'prosumer' ? prosumerWidgets : consumerWidgets;
  const actions = quickActions[role];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center space-x-4 mb-6">
        <span className="font-medium text-gray-700">Profile:</span>
        <button
          className={`px-4 py-2 rounded-lg border ${role === 'prosumer' ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 border-blue-600'} transition`}
          onClick={() => setRole('prosumer')}
        >
          Prosumer
        </button>
        <button
          className={`px-4 py-2 rounded-lg border ${role === 'consumer' ? 'bg-green-600 text-white' : 'bg-white text-green-600 border-green-600'} transition`}
          onClick={() => setRole('consumer')}
        >
          Consumer
        </button>
      </div>

      {/* Widgets */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        {widgets.map((w, idx) => (
          <div key={idx} className={`rounded-lg p-4 flex items-center space-x-4 shadow-sm border ${w.color}`}>
            <w.icon className="h-8 w-8" />
            <div>
              <div className="text-lg font-bold">{w.value}</div>
              <div className="text-sm font-medium">{w.title}</div>
              <div className="text-xs text-gray-500">{w.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
        <div className="flex flex-wrap gap-2">
          {actions.map((a, idx) => (
            <button
              key={idx}
              onClick={a.action}
              className="px-4 py-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition"
            >
              {a.label}
            </button>
          ))}
        </div>
      </div>

      {/* Demo Workflow Steps */}
      <div className="bg-slate-50 border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Demo Workflow</h3>
        <ol className="list-decimal ml-6 text-sm text-gray-700 space-y-1">
          <li>Switch between <b>Prosumer</b> and <b>Consumer</b> to see tailored dashboards and actions.</li>
          <li>Explore <b>Agent Dashboard</b> for real-time agent status, roles, and responsibilities.</li>
          <li>Use <b>AI Assistant</b> for chat-based queries, agent selection, and reasoning display.</li>
          <li>Try <b>Bid Matching</b> and <b>Smart Trading</b> (prosumer) or <b>Personalized Offers</b> (consumer).</li>
          <li>View <b>Energy Map</b> for locality energy flows and community nodes.</li>
          <li>Check <b>Beckn Protocol</b> integration for cross-network energy discovery.</li>
          <li>See <b>Forecast Alerts</b> and <b>Analytics</b> for insights and recommendations.</li>
        </ol>
      </div>
    </div>
  );
};

export default RoleSwitcherDashboard;
