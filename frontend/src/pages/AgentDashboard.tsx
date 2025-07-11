import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  CpuChipIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  BoltIcon,
  ChartBarIcon,
  GlobeAltIcon,
  SunIcon,
  UserGroupIcon,
  CogIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
// import apiService from '../services/api' // For future dynamic agent loading

interface Agent {
  id: string
  name: string
  type: string
  description: string
  status: 'active' | 'idle' | 'busy' | 'error'
  capabilities: string[]
  last_active: string
  performance_metrics: {
    success_rate: number
    avg_response_time: number
    tasks_completed: number
  }
  current_tasks?: string[]
}

interface AgentMetrics {
  total_agents: number
  active_agents: number
  tasks_in_progress: number
  success_rate: number
}

const AgentDashboard: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([])
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadAgentData()
    const interval = setInterval(loadAgentData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadAgentData = async () => {
    try {
      setRefreshing(true)
      // TODO: Replace with actual API call when available, e.g.:
      // const agentsResponse = await apiService.getAgents();
      
      // Mock comprehensive agent data for demo
      const mockAgents: Agent[] = [
        {
          id: 'energy-trading-agent',
          name: 'Energy Trading Agent',
          type: 'ENERGY_TRADING',
          description: 'Optimizes energy trading decisions using real-time market data and ML algorithms',
          status: 'active',
          capabilities: [
            'Market price analysis',
            'Bid optimization',
            'Risk assessment',
            'Portfolio balancing',
            'Automated trading'
          ],
          last_active: new Date().toISOString(),
          performance_metrics: {
            success_rate: 94.2,
            avg_response_time: 1.8,
            tasks_completed: 1847
          },
          current_tasks: ['Analyzing solar energy bids', 'Optimizing trading portfolio']
        },
        {
          id: 'market-analysis-agent',
          name: 'Market Analysis Agent',
          type: 'MARKET_ANALYSIS',
          description: 'Analyzes energy market trends, price predictions, and demand forecasting',
          status: 'active',
          capabilities: [
            'Price forecasting',
            'Demand prediction',
            'Market trend analysis',
            'Competitive intelligence',
            'Risk modeling'
          ],
          last_active: new Date(Date.now() - 300000).toISOString(),
          performance_metrics: {
            success_rate: 91.7,
            avg_response_time: 2.3,
            tasks_completed: 923
          },
          current_tasks: ['Forecasting weekend energy prices', 'Analyzing renewable energy trends']
        },
        {
          id: 'beckn-integration-agent',
          name: 'Beckn Protocol Agent',
          type: 'BECKN_PROTOCOL',
          description: 'Handles cross-network energy discovery and transactions via Beckn protocol',
          status: 'active',
          capabilities: [
            'Cross-network discovery',
            'Protocol translation',
            'Transaction coordination',
            'Network bridging',
            'Interoperability management'
          ],
          last_active: new Date(Date.now() - 120000).toISOString(),
          performance_metrics: {
            success_rate: 88.9,
            avg_response_time: 3.1,
            tasks_completed: 456
          },
          current_tasks: ['Discovering energy offers across networks', 'Processing cross-platform transactions']
        },
        {
          id: 'optimization-agent',
          name: 'Energy Optimization Agent',
          type: 'OPTIMIZATION',
          description: 'Optimizes energy consumption patterns and efficiency recommendations',
          status: 'busy',
          capabilities: [
            'Consumption optimization',
            'Efficiency analysis',
            'Load balancing',
            'Smart scheduling',
            'Carbon footprint reduction'
          ],
          last_active: new Date().toISOString(),
          performance_metrics: {
            success_rate: 96.1,
            avg_response_time: 4.2,
            tasks_completed: 2156
          },
          current_tasks: ['Analyzing household energy patterns', 'Generating optimization recommendations']
        },
        {
          id: 'community-agent',
          name: 'Community Coordination Agent',
          type: 'COMMUNITY',
          description: 'Facilitates community energy sharing and coordination activities',
          status: 'idle',
          capabilities: [
            'Community matching',
            'Resource coordination',
            'Social optimization',
            'Event planning',
            'Peer-to-peer facilitation'
          ],
          last_active: new Date(Date.now() - 600000).toISOString(),
          performance_metrics: {
            success_rate: 89.4,
            avg_response_time: 1.9,
            tasks_completed: 734
          }
        },
        {
          id: 'iot-integration-agent',
          name: 'IoT Integration Agent',
          type: 'IOT_INTEGRATION',
          description: 'Manages IoT device data collection, processing, and automation',
          status: 'active',
          capabilities: [
            'Device monitoring',
            'Data collection',
            'Automated control',
            'Anomaly detection',
            'Predictive maintenance'
          ],
          last_active: new Date(Date.now() - 60000).toISOString(),
          performance_metrics: {
            success_rate: 97.8,
            avg_response_time: 0.9,
            tasks_completed: 3421
          },
          current_tasks: ['Monitoring solar panel performance', 'Processing smart meter data']
        }
      ]

      setAgents(mockAgents)
      
      // Calculate metrics
      const activeAgents = mockAgents.filter(a => a.status === 'active').length
      const totalTasks = mockAgents.reduce((sum, agent) => sum + (agent.current_tasks?.length || 0), 0)
      const avgSuccessRate = mockAgents.reduce((sum, agent) => sum + agent.performance_metrics.success_rate, 0) / mockAgents.length

      setMetrics({
        total_agents: mockAgents.length,
        active_agents: activeAgents,
        tasks_in_progress: totalTasks,
        success_rate: avgSuccessRate
      })

      setIsLoading(false)
    } catch (error) {
      console.error('Failed to load agent data:', error)
    } finally {
      setRefreshing(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'busy':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
      case 'idle':
        return <CogIcon className="h-5 w-5 text-gray-400" />
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      default:
        return <CpuChipIcon className="h-5 w-5 text-gray-400" />
    }
  }

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'ENERGY_TRADING':
        return <BoltIcon className="h-6 w-6" />
      case 'MARKET_ANALYSIS':
        return <ChartBarIcon className="h-6 w-6" />
      case 'BECKN_PROTOCOL':
        return <GlobeAltIcon className="h-6 w-6" />
      case 'OPTIMIZATION':
        return <SunIcon className="h-6 w-6" />
      case 'COMMUNITY':
        return <UserGroupIcon className="h-6 w-6" />
      case 'IOT_INTEGRATION':
        return <CpuChipIcon className="h-6 w-6" />
      default:
        return <CogIcon className="h-6 w-6" />
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-green-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="h-16 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-green-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Agent Dashboard</h1>
            <p className="text-gray-600">Monitor and manage AI agents powering the PowerShare platform</p>
          </motion.div>
          
          <motion.button
            onClick={loadAgentData}
            disabled={refreshing}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </motion.button>
        </div>

        {/* Metrics Overview */}
        {metrics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <CpuChipIcon className="h-8 w-8 text-blue-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Agents</p>
                  <p className="text-2xl font-bold text-gray-900">{metrics.total_agents}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <CheckCircleIcon className="h-8 w-8 text-green-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Agents</p>
                  <p className="text-2xl font-bold text-gray-900">{metrics.active_agents}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <ClockIcon className="h-8 w-8 text-yellow-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Tasks in Progress</p>
                  <p className="text-2xl font-bold text-gray-900">{metrics.tasks_in_progress}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-purple-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{metrics.success_rate.toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Agents Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6"
        >
          {agents.map((agent, index) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * index }}
              className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedAgent(agent)}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg mr-3">
                      {getAgentIcon(agent.type)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <p className="text-sm text-gray-600">{agent.type.replace('_', ' ')}</p>
                    </div>
                  </div>
                  {getStatusIcon(agent.status)}
                </div>
                
                <p className="text-gray-600 text-sm mb-4">{agent.description}</p>
                
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-lg font-bold text-green-600">{agent.performance_metrics.success_rate}%</p>
                    <p className="text-xs text-gray-500">Success Rate</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-blue-600">{agent.performance_metrics.avg_response_time}s</p>
                    <p className="text-xs text-gray-500">Avg Response</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-purple-600">{agent.performance_metrics.tasks_completed}</p>
                    <p className="text-xs text-gray-500">Tasks Done</p>
                  </div>
                </div>
                
                {agent.current_tasks && agent.current_tasks.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Current Tasks:</p>
                    <div className="space-y-1">
                      {agent.current_tasks.slice(0, 2).map((task, idx) => (
                        <div key={idx} className="flex items-center text-xs text-gray-600">
                          <div className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></div>
                          {task}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Agent Detail Modal */}
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedAgent(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center">
                    <div className="p-3 bg-blue-100 rounded-lg mr-4">
                      {getAgentIcon(selectedAgent.type)}
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{selectedAgent.name}</h2>
                      <p className="text-gray-600">{selectedAgent.type.replace('_', ' ')}</p>
                    </div>
                  </div>
                  {getStatusIcon(selectedAgent.status)}
                </div>
                
                <p className="text-gray-700 mb-6">{selectedAgent.description}</p>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">{selectedAgent.performance_metrics.success_rate}%</p>
                    <p className="text-sm text-gray-600">Success Rate</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{selectedAgent.performance_metrics.avg_response_time}s</p>
                    <p className="text-sm text-gray-600">Avg Response Time</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600">{selectedAgent.performance_metrics.tasks_completed}</p>
                    <p className="text-sm text-gray-600">Tasks Completed</p>
                  </div>
                </div>
                
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Capabilities</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {selectedAgent.capabilities.map((capability, idx) => (
                      <div key={idx} className="flex items-center text-sm text-gray-700">
                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                        {capability}
                      </div>
                    ))}
                  </div>
                </div>
                
                {selectedAgent.current_tasks && selectedAgent.current_tasks.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Current Tasks</h3>
                    <div className="space-y-2">
                      {selectedAgent.current_tasks.map((task, idx) => (
                        <div key={idx} className="flex items-center p-3 bg-yellow-50 rounded-lg">
                          <ClockIcon className="h-4 w-4 text-yellow-500 mr-3" />
                          <span className="text-sm text-gray-700">{task}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end">
                  <button
                    onClick={() => setSelectedAgent(null)}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default AgentDashboard
