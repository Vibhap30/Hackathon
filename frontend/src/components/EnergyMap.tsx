import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  MapPinIcon,
  AdjustmentsHorizontalIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';

interface EnergyNode {
  id: string;
  name: string;
  type: 'producer' | 'consumer' | 'community' | 'storage';
  location: {
    lat: number;
    lng: number;
    address: string;
    city: string;
    state: string;
  };
  capacity: number;
  currentProduction: number;
  currentConsumption: number;
  status: 'active' | 'inactive' | 'maintenance';
  energySource?: 'solar' | 'wind' | 'battery' | 'grid';
  community?: {
    id: string;
    name: string;
    memberCount: number;
  };
}

interface EnergyFlow {
  id: string;
  fromNodeId: string;
  toNodeId: string;
  amount: number;
  price: number;
  timestamp: string;
  status: 'active' | 'pending' | 'completed';
}

interface MapFilters {
  nodeTypes: string[];
  energySources: string[];
  communities: string[];
  showFlows: boolean;
  showInactive: boolean;
}

const EnergyMap: React.FC = () => {
  const [nodes, setNodes] = useState<EnergyNode[]>([]);
  const [flows, setFlows] = useState<EnergyFlow[]>([]);
  const [selectedNode, setSelectedNode] = useState<EnergyNode | null>(null);
  const [filters, setFilters] = useState<MapFilters>({
    nodeTypes: ['producer', 'consumer', 'community', 'storage'],
    energySources: ['solar', 'wind', 'battery', 'grid'],
    communities: [],
    showFlows: true,
    showInactive: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMapData();
  }, []);

  const fetchMapData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch communities with location data
      const communitiesResponse = await apiService.getCommunities();

      // Transform community data to energy nodes
      const communityNodes: EnergyNode[] = communitiesResponse.map((community: any) => ({
        id: community.id.toString(),
        name: community.name,
        type: 'community',
        location: {
          lat: community.lat || 40.7128 + (Math.random() - 0.5) * 0.1,
          lng: community.lng || -74.0060 + (Math.random() - 0.5) * 0.1,
          address: community.location || community.address || 'Address not available',
          city: community.city || 'New York',
          state: community.state || 'NY'
        },
        capacity: community.total_energy_capacity || 0,
        currentProduction: community.total_current_energy || 0,
        currentConsumption: community.total_current_energy * 0.8 || 0,
        status: community.is_active ? 'active' : 'inactive',
        community: {
          id: community.id.toString(),
          name: community.name,
          memberCount: community.member_count || 0
        }
      }));

      // Add some mock energy nodes for demonstration
      const mockNodes: EnergyNode[] = [
        {
          id: 'solar-1',
          name: 'Solar Farm Alpha',
          type: 'producer',
          location: {
            lat: 40.7280,
            lng: -74.0020,
            address: '123 Solar Street',
            city: 'New York',
            state: 'NY'
          },
          capacity: 500,
          currentProduction: 350,
          currentConsumption: 0,
          status: 'active',
          energySource: 'solar'
        },
        {
          id: 'wind-1',
          name: 'Wind Farm Beta',
          type: 'producer',
          location: {
            lat: 40.7180,
            lng: -74.0120,
            address: '456 Wind Avenue',
            city: 'New York',
            state: 'NY'
          },
          capacity: 750,
          currentProduction: 480,
          currentConsumption: 0,
          status: 'active',
          energySource: 'wind'
        },
        {
          id: 'battery-1',
          name: 'Battery Storage Center',
          type: 'storage',
          location: {
            lat: 40.7080,
            lng: -74.0080,
            address: '789 Battery Boulevard',
            city: 'New York',
            state: 'NY'
          },
          capacity: 1000,
          currentProduction: 200,
          currentConsumption: 150,
          status: 'active',
          energySource: 'battery'
        }
      ];

      setNodes([...communityNodes, ...mockNodes]);
      
      // Mock energy flows
      const mockFlows: EnergyFlow[] = [
        {
          id: 'flow-1',
          fromNodeId: 'solar-1',
          toNodeId: '1',
          amount: 100,
          price: 0.12,
          timestamp: new Date().toISOString(),
          status: 'active'
        },
        {
          id: 'flow-2',
          fromNodeId: 'wind-1',
          toNodeId: 'battery-1',
          amount: 200,
          price: 0.10,
          timestamp: new Date().toISOString(),
          status: 'active'
        }
      ];

      setFlows(mockFlows);
    } catch (err) {
      console.error('Error fetching map data:', err);
      setError('Failed to load energy map data');
    } finally {
      setLoading(false);
    }
  };

  const getNodeIcon = (node: EnergyNode) => {
    switch (node.type) {
      case 'producer':
        return node.energySource === 'solar' ? '☀️' : node.energySource === 'wind' ? '💨' : '⚡';
      case 'consumer':
        return '🏠';
      case 'community':
        return '🏘️';
      case 'storage':
        return '🔋';
      default:
        return '⚡';
    }
  };

  const getNodeColor = (node: EnergyNode) => {
    if (node.status === 'inactive') return 'bg-gray-400';
    if (node.status === 'maintenance') return 'bg-yellow-500';
    
    switch (node.type) {
      case 'producer':
        return 'bg-green-500';
      case 'consumer':
        return 'bg-blue-500';
      case 'community':
        return 'bg-purple-500';
      case 'storage':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const filteredNodes = nodes.filter(node => {
    if (!filters.nodeTypes.includes(node.type)) return false;
    if (node.energySource && !filters.energySources.includes(node.energySource)) return false;
    if (!filters.showInactive && node.status === 'inactive') return false;
    return true;
  });

  const toggleFilter = (filterType: 'nodeTypes' | 'energySources' | 'communities', value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: prev[filterType].includes(value)
        ? prev[filterType].filter((item: string) => item !== value)
        : [...prev[filterType], value]
    }));
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
          <InformationCircleIcon className="h-5 w-5 text-red-600 mr-2" />
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Map Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MapPinIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Energy Network Map</h2>
              <p className="text-sm text-gray-600">
                Real-time visualization of energy production, consumption, and trading
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Active Nodes:</span>
            <span className="font-semibold text-green-600">{filteredNodes.length}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Map Filters</h3>
          <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-400" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Node Types */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Node Types</h4>
            <div className="space-y-2">
              {['producer', 'consumer', 'community', 'storage'].map(type => (
                <label key={type} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.nodeTypes.includes(type)}
                    onChange={() => toggleFilter('nodeTypes', type)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 capitalize">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Energy Sources */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Energy Sources</h4>
            <div className="space-y-2">
              {['solar', 'wind', 'battery', 'grid'].map(source => (
                <label key={source} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.energySources.includes(source)}
                    onChange={() => toggleFilter('energySources', source)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 capitalize">{source}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Display Options */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Display Options</h4>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.showFlows}
                  onChange={(e) => setFilters(prev => ({ ...prev, showFlows: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Show Energy Flows</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.showInactive}
                  onChange={(e) => setFilters(prev => ({ ...prev, showInactive: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Show Inactive Nodes</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {/* Map Placeholder - In a real implementation, this would be replaced with an actual map component */}
        <div className="relative h-96 bg-gradient-to-br from-blue-50 to-green-50 border-2 border-dashed border-gray-300">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <MapPinIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 text-lg font-medium">Interactive Energy Map</p>
              <p className="text-gray-500 text-sm mt-2">
                Map visualization would be integrated here using libraries like Leaflet or Google Maps
              </p>
            </div>
          </div>
          
          {/* Simulated Map Nodes */}
          <div className="absolute inset-0 p-8">
            {filteredNodes.slice(0, 6).map((node, index) => (
              <motion.div
                key={node.id}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`absolute w-12 h-12 rounded-full ${getNodeColor(node)} 
                  flex items-center justify-center cursor-pointer hover:scale-110 transition-transform`}
                style={{
                  left: `${10 + (index % 3) * 30}%`,
                  top: `${20 + Math.floor(index / 3) * 40}%`
                }}
                onClick={() => setSelectedNode(node)}
              >
                <span className="text-white text-xl">{getNodeIcon(node)}</span>
              </motion.div>
            ))}
            
            {/* Simulated Energy Flows */}
            {filters.showFlows && (
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {flows.map((flow, index) => (
                  <motion.line
                    key={flow.id}
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, delay: index * 0.5 }}
                    x1={`${15 + (index % 3) * 30}%`}
                    y1={`${25 + Math.floor(index / 3) * 40}%`}
                    x2={`${45 + (index % 2) * 30}%`}
                    y2={`${65 - Math.floor(index / 2) * 40}%`}
                    stroke="#3B82F6"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                    className="animate-pulse"
                  />
                ))}
              </svg>
            )}
          </div>
        </div>
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Node Details</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Basic Information</h4>
              <div className="space-y-2">
                <p><span className="font-medium">Name:</span> {selectedNode.name}</p>
                <p><span className="font-medium">Type:</span> {selectedNode.type}</p>
                <p><span className="font-medium">Status:</span> 
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                    selectedNode.status === 'active' ? 'bg-green-100 text-green-800' :
                    selectedNode.status === 'inactive' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {selectedNode.status}
                  </span>
                </p>
                {selectedNode.energySource && (
                  <p><span className="font-medium">Energy Source:</span> {selectedNode.energySource}</p>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Energy Metrics</h4>
              <div className="space-y-2">
                <p><span className="font-medium">Capacity:</span> {selectedNode.capacity} kW</p>
                <p><span className="font-medium">Production:</span> {selectedNode.currentProduction} kW</p>
                <p><span className="font-medium">Consumption:</span> {selectedNode.currentConsumption} kW</p>
                <p><span className="font-medium">Efficiency:</span> 
                  {selectedNode.capacity > 0 ? 
                    Math.round((selectedNode.currentProduction / selectedNode.capacity) * 100) : 0}%
                </p>
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Location</h4>
            <p className="text-sm text-gray-600">
              {selectedNode.location.address}, {selectedNode.location.city}, {selectedNode.location.state}
            </p>
          </div>
          
          {selectedNode.community && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Community</h4>
              <p className="text-sm text-gray-600">
                {selectedNode.community.name} ({selectedNode.community.memberCount} members)
              </p>
            </div>
          )}
        </motion.div>
      )}

      {/* Map Legend */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-700">Energy Producer</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-700">Energy Consumer</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-purple-500 rounded-full"></div>
            <span className="text-sm text-gray-700">Community</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
            <span className="text-sm text-gray-700">Energy Storage</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnergyMap;
