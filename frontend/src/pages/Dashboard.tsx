import React, { useState } from 'react'
import apiService from '../services/api'
import { motion } from 'framer-motion'
import { 
  BoltIcon, 
  ChartBarIcon, 
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  SunIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts'
import BidOptimizer from '../components/BidOptimizer'
import RealTimeStatus from '../components/RealTimeStatus'
import RoleBasedDashboard from '../components/RoleBasedDashboard'
import RoleSwitcherDashboard from '../components/RoleSwitcherDashboard'

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [coinBalance, setCoinBalance] = useState<number>(0);
  const [collecting, setCollecting] = useState(false);
  const [collectMsg, setCollectMsg] = useState<string | null>(null);

  // Optionally, fetch initial balance on mount (not implemented here for demo)
  const handleCollectCoins = async () => {
    setCollecting(true);
    setCollectMsg(null);
    try {
      const res = await apiService.collectCoins();
      setCoinBalance(res.total_balance);
      setCollectMsg(res.message);
    } catch (err) {
      setCollectMsg('Failed to collect coins.');
    } finally {
      setCollecting(false);
    }
  };
  const [userStats] = useState({
    currentEnergy: 85.2,
    energyCapacity: 120.0,
    totalEarnings: 1247.50,
    totalTrades: 34,
    carbonSaved: 2.4,
    reputation: 4.8
  })

  const [marketData] = useState({
    currentPrice: 0.247,
    priceChange: 0.012,
    volume: 2847.3,
    activeTrades: 156
  })

  // Mock energy usage data
  const energyUsageData = [
    { time: '00:00', production: 0, consumption: 2.1 },
    { time: '06:00', production: 1.5, consumption: 2.8 },
    { time: '12:00', production: 8.2, consumption: 3.1 },
    { time: '18:00', production: 4.1, consumption: 4.5 },
    { time: '24:00', production: 0, consumption: 1.9 }
  ]

  // Mock trading history data
  const tradingData = [
    { date: 'Mon', bought: 12.3, sold: 8.7 },
    { date: 'Tue', bought: 15.1, sold: 11.2 },
    { date: 'Wed', bought: 8.9, sold: 14.6 },
    { date: 'Thu', bought: 11.5, sold: 9.8 },
    { date: 'Fri', bought: 13.2, sold: 16.1 },
    { date: 'Sat', bought: 9.7, sold: 12.4 },
    { date: 'Sun', bought: 7.3, sold: 10.9 }
  ]

  // Mock recent transactions
  const recentTransactions = [
    { id: 1, type: 'sell', amount: 5.2, price: 0.251, buyer: 'Community Solar Farm', time: '2 hours ago' },
    { id: 2, type: 'buy', amount: 8.7, price: 0.243, seller: 'Green Valley Co-op', time: '5 hours ago' },
    { id: 3, type: 'sell', amount: 3.1, price: 0.255, buyer: 'EcoHome Network', time: '1 day ago' },
    { id: 4, type: 'buy', amount: 12.5, price: 0.239, seller: 'Wind Power Alliance', time: '2 days ago' }
  ]

  // Mock IoT devices
  const iotDevices = [
    { id: 1, name: 'Solar Panel Array', type: 'solar_panel', status: 'operational', production: 4.2, efficiency: 94 },
    { id: 2, name: 'Home Battery', type: 'battery', status: 'charging', capacity: 85, efficiency: 98 },
    { id: 3, name: 'Smart Meter', type: 'smart_meter', status: 'operational', consumption: 2.1, efficiency: 100 },
    { id: 4, name: 'EV Charger', type: 'ev_charger', status: 'idle', consumption: 0, efficiency: 92 }
  ]

  const energyUtilization = (userStats.currentEnergy / userStats.energyCapacity) * 100

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <RoleSwitcherDashboard />
         <div className="bg-white rounded-lg shadow p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Energy Dashboard</h1>
          <p className="text-gray-600">Monitor your energy usage, trading activity, and AI recommendations</p>
          
          {/* Tab Navigation */}
          <div className="border-b border-gray-200 mt-6">
            <nav className="-mb-px flex space-x-8">
              {[
                { key: 'overview', label: 'Overview' },
                { key: 'role-dashboard', label: 'Role Dashboard' },
                { key: 'bid-optimizer', label: 'AI Bid Optimizer' },
                { key: 'real-time', label: 'Real-Time Status' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </motion.div>

        {/* Tab Content */}
        <div className="mt-8">
          {activeTab === 'overview' && (
            <>
              {/* Key Metrics */}
              {/* Gamification: Coin Collection */}
              <div className="mb-8">
                <div className="flex items-center space-x-4">
                  <div className="bg-yellow-100 p-4 rounded-xl shadow flex items-center">
                    <span className="text-2xl font-bold text-yellow-600 mr-2">{coinBalance}</span>
                    <span className="text-yellow-700 font-medium">Coins</span>
                  </div>
                  <button
                    className="bg-yellow-400 hover:bg-yellow-500 text-white font-bold py-2 px-4 rounded-lg shadow transition-colors disabled:opacity-50"
                    onClick={handleCollectCoins}
                    disabled={collecting}
                  >
                    {collecting ? 'Collecting...' : 'Collect Coins'}
                  </button>
                  {collectMsg && <span className="ml-4 text-green-600 font-medium">{collectMsg}</span>}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 }}
                  className="bg-white p-6 rounded-xl shadow-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm">Current Energy</p>
                      <p className="text-2xl font-bold text-gray-900">{userStats.currentEnergy} kWh</p>
                      <p className="text-sm text-green-600">Capacity: {userStats.energyCapacity} kWh</p>
                    </div>
                    <div className="bg-blue-100 p-3 rounded-lg">
                      <BoltIcon className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 rounded-full h-2 transition-all duration-300"
                        style={{ width: `${energyUtilization}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{energyUtilization.toFixed(1)}% utilized</p>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                  className="bg-white p-6 rounded-xl shadow-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm">Total Earnings</p>
                      <p className="text-2xl font-bold text-gray-900">${userStats.totalEarnings}</p>
                      <p className="text-sm text-green-600">+12.5% this month</p>
                    </div>
                    <div className="bg-green-100 p-3 rounded-lg">
                      <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="bg-white p-6 rounded-xl shadow-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm">Market Price</p>
                      <p className="text-2xl font-bold text-gray-900">${marketData.currentPrice}</p>
                      <div className="flex items-center">
                        {marketData.priceChange >= 0 ? (
                          <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                        ) : (
                          <ArrowTrendingDownIcon className="h-4 w-4 text-red-500 mr-1" />
                        )}
                        <p className={`text-sm ${marketData.priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {marketData.priceChange >= 0 ? '+' : ''}{marketData.priceChange.toFixed(3)}
                        </p>
                      </div>
                    </div>
                    <div className="bg-purple-100 p-3 rounded-lg">
                      <ChartBarIcon className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                  className="bg-white p-6 rounded-xl shadow-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600 text-sm">Carbon Saved</p>
                      <p className="text-2xl font-bold text-gray-900">{userStats.carbonSaved} tons</p>
                      <p className="text-sm text-green-600">CO₂ emissions</p>
                    </div>
                    <div className="bg-green-100 p-3 rounded-lg">
                      <SunIcon className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* AI Insights Section */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-xl shadow-lg mb-8"
              >
                <div className="text-white">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold">AI Energy Assistant</h3>
                    <button className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-white transition-colors">
                      Get New Analysis
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white/10 p-4 rounded-lg backdrop-blur-sm">
                      <h4 className="font-medium mb-2">Market Opportunity</h4>
                      <p className="text-sm opacity-90">Sell 8.2 kWh now at $0.251/kWh for optimal profit</p>
                      <p className="text-xs mt-1 opacity-75">Confidence: 87%</p>
                    </div>
                    
                    <div className="bg-white/10 p-4 rounded-lg backdrop-blur-sm">
                      <h4 className="font-medium mb-2">Weather Forecast</h4>
                      <p className="text-sm opacity-90">High solar production expected tomorrow (+15.3 kWh)</p>
                      <p className="text-xs mt-1 opacity-75">Plan: Schedule battery charging</p>
                    </div>
                    
                    <div className="bg-white/10 p-4 rounded-lg backdrop-blur-sm">
                      <h4 className="font-medium mb-2">Community Recommendation</h4>
                      <p className="text-sm opacity-90">Join "Green Valley Co-op" for 12% better rates</p>
                      <p className="text-xs mt-1 opacity-75">235 members, 4.8★ rating</p>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex items-center space-x-4">
                    <button className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg transition-colors">
                      <BoltIcon className="h-4 w-4" />
                      <span className="text-sm">Quick Trade</span>
                    </button>
                    <button className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg transition-colors">
                      <ChartBarIcon className="h-4 w-4" />
                      <span className="text-sm">Full Analysis</span>
                    </button>
                    <button className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg transition-colors">
                      <UserGroupIcon className="h-4 w-4" />
                      <span className="text-sm">Join Community</span>
                    </button>
                  </div>
                </div>
              </motion.div>

              {/* Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Energy Usage Chart */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 }}
                  className="bg-white p-6 rounded-xl shadow-lg"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Energy Production vs Consumption</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={energyUsageData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="production" stackId="1" stroke="#10b981" fill="#10b981" />
                      <Area type="monotone" dataKey="consumption" stackId="2" stroke="#f59e0b" fill="#f59e0b" />
                    </AreaChart>
                  </ResponsiveContainer>
                </motion.div>

                {/* Trading Activity Chart */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.6 }}
                  className="bg-white p-6 rounded-xl shadow-lg"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Trading Activity</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={tradingData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="bought" fill="#3b82f6" />
                      <Bar dataKey="sold" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </motion.div>
              </div>

              {/* Bottom Section */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Transactions */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.7 }}
                  className="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Transactions</h3>
                  <div className="space-y-4">
                    {recentTransactions.map((transaction) => (
                      <div key={transaction.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <div className={`w-3 h-3 rounded-full mr-3 ${
                            transaction.type === 'sell' ? 'bg-green-500' : 'bg-blue-500'
                          }`}></div>
                          <div>
                            <p className="font-medium text-gray-900">
                              {transaction.type === 'sell' ? 'Sold' : 'Bought'} {transaction.amount} kWh
                            </p>
                            <p className="text-sm text-gray-600">
                              {transaction.type === 'sell' ? `to ${transaction.buyer}` : `from ${transaction.seller}`}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">${(transaction.amount * transaction.price).toFixed(2)}</p>
                          <p className="text-sm text-gray-600">{transaction.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* IoT Devices Status */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.8 }}
                  className="bg-white p-6 rounded-xl shadow-lg"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Device Status</h3>
                  <div className="space-y-4">
                    {iotDevices.map((device) => (
                      <div key={device.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-medium text-gray-900 text-sm">{device.name}</p>
                          <div className={`w-2 h-2 rounded-full ${
                            device.status === 'operational' ? 'bg-green-500' : 
                            device.status === 'charging' ? 'bg-blue-500' : 'bg-gray-400'
                          }`}></div>
                        </div>
                        <p className="text-xs text-gray-600 capitalize">{device.status}</p>
                        {device.production && (
                          <p className="text-xs text-green-600">Producing: {device.production} kWh</p>
                        )}
                        {typeof device.consumption === 'number' && device.consumption > 0 && (
                          <p className="text-xs text-orange-600">Consuming: {device.consumption} kWh</p>
                        )}
                        {device.capacity && (
                          <p className="text-xs text-blue-600">Capacity: {device.capacity}%</p>
                        )}
                      </div>
                    ))}
                  </div>
                </motion.div>
              </div>
            </>
          )}

          {activeTab === 'role-dashboard' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <RoleBasedDashboard />
            </motion.div>
          )}

          {activeTab === 'bid-optimizer' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <BidOptimizer />
            </motion.div>
          )}

          {activeTab === 'real-time' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <RealTimeStatus />
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
