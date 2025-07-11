import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  BoltIcon, 
  ChartBarIcon, 
  CpuChipIcon,
  CheckCircleIcon,
  SunIcon,
  UserGroupIcon,
  LightBulbIcon,
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  GlobeAltIcon,
  BeakerIcon
} from '@heroicons/react/24/outline'
import apiService from '../services/api'

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
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [selectedAgents, setSelectedAgents] = useState<string[]>(['all'])
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

  const quickActions = [
    {
      label: "🔥 Get trading recommendations",
      action: () => setInputMessage("What are the best energy trading opportunities right now?")
    },
    {
      label: "⚡ Optimize my energy usage", 
      action: () => setInputMessage("How can I optimize my energy consumption and reduce costs?")
    },
    {
      label: "🌍 Find local energy sources",
      action: () => setInputMessage("Show me renewable energy sources in my area")
    },
    {
      label: "🤝 Community opportunities",
      action: () => setInputMessage("What community energy programs should I consider?")
    },
    {
      label: "🌐 Cross-network energy options",
      action: () => setInputMessage("Find energy offers from other networks via Beckn protocol")
    },
    {
      label: "📊 Market analysis",
      action: () => setInputMessage("Give me a market analysis for energy trading")
    }
  ]

  useEffect(() => {
    initializeChat()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

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
      // Query agents based on selection using real API
      const response = await apiService.queryAIAgents({
        query: inputMessage,
        context: {
          selected_agents: selectedAgents,
          user_preferences: {},
          current_time: new Date().toISOString()
        }
      })

      // If backend returns a list of agent responses, display them
      if (response && response.agent_responses && Array.isArray(response.agent_responses)) {
        for (const agentResponse of response.agent_responses) {
          const agentMessage: ChatMessage = {
            id: `${Date.now()}_${agentResponse.agent_type || 'agent'}`,
            type: 'agent',
            content: agentResponse.response || agentResponse.content || '',
            timestamp: new Date(),
            agent_type: agentResponse.agent_type,
            agent_name: agentResponse.agent_name,
            reasoning: agentResponse.reasoning,
            confidence: agentResponse.confidence,
            data: agentResponse.data
          }
          setMessages(prev => [...prev, agentMessage])
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      } else if (response && response.response) {
        // If backend returns a single response
        const agentMessage: ChatMessage = {
          id: `${Date.now()}_agent`,
          type: 'agent',
          content: response.response,
          timestamp: new Date(),
          agent_name: response.agent_name,
          reasoning: response.reasoning,
          confidence: response.confidence,
          data: response.data
        }
        setMessages(prev => [...prev, agentMessage])
      } else {
        // Fallback: show a generic error message
        setMessages(prev => [...prev, {
          id: `${Date.now()}_error`,
          type: 'system',
          content: 'Sorry, no response received from the AI agents.',
          timestamp: new Date(),
        }])
      }
    } catch (error) {
      console.error('Failed to query agents:', error)
      setMessages(prev => [...prev, {
        id: `${Date.now()}_error`,
        type: 'system',
        content: 'An error occurred while contacting the AI agents. Please try again later.',
        timestamp: new Date(),
      }])
    } finally {
      setIsTyping(false)
    }

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-green-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
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
          
          <div className="flex items-center space-x-4 text-sm">
            <span className="px-2 py-1 rounded-full bg-green-100 text-green-800">
              Trading Agent: active
            </span>
            <span className="px-2 py-1 rounded-full bg-green-100 text-green-800">
              Optimization Agent: active
            </span>
            <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800">
              Beckn Protocol: active
            </span>
          </div>
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

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Quick Actions</h3>
              <div className="space-y-2">
                {quickActions.map((action, index) => (
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
                          
                          <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</div>
                          
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
