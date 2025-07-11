"""
Geospatial and Local Map Integration for PowerShare Platform
==========================================================

This module implements interactive local map features including:
- Real-time prosumer/consumer location display
- Privacy-preserving location handling
- Radius-based energy trading matching
- Interactive details on hover/click
- Route optimization for energy delivery
- Geospatial analytics and clustering
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geography, Geometry
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_AsGeoJSON, ST_GeomFromText
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import uuid
import json
import math
import asyncio
from decimal import Decimal

Base = declarative_base()

class LocationPrivacyLevel(Enum):
    EXACT = "exact"              # Exact coordinates
    APPROXIMATE = "approximate"  # Fuzzy location within 1km
    HIDDEN = "hidden"           # Location completely hidden
    COMMUNITY_ONLY = "community_only"  # Visible only to community members

class EnergyNodeType(Enum):
    PROSUMER = "prosumer"
    CONSUMER = "consumer"
    STORAGE = "storage"
    GRID_CONNECTION = "grid_connection"
    CHARGING_STATION = "charging_station"

class DeliveryMethod(Enum):
    GRID_INJECTION = "grid_injection"
    DIRECT_LINE = "direct_line"
    BATTERY_SWAP = "battery_swap"
    VIRTUAL_TRADING = "virtual_trading"

# Database Models

class UserLocation(Base):
    __tablename__ = "user_locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    exact_location = Column(Geography('POINT', srid=4326))  # Private exact location
    public_location = Column(Geography('POINT', srid=4326))  # Public/fuzzy location
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    privacy_level = Column(String(20), default=LocationPrivacyLevel.APPROXIMATE.value)
    location_accuracy = Column(Float)  # Accuracy in meters
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="location")
    
    __table_args__ = (
        Index('idx_user_location_geom', 'public_location', postgresql_using='gist'),
        Index('idx_user_location_city', 'city'),
    )

class EnergyNode(Base):
    __tablename__ = "energy_nodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    node_type = Column(String(50), nullable=False)  # EnergyNodeType enum
    name = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(Geography('POINT', srid=4326), nullable=False)
    capacity_kw = Column(Float, default=0.0)
    current_output_kw = Column(Float, default=0.0)
    energy_source = Column(String(50))  # solar, wind, hydro, etc.
    renewable_percentage = Column(Float, default=0.0)
    efficiency_rating = Column(Float, default=0.8)
    installation_date = Column(DateTime)
    last_maintenance = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    availability_zones = relationship("NodeAvailabilityZone", back_populates="node")
    
    __table_args__ = (
        Index('idx_energy_node_location', 'location', postgresql_using='gist'),
        Index('idx_energy_node_type', 'node_type'),
        Index('idx_energy_node_active', 'is_active'),
    )

class NodeAvailabilityZone(Base):
    __tablename__ = "node_availability_zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("energy_nodes.id"), nullable=False)
    zone_name = Column(String(255))
    zone_polygon = Column(Geography('POLYGON', srid=4326))  # Service area polygon
    max_distance_km = Column(Float, default=10.0)
    delivery_methods = Column(JSONB)  # List of supported delivery methods
    pricing_multiplier = Column(Float, default=1.0)  # Distance-based pricing
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    node = relationship("EnergyNode", back_populates="availability_zones")
    
    __table_args__ = (
        Index('idx_availability_zone_geom', 'zone_polygon', postgresql_using='gist'),
    )

class EnergyRoute(Base):
    __tablename__ = "energy_routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("energy_nodes.id"), nullable=False)
    destination_location = Column(Geography('POINT', srid=4326), nullable=False)
    route_geometry = Column(Geography('LINESTRING', srid=4326))
    distance_km = Column(Float, nullable=False)
    estimated_loss_percentage = Column(Float, default=0.02)  # Transmission losses
    delivery_method = Column(String(50), nullable=False)
    estimated_delivery_time = Column(Integer)  # Minutes
    infrastructure_cost = Column(Float, default=0.0)
    is_feasible = Column(Boolean, default=True)
    route_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source_node = relationship("EnergyNode")
    
    __table_args__ = (
        Index('idx_energy_route_geom', 'route_geometry', postgresql_using='gist'),
        Index('idx_energy_route_distance', 'distance_km'),
    )

class GeospatialCache(Base):
    __tablename__ = "geospatial_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(255), unique=True, nullable=False)
    cache_type = Column(String(50), nullable=False)  # 'proximity', 'route', 'cluster'
    location_hash = Column(String(100))  # Hash of location for quick lookup
    radius_km = Column(Float)
    result_data = Column(JSONB, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_geospatial_cache_key', 'cache_key'),
        Index('idx_geospatial_cache_expires', 'expires_at'),
    )

# Service Classes

@dataclass
class LocationInfo:
    latitude: float
    longitude: float
    address: str
    city: str
    privacy_level: LocationPrivacyLevel
    accuracy: float

@dataclass
class NearbyNode:
    node_id: str
    user_id: int
    node_type: EnergyNodeType
    name: str
    distance_km: float
    capacity_kw: float
    current_output_kw: float
    energy_source: str
    renewable_percentage: float
    location: Tuple[float, float]
    pricing_per_kwh: float
    availability_status: str
    estimated_delivery_time: int

@dataclass
class RouteInfo:
    distance_km: float
    estimated_time_minutes: int
    transmission_loss_percentage: float
    delivery_method: DeliveryMethod
    infrastructure_required: bool
    estimated_cost: float
    route_coordinates: List[Tuple[float, float]]

class GeospatialService:
    """Service for geospatial operations and location management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def update_user_location(self, user_id: int, latitude: float, longitude: float,
                                  address: str = None, privacy_level: LocationPrivacyLevel = LocationPrivacyLevel.APPROXIMATE) -> bool:
        """Update user's location with privacy protection"""
        try:
            exact_point = f'POINT({longitude} {latitude})'
            
            # Create fuzzy location based on privacy level
            fuzzy_point = await self._create_fuzzy_location(latitude, longitude, privacy_level)
            
            location = self.db.query(UserLocation).filter(UserLocation.user_id == user_id).first()
            
            if not location:
                location = UserLocation(user_id=user_id)
                self.db.add(location)
            
            location.exact_location = exact_point
            location.public_location = fuzzy_point
            location.address = address
            location.privacy_level = privacy_level.value
            location.last_updated = datetime.utcnow()
            
            # Geocoding for address components (simplified)
            if address:
                address_parts = address.split(',')
                if len(address_parts) >= 2:
                    location.city = address_parts[-2].strip()
                    location.country = address_parts[-1].strip()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error updating user location: {e}")
            return False
    
    async def find_nearby_nodes(self, user_id: int, radius_km: float = 10.0, 
                               node_types: List[EnergyNodeType] = None) -> List[NearbyNode]:
        """Find nearby energy nodes within specified radius"""
        try:
            # Get user's location
            user_location = self.db.query(UserLocation).filter(UserLocation.user_id == user_id).first()
            if not user_location or not user_location.public_location:
                return []
            
            # Check cache first
            cache_key = f"nearby_nodes_{user_id}_{radius_km}_{hash(tuple(node_types) if node_types else ())}"
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                return [NearbyNode(**node) for node in cached_result]
            
            # Build query for nearby nodes
            query = self.db.query(EnergyNode).filter(
                EnergyNode.is_active == True,
                EnergyNode.is_public == True,
                ST_DWithin(EnergyNode.location, user_location.public_location, radius_km * 1000)  # Convert to meters
            )
            
            if node_types:
                query = query.filter(EnergyNode.node_type.in_([nt.value for nt in node_types]))
            
            # Order by distance
            query = query.order_by(ST_Distance(EnergyNode.location, user_location.public_location))
            
            nodes = query.limit(50).all()  # Limit to 50 nearest nodes
            
            nearby_nodes = []
            for node in nodes:
                distance = await self._calculate_distance(user_location.public_location, node.location)
                
                # Get current pricing (simplified)
                pricing = await self._get_node_pricing(node.id)
                
                nearby_node = NearbyNode(
                    node_id=str(node.id),
                    user_id=node.user_id,
                    node_type=EnergyNodeType(node.node_type),
                    name=node.name,
                    distance_km=distance,
                    capacity_kw=node.capacity_kw,
                    current_output_kw=node.current_output_kw,
                    energy_source=node.energy_source or "unknown",
                    renewable_percentage=node.renewable_percentage,
                    location=await self._extract_coordinates(node.location),
                    pricing_per_kwh=pricing,
                    availability_status="available" if node.current_output_kw > 0 else "limited",
                    estimated_delivery_time=await self._estimate_delivery_time(distance, node.node_type)
                )
                nearby_nodes.append(nearby_node)
            
            # Cache the result
            await self._cache_result(cache_key, [asdict(node) for node in nearby_nodes], 
                                   expires_in_minutes=15)
            
            return nearby_nodes
            
        except Exception as e:
            print(f"Error finding nearby nodes: {e}")
            return []
    
    async def calculate_optimal_route(self, source_node_id: str, destination_user_id: int,
                                    delivery_method: DeliveryMethod = DeliveryMethod.GRID_INJECTION) -> RouteInfo:
        """Calculate optimal route between energy source and destination"""
        try:
            # Get source node
            source_node = self.db.query(EnergyNode).filter(EnergyNode.id == source_node_id).first()
            if not source_node:
                return None
            
            # Get destination location
            dest_location = self.db.query(UserLocation).filter(UserLocation.user_id == destination_user_id).first()
            if not dest_location:
                return None
            
            # Check for existing route in cache
            cache_key = f"route_{source_node_id}_{destination_user_id}_{delivery_method.value}"
            cached_route = await self._get_cached_result(cache_key)
            if cached_route:
                return RouteInfo(**cached_route)
            
            # Calculate direct distance
            distance_km = await self._calculate_distance(source_node.location, dest_location.public_location)
            
            # Generate route based on delivery method
            route_info = await self._generate_route_info(source_node, dest_location, delivery_method, distance_km)
            
            # Cache the result
            await self._cache_result(cache_key, asdict(route_info), expires_in_minutes=60)
            
            # Store in database for future reference
            await self._store_route_in_db(source_node.id, dest_location.public_location, route_info, delivery_method)
            
            return route_info
            
        except Exception as e:
            print(f"Error calculating optimal route: {e}")
            return None
    
    async def get_energy_clusters(self, center_lat: float, center_lon: float, 
                                radius_km: float = 20.0) -> Dict[str, Any]:
        """Get clustered energy nodes for map visualization"""
        try:
            center_point = f'POINT({center_lon} {center_lat})'
            
            # Get nodes within radius
            nodes = self.db.query(EnergyNode).filter(
                EnergyNode.is_active == True,
                EnergyNode.is_public == True,
                ST_DWithin(EnergyNode.location, center_point, radius_km * 1000)
            ).all()
            
            # Create clusters based on proximity and type
            clusters = await self._create_node_clusters(nodes)
            
            return {
                "clusters": clusters,
                "total_nodes": len(nodes),
                "total_capacity_kw": sum(node.capacity_kw for node in nodes),
                "renewable_percentage": self._calculate_renewable_percentage(nodes),
                "energy_sources": self._get_energy_source_distribution(nodes)
            }
            
        except Exception as e:
            print(f"Error getting energy clusters: {e}")
            return {}
    
    async def register_energy_node(self, user_id: int, node_data: Dict[str, Any]) -> str:
        """Register a new energy node with location"""
        try:
            node_id = uuid.uuid4()
            location_point = f'POINT({node_data["longitude"]} {node_data["latitude"]})'
            
            node = EnergyNode(
                id=node_id,
                user_id=user_id,
                node_type=node_data['node_type'],
                name=node_data['name'],
                description=node_data.get('description'),
                location=location_point,
                capacity_kw=node_data['capacity_kw'],
                energy_source=node_data['energy_source'],
                renewable_percentage=node_data.get('renewable_percentage', 0.0),
                efficiency_rating=node_data.get('efficiency_rating', 0.8),
                installation_date=node_data.get('installation_date'),
                metadata=node_data.get('metadata', {})
            )
            
            self.db.add(node)
            
            # Create availability zone if specified
            if 'availability_radius' in node_data:
                await self._create_availability_zone(node_id, node_data)
            
            self.db.commit()
            return str(node_id)
            
        except Exception as e:
            self.db.rollback()
            print(f"Error registering energy node: {e}")
            return None
    
    async def _create_fuzzy_location(self, lat: float, lon: float, 
                                   privacy_level: LocationPrivacyLevel) -> str:
        """Create fuzzy location based on privacy level"""
        if privacy_level == LocationPrivacyLevel.EXACT:
            return f'POINT({lon} {lat})'
        elif privacy_level == LocationPrivacyLevel.APPROXIMATE:
            # Add random offset within 1km
            import random
            offset_km = random.uniform(0.2, 1.0)
            angle = random.uniform(0, 2 * math.pi)
            
            # Convert km to degrees (approximate)
            lat_offset = (offset_km / 111.0) * math.cos(angle)
            lon_offset = (offset_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(angle)
            
            fuzzy_lat = lat + lat_offset
            fuzzy_lon = lon + lon_offset
            
            return f'POINT({fuzzy_lon} {fuzzy_lat})'
        else:
            # For HIDDEN and COMMUNITY_ONLY, return city center or null island
            return f'POINT(0 0)'
    
    async def _calculate_distance(self, location1, location2) -> float:
        """Calculate distance between two geographic points in km"""
        # Use PostGIS for accurate distance calculation
        result = self.db.execute(
            f"SELECT ST_Distance({location1}::geography, {location2}::geography) / 1000.0 as distance"
        ).fetchone()
        return result[0] if result else 0.0
    
    async def _extract_coordinates(self, location) -> Tuple[float, float]:
        """Extract latitude and longitude from PostGIS point"""
        result = self.db.execute(
            f"SELECT ST_Y({location}) as lat, ST_X({location}) as lon"
        ).fetchone()
        return (result[0], result[1]) if result else (0.0, 0.0)
    
    async def _get_node_pricing(self, node_id: str) -> float:
        """Get current pricing for an energy node"""
        # This would integrate with pricing service
        # For now, return a default rate
        return 0.25  # ₹0.25 per kWh
    
    async def _estimate_delivery_time(self, distance_km: float, node_type: str) -> int:
        """Estimate delivery time based on distance and node type"""
        if node_type == EnergyNodeType.GRID_CONNECTION.value:
            return 5  # Instant grid delivery
        elif distance_km <= 1.0:
            return 15  # 15 minutes for local delivery
        elif distance_km <= 5.0:
            return 30  # 30 minutes for nearby delivery
        else:
            return int(distance_km * 10)  # 10 minutes per km for longer distances
    
    async def _generate_route_info(self, source_node, dest_location, 
                                 delivery_method: DeliveryMethod, distance_km: float) -> RouteInfo:
        """Generate route information based on delivery method"""
        
        if delivery_method == DeliveryMethod.GRID_INJECTION:
            return RouteInfo(
                distance_km=distance_km,
                estimated_time_minutes=5,  # Instant grid injection
                transmission_loss_percentage=0.05,  # 5% grid losses
                delivery_method=delivery_method,
                infrastructure_required=False,
                estimated_cost=distance_km * 0.01,  # Grid usage cost
                route_coordinates=[]  # No physical route for grid injection
            )
        elif delivery_method == DeliveryMethod.DIRECT_LINE:
            return RouteInfo(
                distance_km=distance_km,
                estimated_time_minutes=int(distance_km * 10),
                transmission_loss_percentage=distance_km * 0.02,  # 2% per km
                delivery_method=delivery_method,
                infrastructure_required=distance_km > 1.0,
                estimated_cost=distance_km * 50.0,  # Infrastructure cost
                route_coordinates=await self._generate_direct_line_coordinates(source_node, dest_location)
            )
        else:
            # Default case
            return RouteInfo(
                distance_km=distance_km,
                estimated_time_minutes=30,
                transmission_loss_percentage=0.02,
                delivery_method=delivery_method,
                infrastructure_required=False,
                estimated_cost=distance_km * 0.05,
                route_coordinates=[]
            )
    
    async def _generate_direct_line_coordinates(self, source_node, dest_location) -> List[Tuple[float, float]]:
        """Generate coordinates for direct line route"""
        source_coords = await self._extract_coordinates(source_node.location)
        dest_coords = await self._extract_coordinates(dest_location.public_location)
        
        # Simple straight line - in production, this would use routing services
        return [source_coords, dest_coords]
    
    async def _create_node_clusters(self, nodes: List[EnergyNode]) -> List[Dict[str, Any]]:
        """Create clusters of nearby nodes for map visualization"""
        clusters = []
        cluster_radius_km = 2.0  # 2km cluster radius
        
        unclustered_nodes = list(nodes)
        
        while unclustered_nodes:
            # Start new cluster with first unclustered node
            cluster_center = unclustered_nodes.pop(0)
            cluster_nodes = [cluster_center]
            
            # Find nodes within cluster radius
            remaining_nodes = []
            for node in unclustered_nodes:
                distance = await self._calculate_distance(cluster_center.location, node.location)
                if distance <= cluster_radius_km:
                    cluster_nodes.append(node)
                else:
                    remaining_nodes.append(node)
            
            unclustered_nodes = remaining_nodes
            
            # Create cluster info
            center_coords = await self._extract_coordinates(cluster_center.location)
            total_capacity = sum(node.capacity_kw for node in cluster_nodes)
            avg_renewable = sum(node.renewable_percentage for node in cluster_nodes) / len(cluster_nodes)
            
            clusters.append({
                "id": f"cluster_{len(clusters)}",
                "center": {"lat": center_coords[0], "lng": center_coords[1]},
                "node_count": len(cluster_nodes),
                "total_capacity_kw": total_capacity,
                "average_renewable_percentage": avg_renewable,
                "energy_sources": list(set(node.energy_source for node in cluster_nodes if node.energy_source)),
                "nodes": [
                    {
                        "id": str(node.id),
                        "name": node.name,
                        "type": node.node_type,
                        "capacity_kw": node.capacity_kw,
                        "current_output_kw": node.current_output_kw,
                        "location": await self._extract_coordinates(node.location)
                    }
                    for node in cluster_nodes
                ]
            })
        
        return clusters
    
    def _calculate_renewable_percentage(self, nodes: List[EnergyNode]) -> float:
        """Calculate average renewable percentage for a list of nodes"""
        if not nodes:
            return 0.0
        return sum(node.renewable_percentage for node in nodes) / len(nodes)
    
    def _get_energy_source_distribution(self, nodes: List[EnergyNode]) -> Dict[str, int]:
        """Get distribution of energy sources"""
        distribution = {}
        for node in nodes:
            source = node.energy_source or "unknown"
            distribution[source] = distribution.get(source, 0) + 1
        return distribution
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get result from geospatial cache"""
        try:
            cache_entry = self.db.query(GeospatialCache).filter(
                GeospatialCache.cache_key == cache_key,
                GeospatialCache.expires_at > datetime.utcnow()
            ).first()
            
            return cache_entry.result_data if cache_entry else None
            
        except Exception as e:
            print(f"Error getting cached result: {e}")
            return None
    
    async def _cache_result(self, cache_key: str, result_data: Any, expires_in_minutes: int = 30):
        """Cache result in geospatial cache"""
        try:
            expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            
            # Remove existing cache entry
            self.db.query(GeospatialCache).filter(GeospatialCache.cache_key == cache_key).delete()
            
            cache_entry = GeospatialCache(
                cache_key=cache_key,
                cache_type="proximity",
                result_data=result_data,
                expires_at=expires_at
            )
            
            self.db.add(cache_entry)
            self.db.commit()
            
        except Exception as e:
            print(f"Error caching result: {e}")
    
    async def _store_route_in_db(self, source_node_id: str, destination_location, 
                               route_info: RouteInfo, delivery_method: DeliveryMethod):
        """Store calculated route in database for future reference"""
        try:
            route = EnergyRoute(
                source_node_id=source_node_id,
                destination_location=destination_location,
                route_geometry=None,  # Would store actual route geometry
                distance_km=route_info.distance_km,
                estimated_loss_percentage=route_info.transmission_loss_percentage,
                delivery_method=delivery_method.value,
                estimated_delivery_time=route_info.estimated_time_minutes,
                infrastructure_cost=route_info.estimated_cost,
                route_metadata={
                    "infrastructure_required": route_info.infrastructure_required,
                    "route_coordinates": route_info.route_coordinates
                }
            )
            
            self.db.add(route)
            self.db.commit()
            
        except Exception as e:
            print(f"Error storing route: {e}")
    
    async def _create_availability_zone(self, node_id: str, node_data: Dict[str, Any]):
        """Create availability zone for an energy node"""
        try:
            radius_km = node_data.get('availability_radius', 10.0)
            
            # Create circular polygon around node location
            # This is simplified - in production, would create proper polygon
            zone = NodeAvailabilityZone(
                node_id=node_id,
                zone_name=f"Service Area - {node_data['name']}",
                max_distance_km=radius_km,
                delivery_methods=node_data.get('delivery_methods', [DeliveryMethod.GRID_INJECTION.value]),
                pricing_multiplier=1.0
            )
            
            self.db.add(zone)
            
        except Exception as e:
            print(f"Error creating availability zone: {e}")

# Export classes and functions
__all__ = [
    'LocationPrivacyLevel', 'EnergyNodeType', 'DeliveryMethod',
    'UserLocation', 'EnergyNode', 'NodeAvailabilityZone', 'EnergyRoute', 'GeospatialCache',
    'LocationInfo', 'NearbyNode', 'RouteInfo', 'GeospatialService'
]
