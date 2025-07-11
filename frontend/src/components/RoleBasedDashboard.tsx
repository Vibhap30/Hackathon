import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import {
  UserIcon,
  BuildingOfficeIcon,
  CpuChipIcon,
  ChartBarIcon,
  BoltIcon,
  CogIcon,
  ClockIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';

interface DashboardStats {
  energyProduced: number;
  energyConsumed: number;
  energyTraded: number;
  totalEarnings: number;
  totalSpent: number;
  communitiesJoined: number;
  reputationScore: number;
  activeTransactions: number;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  action: () => void;
  available: boolean;
}

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

const RoleBasedDashboard: React.FC = () => {
  const { user, isRole } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [quickActions, setQuickActions] = useState<QuickAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load user analytics and stats
      const userStats = await apiService.getUserAnalytics();
      
      // Mock dashboard stats based on user role
      const dashboardStats: DashboardStats = {
        energyProduced: userStats?.total_energy_produced || 0,
        energyConsumed: userStats?.total_energy_consumed || 0,
        energyTraded: userStats?.total_energy_traded || 0,
        totalEarnings: userStats?.total_earnings || 0,
        totalSpent: userStats?.total_spent || 0,
        communitiesJoined: userStats?.communities_count || 0,
        reputationScore: 0, // user?.reputation_score || 0,
        activeTransactions: userStats?.active_transactions || 0
      };
      
      setStats(dashboardStats);
      
      // Load notifications
      const mockNotifications: Notification[] = [
        {
          id: '1',
          type: 'success',
          title: 'Energy Transaction Complete',
          message: 'Your energy sale of 50 kWh has been completed successfully.',
          timestamp: new Date().toISOString(),
          read: false
        },
        {
          id: '2',
          type: 'warning',
          title: 'Low Energy Production',
          message: 'Your solar panels are producing below expected capacity.',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          read: false
        },
        {
          id: '3',
          type: 'info',
          title: 'Community Meeting',
          message: 'Monthly community meeting scheduled for tomorrow at 7 PM.',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          read: true
        }
      ];
      
      setNotifications(mockNotifications);
      
      // Generate role-based quick actions
      generateQuickActions();
      
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const generateQuickActions = () => {
    const baseActions: QuickAction[] = [
      {
        id: 'view-energy',
        title: 'View Energy Usage',
        description: 'Check your current energy consumption and production',
        icon: BoltIcon,
        color: 'bg-blue-500',
        action: () => console.log('Navigate to energy usage'),
        available: true
      },
      {
        id: 'marketplace',
        title: 'Energy Marketplace',
        description: 'Buy or sell energy in the community marketplace',
        icon: ChartBarIcon,
        color: 'bg-green-500',
        action: () => console.log('Navigate to marketplace'),
        available: true
      },
      {
        id: 'communities',
        title: 'My Communities',
        description: 'View and manage your community memberships',
        icon: BuildingOfficeIcon,
        color: 'bg-purple-500',
        action: () => console.log('Navigate to communities'),
        available: true
      },
      {
        id: 'settings',
        title: 'Account Settings',
        description: 'Update your profile and preferences',
        icon: CogIcon,
        color: 'bg-gray-500',
        action: () => console.log('Navigate to settings'),
        available: true
      }
    ];

    if (isRole('admin')) {
      baseActions.push({
        id: 'admin-panel',
        title: 'Admin Panel',
        description: 'Manage platform settings and users',
        icon: CpuChipIcon,
        color: 'bg-red-500',
        action: () => console.log('Navigate to admin panel'),
        available: true
      });
    }

    if (isRole('community_manager')) {
      baseActions.push({
        id: 'manage-community',
        title: 'Manage Community',
        description: 'Admin tools for community management',
        icon: UserIcon,
        color: 'bg-orange-500',
        action: () => console.log('Navigate to community management'),
        available: true
      });
    }

    if (isRole('producer')) {
      baseActions.push({
        id: 'production-analytics',
        title: 'Production Analytics',
        description: 'View detailed analytics of your energy production',
        icon: ChartBarIcon,
        color: 'bg-yellow-500',
        action: () => console.log('Navigate to production analytics'),
        available: true
      });
    }

    setQuickActions(baseActions);
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const markNotificationAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-500 to-green-500 rounded-lg shadow-sm p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Welcome back, {user?.name}!</h1>
            <p className="text-blue-100">
              Role: {user?.role.replace('_', ' ').toUpperCase()} | 
              Reputation: {100} points
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <TrophyIcon className="h-8 w-8 text-yellow-300" />
            <span className="text-lg font-semibold">{100}</span>
          </div>
        </div>
      </div>

      {/* Dashboard Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Energy Produced</p>
                <p className="text-2xl font-bold text-green-600">{stats.energyProduced}</p>
                <p className="text-xs text-gray-500">kWh</p>
              </div>
              <BoltIcon className="h-8 w-8 text-green-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Energy Consumed</p>
                <p className="text-2xl font-bold text-blue-600">{stats.energyConsumed}</p>
                <p className="text-xs text-gray-500">kWh</p>
              </div>
              <BoltIcon className="h-8 w-8 text-blue-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Earnings</p>
                <p className="text-2xl font-bold text-purple-600">${stats.totalEarnings}</p>
                <p className="text-xs text-gray-500">This month</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Communities</p>
                <p className="text-2xl font-bold text-orange-600">{stats.communitiesJoined}</p>
                <p className="text-xs text-gray-500">Joined</p>
              </div>
              <BuildingOfficeIcon className="h-8 w-8 text-orange-600" />
            </div>
          </motion.div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {quickActions.map((action, index) => (
              <motion.button
                key={action.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                onClick={action.action}
                disabled={!action.available}
                className={`p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all ${
                  action.available ? 'cursor-pointer hover:shadow-md' : 'opacity-50 cursor-not-allowed'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${action.color}`}>
                    <action.icon className="h-5 w-5 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-medium text-gray-900">{action.title}</h3>
                    <p className="text-sm text-gray-600">{action.description}</p>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Recent Notifications */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Notifications</h2>
          <div className="space-y-4">
            {notifications.slice(0, 5).map((notification, index) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-3 rounded-lg border ${
                  notification.read 
                    ? 'bg-gray-50 border-gray-200' 
                    : 'bg-blue-50 border-blue-200'
                }`}
                onClick={() => markNotificationAsRead(notification.id)}
              >
                <div className="flex items-start space-x-3">
                  {getNotificationIcon(notification.type)}
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{notification.title}</h4>
                    <p className="text-sm text-gray-600">{notification.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(notification.timestamp).toLocaleString()}
                    </p>
                  </div>
                  {!notification.read && (
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  )}
                </div>
              </motion.div>
            ))}
            {notifications.length === 0 && (
              <p className="text-gray-500 text-center py-4">No recent notifications</p>
            )}
          </div>
        </div>
      </div>

      {/* Role-specific Additional Stats */}
      {isRole('producer') && stats && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Producer Analytics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{stats.energyProduced}</p>
              <p className="text-sm text-gray-600">kWh Produced</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.energyTraded}</p>
              <p className="text-sm text-gray-600">kWh Traded</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">${stats.totalEarnings}</p>
              <p className="text-sm text-gray-600">Total Earnings</p>
            </div>
          </div>
        </div>
      )}

      {isRole('admin') && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Platform Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">2,547</p>
              <p className="text-sm text-gray-600">Total Users</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">1,234</p>
              <p className="text-sm text-gray-600">Active Trades</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">$45,678</p>
              <p className="text-sm text-gray-600">Total Volume</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">87</p>
              <p className="text-sm text-gray-600">Communities</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleBasedDashboard;
