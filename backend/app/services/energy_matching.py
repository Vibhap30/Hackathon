"""
Advanced Energy Matching Algorithm
PowerShare Energy Trading Platform
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
import numpy as np
from geopy.distance import geodesic
import structlog

logger = structlog.get_logger()


class MatchingPriority(Enum):
    COST_OPTIMIZATION = "cost"
    CARBON_MINIMIZATION = "carbon"
    LOCAL_PREFERENCE = "local"
    RELIABILITY = "reliability"
    BALANCED = "balanced"


class EnergySource(Enum):
    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    GEOTHERMAL = "geothermal"
    BATTERY = "battery"
    GRID = "grid"


@dataclass
class EnergyOffer:
    id: str
    seller_id: str
    amount_kwh: float
    price_per_kwh: float
    energy_source: EnergySource
    location: Tuple[float, float]  # (lat, lng)
    availability_start: datetime
    availability_end: datetime
    carbon_intensity: float  # kg CO2/kWh
    reliability_score: float  # 0.0 to 1.0
    quality_metrics: Dict[str, float]
    seller_reputation: float
    renewable_percentage: float


@dataclass
class EnergyRequest:
    id: str
    buyer_id: str
    amount_kwh: float
    max_price_per_kwh: float
    location: Tuple[float, float]
    needed_by: datetime
    priority: MatchingPriority
    preferences: Dict[str, Any]
    urgency_factor: float  # 0.0 to 1.0
    quality_requirements: Dict[str, float]


@dataclass
class MatchResult:
    offer_id: str
    request_id: str
    matched_amount: float
    final_price: float
    matching_score: float
    distance_km: float
    carbon_impact: float
    estimated_delivery_time: timedelta
    reasoning: List[str]
    confidence_score: float


class EnergyMatchingEngine:
    """Advanced algorithm for matching energy supply with demand"""
    
    def __init__(self):
        self.scoring_weights = {
            MatchingPriority.COST_OPTIMIZATION: {
                'price': 0.5, 'distance': 0.2, 'carbon': 0.1, 'reliability': 0.1, 'renewable': 0.1
            },
            MatchingPriority.CARBON_MINIMIZATION: {
                'carbon': 0.4, 'renewable': 0.3, 'price': 0.15, 'distance': 0.1, 'reliability': 0.05
            },
            MatchingPriority.LOCAL_PREFERENCE: {
                'distance': 0.4, 'price': 0.25, 'reliability': 0.15, 'carbon': 0.1, 'renewable': 0.1
            },
            MatchingPriority.RELIABILITY: {
                'reliability': 0.4, 'price': 0.25, 'distance': 0.15, 'carbon': 0.1, 'renewable': 0.1
            },
            MatchingPriority.BALANCED: {
                'price': 0.25, 'distance': 0.2, 'carbon': 0.2, 'reliability': 0.2, 'renewable': 0.15
            }
        }
    
    async def find_optimal_matches(
        self, 
        requests: List[EnergyRequest], 
        offers: List[EnergyOffer]
    ) -> List[MatchResult]:
        """Find optimal matches for energy requests and offers"""
        
        matches = []
        remaining_offers = offers.copy()
        
        # Sort requests by urgency and priority
        sorted_requests = sorted(requests, key=lambda r: (-r.urgency_factor, r.needed_by))
        
        for request in sorted_requests:
            # Find compatible offers for this request
            compatible_offers = await self._filter_compatible_offers(request, remaining_offers)
            
            if not compatible_offers:
                logger.warning(f"No compatible offers found for request {request.id}")
                continue
            
            # Score and rank offers
            scored_offers = await self._score_offers(request, compatible_offers)
            
            # Select best match(es) - may split across multiple offers
            selected_matches = await self._select_optimal_matches(request, scored_offers)
            
            matches.extend(selected_matches)
            
            # Update remaining offers
            remaining_offers = await self._update_remaining_offers(remaining_offers, selected_matches)
        
        return matches
    
    async def _filter_compatible_offers(
        self, 
        request: EnergyRequest, 
        offers: List[EnergyOffer]
    ) -> List[EnergyOffer]:
        """Filter offers that are compatible with the request"""
        
        compatible = []
        
        for offer in offers:
            # Basic compatibility checks
            if offer.amount_kwh <= 0:
                continue
            
            if offer.price_per_kwh > request.max_price_per_kwh:
                continue
            
            if offer.availability_end < request.needed_by:
                continue
            
            # Distance check (within reasonable range)
            distance = geodesic(request.location, offer.location).kilometers
            max_distance = request.preferences.get('max_distance_km', 100)
            if distance > max_distance:
                continue
            
            # Quality requirements check
            if not await self._meets_quality_requirements(offer, request.quality_requirements):
                continue
            
            # Renewable energy preference
            min_renewable = request.preferences.get('min_renewable_percentage', 0)
            if offer.renewable_percentage < min_renewable:
                continue
            
            compatible.append(offer)
        
        return compatible
    
    async def _score_offers(
        self, 
        request: EnergyRequest, 
        offers: List[EnergyOffer]
    ) -> List[Tuple[EnergyOffer, float, Dict[str, float]]]:
        """Score offers based on request priority and preferences"""
        
        scored_offers = []
        weights = self.scoring_weights[request.priority]
        
        for offer in offers:
            scores = {}
            
            # Price score (lower price = higher score)
            price_ratio = offer.price_per_kwh / request.max_price_per_kwh
            scores['price'] = max(0, 1 - price_ratio)
            
            # Distance score (closer = higher score)
            distance = geodesic(request.location, offer.location).kilometers
            max_distance = request.preferences.get('max_distance_km', 100)
            scores['distance'] = max(0, 1 - (distance / max_distance))
            
            # Carbon score (lower carbon = higher score)
            max_carbon = request.preferences.get('max_carbon_intensity', 1.0)
            scores['carbon'] = max(0, 1 - (offer.carbon_intensity / max_carbon))
            
            # Reliability score
            scores['reliability'] = offer.reliability_score
            
            # Renewable energy score
            scores['renewable'] = offer.renewable_percentage
            
            # Calculate weighted total score
            total_score = sum(scores[metric] * weights[metric] for metric in scores)
            
            # Apply urgency factor
            if request.urgency_factor > 0.7:
                # For urgent requests, prioritize availability and reliability
                total_score += (scores['reliability'] * 0.2 + scores['distance'] * 0.1)
            
            scored_offers.append((offer, total_score, scores))
        
        # Sort by score (highest first)
        scored_offers.sort(key=lambda x: x[1], reverse=True)
        
        return scored_offers
    
    async def _select_optimal_matches(
        self, 
        request: EnergyRequest, 
        scored_offers: List[Tuple[EnergyOffer, float, Dict[str, float]]]
    ) -> List[MatchResult]:
        """Select optimal matches, potentially splitting across multiple offers"""
        
        matches = []
        remaining_demand = request.amount_kwh
        
        for offer, score, detailed_scores in scored_offers:
            if remaining_demand <= 0:
                break
            
            # Determine how much to take from this offer
            available_amount = offer.amount_kwh
            matched_amount = min(remaining_demand, available_amount)
            
            # Calculate distance and delivery time
            distance = geodesic(request.location, offer.location).kilometers
            estimated_delivery = timedelta(hours=max(1, distance / 50))  # Assume 50 km/h avg speed
            
            # Dynamic pricing based on urgency and quality
            base_price = offer.price_per_kwh
            urgency_multiplier = 1 + (request.urgency_factor * 0.1)  # Up to 10% premium for urgent
            quality_multiplier = 1 + (score - 0.5) * 0.05  # Up to 2.5% adjustment for quality
            final_price = base_price * urgency_multiplier * quality_multiplier
            
            # Calculate carbon impact
            carbon_impact = matched_amount * offer.carbon_intensity
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(request, offer, detailed_scores, score)
            
            match = MatchResult(
                offer_id=offer.id,
                request_id=request.id,
                matched_amount=matched_amount,
                final_price=final_price,
                matching_score=score,
                distance_km=distance,
                carbon_impact=carbon_impact,
                estimated_delivery_time=estimated_delivery,
                reasoning=reasoning,
                confidence_score=min(0.95, score + 0.2)
            )
            
            matches.append(match)
            remaining_demand -= matched_amount
            
            # For single-offer preference, break after first match
            if request.preferences.get('single_supplier_preference', False):
                break
        
        return matches
    
    async def _meets_quality_requirements(
        self, 
        offer: EnergyOffer, 
        requirements: Dict[str, float]
    ) -> bool:
        """Check if offer meets quality requirements"""
        
        for metric, min_value in requirements.items():
            offer_value = offer.quality_metrics.get(metric, 0)
            if offer_value < min_value:
                return False
        
        return True
    
    async def _update_remaining_offers(
        self, 
        offers: List[EnergyOffer], 
        matches: List[MatchResult]
    ) -> List[EnergyOffer]:
        """Update remaining offers after matches"""
        
        updated_offers = []
        
        for offer in offers:
            remaining_amount = offer.amount_kwh
            
            # Subtract matched amounts
            for match in matches:
                if match.offer_id == offer.id:
                    remaining_amount -= match.matched_amount
            
            if remaining_amount > 0:
                # Create updated offer with remaining amount
                updated_offer = EnergyOffer(
                    id=offer.id,
                    seller_id=offer.seller_id,
                    amount_kwh=remaining_amount,
                    price_per_kwh=offer.price_per_kwh,
                    energy_source=offer.energy_source,
                    location=offer.location,
                    availability_start=offer.availability_start,
                    availability_end=offer.availability_end,
                    carbon_intensity=offer.carbon_intensity,
                    reliability_score=offer.reliability_score,
                    quality_metrics=offer.quality_metrics,
                    seller_reputation=offer.seller_reputation,
                    renewable_percentage=offer.renewable_percentage
                )
                updated_offers.append(updated_offer)
        
        return updated_offers
    
    async def _generate_reasoning(
        self, 
        request: EnergyRequest, 
        offer: EnergyOffer, 
        scores: Dict[str, float], 
        total_score: float
    ) -> List[str]:
        """Generate human-readable reasoning for the match"""
        
        reasoning = []
        
        # Primary matching factors
        if scores['price'] > 0.8:
            reasoning.append(f"Excellent price: ${offer.price_per_kwh:.3f}/kWh vs max ${request.max_price_per_kwh:.3f}/kWh")
        elif scores['price'] > 0.6:
            reasoning.append(f"Good price: ${offer.price_per_kwh:.3f}/kWh within budget")
        
        distance = geodesic(request.location, offer.location).kilometers
        if distance < 10:
            reasoning.append(f"Very local supply: {distance:.1f}km away")
        elif distance < 50:
            reasoning.append(f"Regional supply: {distance:.1f}km away")
        
        if offer.renewable_percentage > 0.9:
            reasoning.append(f"Highly renewable: {offer.renewable_percentage*100:.0f}% clean energy")
        elif offer.renewable_percentage > 0.5:
            reasoning.append(f"Renewable source: {offer.renewable_percentage*100:.0f}% clean energy")
        
        if offer.reliability_score > 0.8:
            reasoning.append(f"High reliability: {offer.reliability_score*100:.0f}% reliability score")
        
        if offer.carbon_intensity < 0.1:
            reasoning.append(f"Ultra-low carbon: {offer.carbon_intensity:.3f} kg CO2/kWh")
        elif offer.carbon_intensity < 0.5:
            reasoning.append(f"Low carbon: {offer.carbon_intensity:.3f} kg CO2/kWh")
        
        # Overall assessment
        if total_score > 0.8:
            reasoning.append("Excellent overall match for your requirements")
        elif total_score > 0.6:
            reasoning.append("Good match balancing your priorities")
        else:
            reasoning.append("Acceptable match given current market conditions")
        
        return reasoning


class LocalityEnergyMapper:
    """Maps energy supply and demand in specific localities"""
    
    def __init__(self):
        pass
    
    async def generate_locality_map(
        self, 
        center_location: Tuple[float, float], 
        radius_km: float = 50
    ) -> Dict[str, Any]:
        """Generate energy map for a specific locality"""
        
        # Mock data for demonstration - integrate with real IoT and grid data
        energy_nodes = [
            {
                "id": "solar_farm_001",
                "type": "producer",
                "source": "solar",
                "location": (center_location[0] + 0.01, center_location[1] + 0.01),
                "capacity_kw": 500,
                "current_output": 380,
                "status": "active",
                "efficiency": 0.76
            },
            {
                "id": "residential_001",
                "type": "prosumer",
                "location": (center_location[0] - 0.005, center_location[1] + 0.008),
                "production": 8.5,
                "consumption": 12.3,
                "net_demand": 3.8,
                "status": "consuming"
            },
            {
                "id": "commercial_001",
                "type": "consumer",
                "location": (center_location[0] + 0.008, center_location[1] - 0.005),
                "demand": 45.2,
                "peak_demand": 67.8,
                "status": "high_demand"
            },
            {
                "id": "wind_turbine_001",
                "type": "producer",
                "source": "wind",
                "location": (center_location[0] - 0.02, center_location[1] + 0.015),
                "capacity_kw": 300,
                "current_output": 189,
                "status": "active",
                "efficiency": 0.63
            }
        ]
        
        # Calculate energy flows
        energy_flows = await self._calculate_energy_flows(energy_nodes)
        
        # Generate grid stability metrics
        grid_metrics = await self._calculate_grid_metrics(energy_nodes, energy_flows)
        
        return {
            "center": center_location,
            "radius_km": radius_km,
            "energy_nodes": energy_nodes,
            "energy_flows": energy_flows,
            "grid_metrics": grid_metrics,
            "recommendations": await self._generate_locality_recommendations(energy_nodes, grid_metrics),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _calculate_energy_flows(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate energy flows between nodes"""
        
        flows = []
        producers = [n for n in nodes if n.get('type') == 'producer']
        consumers = [n for n in nodes if n.get('type') in ['consumer', 'prosumer'] and n.get('net_demand', 0) > 0]
        
        for producer in producers:
            available_energy = producer.get('current_output', 0)
            
            for consumer in consumers:
                if available_energy <= 0:
                    break
                
                demand = consumer.get('net_demand', consumer.get('demand', 0))
                flow_amount = min(available_energy, demand)
                
                if flow_amount > 0:
                    distance = geodesic(producer['location'], consumer['location']).kilometers
                    
                    flows.append({
                        "from": producer['id'],
                        "to": consumer['id'],
                        "amount_kw": flow_amount,
                        "distance_km": distance,
                        "efficiency": max(0.85, 1 - (distance * 0.001)),  # transmission losses
                        "source_type": producer.get('source', 'grid')
                    })
                    
                    available_energy -= flow_amount
                    consumer['net_demand'] = demand - flow_amount
        
        return flows
    
    async def _calculate_grid_metrics(
        self, 
        nodes: List[Dict[str, Any]], 
        flows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate grid stability and efficiency metrics"""
        
        total_production = sum(n.get('current_output', 0) for n in nodes if n.get('type') == 'producer')
        total_demand = sum(n.get('demand', n.get('net_demand', 0)) for n in nodes if n.get('type') in ['consumer', 'prosumer'])
        
        supply_demand_ratio = total_production / total_demand if total_demand > 0 else 1.0
        grid_stability = min(1.0, supply_demand_ratio) * 0.9 + 0.1  # Base stability
        
        renewable_production = sum(
            n.get('current_output', 0) for n in nodes 
            if n.get('type') == 'producer' and n.get('source') in ['solar', 'wind', 'hydro']
        )
        renewable_percentage = renewable_production / total_production if total_production > 0 else 0
        
        avg_transmission_efficiency = np.mean([f['efficiency'] for f in flows]) if flows else 0.95
        
        return {
            "total_production_kw": total_production,
            "total_demand_kw": total_demand,
            "supply_demand_ratio": supply_demand_ratio,
            "grid_stability_score": grid_stability,
            "renewable_percentage": renewable_percentage,
            "transmission_efficiency": avg_transmission_efficiency,
            "active_flows": len(flows),
            "carbon_intensity": 0.2 * (1 - renewable_percentage) + 0.05 * renewable_percentage
        }
    
    async def _generate_locality_recommendations(
        self, 
        nodes: List[Dict[str, Any]], 
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for the locality"""
        
        recommendations = []
        
        if metrics['supply_demand_ratio'] < 0.9:
            recommendations.append("Consider adding more renewable generation capacity")
        elif metrics['supply_demand_ratio'] > 1.2:
            recommendations.append("Excess generation available - consider energy storage or exports")
        
        if metrics['renewable_percentage'] < 0.5:
            recommendations.append("Increase renewable energy sources to improve sustainability")
        
        if metrics['transmission_efficiency'] < 0.9:
            recommendations.append("Optimize energy flows to reduce transmission losses")
        
        if metrics['grid_stability_score'] < 0.8:
            recommendations.append("Improve grid stability through demand response programs")
        
        # Identify optimization opportunities
        high_demand_nodes = [n for n in nodes if n.get('demand', 0) > 40]
        if high_demand_nodes:
            recommendations.append("High-demand consumers identified - consider on-site generation")
        
        return recommendations
