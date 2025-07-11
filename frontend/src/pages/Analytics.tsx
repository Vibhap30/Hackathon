import React, { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface MarketAnalytics {
  total_volume: number
  average_price: number
  price_trend: string
  volume_trend: string
  peak_hours: number[]
  active_traders: number
  price_volatility: number
  market_efficiency: number
}

interface PlatformAnalytics {
  total_users: number
  active_users: number
  total_energy_traded: number
  total_transactions: number
  average_transaction_size: number
  user_growth_rate: number
  energy_efficiency_score: number
  carbon_savings: number
}

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'market' | 'user' | 'community' | 'platform' | 'predictions'>('market')
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d' | '1y'>('7d')
  const [loading, setLoading] = useState(false)

  // Analytics data
  const [marketAnalytics, setMarketAnalytics] = useState<MarketAnalytics | null>(null)
  const [platformAnalytics, setPlatformAnalytics] = useState<PlatformAnalytics | null>(null)
  const [priceHistory, setPriceHistory] = useState<any[]>([])
  const [volumeHistory, setVolumeHistory] = useState<any[]>([])
  const [userStats, setUserStats] = useState<any>(null)
  const [communityStats, setCommunityStats] = useState<any[]>([])
  const [energyDistribution, setEnergyDistribution] = useState<any[]>([])
  const [predictions, setPredictions] = useState<any[]>([])

  useEffect(() => {
    loadAnalyticsData()
  }, [activeTab, timeframe])

  const loadAnalyticsData = async () => {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'market':
          const [market, priceData, volumeData] = await Promise.all([
            apiService.getMarketAnalytics(),
            apiService.getPriceHistory(timeframe),
            apiService.getVolumeHistory(timeframe)
          ])
          setMarketAnalytics(market)
          setPriceHistory(priceData)
          setVolumeHistory(volumeData)
          break

        case 'user':
          const userStatsData = await apiService.getUserAnalytics()
          setUserStats(userStatsData)
          break

        case 'community':
          const communityData = await apiService.getCommunityAnalytics()
          setCommunityStats(communityData)
          break

        case 'platform':
          const platformData = await apiService.getPlatformAnalytics()
          setPlatformAnalytics(platformData)
          break

        case 'predictions':
          const predictionsData = await apiService.getPredictiveAnalytics(timeframe)
          setPredictions(predictionsData)
          break
      }
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportData = async (format: 'csv' | 'json') => {
    try {
      const data = await apiService.exportAnalyticsData(activeTab, timeframe, format)
      const blob = new Blob([data], { type: format === 'csv' ? 'text/csv' : 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics-${activeTab}-${timeframe}.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export data:', error)
    }
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8']

  // Mock data for demonstration (replace with real data)
  const mockPriceHistory = [
    { date: '2024-01-01', price: 0.12 },
    { date: '2024-01-02', price: 0.11 },
    { date: '2024-01-03', price: 0.13 },
    { date: '2024-01-04', price: 0.14 },
    { date: '2024-01-05', price: 0.12 },
    { date: '2024-01-06', price: 0.15 },
    { date: '2024-01-07', price: 0.13 }
  ]

  const mockVolumeHistory = [
    { date: '2024-01-01', volume: 1200 },
    { date: '2024-01-02', volume: 1350 },
    { date: '2024-01-03', volume: 1100 },
    { date: '2024-01-04', volume: 1500 },
    { date: '2024-01-05', volume: 1400 },
    { date: '2024-01-06', volume: 1650 },
    { date: '2024-01-07', volume: 1300 }
  ]

  const mockEnergyDistribution = [
    { name: 'Solar', value: 45, color: '#FFD700' },
    { name: 'Wind', value: 30, color: '#87CEEB' },
    { name: 'Hydro', value: 15, color: '#4682B4' },
    { name: 'Grid', value: 10, color: '#696969' }
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
              <p className="text-gray-600 mt-2">Insights into energy trading patterns and performance</p>
            </div>
            <div className="flex space-x-4">
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value as any)}
                className="border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="1y">Last Year</option>
              </select>
              <button
                onClick={() => exportData('csv')}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200"
              >
                Export CSV
              </button>
              <button
                onClick={() => exportData('json')}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200"
              >
                Export JSON
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'market', label: 'Market Analytics' },
              { key: 'user', label: 'User Analytics' },
              { key: 'community', label: 'Community Analytics' },
              { key: 'platform', label: 'Platform Analytics' },
              { key: 'predictions', label: 'Predictions' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading analytics...</p>
          </div>
        ) : (
          <>
            {/* Market Analytics */}
            {activeTab === 'market' && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Avg Price</p>
                        <p className="text-2xl font-bold text-green-600">$0.13/kWh</p>
                        <p className="text-sm text-green-500">+2.3% from last week</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Volume</p>
                        <p className="text-2xl font-bold text-blue-600">9,234 kWh</p>
                        <p className="text-sm text-blue-500">+15.2% from last week</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Active Traders</p>
                        <p className="text-2xl font-bold text-purple-600">147</p>
                        <p className="text-sm text-purple-500">+8.1% from last week</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Market Efficiency</p>
                        <p className="text-2xl font-bold text-orange-600">87.3%</p>
                        <p className="text-sm text-orange-500">+1.2% from last week</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Price Trend */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Price Trend</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={mockPriceHistory}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="price" stroke="#10B981" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Volume Trend */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Volume Trend</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={mockVolumeHistory}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Area type="monotone" dataKey="volume" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Energy Source Distribution */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Energy Source Distribution</h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={mockEnergyDistribution}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label
                        >
                          {mockEnergyDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="space-y-4">
                      {mockEnergyDistribution.map((source, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div 
                              className="w-4 h-4 rounded-full" 
                              style={{ backgroundColor: source.color }}
                            ></div>
                            <span className="font-medium">{source.name}</span>
                          </div>
                          <span className="text-lg font-bold">{source.value}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* User Analytics */}
            {activeTab === 'user' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Your Trading Stats</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Energy Sold</span>
                        <span className="font-semibold">2,341 kWh</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Energy Bought</span>
                        <span className="font-semibold">1,876 kWh</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Transactions</span>
                        <span className="font-semibold">47</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Average Price</span>
                        <span className="font-semibold">$0.127/kWh</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Energy Production</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Current Capacity</span>
                        <span className="font-semibold">15.2 kWh</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Available</span>
                        <span className="font-semibold text-green-600">8.7 kWh</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Monthly Production</span>
                        <span className="font-semibold">456 kWh</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Efficiency</span>
                        <span className="font-semibold">92.3%</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Reputation</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Current Score</span>
                        <span className="font-semibold text-blue-600">847</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Rank</span>
                        <span className="font-semibold">#23</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Successful Trades</span>
                        <span className="font-semibold">98.7%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Response Time</span>
                        <span className="font-semibold">4.2 min</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Community Analytics */}
            {activeTab === 'community' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Community Performance</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">12</div>
                      <div className="text-sm text-blue-800">Active Communities</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">324</div>
                      <div className="text-sm text-green-800">Total Members</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">5,678</div>
                      <div className="text-sm text-purple-800">Total Energy (kWh)</div>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">89.2%</div>
                      <div className="text-sm text-orange-800">Avg Efficiency</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Platform Analytics */}
            {activeTab === 'platform' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Users</p>
                        <p className="text-2xl font-bold text-indigo-600">1,247</p>
                        <p className="text-sm text-indigo-500">+12.5% this month</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Active Users</p>
                        <p className="text-2xl font-bold text-green-600">892</p>
                        <p className="text-sm text-green-500">71.5% of total</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Energy Traded</p>
                        <p className="text-2xl font-bold text-blue-600">45.2k kWh</p>
                        <p className="text-sm text-blue-500">+28.7% this month</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Carbon Savings</p>
                        <p className="text-2xl font-bold text-green-600">18.9 tons</p>
                        <p className="text-sm text-green-500">CO2 equivalent</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Predictions */}
            {activeTab === 'predictions' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Price Predictions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center p-4 bg-yellow-50 rounded-lg">
                      <div className="text-lg font-semibold text-yellow-800">Next Hour</div>
                      <div className="text-2xl font-bold text-yellow-600">$0.134/kWh</div>
                      <div className="text-sm text-yellow-600">+3.2% expected</div>
                    </div>
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-lg font-semibold text-blue-800">Next Day</div>
                      <div className="text-2xl font-bold text-blue-600">$0.129/kWh</div>
                      <div className="text-sm text-blue-600">-0.8% expected</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-lg font-semibold text-green-800">Next Week</div>
                      <div className="text-2xl font-bold text-green-600">$0.125/kWh</div>
                      <div className="text-sm text-green-600">-3.8% expected</div>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Demand Forecast</h3>
                  <p className="text-gray-600">
                    Based on historical patterns and weather forecasts, energy demand is expected to 
                    increase by 15% in the next 48 hours due to predicted temperature changes.
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default Analytics
