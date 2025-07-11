
/**
 * API Service for PowerShare Frontend
 * Handles all HTTP requests to the backend
 */

import axios, { AxiosInstance } from 'axios'

// Types
export interface User {
  id: number
  email: string
  full_name: string
  phone?: string
  location?: string
  bio?: string
  wallet_address?: string
  energy_capacity: number
  current_energy: number
  is_active: boolean
  reputation_score: number
  created_at: string
}

export interface EnergyTransaction {
  id: number
  seller_id: number
  buyer_id: number
  amount: number
  price: number
  status: string
  transaction_type: string
  blockchain_tx_hash?: string
  created_at: string
}

export interface IoTDevice {
  id: number
  user_id: number
  device_type: string
  name: string
  location?: string
  specifications: Record<string, any>
  energy_production: number
  energy_consumption: number
  status: string
  is_active: boolean
  last_reading_at?: string
  created_at: string
}

export interface Community {
  id: number
  name: string
  description: string
  location?: string
  community_type: string
  creator_id: number
  member_count: number
  max_members: number
  total_energy_capacity: number
  total_current_energy: number
  is_active: boolean
  created_at: string
}

export interface TradingRecommendation {
  action: string
  suggested_price: number
  suggested_amount: number
  confidence_score: number
  reasoning: string
  market_conditions: Record<string, any>
  alternative_options: Array<Record<string, any>>
}

export interface MarketAnalytics {
  total_volume: number
  average_price: number
  price_trend: string
  volume_trend: string
  peak_hours: number[]
  active_traders: number
  price_volatility: number
  market_efficiency: number
}

// API Configuration
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiService {

  // Collect coins (gamification)
  async collectCoins(): Promise<{ message: string; coins_collected: number; total_balance: number }> {
    const response = await this.client.post('/blockchain/tokens/collect')
    return response.data
  }
  private client: AxiosInstance
  private token: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout()
        }
        return Promise.reject(error)
      }
    )

    // Load token from localStorage
    this.token = localStorage.getItem('auth_token')
  }

  // Authentication Methods
  async login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    this.token = response.data.access_token
    localStorage.setItem('auth_token', this.token!)
    
    return response.data
  }

  async register(email: string, password: string, full_name: string, wallet_address?: string): Promise<User> {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      full_name,
      wallet_address
    })
    return response.data
  }

  logout(): void {
    this.token = null
    localStorage.removeItem('auth_token')
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/auth/me')
    return response.data
  }

  // User Methods
  async getUsers(skip = 0, limit = 100): Promise<User[]> {
    const response = await this.client.get('/users/', {
      params: { skip, limit }
    })
    return response.data
  }

  async updateUser(data: Partial<User>): Promise<User> {
    const response = await this.client.put('/users/me', data)
    return response.data
  }

  async updateUserEnergy(current_energy: number): Promise<User> {
    const response = await this.client.put('/users/me/energy', { current_energy })
    return response.data
  }

  async getUserStats(): Promise<any> {
    const response = await this.client.get('/users/me/stats')
    return response.data
  }

  // Energy Trading Methods
  async getEnergyOffers(
    skip = 0, 
    limit = 100, 
    min_amount?: number, 
    max_price?: number, 
    seller_location?: string
  ): Promise<any[]> {
    const response = await this.client.get('/energy/offers', {
      params: { skip, limit, min_amount, max_price, seller_location }
    })
    return response.data
  }

  async createEnergyOffer(amount: number, price: number, location?: string): Promise<any> {
    const response = await this.client.post('/energy/offers', {
      amount,
      price,
      location
    })
    return response.data
  }

  async purchaseEnergy(offer_id: number, amount: number): Promise<any> {
    const response = await this.client.post('/energy/purchase', {
      offer_id,
      amount
    })
    return response.data
  }

  async getEnergyRequests(
    skip = 0, 
    limit = 100, 
    min_amount?: number, 
    max_price?: number, 
    buyer_location?: string
  ): Promise<any[]> {
    const response = await this.client.get('/energy/requests', {
      params: { skip, limit, min_amount, max_price, buyer_location }
    })
    return response.data
  }

  async createEnergyRequest(amount: number, max_price: number, location?: string): Promise<any> {
    const response = await this.client.post('/energy/requests', {
      amount,
      max_price,
      location
    })
    return response.data
  }

  async getMyEnergyOffers(skip = 0, limit = 100): Promise<any[]> {
    const response = await this.client.get('/energy/my-offers', {
      params: { skip, limit }
    })
    return response.data
  }

  async getMyEnergyRequests(skip = 0, limit = 100): Promise<any[]> {
    const response = await this.client.get('/energy/my-requests', {
      params: { skip, limit }
    })
    return response.data
  }

  // IoT Device Methods
  async getIoTDevices(skip = 0, limit = 100, device_type?: string): Promise<IoTDevice[]> {
    const response = await this.client.get('/iot/', {
      params: { skip, limit, device_type }
    })
    return response.data
  }

  async createIoTDevice(data: {
    device_type: string
    name: string
    location?: string
    specifications?: Record<string, any>
  }): Promise<IoTDevice> {
    const response = await this.client.post('/iot/', data)
    return response.data
  }

  async updateIoTDevice(device_id: number, data: Partial<IoTDevice>): Promise<IoTDevice> {
    const response = await this.client.put(`/iot/${device_id}`, data)
    return response.data
  }

  async updateDeviceReading(device_id: number, data: {
    energy_production: number
    energy_consumption: number
    status?: string
    metadata?: Record<string, any>
  }): Promise<any> {
    const response = await this.client.post(`/iot/${device_id}/readings`, data)
    return response.data
  }

  async deleteIoTDevice(device_id: number): Promise<void> {
    await this.client.delete(`/iot/${device_id}`)
  }

  // Community Methods
  async getCommunities(
    skip = 0, 
    limit = 100, 
    community_type?: string, 
    location?: string
  ): Promise<Community[]> {
    const response = await this.client.get('/communities/', {
      params: { skip, limit, community_type, location }
    })
    return response.data
  }

  async createCommunity(data: {
    name: string
    description: string
    location?: string
    community_type?: string
    max_members?: number
  }): Promise<Community> {
    const response = await this.client.post('/communities/', data)
    return response.data
  }

  async joinCommunity(community_id: number): Promise<any> {
    const response = await this.client.post(`/communities/${community_id}/join`)
    return response.data
  }

  async leaveCommunity(community_id: number): Promise<any> {
    const response = await this.client.post(`/communities/${community_id}/leave`)
    return response.data
  }

  async getCommunityMembers(community_id: number): Promise<any[]> {
    const response = await this.client.get(`/communities/${community_id}/members`)
    return response.data
  }

  async getMyCommunities(): Promise<Community[]> {
    const response = await this.client.get('/communities/my')
    return response.data
  }

  // Analytics Methods
  async getMarketAnalytics(): Promise<any> {
    const response = await this.client.get('/analytics/market')
    return response.data
  }

  async getPriceHistory(timeframe: string): Promise<any[]> {
    const response = await this.client.get('/analytics/price-history', {
      params: { timeframe }
    })
    return response.data
  }

  async getVolumeHistory(timeframe: string): Promise<any[]> {
    const response = await this.client.get('/analytics/volume-history', {
      params: { timeframe }
    })
    return response.data
  }

  async getUserAnalytics(): Promise<any> {
    const response = await this.client.get('/analytics/user')
    return response.data
  }

  async getCommunityAnalytics(community_id?: number): Promise<any> {
    const response = await this.client.get('/analytics/community', {
      params: community_id ? { community_id } : {}
    })
    return response.data
  }

  async getPlatformAnalytics(): Promise<any> {
    const response = await this.client.get('/analytics/platform')
    return response.data
  }

  async getPredictiveAnalytics(timeframe: string): Promise<any[]> {
    const response = await this.client.get('/analytics/predictive', {
      params: { timeframe }
    })
    return response.data
  }

  async exportAnalyticsData(type: string, timeframe: string, format: string): Promise<string> {
    const response = await this.client.get('/analytics/export', {
      params: { type, timeframe, format },
      responseType: 'text'
    })
    return response.data
  }

  // Security and Settings Methods
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.client.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  }

  async enableTwoFactor(): Promise<any> {
    const response = await this.client.post('/auth/enable-2fa')
    return response.data
  }

  async disableTwoFactor(): Promise<void> {
    await this.client.post('/auth/disable-2fa')
  }

  async getUserSettings(): Promise<any> {
    const response = await this.client.get('/users/settings')
    return response.data
  }

  async updateUserSettings(settings: any): Promise<void> {
    await this.client.put('/users/settings', settings)
  }

  // AI Agent Methods
  async getTradingRecommendation(data: {
    energy_amount: number
    max_price?: number
    preferred_sellers?: number[]
    urgency?: string
  }): Promise<TradingRecommendation> {
    const response = await this.client.post('/ai/recommendations/trading', data)
    return response.data
  }

  async getEnergyPredictions(data: {
    prediction_type: string
    timeframe?: string
    location?: string
  }): Promise<any> {
    const response = await this.client.post('/ai/predictions', data)
    return response.data
  }

  async getOptimizationRecommendations(data: {
    optimization_type: string
    constraints?: Record<string, any>
    objectives?: string[]
  }): Promise<any> {
    const response = await this.client.post('/ai/optimization', data)
    return response.data
  }

  async getAutoTradingConfig(): Promise<any> {
    const response = await this.client.get('/ai/auto-trading/config')
    return response.data
  }

  async updateAutoTradingConfig(config: any): Promise<any> {
    const response = await this.client.put('/ai/auto-trading/config', config)
    return response.data
  }

  async requestEnergyTradingAnalysis(data: {
    energy_amount: number
    max_price?: number
    preferred_sellers?: number[]
    urgency?: string
  }): Promise<any> {
    const response = await this.client.post('/ai/energy-trading/analyze', data)
    return response.data
  }

  async requestEnergyOptimization(data: {
    optimization_goals?: string[]
    location?: { lat: number; lng: number }
    preferences?: Record<string, any>
  }): Promise<any> {
    const response = await this.client.post('/ai/optimization/analyze', data)
    return response.data
  }

  async getAIRecommendations(): Promise<any> {
    const response = await this.client.get('/ai/recommendations')
    return response.data
  }

  async getOptimizationResults(): Promise<any> {
    const response = await this.client.get('/ai/optimization/results')
    return response.data
  }

  async getAIActionItems(): Promise<any> {
    const response = await this.client.get('/ai/action-items')
    return response.data
  }

  async completeActionItem(actionId: string): Promise<any> {
    const response = await this.client.post(`/ai/action-items/${actionId}/complete`)
    return response.data
  }

  // Enhanced AI Analytics
  async getAIMarketAnalysis(): Promise<any> {
    const response = await this.client.get('/ai/market-analysis')
    return response.data
  }

  async getAIAgentsStatus(): Promise<any> {
    const response = await this.client.get('/ai/status')
    return response.data
  }

  async resetAISession(): Promise<any> {
    const response = await this.client.post('/ai/reset-session')
    return response.data
  }

  // Blockchain Methods
  async getSmartContractInfo(): Promise<any> {
    const response = await this.client.get('/blockchain/info')
    return response.data
  }

  async getWalletInfo(address: string): Promise<any> {
    const response = await this.client.get(`/blockchain/wallet/${address}`)
    return response.data
  }

  async callSmartContract(data: {
    function_name: string
    parameters: Record<string, any>
    gas_limit?: number
  }): Promise<any> {
    const response = await this.client.post('/blockchain/contract/call', data)
    return response.data
  }

  async createBlockchainEnergyOffer(amount: number, price_per_unit: number): Promise<any> {
    const response = await this.client.post('/blockchain/energy-offer', {
      amount,
      price_per_unit
    })
    return response.data
  }

  // Add the missing queryAIAgents method
  async queryAIAgents(payload: {
    query: string,
    context: any
  }) {
    const response = await this.client.post('/ai/query', payload)
    return response.data
  }

  // Get all available AI agents
  async getAgents(): Promise<any> {
    const response = await this.client.get('/ai/agents')
    return response.data
  }

  // Get demo recommendations for prosumers
  async getDemoProsumerRecommendations(): Promise<any> {
    const response = await this.client.get('/ai/demo/prosumer-recommendations')
    return response.data
  }

  // Get demo recommendations for consumers
  async getDemoConsumerRecommendations(): Promise<any> {
    const response = await this.client.get('/ai/demo/consumer-recommendations')
    return response.data
  }

  // Get personalized recommendations
  async getPersonalizedRecommendations(context?: any): Promise<any> {
    const response = await this.client.post('/ai/demo/personalized-recommendations', context)
    return response.data
  }

  // Get Beckn protocol integration showcase
  async getBecknIntegrationShowcase(): Promise<any> {
    const response = await this.client.get('/ai/demo/beckn-integration-showcase')
    return response.data
  }

  // Get locality energy map
  async getLocalityEnergyMap(latitude: number, longitude: number, radius_km?: number): Promise<any> {
    const response = await this.client.post('/ai/locality-map', {
      latitude,
      longitude,
      radius_km
    })
    return response.data
  }

  // Get bid matching results
  async getBidMatching(request: {
    energy_amount: number,
    max_price?: number,
    preferred_sellers?: number[],
    urgency?: string,
    location?: { latitude: number, longitude: number }
  }): Promise<any> {
    const response = await this.client.post('/ai/bid-matching', request)
    return response.data
  }

  // Generic GET request
  async get(endpoint: string, params?: any): Promise<any> {
    const response = await this.client.get(endpoint, { params })
    return response.data
  }

  // Generic POST request
  async post(endpoint: string, data?: any): Promise<any> {
    const response = await this.client.post(endpoint, data)
    return response.data
  }

  // Generic PUT request
  async put(endpoint: string, data?: any): Promise<any> {
    const response = await this.client.put(endpoint, data)
    return response.data
  }

  // Generic DELETE request
  async delete(endpoint: string): Promise<any> {
    const response = await this.client.delete(endpoint)
    return response.data
  }
}

// Export singleton instance
export const apiService = new ApiService()
export default apiService
