
import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  BoltIcon, 
  ChartBarIcon, 
  CpuChipIcon,
  CheckCircleIcon,
  SunIcon,
  BanknotesIcon,
  UserGroupIcon,
  LightBulbIcon,
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  GlobeAltIcon,
  BeakerIcon
} from '@heroicons/react/24/outline'
import apiService from '../services/api'

type UserRole = 'prosumer' | 'consumer';
// Profile role state and switcher must be inside the component


interface ActionItem {
  id: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  timeline: string
  type: string
  data?: any
}


interface ChatMessage {
  id: string
  type: 'user' | 'agent' | 'system'
  content: string
  timestamp: Date
  agent_type?: string
  reasoning?: string
  confidence?: number
  data?: any
  agent_name?: string
}


const AIAssistant: React.FC = () => {
  const [userRole, setUserRole] = useState<UserRole>('prosumer');
  // Profile switcher UI
  const ProfileSwitcher = () => (
    <div className="flex items-center space-x-4 mb-6">
      <span className="font-medium text-gray-700">Profile:</span>
      <button
        className={`px-4 py-2 rounded-lg border ${userRole === 'prosumer' ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 border-blue-600'} transition`}
        onClick={() => setUserRole('prosumer')}
      >
        Prosumer
      </button>
      <button
        className={`px-4 py-2 rounded-lg border ${userRole === 'consumer' ? 'bg-green-600 text-white' : 'bg-white text-green-600 border-green-600'} transition`}
        onClick={() => setUserRole('consumer')}
      >
        Consumer
      </button>
    </div>
  );
  // const [isAnalyzing, setIsAnalyzing] = useState(false)
  // const [optimizationResults, setOptimizationResults] = useState<OptimizationResult | null>(null)
  const [actionItems, setActionItems] = useState<ActionItem[]>([])
  const [aiRecommendations, setAIRecommendations] = useState<any[]>([])
  const [agentsStatus, setAgentsStatus] = useState<any>(null)
  // const [analysisProgress, setAnalysisProgress] = useState(0)
  
  // New chat functionality
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [selectedAgents, setSelectedAgents] = useState<string[]>(['all'])
  const [showRecommendations] = useState(true)
  // const [showEnergyMap, setShowEnergyMap] = useState(false)
  // const [showBidMatching, setShowBidMatching] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const availableAgents = [
    { id: 'all', name: 'All Agents', icon: CpuChipIcon, color: 'bg-purple-500' },
    { id: 'energy-trading', name: 'Energy Trading', icon: BoltIcon, color: 'bg-blue-500' },
    { id: 'market-analysis', name: 'Market Analysis', icon: ChartBarIcon, color: 'bg-green-500' },
    { id: 'beckn-protocol', name: 'Beckn Protocol', icon: GlobeAltIcon, color: 'bg-orange-500' },
    { id: 'optimization', name: 'Optimization', icon: SunIcon, color: 'bg-yellow-500' },
    { id: 'community', name: 'Community', icon: UserGroupIcon, color: 'bg-pink-500' },
    { id: 'iot-integration', name: 'IoT Integration', icon: BeakerIcon, color: 'bg-indigo-500' }
  ]

  useEffect(() => {
    loadInitialData()
    initializeChat()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const initializeChat = () => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'system',
      content: '👋 Welcome! I\'m your AI Energy Assistant powered by multiple specialized agents. Ask me about energy trading, optimization, market analysis, or anything related to your energy needs!',
      timestamp: new Date(),
      agent_name: 'PowerShare AI'
    }
    setMessages([welcomeMessage])
  }

  const loadInitialData = async () => {
    try {
      // Load existing results and recommendations
      const [recommendations, actionItems, , status] = await Promise.all([
        apiService.getAIRecommendations().catch(() => ({ recommendations: [] })),
        apiService.getAIActionItems().catch(() => ({ action_items: [] })),
        apiService.getOptimizationResults().catch(() => ({ results: null })),
        apiService.getAIAgentsStatus().catch(() => null)
      ])

      setAIRecommendations(recommendations.recommendations || [])
      setActionItems(actionItems.action_items || [])
      // setOptimizationResults(optimizationResults.results)
      setAgentsStatus(status)
    } catch (error) {
      console.error('Failed to load AI data:', error)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsTyping(true)

    try {
      // Query agents based on selection
      const response = await apiService.queryAIAgents({
        query: inputMessage,
        context: {
          selected_agents: selectedAgents,
          user_preferences: {},
          current_time: new Date().toISOString()
        }
      })

      // Create agent response messages
      if (response.agent_responses) {
        for (const agentResponse of response.agent_responses) {
          const agentMessage: ChatMessage = {
            id: `${Date.now()}_${agentResponse.agent_type}`,
            type: 'agent',
            content: agentResponse.response,
            timestamp: new Date(),
            agent_type: agentResponse.agent_type,
            agent_name: agentResponse.agent_name,
            reasoning: agentResponse.reasoning,
            confidence: agentResponse.confidence,
            data: agentResponse.data
          }
          
          setMessages(prev => [...prev, agentMessage])
          
          // Small delay between agent responses for better UX
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      } else {
        // Fallback single response
        const agentMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'agent',
          content: response.response || 'I apologize, but I encountered an issue processing your request.',
          timestamp: new Date(),
          agent_name: 'PowerShare AI',
          reasoning: response.reasoning,
          confidence: response.confidence || 0.8
        }
        
        setMessages(prev => [...prev, agentMessage])
      }

    } catch (error) {
      console.error('Failed to query agents:', error)
      
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'system',
        content: 'I apologize, but I\'m having trouble connecting to the AI agents. Please try again in a moment.',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }

    // Scroll to bottom
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  const toggleAgentSelection = (agentId: string) => {
    if (agentId === 'all') {
      setSelectedAgents(['all'])
    } else {
      setSelectedAgents(prev => {
        const filtered = prev.filter(id => id !== 'all')
        if (filtered.includes(agentId)) {
          const newSelection = filtered.filter(id => id !== agentId)
          return newSelection.length === 0 ? ['all'] : newSelection
        } else {
          return [...filtered, agentId]
        }
      })
    }
  }

  // Role-based quick actions (must be after setInputMessage is defined)
  const roleQuickActions = userRole === 'prosumer' ? [
    {
      label: "� Sell excess energy",
      action: () => setInputMessage("I want to sell my excess solar energy. Show me the best bids.")
    },
    {
      label: "📈 View trading recommendations",
      action: () => setInputMessage("What are the best energy trading opportunities for prosumers?")
    },
    {
      label: "⚡ Optimize my production",
      action: () => setInputMessage("How can I optimize my solar energy production and maximize revenue?")
    },
    {
      label: "🌍 Community energy sharing",
      action: () => setInputMessage("Show me local community energy sharing opportunities.")
    },
    {
      label: "🔔 Forecast alerts",
      action: () => setInputMessage("Give me weather and price forecast alerts for my area.")
    },
    {
      label: "🌐 Beckn cross-network trading",
      action: () => setInputMessage("Find buyers from other networks using Beckn protocol.")
    }
  ] : [
    {
      label: "💡 Buy energy at best price",
      action: () => setInputMessage("I want to buy energy. Show me the best offers.")
    },
    {
      label: "📊 Personalized recommendations",
      action: () => setInputMessage("What are the best energy saving tips for me?")
    },
    {
      label: "⚡ Optimize my consumption",
      action: () => setInputMessage("How can I optimize my energy usage and reduce costs?")
    },
    {
      label: "🌍 Find local green energy",
      action: () => setInputMessage("Show me renewable energy sources in my area.")
    },
    {
      label: "� Forecast alerts",
      action: () => setInputMessage("Give me consumption and price forecast alerts for my area.")
    },
    {
      label: "🌐 Beckn cross-network search",
      action: () => setInputMessage("Find energy offers from other networks using Beckn protocol.")
    }
  ];


  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'trading': return BanknotesIcon
      case 'community': return UserGroupIcon
      case 'optimization': return CpuChipIcon
      case 'analysis': return ChartBarIcon
      default: return LightBulbIcon
    }
  }
      // ...existing code...

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header & Profile Switcher */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-lg">
              <ChatBubbleLeftRightIcon className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Energy Assistant</h1>
              <p className="text-gray-600">Powered by specialized AI agents for comprehensive energy management</p>
            </div>
          </div>
          <ProfileSwitcher />
          {agentsStatus && (
            <div className="flex items-center space-x-4 text-sm">
              <span className={`px-2 py-1 rounded-full ${agentsStatus.agents?.energy_trading?.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                Trading Agent: {agentsStatus.agents?.energy_trading?.status || 'active'}
              </span>
              <span className={`px-2 py-1 rounded-full ${agentsStatus.agents?.energy_optimization?.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                Optimization Agent: {agentsStatus.agents?.energy_optimization?.status || 'active'}
              </span>
              <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                Beckn Protocol: active
              </span>
            </div>
          )}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Agent Selection Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-1"
          >
            <div className="bg-white rounded-lg shadow-sm border p-4 mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Active Agents</h3>
              <div className="space-y-2">
                {availableAgents.map(agent => {
                  const IconComponent = agent.icon
                  const isSelected = selectedAgents.includes(agent.id)
                  return (
                    <button
                      key={agent.id}
                      onClick={() => toggleAgentSelection(agent.id)}
                      className={`w-full flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                        isSelected 
                          ? 'border-blue-500 bg-blue-50 text-blue-700' 
                          : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className={`p-1 rounded ${agent.color} text-white`}>
                        <IconComponent className="h-4 w-4" />
                      </div>
                      <span className="text-sm font-medium">{agent.name}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Quick Actions (role-based) */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Quick Actions ({userRole === 'prosumer' ? 'Prosumer' : 'Consumer'})</h3>
              <div className="space-y-2">
                {roleQuickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={action.action}
                    className="w-full text-left p-3 text-sm text-gray-700 hover:bg-gray-50 rounded-lg border border-gray-200 transition-colors"
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Chat Interface */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-3"
          >
            <div className="bg-white rounded-lg shadow-sm border h-[600px] flex flex-col">
              {/* Chat Messages */}
              <div className="flex-1 p-4 overflow-y-auto">
                <div className="space-y-4">
                  <AnimatePresence>
                    {messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-[80%] ${
                          message.type === 'user' 
                            ? 'bg-blue-600 text-white' 
                            : message.type === 'system'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-white border border-gray-200 text-gray-800'
                        } rounded-lg p-4 shadow-sm`}>
                          {message.agent_name && (
                            <div className="flex items-center space-x-2 mb-2">
                              <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                <CpuChipIcon className="h-3 w-3 text-white" />
                              </div>
                              <span className="text-xs font-semibold text-blue-600">
                                {message.agent_name}
                              </span>
                              {message.confidence && (
                                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                  {Math.round(message.confidence * 100)}% confident
                                </span>
                              )}
                            </div>
                          )}
                          
                          <p className="text-sm leading-relaxed">{message.content}</p>
                          
                          {message.reasoning && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <div className="flex items-center space-x-1 mb-1">
                                <LightBulbIcon className="h-3 w-3 text-yellow-500" />
                                <span className="text-xs font-medium text-gray-600">Reasoning:</span>
                              </div>
                              <p className="text-xs text-gray-600 italic">{message.reasoning}</p>
                            </div>
                          )}
                          
                          {message.data && (
                            <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
                              <strong>Data insights:</strong> {JSON.stringify(message.data, null, 2).slice(0, 100)}...
                            </div>
                          )}
                          
                          <div className="mt-2 text-xs text-gray-500">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex justify-start"
                    >
                      <div className="bg-gray-100 rounded-lg p-4 max-w-[80%]">
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                          <span className="text-xs text-gray-500">Agents are thinking...</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </div>
              
              {/* Chat Input */}
              <div className="border-t border-gray-200 p-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask about energy trading, optimization, community opportunities..."
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isTyping}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <PaperAirplaneIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Enhanced Recommendations Panel */}
        {(showRecommendations && (actionItems.length > 0 || aiRecommendations.length > 0)) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            {/* Priority Recommendations */}
            {actionItems.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Priority Recommendations</h3>
                <div className="space-y-3">
                  {actionItems.slice(0, 3).map((item) => {
                    const IconComponent = getTypeIcon(item.type)
                    return (
                      <div key={item.id} className="border border-gray-200 p-4 rounded-lg">
                        <div className="flex items-start space-x-3">
                          <div className="bg-blue-100 p-2 rounded-lg">
                            <IconComponent className="h-4 w-4 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <h4 className="font-medium text-gray-900">{item.title}</h4>
                              <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(item.priority)}`}>
                                {item.priority}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{item.description}</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span>⏱️ {item.timeline}</span>
                              <span className="capitalize">📊 {item.type}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Energy Insights */}
            {aiRecommendations.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Energy Insights</h3>
                <div className="space-y-3">
                  {aiRecommendations.slice(0, 3).map((recommendation, idx) => (
                    <div key={idx} className="border border-gray-200 p-4 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <BoltIcon className="h-4 w-4 text-yellow-500" />
                        <span className="font-medium text-gray-900">Market Opportunity</span>
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          {Math.round((recommendation.confidence_score || 0.8) * 100)}% confidence
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{recommendation.reasoning || 'Favorable market conditions detected'}</p>
                      <div className="text-xs text-gray-500">
                        💰 Estimated savings: ${(recommendation.estimated_savings || 15.50).toFixed(2)} | 
                        ⏰ {recommendation.timing_recommendation || 'Act within 2 hours'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Beckn Protocol Integration Notice */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-8 bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-6"
        >
          <div className="flex items-center space-x-3 mb-3">
            <GlobeAltIcon className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Beckn Protocol Integration</h3>
          </div>
          <p className="text-gray-700 mb-3">
            🌐 PowerShare is connected to the Beckn network, enabling cross-platform energy discovery and transactions. 
            This expands your trading opportunities by 40-60% by accessing energy offers from multiple networks.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-4 w-4 text-green-500" />
              <span>Cross-network discovery</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-4 w-4 text-green-500" />
              <span>Standardized transactions</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-4 w-4 text-green-500" />
              <span>Seamless interoperability</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default AIAssistant
