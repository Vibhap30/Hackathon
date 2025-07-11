import React, { useState, useEffect } from 'react'
import { apiService } from '../services/api'

interface EnergyOffer {
  id: number
  seller_id: number
  seller_name: string
  amount: number
  price: number
  location?: string
  renewable_source: boolean
  availability_start: string
  availability_end: string
  created_at: string
}

interface EnergyRequest {
  id: number
  buyer_id: number
  buyer_name: string
  amount: number
  max_price: number
  location?: string
  preferred_renewable: boolean
  required_by: string
  created_at: string
}

const EnergyMarketplace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'offers' | 'requests' | 'my-offers' | 'my-requests'>('offers')
  const [offers, setOffers] = useState<EnergyOffer[]>([])
  const [requests, setRequests] = useState<EnergyRequest[]>([])
  const [myOffers, setMyOffers] = useState<EnergyOffer[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateOffer, setShowCreateOffer] = useState(false)
  const [showCreateRequest, setShowCreateRequest] = useState(false)

  // Filters
  const [filters, setFilters] = useState({
    minAmount: '',
    maxPrice: '',
    location: '',
    renewableOnly: false
  })

  // Form states
  const [offerForm, setOfferForm] = useState({
    amount: '',
    price: '',
    location: '',
    renewable_source: true,
    availability_start: '',
    availability_end: ''
  })

  const [requestForm, setRequestForm] = useState({
    amount: '',
    max_price: '',
    location: '',
    preferred_renewable: true,
    required_by: ''
  })

  useEffect(() => {
    loadData()
  }, [activeTab, filters])

  const loadData = async () => {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'offers':
          const offersData = await apiService.getEnergyOffers(
            0, 100, 
            filters.minAmount ? parseFloat(filters.minAmount) : undefined,
            filters.maxPrice ? parseFloat(filters.maxPrice) : undefined,
            filters.location || undefined
          )
          setOffers(offersData)
          break
        case 'requests':
          const requestsData = await apiService.getEnergyRequests(
            0, 100,
            filters.minAmount ? parseFloat(filters.minAmount) : undefined,
            filters.maxPrice ? parseFloat(filters.maxPrice) : undefined,
            filters.location || undefined
          )
          setRequests(requestsData)
          break
        case 'my-offers':
          const myOffersData = await apiService.getMyEnergyOffers()
          setMyOffers(myOffersData)
          break
        case 'my-requests':
          // Load user's requests
          break
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createOffer = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiService.createEnergyOffer(
        parseFloat(offerForm.amount),
        parseFloat(offerForm.price),
        offerForm.location
      )
      setShowCreateOffer(false)
      setOfferForm({
        amount: '',
        price: '',
        location: '',
        renewable_source: true,
        availability_start: '',
        availability_end: ''
      })
      loadData()
    } catch (error) {
      console.error('Failed to create offer:', error)
    }
  }

  const createRequest = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiService.createEnergyRequest(
        parseFloat(requestForm.amount),
        parseFloat(requestForm.max_price),
        requestForm.location
      )
      setShowCreateRequest(false)
      setRequestForm({
        amount: '',
        max_price: '',
        location: '',
        preferred_renewable: true,
        required_by: ''
      })
      loadData()
    } catch (error) {
      console.error('Failed to create request:', error)
    }
  }

  const purchaseEnergy = async (offerId: number, amount: number) => {
    try {
      await apiService.purchaseEnergy(offerId, amount)
      loadData()
      alert('Energy purchase initiated successfully!')
    } catch (error) {
      console.error('Failed to purchase energy:', error)
      alert('Failed to purchase energy. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Energy Marketplace</h1>
          <p className="text-gray-600 mt-2">Buy and sell renewable energy in your community</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'offers', label: 'Available Offers' },
              { key: 'requests', label: 'Energy Requests' },
              { key: 'my-offers', label: 'My Offers' },
              { key: 'my-requests', label: 'My Requests' }
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

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Min Amount (kWh)</label>
                  <input
                    type="number"
                    value={filters.minAmount}
                    onChange={(e) => setFilters({...filters, minAmount: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Max Price ($/kWh)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={filters.maxPrice}
                    onChange={(e) => setFilters({...filters, maxPrice: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location</label>
                  <input
                    type="text"
                    value={filters.location}
                    onChange={(e) => setFilters({...filters, location: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="renewable-only"
                    checked={filters.renewableOnly}
                    onChange={(e) => setFilters({...filters, renewableOnly: e.target.checked})}
                    className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label htmlFor="renewable-only" className="ml-2 block text-sm text-gray-900">
                    Renewable only
                  </label>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-6 space-y-2">
                <button
                  onClick={() => setShowCreateOffer(true)}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition duration-200"
                >
                  Create Offer
                </button>
                <button
                  onClick={() => setShowCreateRequest(true)}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-200"
                >
                  Request Energy
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
                <p className="text-gray-600 mt-4">Loading...</p>
              </div>
            ) : (
              <>
                {/* Energy Offers */}
                {activeTab === 'offers' && (
                  <div className="space-y-4">
                    {offers.map((offer) => (
                      <div key={offer.id} className="bg-white rounded-lg shadow p-6">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h3 className="text-lg font-medium text-gray-900">
                                {offer.amount} kWh
                              </h3>
                              {offer.renewable_source && (
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                  🌱 Renewable
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              Seller: {offer.seller_name}
                            </p>
                            <p className="text-sm text-gray-600">
                              Location: {offer.location || 'Not specified'}
                            </p>
                            <p className="text-lg font-bold text-green-600 mt-2">
                              ${offer.price}/kWh
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                              Available: {new Date(offer.availability_start).toLocaleDateString()} - 
                              {new Date(offer.availability_end).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="ml-4">
                            <button
                              onClick={() => purchaseEnergy(offer.id, offer.amount)}
                              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200"
                            >
                              Purchase
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                    {offers.length === 0 && (
                      <div className="text-center py-8">
                        <p className="text-gray-600">No energy offers available</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Energy Requests */}
                {activeTab === 'requests' && (
                  <div className="space-y-4">
                    {requests.map((request) => (
                      <div key={request.id} className="bg-white rounded-lg shadow p-6">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h3 className="text-lg font-medium text-gray-900">
                                Looking for {request.amount} kWh
                              </h3>
                              {request.preferred_renewable && (
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                  🌱 Prefers Renewable
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              Buyer: {request.buyer_name}
                            </p>
                            <p className="text-sm text-gray-600">
                              Location: {request.location || 'Not specified'}
                            </p>
                            <p className="text-lg font-bold text-blue-600 mt-2">
                              Up to ${request.max_price}/kWh
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                              Required by: {new Date(request.required_by).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="ml-4">
                            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200">
                              Make Offer
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                    {requests.length === 0 && (
                      <div className="text-center py-8">
                        <p className="text-gray-600">No energy requests available</p>
                      </div>
                    )}
                  </div>
                )}

                {/* My Offers */}
                {activeTab === 'my-offers' && (
                  <div className="space-y-4">
                    {myOffers.map((offer) => (
                      <div key={offer.id} className="bg-white rounded-lg shadow p-6">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="text-lg font-medium text-gray-900">
                              {offer.amount} kWh - ${offer.price}/kWh
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">
                              Location: {offer.location || 'Not specified'}
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                              Created: {new Date(offer.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="ml-4 space-x-2">
                            <button className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition duration-200">
                              Edit
                            </button>
                            <button className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition duration-200">
                              Cancel
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                    {myOffers.length === 0 && (
                      <div className="text-center py-8">
                        <p className="text-gray-600">You haven't created any offers yet</p>
                        <button
                          onClick={() => setShowCreateOffer(true)}
                          className="mt-4 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200"
                        >
                          Create Your First Offer
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Create Offer Modal */}
        {showCreateOffer && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Energy Offer</h3>
              <form onSubmit={createOffer} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Amount (kWh)</label>
                  <input
                    type="number"
                    required
                    value={offerForm.amount}
                    onChange={(e) => setOfferForm({...offerForm, amount: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Price ($/kWh)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={offerForm.price}
                    onChange={(e) => setOfferForm({...offerForm, price: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location</label>
                  <input
                    type="text"
                    value={offerForm.location}
                    onChange={(e) => setOfferForm({...offerForm, location: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="renewable-source"
                    checked={offerForm.renewable_source}
                    onChange={(e) => setOfferForm({...offerForm, renewable_source: e.target.checked})}
                    className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label htmlFor="renewable-source" className="ml-2 block text-sm text-gray-900">
                    Renewable Energy Source
                  </label>
                </div>
                <div className="flex space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateOffer(false)}
                    className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition duration-200"
                  >
                    Create Offer
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Create Request Modal */}
        {showCreateRequest && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Request Energy</h3>
              <form onSubmit={createRequest} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Amount (kWh)</label>
                  <input
                    type="number"
                    required
                    value={requestForm.amount}
                    onChange={(e) => setRequestForm({...requestForm, amount: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Max Price ($/kWh)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={requestForm.max_price}
                    onChange={(e) => setRequestForm({...requestForm, max_price: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location</label>
                  <input
                    type="text"
                    value={requestForm.location}
                    onChange={(e) => setRequestForm({...requestForm, location: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Required By</label>
                  <input
                    type="datetime-local"
                    required
                    value={requestForm.required_by}
                    onChange={(e) => setRequestForm({...requestForm, required_by: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="preferred-renewable"
                    checked={requestForm.preferred_renewable}
                    onChange={(e) => setRequestForm({...requestForm, preferred_renewable: e.target.checked})}
                    className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label htmlFor="preferred-renewable" className="ml-2 block text-sm text-gray-900">
                    Prefer Renewable Energy
                  </label>
                </div>
                <div className="flex space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateRequest(false)}
                    className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-200"
                  >
                    Create Request
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default EnergyMarketplace
