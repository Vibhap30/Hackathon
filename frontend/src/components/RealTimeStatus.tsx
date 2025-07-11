import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAPI } from '../hooks/useAPI';
import {
  BoltIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  SignalIcon,
  CpuChipIcon,
  WifiIcon
} from '@heroicons/react/24/outline';

interface SystemStatus {
  id: string;
  service: string;
  status: 'healthy' | 'warning' | 'critical' | 'offline';
  lastCheck: string;
  responseTime: number;
  uptime: number;
  details?: string;
}

interface MarketMetrics {
  totalTrades: number;
  activeUsers: number;
  energyTraded: number;
  averagePrice: number;
  marketVolume: number;
  networkLoad: number;
}

interface RealtimeAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

interface QuantumStatus {
  isOnline: boolean;
  quantumAdvantage: number;
  activeAlgorithms: string[];
  processingPower: number;
  errorRate: number;
}

const RealTimeStatus: React.FC = () => {
  const [systemStatuses, setSystemStatuses] = useState<SystemStatus[]>([]);
  const [marketMetrics, setMarketMetrics] = useState<MarketMetrics | null>(null);
  const [alerts, setAlerts] = useState<RealtimeAlert[]>([]);
  const [quantumStatus, setQuantumStatus] = useState<QuantumStatus | null>(null);
  const [isConnected, setIsConnected] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  const api = useAPI();

  useEffect(() => {
    // Initial load
    loadSystemStatus();
    loadMarketMetrics();
    loadAlerts();
    loadQuantumStatus();

    // Set up auto-refresh
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        loadSystemStatus();
        loadMarketMetrics();
        loadAlerts();
        loadQuantumStatus();
      }, 5000); // Refresh every 5 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const loadSystemStatus = async () => {
    try {
      const data = await api.get<SystemStatus[]>('/api/v1/system/status');
      setSystemStatuses(data);
      setIsConnected(true);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to load system status:', err);
      setIsConnected(false);
    }
  };

  const loadMarketMetrics = async () => {
    try {
      const data = await api.get<MarketMetrics>('/api/v1/analytics/realtime-metrics');
      setMarketMetrics(data);
    } catch (err) {
      console.error('Failed to load market metrics:', err);
    }
  };

  const loadAlerts = async () => {
    try {
      const data = await api.get<RealtimeAlert[]>('/api/v1/alerts/active');
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
  };

  const loadQuantumStatus = async () => {
    try {
      const data = await api.get<QuantumStatus>('/api/v1/quantum/status');
      setQuantumStatus(data);
    } catch (err) {
      console.error('Failed to load quantum status:', err);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await api.post(`/api/v1/alerts/${alertId}/acknowledge`);
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      ));
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const getStatusIcon = (status: SystemStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'critical':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'offline':
        return <XCircleIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <XCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: SystemStatus['status']) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'offline':
        return 'bg-gray-50 border-gray-200 text-gray-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getAlertIcon = (type: RealtimeAlert['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <SignalIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const formatUptime = (uptime: number) => {
    const days = Math.floor(uptime / (24 * 60 * 60));
    const hours = Math.floor((uptime % (24 * 60 * 60)) / (60 * 60));
    const minutes = Math.floor((uptime % (60 * 60)) / 60);
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <SignalIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">System Status</h1>
              <p className="text-gray-600">Real-time monitoring of PowerShare platform</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm ${
                autoRefresh 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              <ArrowPathIcon className="h-4 w-4" />
              <span>Auto Refresh</span>
            </button>
            
            <span className="text-sm text-gray-500">
              Last update: {lastUpdate.toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>

      {/* Market Metrics */}
      {marketMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-sm p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-gray-900">{marketMetrics.activeUsers}</p>
              </div>
              <BoltIcon className="h-8 w-8 text-blue-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg shadow-sm p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Trades</p>
                <p className="text-2xl font-bold text-gray-900">{marketMetrics.totalTrades}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-green-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg shadow-sm p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Energy Traded</p>
                <p className="text-2xl font-bold text-gray-900">{marketMetrics.energyTraded.toFixed(1)}</p>
                <p className="text-xs text-gray-500">kWh</p>
              </div>
              <BoltIcon className="h-8 w-8 text-yellow-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-sm p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Price</p>
                <p className="text-2xl font-bold text-gray-900">${marketMetrics.averagePrice.toFixed(3)}</p>
                <p className="text-xs text-gray-500">per kWh</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-lg shadow-sm p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Market Volume</p>
                <p className="text-2xl font-bold text-gray-900">${marketMetrics.marketVolume.toFixed(0)}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-indigo-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-lg shadow-sm p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Network Load</p>
                <p className="text-2xl font-bold text-gray-900">{marketMetrics.networkLoad.toFixed(0)}%</p>
              </div>
              <WifiIcon className="h-8 w-8 text-red-600" />
            </div>
          </motion.div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Services Status */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Services</h2>
          <div className="space-y-3">
            {systemStatuses.map((status, index) => (
              <motion.div
                key={status.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-3 rounded-lg border ${getStatusColor(status.status)}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(status.status)}
                    <div>
                      <p className="font-medium">{status.service}</p>
                      <p className="text-xs opacity-75">
                        Uptime: {formatUptime(status.uptime)} • Response: {status.responseTime}ms
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs opacity-75">
                      {new Date(status.lastCheck).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                {status.details && (
                  <p className="text-xs mt-2 opacity-75">{status.details}</p>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Quantum Computing Status */}
        {quantumStatus && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <CpuChipIcon className="h-5 w-5 mr-2 text-purple-600" />
              Quantum Computing
            </h2>
            <div className="space-y-4">
              <div className={`p-4 rounded-lg ${
                quantumStatus.isOnline 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-red-50 border border-red-200'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Quantum Engine</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    quantumStatus.isOnline
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {quantumStatus.isOnline ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Quantum Advantage:</span>
                  <span className="ml-2 font-medium text-purple-600">
                    {quantumStatus.quantumAdvantage.toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Processing Power:</span>
                  <span className="ml-2 font-medium">
                    {quantumStatus.processingPower.toFixed(0)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Error Rate:</span>
                  <span className="ml-2 font-medium">
                    {(quantumStatus.errorRate * 100).toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Active Algorithms:</span>
                  <span className="ml-2 font-medium">
                    {quantumStatus.activeAlgorithms.length}
                  </span>
                </div>
              </div>

              {quantumStatus.activeAlgorithms.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Active Algorithms:</p>
                  <div className="flex flex-wrap gap-2">
                    {quantumStatus.activeAlgorithms.map((algorithm, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full"
                      >
                        {algorithm}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Active Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Alerts</h2>
          <div className="space-y-3">
            <AnimatePresence>
              {alerts.filter(alert => !alert.acknowledged).map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 border rounded-lg bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getAlertIcon(alert.type)}
                      <div>
                        <p className="font-medium text-gray-900">{alert.title}</p>
                        <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(alert.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      Acknowledge
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeStatus;