import React, { useState, useEffect } from 'react'
import { apiService } from '../services/api'

interface Community {
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
  is_member?: boolean
}

interface CommunityMember {
  id: number
  user_id: number
  user_name: string
  energy_contribution: number
  reputation_score: number
  joined_at: string
  role: string
}

const Community: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'discover' | 'my-communities' | 'create'>('discover')
  const [communities, setCommunities] = useState<Community[]>([])
  const [myCommunities, setMyCommunities] = useState<Community[]>([])
  const [selectedCommunity, setSelectedCommunity] = useState<Community | null>(null)
  const [communityMembers, setCommunityMembers] = useState<CommunityMember[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)

  // Filters
  const [filters, setFilters] = useState({
    community_type: '',
    location: '',
    min_capacity: '',
    has_space: false
  })

  // Create form
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
    location: '',
    community_type: 'residential',
    max_members: '50'
  })

  useEffect(() => {
    loadData()
  }, [activeTab, filters])

  const loadData = async () => {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'discover':
          const communitiesData = await apiService.getCommunities(
            0, 100, 
            filters.community_type || undefined,
            filters.location || undefined
          )
          setCommunities(communitiesData)
          break
        case 'my-communities':
          const myCommunitiesData = await apiService.getMyCommunities()
          setMyCommunities(myCommunitiesData)
          break
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCommunityDetails = async (communityId: number) => {
    try {
      const members = await apiService.getCommunityMembers(communityId)
      setCommunityMembers(members)
    } catch (error) {
      console.error('Failed to load community details:', error)
    }
  }

  const joinCommunity = async (communityId: number) => {
    try {
      await apiService.joinCommunity(communityId)
      alert('Successfully joined the community!')
      loadData()
    } catch (error) {
      console.error('Failed to join community:', error)
      alert('Failed to join community. Please try again.')
    }
  }

  const leaveCommunity = async (communityId: number) => {
    try {
      await apiService.leaveCommunity(communityId)
      alert('Successfully left the community!')
      loadData()
      setSelectedCommunity(null)
    } catch (error) {
      console.error('Failed to leave community:', error)
      alert('Failed to leave community. Please try again.')
    }
  }

  const createCommunity = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiService.createCommunity({
        name: createForm.name,
        description: createForm.description,
        location: createForm.location,
        community_type: createForm.community_type,
        max_members: parseInt(createForm.max_members)
      })
      setShowCreateForm(false)
      setCreateForm({
        name: '',
        description: '',
        location: '',
        community_type: 'residential',
        max_members: '50'
      })
      alert('Community created successfully!')
      loadData()
    } catch (error) {
      console.error('Failed to create community:', error)
      alert('Failed to create community. Please try again.')
    }
  }

  const CommunityCard = ({ community, showJoinButton = true }: { community: Community, showJoinButton?: boolean }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">{community.name}</h3>
          <div className="flex items-center space-x-2 mt-1">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {community.community_type}
            </span>
            {community.location && (
              <span className="text-sm text-gray-500">📍 {community.location}</span>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-500">Energy Available</div>
          <div className="text-lg font-bold text-green-600">
            {community.total_current_energy.toFixed(1)} kWh
          </div>
        </div>
      </div>

      <p className="text-gray-600 mb-4">{community.description}</p>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-lg font-semibold text-gray-900">{community.member_count}</div>
          <div className="text-sm text-gray-600">Members</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-lg font-semibold text-gray-900">
            {community.total_energy_capacity.toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">Total Capacity (kWh)</div>
        </div>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => {
            setSelectedCommunity(community)
            loadCommunityDetails(community.id)
          }}
          className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition duration-200"
        >
          View Details
        </button>
        {showJoinButton && !community.is_member && community.member_count < community.max_members && (
          <button
            onClick={() => joinCommunity(community.id)}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition duration-200"
          >
            Join Community
          </button>
        )}
        {community.is_member && (
          <button
            onClick={() => leaveCommunity(community.id)}
            className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition duration-200"
          >
            Leave
          </button>
        )}
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Energy Communities</h1>
          <p className="text-gray-600 mt-2">Join or create communities to share renewable energy</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'discover', label: 'Discover Communities' },
              { key: 'my-communities', label: 'My Communities' },
              { key: 'create', label: 'Create Community' }
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

        {/* Discover Communities */}
        {activeTab === 'discover' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Filters */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Community Type</label>
                    <select
                      value={filters.community_type}
                      onChange={(e) => setFilters({...filters, community_type: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                    >
                      <option value="">All Types</option>
                      <option value="residential">Residential</option>
                      <option value="commercial">Commercial</option>
                      <option value="industrial">Industrial</option>
                      <option value="mixed">Mixed</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Location</label>
                    <input
                      type="text"
                      value={filters.location}
                      onChange={(e) => setFilters({...filters, location: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                      placeholder="Enter city or area"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Min Capacity (kWh)</label>
                    <input
                      type="number"
                      value={filters.min_capacity}
                      onChange={(e) => setFilters({...filters, min_capacity: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="has-space"
                      checked={filters.has_space}
                      onChange={(e) => setFilters({...filters, has_space: e.target.checked})}
                      className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                    />
                    <label htmlFor="has-space" className="ml-2 block text-sm text-gray-900">
                      Has available spots
                    </label>
                  </div>
                </div>

                <button
                  onClick={() => setShowCreateForm(true)}
                  className="w-full mt-6 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition duration-200"
                >
                  Create New Community
                </button>
              </div>
            </div>

            {/* Communities Grid */}
            <div className="lg:col-span-3">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
                  <p className="text-gray-600 mt-4">Loading communities...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {communities.map((community) => (
                    <CommunityCard key={community.id} community={community} />
                  ))}
                  {communities.length === 0 && (
                    <div className="col-span-2 text-center py-8">
                      <p className="text-gray-600">No communities found matching your criteria</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* My Communities */}
        {activeTab === 'my-communities' && (
          <div>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
                <p className="text-gray-600 mt-4">Loading your communities...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {myCommunities.map((community) => (
                  <CommunityCard key={community.id} community={community} showJoinButton={false} />
                ))}
                {myCommunities.length === 0 && (
                  <div className="col-span-3 text-center py-8">
                    <p className="text-gray-600">You haven't joined any communities yet</p>
                    <button
                      onClick={() => setActiveTab('discover')}
                      className="mt-4 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200"
                    >
                      Discover Communities
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Create Community */}
        {activeTab === 'create' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6">Create New Community</h3>
              <form onSubmit={createCommunity} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Community Name</label>
                  <input
                    type="text"
                    required
                    value={createForm.name}
                    onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                    placeholder="Enter community name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    required
                    rows={4}
                    value={createForm.description}
                    onChange={(e) => setCreateForm({...createForm, description: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                    placeholder="Describe your community's purpose and goals"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Location</label>
                    <input
                      type="text"
                      value={createForm.location}
                      onChange={(e) => setCreateForm({...createForm, location: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                      placeholder="City, Area"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Community Type</label>
                    <select
                      value={createForm.community_type}
                      onChange={(e) => setCreateForm({...createForm, community_type: e.target.value})}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                    >
                      <option value="residential">Residential</option>
                      <option value="commercial">Commercial</option>
                      <option value="industrial">Industrial</option>
                      <option value="mixed">Mixed</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Maximum Members</label>
                  <input
                    type="number"
                    required
                    min="2"
                    max="1000"
                    value={createForm.max_members}
                    onChange={(e) => setCreateForm({...createForm, max_members: e.target.value})}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                  />
                </div>

                <div className="flex space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setActiveTab('discover')}
                    className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition duration-200"
                  >
                    Create Community
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Community Details Modal */}
        {selectedCommunity && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">{selectedCommunity.name}</h3>
                  <p className="text-gray-600 mt-1">{selectedCommunity.description}</p>
                </div>
                <button
                  onClick={() => setSelectedCommunity(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600">{selectedCommunity.member_count}</div>
                  <div className="text-sm text-blue-800">Active Members</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {selectedCommunity.total_current_energy.toFixed(1)}
                  </div>
                  <div className="text-sm text-green-800">Available Energy (kWh)</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {selectedCommunity.total_energy_capacity.toFixed(1)}
                  </div>
                  <div className="text-sm text-purple-800">Total Capacity (kWh)</div>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">Community Members</h4>
                <div className="space-y-3">
                  {communityMembers.map((member) => (
                    <div key={member.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-900">{member.user_name}</div>
                        <div className="text-sm text-gray-600">
                          Joined: {new Date(member.joined_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-green-600">
                          {member.energy_contribution.toFixed(1)} kWh contributed
                        </div>
                        <div className="text-sm text-gray-600">
                          Reputation: {member.reputation_score}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Community
