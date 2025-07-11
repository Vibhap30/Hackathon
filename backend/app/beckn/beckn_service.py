"""
Beckn Protocol Integration for PowerShare Platform
=================================================

This module implements the Beckn Protocol for standardized energy trading
following the Unified Energy Interface (UEI) specifications.

Beckn Protocol enables:
- Standardized discovery across energy platforms
- Decentralized marketplace communication
- Interoperable energy transactions
- Federated network participation
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
import asyncio
import aiohttp
from fastapi import HTTPException, status
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class BecknMessageType(Enum):
    SEARCH = "search"
    SELECT = "select"
    INIT = "init"
    CONFIRM = "confirm"
    STATUS = "status"
    TRACK = "track"
    CANCEL = "cancel"
    UPDATE = "update"
    RATING = "rating"

class BecknAction(Enum):
    SEARCH = "search"
    ON_SEARCH = "on_search"
    SELECT = "select"
    ON_SELECT = "on_select"
    INIT = "init"
    ON_INIT = "on_init"
    CONFIRM = "confirm"
    ON_CONFIRM = "on_confirm"
    STATUS = "status"
    ON_STATUS = "on_status"
    TRACK = "track"
    ON_TRACK = "on_track"
    CANCEL = "cancel"
    ON_CANCEL = "on_cancel"
    UPDATE = "update"
    ON_UPDATE = "on_update"
    RATING = "rating"
    ON_RATING = "on_rating"

class EnergyFulfillmentType(Enum):
    PHYSICAL_DELIVERY = "physical_delivery"
    GRID_INJECTION = "grid_injection"
    VIRTUAL_TRADING = "virtual_trading"
    PEER_TO_PEER = "peer_to_peer"

class PaymentMethod(Enum):
    CRYPTOCURRENCY = "cryptocurrency"
    FIAT = "fiat"
    CARBON_CREDITS = "carbon_credits"
    ENERGY_CREDITS = "energy_credits"
    BARTER = "barter"

# Beckn Core Models
@dataclass
class BecknContext:
    """Beckn protocol context"""
    domain: str = "energy"
    country: str = "IND"
    city: str = "Delhi"
    action: str = ""
    core_version: str = "1.1.0"
    bap_id: str = ""
    bap_uri: str = ""
    bpp_id: str = ""
    bpp_uri: str = ""
    transaction_id: str = ""
    message_id: str = ""
    timestamp: str = ""
    key: str = ""
    ttl: str = "PT30S"

@dataclass
class BecknAgent:
    """Beckn network participant (BAP/BPP)"""
    id: str
    name: str
    uri: str
    type: str  # "BAP" or "BPP"
    
@dataclass
class EnergyIntent:
    """Energy search intent"""
    energy_type: Optional[str] = None  # solar, wind, hydro, grid
    capacity_range: Optional[Dict[str, float]] = None  # min_kw, max_kw
    location: Optional[Dict[str, Any]] = None  # coordinates, radius
    time_range: Optional[Dict[str, str]] = None  # start_time, end_time
    price_range: Optional[Dict[str, float]] = None  # min_price, max_price
    renewable_percentage: Optional[float] = None
    delivery_preferences: Optional[List[str]] = None
    quality_requirements: Optional[Dict[str, Any]] = None

@dataclass
class EnergyItem:
    """Energy product/service item"""
    id: str
    parent_item_id: Optional[str] = None
    descriptor: Dict[str, Any] = None
    price: Dict[str, Any] = None
    category_id: str = ""
    location_id: str = ""
    time: Dict[str, Any] = None
    matched: bool = True
    related: bool = True
    recommended: bool = False
    tags: List[Dict[str, Any]] = None

@dataclass
class EnergyProvider:
    """Energy provider (prosumer/utility)"""
    id: str
    descriptor: Dict[str, Any]
    category_id: str
    rating: Optional[float] = None
    time: Optional[Dict[str, Any]] = None
    locations: Optional[List[Dict[str, Any]]] = None
    items: Optional[List[EnergyItem]] = None
    fulfillments: Optional[List[Dict[str, Any]]] = None
    payments: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[Dict[str, Any]]] = None

@dataclass
class BecknCatalog:
    """Beckn catalog of energy offerings"""
    bpp_descriptor: Dict[str, Any]
    bpp_providers: List[EnergyProvider]

@dataclass
class BecknMessage:
    """Generic Beckn message structure"""
    intent: Optional[Dict[str, Any]] = None
    catalog: Optional[BecknCatalog] = None
    order: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

@dataclass
class BecknRequest:
    """Complete Beckn request"""
    context: BecknContext
    message: BecknMessage

@dataclass
class BecknResponse:
    """Complete Beckn response"""
    context: BecknContext
    message: BecknMessage
    error: Optional[Dict[str, Any]] = None

class BecknEnergyCategory:
    """Energy categories for Beckn protocol"""
    
    RENEWABLE_ENERGY = "renewable_energy"
    SOLAR_ENERGY = "solar_energy"
    WIND_ENERGY = "wind_energy"
    HYDRO_ENERGY = "hydro_energy"
    GRID_ENERGY = "grid_energy"
    BATTERY_STORAGE = "battery_storage"
    ENERGY_TRADING = "energy_trading"
    CARBON_CREDITS = "carbon_credits"

class BecknGateway:
    """Beckn Gateway for network communication"""
    
    def __init__(self, gateway_url: str, registry_url: str):
        self.gateway_url = gateway_url
        self.registry_url = registry_url
        self.session = None
    
    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def broadcast_to_network(self, request: BecknRequest) -> List[BecknResponse]:
        """Broadcast request to Beckn network participants"""
        try:
            # Get network participants from registry
            participants = await self._get_network_participants(request.context.domain)
            
            responses = []
            tasks = []
            
            for participant in participants:
                if participant['type'] == 'BPP':  # Only send to providers
                    task = self._send_to_participant(participant, request)
                    tasks.append(task)
            
            # Execute all requests concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, BecknResponse):
                        responses.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Error in network broadcast: {result}")
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to broadcast to network: {e}")
            raise HTTPException(status_code=500, detail="Network broadcast failed")
    
    async def _get_network_participants(self, domain: str) -> List[Dict[str, Any]]:
        """Get registered network participants for domain"""
        try:
            async with self.session.get(
                f"{self.registry_url}/participants",
                params={"domain": domain}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("participants", [])
                else:
                    logger.warning(f"Failed to get participants: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting participants: {e}")
            return []
    
    async def _send_to_participant(self, participant: Dict[str, Any], 
                                 request: BecknRequest) -> Optional[BecknResponse]:
        """Send request to specific network participant"""
        try:
            endpoint = f"{participant['uri']}/{request.context.action}"
            
            async with self.session.post(
                endpoint,
                json=asdict(request),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return BecknResponse(**data)
                else:
                    logger.warning(f"Participant {participant['id']} returned {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending to participant {participant['id']}: {e}")
            return None

class BecknEnergyAdapter:
    """Adapter to convert PowerShare data to Beckn format"""
    
    @staticmethod
    def create_energy_intent(search_params: Dict[str, Any]) -> EnergyIntent:
        """Create energy intent from search parameters"""
        return EnergyIntent(
            energy_type=search_params.get("energy_type"),
            capacity_range={
                "min_kw": search_params.get("min_capacity", 0),
                "max_kw": search_params.get("max_capacity", 1000)
            },
            location={
                "lat": search_params.get("lat"),
                "lng": search_params.get("lng"),
                "radius": search_params.get("radius", 50)
            },
            time_range={
                "start_time": search_params.get("start_time", datetime.utcnow().isoformat()),
                "end_time": search_params.get("end_time", (datetime.utcnow() + timedelta(hours=24)).isoformat())
            },
            price_range={
                "min_price": search_params.get("min_price", 0),
                "max_price": search_params.get("max_price", 20)
            },
            renewable_percentage=search_params.get("min_renewable", 0),
            delivery_preferences=search_params.get("delivery_types", ["grid_injection"]),
            quality_requirements=search_params.get("quality_reqs", {})
        )
    
    @staticmethod
    def convert_energy_node_to_provider(node: Dict[str, Any]) -> EnergyProvider:
        """Convert PowerShare energy node to Beckn provider"""
        
        # Create energy item
        energy_item = EnergyItem(
            id=f"energy_{node['id']}",
            descriptor={
                "name": f"{node['energy_source'].title()} Energy",
                "code": node['energy_source'],
                "symbol": "⚡",
                "short_desc": f"Clean {node['energy_source']} energy from {node['name']}",
                "long_desc": f"High-quality {node['energy_source']} energy with {node['renewable_percentage']}% renewable content",
                "images": [{"url": f"/images/{node['energy_source']}.jpg"}]
            },
            price={
                "currency": "INR",
                "value": str(node['pricing_per_kwh']),
                "estimated_value": str(node['pricing_per_kwh']),
                "computed_value": str(node['pricing_per_kwh']),
                "listed_value": str(node['pricing_per_kwh']),
                "offered_value": str(node['pricing_per_kwh'])
            },
            category_id=BecknEnergyCategory.RENEWABLE_ENERGY if node['renewable_percentage'] > 80 else BecknEnergyCategory.GRID_ENERGY,
            location_id=f"loc_{node['id']}",
            time={
                "label": "Available",
                "timestamp": datetime.utcnow().isoformat(),
                "duration": "PT24H",
                "range": {
                    "start": datetime.utcnow().isoformat(),
                    "end": (datetime.utcnow() + timedelta(days=1)).isoformat()
                },
                "days": "1,2,3,4,5,6,7"
            },
            tags=[
                {
                    "name": "energy_source",
                    "value": node['energy_source']
                },
                {
                    "name": "renewable_percentage",
                    "value": str(node['renewable_percentage'])
                },
                {
                    "name": "capacity_kw",
                    "value": str(node['capacity_kw'])
                },
                {
                    "name": "current_output_kw",
                    "value": str(node['current_output_kw'])
                },
                {
                    "name": "availability_status",
                    "value": node['availability_status']
                },
                {
                    "name": "reputation_score",
                    "value": str(node.get('reputation_score', 0))
                },
                {
                    "name": "verified",
                    "value": str(node.get('verified', False))
                }
            ]
        )
        
        # Create provider
        return EnergyProvider(
            id=f"provider_{node['user_id']}",
            descriptor={
                "name": node['name'],
                "code": f"ENERGY_{node['user_id']}",
                "symbol": "🔋",
                "short_desc": f"Energy provider - {node['node_type']}",
                "long_desc": f"Renewable energy provider specializing in {node['energy_source']} energy",
                "images": [{"url": f"/images/providers/provider_{node['user_id']}.jpg"}]
            },
            category_id=BecknEnergyCategory.ENERGY_TRADING,
            rating=node.get('reputation_score', 0),
            time={
                "label": "Operating Hours",
                "timestamp": datetime.utcnow().isoformat(),
                "duration": "PT24H",
                "range": {
                    "start": "00:00:00",
                    "end": "23:59:59"
                },
                "days": "1,2,3,4,5,6,7"
            },
            locations=[
                {
                    "id": f"loc_{node['id']}",
                    "descriptor": {
                        "name": f"Location {node['id']}",
                        "code": f"LOC_{node['id']}"
                    },
                    "gps": f"{node['location'][0]},{node['location'][1]}",
                    "address": {
                        "locality": "Energy District",
                        "street": f"Grid Lane {node['id']}",
                        "city": "Delhi",
                        "state": "Delhi",
                        "country": "India",
                        "area_code": "110001"
                    },
                    "station_code": f"ENERGY_{node['id']}",
                    "city": {
                        "name": "Delhi",
                        "code": "DEL"
                    },
                    "country": {
                        "name": "India",
                        "code": "IND"
                    }
                }
            ],
            items=[energy_item],
            fulfillments=[
                {
                    "id": f"fulfillment_{node['id']}",
                    "type": EnergyFulfillmentType.GRID_INJECTION.value,
                    "state": {
                        "descriptor": {
                            "name": "Available",
                            "code": "AVAILABLE"
                        }
                    },
                    "tracking": True,
                    "agent": {
                        "name": node['name'],
                        "phone": node.get('contact_info', {}).get('phone', '+91-XXXXXXXXXX')
                    },
                    "vehicle": {
                        "category": "ENERGY_TRANSMISSION",
                        "capacity": node['capacity_kw'],
                        "make": node['energy_source'].title(),
                        "model": f"Model {node['id']}",
                        "size": "MEDIUM",
                        "variant": "RENEWABLE" if node['renewable_percentage'] > 80 else "CONVENTIONAL",
                        "color": "GREEN" if node['renewable_percentage'] > 80 else "BLUE",
                        "energy_type": "CLEAN" if node['renewable_percentage'] > 80 else "MIXED",
                        "registration": f"ENERGY{node['id']:04d}"
                    },
                    "start": {
                        "time": {
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        "location": {
                            "gps": f"{node['location'][0]},{node['location'][1]}",
                            "address": {
                                "locality": "Energy District",
                                "city": "Delhi",
                                "state": "Delhi",
                                "country": "India"
                            }
                        }
                    },
                    "end": {
                        "time": {
                            "timestamp": (datetime.utcnow() + timedelta(minutes=node.get('estimated_delivery_time', 30))).isoformat()
                        }
                    },
                    "rateable": True,
                    "tags": [
                        {
                            "name": "estimated_delivery_time",
                            "value": str(node.get('estimated_delivery_time', 30))
                        }
                    ]
                }
            ],
            payments=[
                {
                    "uri": "https://razorpay.com/",
                    "tl_method": "http/get",
                    "params": {
                        "amount": str(node['pricing_per_kwh']),
                        "currency": "INR",
                        "transaction_id": ""
                    },
                    "type": "ON-ORDER",
                    "status": "NOT-PAID",
                    "time": {
                        "label": "Payment",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "collected_by": "BAP",
                    "tags": [
                        {
                            "name": "payment_methods",
                            "value": "cryptocurrency,fiat,energy_credits"
                        }
                    ]
                }
            ],
            tags=[
                {
                    "name": "energy_trading",
                    "value": "enabled"
                },
                {
                    "name": "sustainable_energy",
                    "value": "true" if node['renewable_percentage'] > 80 else "false"
                },
                {
                    "name": "auto_trading",
                    "value": str(node.get('trading_preferences', {}).get('auto_trading_enabled', False))
                }
            ]
        )

class BecknEnergyService:
    """Main service for Beckn energy trading operations"""
    
    def __init__(self, gateway: BecknGateway, bap_id: str, bap_uri: str):
        self.gateway = gateway
        self.bap_id = bap_id
        self.bap_uri = bap_uri
        self.adapter = BecknEnergyAdapter()
    
    async def search_energy(self, search_params: Dict[str, Any]) -> List[EnergyProvider]:
        """Search for energy offerings using Beckn protocol"""
        try:
            # Create context
            context = BecknContext(
                action=BecknAction.SEARCH.value,
                bap_id=self.bap_id,
                bap_uri=self.bap_uri,
                transaction_id=str(uuid.uuid4()),
                message_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Create intent
            intent = self.adapter.create_energy_intent(search_params)
            
            # Create message
            message = BecknMessage(
                intent={
                    "item": {
                        "descriptor": {
                            "name": "Energy Search"
                        }
                    },
                    "category": {
                        "id": BecknEnergyCategory.ENERGY_TRADING
                    },
                    "location": intent.location,
                    "time": intent.time_range,
                    "tags": [
                        {"name": "energy_type", "value": intent.energy_type},
                        {"name": "capacity_range", "value": json.dumps(intent.capacity_range)},
                        {"name": "price_range", "value": json.dumps(intent.price_range)},
                        {"name": "renewable_percentage", "value": str(intent.renewable_percentage)}
                    ]
                }
            )
            
            # Create request
            request = BecknRequest(context=context, message=message)
            
            # Broadcast to network
            responses = await self.gateway.broadcast_to_network(request)
            
            # Collect providers from responses
            providers = []
            for response in responses:
                if response.message.catalog:
                    providers.extend(response.message.catalog.bpp_providers)
            
            return providers
            
        except Exception as e:
            logger.error(f"Energy search failed: {e}")
            raise HTTPException(status_code=500, detail="Energy search failed")
    
    async def select_energy_offer(self, provider_id: str, item_id: str, 
                                quantity: float) -> Dict[str, Any]:
        """Select specific energy offer"""
        try:
            context = BecknContext(
                action=BecknAction.SELECT.value,
                bap_id=self.bap_id,
                bap_uri=self.bap_uri,
                transaction_id=str(uuid.uuid4()),
                message_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat()
            )
            
            message = BecknMessage(
                order={
                    "provider": {"id": provider_id},
                    "items": [
                        {
                            "id": item_id,
                            "quantity": {
                                "count": quantity,
                                "measure": {
                                    "unit": "kWh",
                                    "value": quantity
                                }
                            }
                        }
                    ]
                }
            )
            
            request = BecknRequest(context=context, message=message)
            responses = await self.gateway.broadcast_to_network(request)
            
            if responses:
                return asdict(responses[0])
            else:
                raise HTTPException(status_code=404, detail="No response from providers")
                
        except Exception as e:
            logger.error(f"Energy selection failed: {e}")
            raise HTTPException(status_code=500, detail="Energy selection failed")
    
    async def init_energy_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize energy order"""
        try:
            context = BecknContext(
                action=BecknAction.INIT.value,
                bap_id=self.bap_id,
                bap_uri=self.bap_uri,
                transaction_id=order_data.get("transaction_id", str(uuid.uuid4())),
                message_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat()
            )
            
            message = BecknMessage(order=order_data)
            request = BecknRequest(context=context, message=message)
            
            responses = await self.gateway.broadcast_to_network(request)
            
            if responses:
                return asdict(responses[0])
            else:
                raise HTTPException(status_code=404, detail="Order initialization failed")
                
        except Exception as e:
            logger.error(f"Order initialization failed: {e}")
            raise HTTPException(status_code=500, detail="Order initialization failed")
    
    async def confirm_energy_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Confirm energy order"""
        try:
            context = BecknContext(
                action=BecknAction.CONFIRM.value,
                bap_id=self.bap_id,
                bap_uri=self.bap_uri,
                transaction_id=order_data.get("transaction_id", str(uuid.uuid4())),
                message_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat()
            )
            
            message = BecknMessage(order=order_data)
            request = BecknRequest(context=context, message=message)
            
            responses = await self.gateway.broadcast_to_network(request)
            
            if responses:
                return asdict(responses[0])
            else:
                raise HTTPException(status_code=404, detail="Order confirmation failed")
                
        except Exception as e:
            logger.error(f"Order confirmation failed: {e}")
            raise HTTPException(status_code=500, detail="Order confirmation failed")
    
    async def track_energy_order(self, order_id: str) -> Dict[str, Any]:
        """Track energy order status"""
        try:
            context = BecknContext(
                action=BecknAction.TRACK.value,
                bap_id=self.bap_id,
                bap_uri=self.bap_uri,
                transaction_id=str(uuid.uuid4()),
                message_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat()
            )
            
            message = BecknMessage(
                order={"id": order_id}
            )
            
            request = BecknRequest(context=context, message=message)
            responses = await self.gateway.broadcast_to_network(request)
            
            if responses:
                return asdict(responses[0])
            else:
                raise HTTPException(status_code=404, detail="Order not found")
                
        except Exception as e:
            logger.error(f"Order tracking failed: {e}")
            raise HTTPException(status_code=500, detail="Order tracking failed")

# Example usage and testing
async def main():
    """Example Beckn protocol usage"""
    
    # Initialize gateway
    gateway = BecknGateway(
        gateway_url="https://beckn-gateway.example.com",
        registry_url="https://beckn-registry.example.com"
    )
    
    await gateway.initialize()
    
    try:
        # Initialize Beckn service
        beckn_service = BecknEnergyService(
            gateway=gateway,
            bap_id="powershare-bap-001",
            bap_uri="https://powershare.example.com/beckn"
        )
        
        # Search for energy
        search_params = {
            "energy_type": "solar",
            "min_capacity": 5.0,
            "max_capacity": 50.0,
            "lat": 28.6139,
            "lng": 77.2090,
            "radius": 25,
            "min_renewable": 80,
            "max_price": 8.0
        }
        
        providers = await beckn_service.search_energy(search_params)
        print(f"Found {len(providers)} energy providers")
        
        if providers:
            # Select first provider
            provider = providers[0]
            if provider.items:
                item = provider.items[0]
                
                # Select energy offer
                selection = await beckn_service.select_energy_offer(
                    provider_id=provider.id,
                    item_id=item.id,
                    quantity=10.0
                )
                print(f"Energy offer selected: {selection}")
                
                # Initialize order
                order_data = {
                    "provider": {"id": provider.id},
                    "items": [{"id": item.id, "quantity": {"count": 10.0}}],
                    "billing": {
                        "name": "John Doe",
                        "email": "john@example.com",
                        "phone": "+91-9876543210"
                    }
                }
                
                init_response = await beckn_service.init_energy_order(order_data)
                print(f"Order initialized: {init_response}")
    
    finally:
        await gateway.close()

if __name__ == "__main__":
    asyncio.run(main())
