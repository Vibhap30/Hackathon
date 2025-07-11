import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAPI } from '../hooks/useAPI';
import {
  ChartBarIcon,
  CpuChipIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  LightBulbIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface BidOptimizationRequest {
  energyAmount: number;
  timeSlot: string;
  maxPrice: number;
  urgency: 'low' | 'medium' | 'high';
  preferences: {
    renewable_only: boolean;
    local_priority: boolean;
    carbon_neutral: boolean;
  };
}

interface OptimizedBid {
  suggestedPrice: number;
  confidence: number;
  potentialSavings: number;
  matchProbability: number;
  recommendations: string[];
  marketAnalysis: {
    currentMarketPrice: number;
    predictedPriceChange: number;
    demandLevel: string;
    supplyLevel: string;
  };
  quantumAnalysis?: {
    optimalTimingWindow: string;
    quantumAdvantage: number;
    probabilityDistribution: Array<{ price: number; probability: number }>;
  };
}

interface HistoricalData {
  timestamp: string;
  price: number;
  demand: number;
  supply: number;
  savings: number;
}

const BidOptimizer: React.FC = () => {
  const [bidRequest, setBidRequest] = useState<BidOptimizationRequest>({
    energyAmount: 50,
    timeSlot: '14:00',
    maxPrice: 0.25,
    urgency: 'medium',
    preferences: {
      renewable_only: false,
      local_priority: true,
      carbon_neutral: false
    }
  });
  
  const [optimizedBid, setOptimizedBid] = useState<OptimizedBid | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [useQuantum, setUseQuantum] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const api = useAPI();

  useEffect(() => {
    // Load historical optimization data
    loadHistoricalData();
  }, []);

  const loadHistoricalData = async () => {
    try {
      const data = await api.get<HistoricalData[]>('/api/v1/bid-optimization/history');
      setHistoricalData(data);
    } catch (err) {
      console.error('Failed to load historical data:', err);
    }
  };

  const handleOptimizeBid = async () => {
    setIsOptimizing(true);
    setError(null);
    
    try {
      const endpoint = useQuantum 
        ? '/api/v1/bid-optimization/quantum-optimize'
        : '/api/v1/bid-optimization/optimize';
      
      const response = await api.post<OptimizedBid>(endpoint, bidRequest);
      setOptimizedBid(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Optimization failed');
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleInputChange = (field: keyof BidOptimizationRequest, value: any) => {
    setBidRequest(prev => ({ ...prev, [field]: value }));
  };

  const handlePreferenceChange = (preference: keyof BidOptimizationRequest['preferences']) => {
    setBidRequest(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [preference]: !prev.preferences[preference]
      }
    }));
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSavingsColor = (savings: number) => {
    if (savings > 0) return 'text-green-600';
    if (savings < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <CpuChipIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Bid Optimizer</h1>
              <p className="text-gray-600">Optimize your energy bids with machine learning and quantum computing</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={useQuantum}
                onChange={(e) => setUseQuantum(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-2 text-sm text-gray-700">Enable Quantum Optimization</span>
            </label>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bid Configuration */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Bid Configuration</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Energy Amount (kWh)
              </label>
              <input
                type="number"
                value={bidRequest.energyAmount}
                onChange={(e) => handleInputChange('energyAmount', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                step="0.1"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Time Slot
              </label>
              <input
                type="time"
                value={bidRequest.timeSlot}
                onChange={(e) => handleInputChange('timeSlot', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Price ($/kWh)
              </label>
              <input
                type="number"
                value={bidRequest.maxPrice}
                onChange={(e) => handleInputChange('maxPrice', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                step="0.01"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Urgency Level
              </label>
              <select
                value={bidRequest.urgency}
                onChange={(e) => handleInputChange('urgency', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferences
              </label>
              <div className="space-y-2">
                {Object.entries(bidRequest.preferences).map(([key, value]) => (
                  <label key={key} className="inline-flex items-center">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={() => handlePreferenceChange(key as keyof BidOptimizationRequest['preferences'])}
                      className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-700 capitalize">
                      {key.replace('_', ' ')}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <motion.button
              onClick={handleOptimizeBid}
              disabled={isOptimizing}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-md text-white font-medium ${
                isOptimizing
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isOptimizing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Optimizing...</span>
                </>
              ) : (
                <>
                  <LightBulbIcon className="h-5 w-5" />
                  <span>Optimize Bid</span>
                </>
              )}
            </motion.button>
          </div>
        </div>

        {/* Optimization Results */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Optimization Results</h2>
          
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-center">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
                <span className="text-sm text-red-600">{error}</span>
              </div>
            </div>
          )}

          {optimizedBid ? (
            <div className="space-y-4">
              {/* Key Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Suggested Price</p>
                      <p className="text-lg font-semibold text-gray-900">
                        ${optimizedBid.suggestedPrice.toFixed(3)}/kWh
                      </p>
                    </div>
                    <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
                  </div>
                </div>

                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Potential Savings</p>
                      <p className={`text-lg font-semibold ${getSavingsColor(optimizedBid.potentialSavings)}`}>
                        ${optimizedBid.potentialSavings.toFixed(2)}
                      </p>
                    </div>
                    {optimizedBid.potentialSavings > 0 ? (
                      <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-8 w-8 text-red-600" />
                    )}
                  </div>
                </div>

                <div className="p-4 bg-yellow-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Confidence</p>
                      <p className={`text-lg font-semibold ${getConfidenceColor(optimizedBid.confidence)}`}>
                        {optimizedBid.confidence.toFixed(0)}%
                      </p>
                    </div>
                    <ChartBarIcon className="h-8 w-8 text-yellow-600" />
                  </div>
                </div>

                <div className="p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Match Probability</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {optimizedBid.matchProbability.toFixed(0)}%
                      </p>
                    </div>
                    <CheckCircleIcon className="h-8 w-8 text-purple-600" />
                  </div>
                </div>
              </div>

              {/* Market Analysis */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Market Analysis</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Current Price:</span>
                    <span className="ml-2 font-medium">${optimizedBid.marketAnalysis.currentMarketPrice.toFixed(3)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Price Trend:</span>
                    <span className={`ml-2 font-medium ${
                      optimizedBid.marketAnalysis.predictedPriceChange > 0 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {optimizedBid.marketAnalysis.predictedPriceChange > 0 ? '+' : ''}
                      {optimizedBid.marketAnalysis.predictedPriceChange.toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Demand:</span>
                    <span className="ml-2 font-medium capitalize">{optimizedBid.marketAnalysis.demandLevel}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Supply:</span>
                    <span className="ml-2 font-medium capitalize">{optimizedBid.marketAnalysis.supplyLevel}</span>
                  </div>
                </div>
              </div>

              {/* Quantum Analysis (if enabled) */}
              {useQuantum && optimizedBid.quantumAnalysis && (
                <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                  <h3 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                    <CpuChipIcon className="h-4 w-4 mr-1 text-purple-600" />
                    Quantum Analysis
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Optimal Timing:</span>
                      <span className="ml-2 font-medium">{optimizedBid.quantumAnalysis.optimalTimingWindow}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Quantum Advantage:</span>
                      <span className="ml-2 font-medium text-purple-600">
                        {optimizedBid.quantumAnalysis.quantumAdvantage.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-2">Recommendations</h3>
                <ul className="space-y-1">
                  {optimizedBid.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Configure your bid and click "Optimize Bid" to get AI-powered recommendations</p>
            </div>
          )}
        </div>
      </div>

      {/* Historical Performance Chart */}
      {historicalData.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Historical Performance</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="savings"
                  stroke="#10B981"
                  fill="#10B981"
                  fillOpacity={0.2}
                  name="Savings ($)"
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.2}
                  name="Price ($/kWh)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default BidOptimizer;