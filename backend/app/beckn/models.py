"""
Beckn Protocol Integration for PowerShare Energy Trading Platform
================================================================

This module implements comprehensive Beckn Protocol integration for energy trading:
- BAP (Buyer App Participant) - Consumer-side application
- BPP (Buyer Platform Provider) - Prosumer-side platform  
- Beckn Gateway integration for network communication
- Discovery, Search, Select, Order, Fulfillment, and Payment APIs
- Energy-specific schemas and business logic

Beckn Protocol enables interoperable energy trading across multiple platforms
and networks, creating a unified ecosystem for energy commerce.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field, validator
import uuid
import json
import asyncio
import aiohttp
import hashlib
import hmac
from decimal import Decimal

Base = declarative_base()

class BecknDomain(Enum):
    ENERGY = "energy"
    RENEWABLE_ENERGY = "renewable-energy"
    P2P_ENERGY = "p2p-energy"

class BecknAction(Enum):
    SEARCH = "search"
    SELECT = "select"
    INIT = "init"
    CONFIRM = "confirm"
    STATUS = "status"
    TRACK = "track"
    CANCEL = "cancel"
    UPDATE = "update"
    RATING = "rating"
    SUPPORT = "support"

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class EnergySourceType(Enum):
    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    BIOMASS = "biomass"
    GEOTHERMAL = "geothermal"
    NUCLEAR = "nuclear"
    NATURAL_GAS = "natural_gas"
    COAL = "coal"
    MIXED = "mixed"

# Beckn Protocol Models

class BecknContext(BaseModel):
    """Beckn Protocol Context"""
    domain: str
    country: str = "IN"
    city: str = "*"
    action: str
    core_version: str = "1.1.0"
    bap_id: str
    bap_uri: str
    bpp_id: Optional[str] = None
    bpp_uri: Optional[str] = None
    transaction_id: str
    message_id: str
    timestamp: datetime
    key: Optional[str] = None
    ttl: Optional[str] = "PT30S"

class BecknLocation(BaseModel):
    """Beckn Location Schema"""
    id: Optional[str] = None
    descriptor: Optional[Dict[str, str]] = None
    gps: Optional[str] = None  # latitude,longitude
    address: Optional[Dict[str, str]] = None
    city: Optional[Dict[str, str]] = None
    country: Optional[Dict[str, str]] = None
    area_code: Optional[str] = None

class BecknPrice(BaseModel):
    """Beckn Price Schema"""
    currency: str = "INR"
    value: str  # Decimal as string
    estimated_value: Optional[str] = None
    computed_value: Optional[str] = None
    listed_value: Optional[str] = None
    offered_value: Optional[str] = None
    minimum_value: Optional[str] = None
    maximum_value: Optional[str] = None

class BecknQuantity(BaseModel):
    """Beckn Quantity Schema"""
    count: Optional[int] = None
    measure: Optional[Dict[str, str]] = None  # unit and value
    
class BecknItem(BaseModel):
    """Beckn Item Schema for Energy Products"""
    id: str
    parent_item_id: Optional[str] = None
    descriptor: Dict[str, str]  # name, short_desc, long_desc, images
    price: BecknPrice
    category_id: str
    fulfillment_id: str
    location_id: str
    time: Optional[Dict[str, Any]] = None  # availability time
    matched: Optional[bool] = None
    related: Optional[bool] = None
    recommended: Optional[bool] = None
    tags: Optional[List[Dict[str, Any]]] = None
    
    # Energy-specific properties
    energy_source: Optional[str] = None
    renewable_percentage: Optional[float] = None
    carbon_intensity: Optional[float] = None  # gCO2/kWh
    quantity: Optional[BecknQuantity] = None

class BecknProvider(BaseModel):
    """Beckn Provider Schema for Energy Suppliers"""
    id: str
    descriptor: Dict[str, str]
    category_id: Optional[str] = None
    rating: Optional[float] = None
    time: Optional[Dict[str, Any]] = None
    categories: Optional[List[Dict[str, str]]] = None
    fulfillments: Optional[List[Dict[str, Any]]] = None
    payments: Optional[List[Dict[str, Any]]] = None
    locations: Optional[List[BecknLocation]] = None
    items: Optional[List[BecknItem]] = None
    tags: Optional[List[Dict[str, Any]]] = None
    
    # Energy-specific properties
    grid_connection: Optional[bool] = None
    capacity_mw: Optional[float] = None
    efficiency_rating: Optional[str] = None

class BecknCatalog(BaseModel):
    """Beckn Catalog Schema"""
    bpp_descriptor: Dict[str, str]
    bpp_providers: List[BecknProvider]

class BecknOrder(BaseModel):
    """Beckn Order Schema for Energy Trading"""
    id: str
    state: str
    provider: BecknProvider
    items: List[BecknItem]
    billing: Optional[Dict[str, Any]] = None
    fulfillment: Optional[Dict[str, Any]] = None
    quote: Optional[Dict[str, Any]] = None
    payment: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    # Energy-specific properties
    delivery_schedule: Optional[Dict[str, Any]] = None
    grid_injection_point: Optional[str] = None
    meter_reading_required: Optional[bool] = None

# Database Models for Beckn Integration

class BecknTransaction(Base):
    __tablename__ = "beckn_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(255), unique=True, nullable=False)
    domain = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    bap_id = Column(String(255), nullable=False)
    bap_uri = Column(String(500), nullable=False)
    bpp_id = Column(String(255))
    bpp_uri = Column(String(500))
    status = Column(String(50), default="initiated")
    context_data = Column(JSONB)
    request_payload = Column(JSONB)
    response_payload = Column(JSONB)
    error_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class BecknEnergyProduct(Base):
    __tablename__ = "beckn_energy_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beckn_item_id = Column(String(255), unique=True, nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    energy_source = Column(String(50), nullable=False)
    capacity_kwh = Column(Float, nullable=False)
    price_per_kwh = Column(Float, nullable=False)
    renewable_percentage = Column(Float, default=0.0)
    carbon_intensity = Column(Float, default=0.0)
    location_gps = Column(String(100))  # "lat,lon"
    availability_start = Column(DateTime)
    availability_end = Column(DateTime)
    is_active = Column(Boolean, default=True)
    beckn_catalog_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    provider = relationship("User")

class BecknEnergyOrder(Base):
    __tablename__ = "beckn_energy_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beckn_order_id = Column(String(255), unique=True, nullable=False)
    beckn_transaction_id = Column(UUID(as_uuid=True), ForeignKey("beckn_transactions.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("beckn_energy_products.id"))
    quantity_kwh = Column(Float, nullable=False)
    price_per_kwh = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    order_status = Column(String(50), default=OrderStatus.PENDING.value)
    delivery_schedule = Column(JSONB)
    payment_status = Column(String(50), default="pending")
    fulfillment_status = Column(String(50), default="pending")
    beckn_order_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transaction = relationship("BecknTransaction")
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    product = relationship("BecknEnergyProduct")

# Beckn Protocol Service Classes

class BecknConfigService:
    """Configuration service for Beckn Protocol integration"""
    
    def __init__(self):
        self.domain = BecknDomain.ENERGY.value
        self.country = "IN"
        self.core_version = "1.1.0"
        self.bap_id = "powershare.bap.io"
        self.bap_uri = "https://api.powershare.com/beckn/bap"
        self.bpp_id = "powershare.bpp.io"
        self.bpp_uri = "https://api.powershare.com/beckn/bpp"
        self.gateway_uri = "https://gateway.beckn.org"
        self.private_key = "your-beckn-private-key"  # Should be from environment
        
    def create_context(self, action: BecknAction, transaction_id: str = None, 
                      message_id: str = None, bpp_id: str = None, bpp_uri: str = None) -> BecknContext:
        """Create Beckn context for requests"""
        return BecknContext(
            domain=self.domain,
            country=self.country,
            action=action.value,
            core_version=self.core_version,
            bap_id=self.bap_id,
            bap_uri=self.bap_uri,
            bpp_id=bpp_id or self.bpp_id,
            bpp_uri=bpp_uri or self.bpp_uri,
            transaction_id=transaction_id or str(uuid.uuid4()),
            message_id=message_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )

class BecknCatalogService:
    """Service for managing Beckn catalog and energy products"""
    
    def __init__(self, db_session: Session, config: BecknConfigService):
        self.db = db_session
        self.config = config
    
    async def create_energy_product(self, provider_id: int, product_data: Dict[str, Any]) -> str:
        """Create a new energy product for Beckn catalog"""
        try:
            beckn_item_id = f"energy_{provider_id}_{uuid.uuid4().hex[:8]}"
            
            product = BecknEnergyProduct(
                beckn_item_id=beckn_item_id,
                provider_id=provider_id,
                energy_source=product_data['energy_source'],
                capacity_kwh=product_data['capacity_kwh'],
                price_per_kwh=product_data['price_per_kwh'],
                renewable_percentage=product_data.get('renewable_percentage', 0.0),
                carbon_intensity=product_data.get('carbon_intensity', 0.0),
                location_gps=product_data.get('location_gps'),
                availability_start=product_data.get('availability_start'),
                availability_end=product_data.get('availability_end'),
                beckn_catalog_data=await self._create_beckn_item_data(beckn_item_id, product_data)
            )
            
            self.db.add(product)
            self.db.commit()
            
            return beckn_item_id
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creating energy product: {e}")
            return None
    
    async def get_catalog(self, filters: Dict[str, Any] = None) -> BecknCatalog:
        """Get Beckn catalog for energy products"""
        query = self.db.query(BecknEnergyProduct).filter(BecknEnergyProduct.is_active == True)
        
        # Apply filters
        if filters:
            if 'energy_source' in filters:
                query = query.filter(BecknEnergyProduct.energy_source == filters['energy_source'])
            if 'min_renewable_percentage' in filters:
                query = query.filter(BecknEnergyProduct.renewable_percentage >= filters['min_renewable_percentage'])
            if 'max_price' in filters:
                query = query.filter(BecknEnergyProduct.price_per_kwh <= filters['max_price'])
        
        products = query.all()
        
        # Group products by provider
        providers_map = {}
        for product in products:
            provider_id = product.provider_id
            if provider_id not in providers_map:
                providers_map[provider_id] = {
                    'provider': product.provider,
                    'items': []
                }
            providers_map[provider_id]['items'].append(product)
        
        # Create Beckn providers
        beckn_providers = []
        for provider_data in providers_map.values():
            provider = await self._create_beckn_provider(provider_data['provider'], provider_data['items'])
            beckn_providers.append(provider)
        
        return BecknCatalog(
            bpp_descriptor={
                "name": "PowerShare Energy Platform",
                "short_desc": "Decentralized P2P Energy Trading",
                "long_desc": "AI-powered community energy trading platform"
            },
            bpp_providers=beckn_providers
        )
    
    async def _create_beckn_item_data(self, item_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Beckn item data structure"""
        return {
            "id": item_id,
            "descriptor": {
                "name": f"{product_data['energy_source'].title()} Energy",
                "short_desc": f"Clean {product_data['energy_source']} energy",
                "long_desc": f"Renewable {product_data['energy_source']} energy with {product_data.get('renewable_percentage', 0)}% green content"
            },
            "price": {
                "currency": "INR",
                "value": str(product_data['price_per_kwh'])
            },
            "category_id": "renewable_energy",
            "quantity": {
                "measure": {
                    "unit": "kWh",
                    "value": str(product_data['capacity_kwh'])
                }
            },
            "tags": [
                {
                    "name": "energy_attributes",
                    "list": [
                        {"key": "source", "value": product_data['energy_source']},
                        {"key": "renewable_percentage", "value": str(product_data.get('renewable_percentage', 0))},
                        {"key": "carbon_intensity", "value": str(product_data.get('carbon_intensity', 0))}
                    ]
                }
            ]
        }
    
    async def _create_beckn_provider(self, provider, items: List[BecknEnergyProduct]) -> BecknProvider:
        """Create Beckn provider from user and items"""
        beckn_items = []
        total_capacity = 0
        
        for item in items:
            beckn_item = BecknItem(
                id=item.beckn_item_id,
                descriptor=item.beckn_catalog_data.get('descriptor', {}),
                price=BecknPrice(**item.beckn_catalog_data.get('price', {})),
                category_id=item.beckn_catalog_data.get('category_id', 'energy'),
                fulfillment_id="energy_delivery",
                location_id=f"loc_{provider.id}",
                energy_source=item.energy_source,
                renewable_percentage=item.renewable_percentage,
                carbon_intensity=item.carbon_intensity,
                quantity=BecknQuantity(measure={"unit": "kWh", "value": str(item.capacity_kwh)})
            )
            beckn_items.append(beckn_item)
            total_capacity += item.capacity_kwh
        
        return BecknProvider(
            id=f"provider_{provider.id}",
            descriptor={
                "name": provider.full_name,
                "short_desc": f"Energy provider with {total_capacity:.1f} kWh capacity",
                "long_desc": f"Renewable energy provider offering various clean energy sources"
            },
            category_id="energy_provider",
            locations=[
                BecknLocation(
                    id=f"loc_{provider.id}",
                    gps=getattr(provider, 'location_gps', None),
                    address={"full": getattr(provider, 'location', 'Unknown')}
                )
            ],
            items=beckn_items,
            grid_connection=True,
            capacity_mw=total_capacity / 1000.0,
            efficiency_rating="A+"
        )

class BecknOrderService:
    """Service for managing Beckn orders and transactions"""
    
    def __init__(self, db_session: Session, config: BecknConfigService):
        self.db = db_session
        self.config = config
    
    async def create_transaction(self, context: BecknContext, action: BecknAction, 
                               request_payload: Dict[str, Any]) -> str:
        """Create a new Beckn transaction"""
        try:
            transaction = BecknTransaction(
                transaction_id=context.transaction_id,
                domain=context.domain,
                action=action.value,
                bap_id=context.bap_id,
                bap_uri=context.bap_uri,
                bpp_id=context.bpp_id,
                bpp_uri=context.bpp_uri,
                context_data=context.dict(),
                request_payload=request_payload
            )
            
            self.db.add(transaction)
            self.db.commit()
            
            return str(transaction.id)
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creating transaction: {e}")
            return None
    
    async def create_energy_order(self, order_data: Dict[str, Any]) -> str:
        """Create a new energy order through Beckn"""
        try:
            beckn_order_id = f"order_{uuid.uuid4().hex[:12]}"
            
            order = BecknEnergyOrder(
                beckn_order_id=beckn_order_id,
                beckn_transaction_id=order_data.get('transaction_id'),
                buyer_id=order_data['buyer_id'],
                seller_id=order_data['seller_id'],
                product_id=order_data['product_id'],
                quantity_kwh=order_data['quantity_kwh'],
                price_per_kwh=order_data['price_per_kwh'],
                total_amount=order_data['quantity_kwh'] * order_data['price_per_kwh'],
                delivery_schedule=order_data.get('delivery_schedule'),
                beckn_order_data=await self._create_beckn_order_data(beckn_order_id, order_data)
            )
            
            self.db.add(order)
            self.db.commit()
            
            return beckn_order_id
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creating energy order: {e}")
            return None
    
    async def update_order_status(self, order_id: str, status: OrderStatus, 
                                fulfillment_data: Dict[str, Any] = None) -> bool:
        """Update order status and fulfillment data"""
        try:
            order = self.db.query(BecknEnergyOrder).filter(
                BecknEnergyOrder.beckn_order_id == order_id
            ).first()
            
            if not order:
                return False
            
            order.order_status = status.value
            order.updated_at = datetime.utcnow()
            
            if fulfillment_data:
                current_data = order.beckn_order_data or {}
                current_data.update(fulfillment_data)
                order.beckn_order_data = current_data
                
                if 'payment_status' in fulfillment_data:
                    order.payment_status = fulfillment_data['payment_status']
                if 'fulfillment_status' in fulfillment_data:
                    order.fulfillment_status = fulfillment_data['fulfillment_status']
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error updating order status: {e}")
            return False
    
    async def _create_beckn_order_data(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Beckn order data structure"""
        return {
            "id": order_id,
            "state": "Created",
            "billing": {
                "name": "Energy Purchase",
                "phone": "+91-9999999999",
                "email": "buyer@powershare.com"
            },
            "fulfillment": {
                "id": "energy_delivery",
                "type": "GRID_INJECTION",
                "state": {
                    "descriptor": {
                        "name": "Order placed"
                    }
                },
                "tracking": True,
                "start": {
                    "time": {
                        "range": {
                            "start": order_data.get('delivery_start', datetime.utcnow().isoformat()),
                            "end": order_data.get('delivery_end', (datetime.utcnow() + timedelta(hours=1)).isoformat())
                        }
                    }
                }
            },
            "quote": {
                "price": {
                    "currency": "INR",
                    "value": str(order_data['quantity_kwh'] * order_data['price_per_kwh'])
                },
                "breakup": [
                    {
                        "title": "Energy Cost",
                        "price": {
                            "currency": "INR",
                            "value": str(order_data['quantity_kwh'] * order_data['price_per_kwh'])
                        }
                    }
                ]
            },
            "payment": {
                "uri": "https://api.powershare.com/payments",
                "tl_method": "http/get",
                "params": {
                    "amount": str(order_data['quantity_kwh'] * order_data['price_per_kwh']),
                    "currency": "INR"
                },
                "type": "ON-FULFILLMENT",
                "status": "NOT-PAID"
            }
        }

class BecknGatewayService:
    """Service for communicating with Beckn Gateway"""
    
    def __init__(self, config: BecknConfigService):
        self.config = config
        self.session = aiohttp.ClientSession()
    
    async def send_request(self, action: BecknAction, payload: Dict[str, Any], 
                          target_uri: str = None) -> Dict[str, Any]:
        """Send request to Beckn network"""
        try:
            uri = target_uri or self.config.gateway_uri
            
            # Create authorization header
            auth_header = self._create_auth_header(payload)
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": auth_header,
                "Accept": "application/json"
            }
            
            async with self.session.post(f"{uri}/{action.value}", 
                                       json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    print(f"Beckn request failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            print(f"Error sending Beckn request: {e}")
            return None
    
    def _create_auth_header(self, payload: Dict[str, Any]) -> str:
        """Create authorization header for Beckn request"""
        # Simplified authorization - in production, implement proper Beckn signature
        timestamp = str(int(datetime.utcnow().timestamp()))
        message = json.dumps(payload, separators=(',', ':'))
        
        signature = hmac.new(
            self.config.private_key.encode(),
            f"{timestamp}{message}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"Signature keyId=\"{self.config.bap_id}\",algorithm=\"hmac-sha256\",created=\"{timestamp}\",signature=\"{signature}\""
    
    async def close(self):
        """Close HTTP session"""
        await self.session.close()

class BecknAPIService:
    """Main service coordinating all Beckn Protocol operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.config = BecknConfigService()
        self.catalog_service = BecknCatalogService(db_session, self.config)
        self.order_service = BecknOrderService(db_session, self.config)
        self.gateway_service = BecknGatewayService(self.config)
    
    async def search_energy_products(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """BAP: Search for energy products across Beckn network"""
        try:
            context = self.config.create_context(BecknAction.SEARCH)
            
            search_payload = {
                "context": context.dict(),
                "message": {
                    "intent": {
                        "item": {
                            "descriptor": {
                                "name": search_criteria.get('energy_type', 'renewable energy')
                            }
                        },
                        "fulfillment": {
                            "start": {
                                "location": {
                                    "gps": search_criteria.get('location_gps')
                                }
                            }
                        },
                        "payment": {
                            "type": "ON-FULFILLMENT"
                        }
                    }
                }
            }
            
            # Create transaction record
            transaction_id = await self.order_service.create_transaction(
                context, BecknAction.SEARCH, search_payload
            )
            
            # Send to Beckn network
            response = await self.gateway_service.send_request(BecknAction.SEARCH, search_payload)
            
            return {
                "transaction_id": transaction_id,
                "search_results": response
            }
            
        except Exception as e:
            print(f"Error in search_energy_products: {e}")
            return None
    
    async def select_energy_product(self, item_id: str, quantity: float, buyer_id: int) -> Dict[str, Any]:
        """BAP: Select specific energy product"""
        try:
            context = self.config.create_context(BecknAction.SELECT)
            
            select_payload = {
                "context": context.dict(),
                "message": {
                    "order": {
                        "items": [
                            {
                                "id": item_id,
                                "quantity": {
                                    "count": 1,
                                    "measure": {
                                        "unit": "kWh",
                                        "value": str(quantity)
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            transaction_id = await self.order_service.create_transaction(
                context, BecknAction.SELECT, select_payload
            )
            
            response = await self.gateway_service.send_request(BecknAction.SELECT, select_payload)
            
            return {
                "transaction_id": transaction_id,
                "selection_response": response
            }
            
        except Exception as e:
            print(f"Error in select_energy_product: {e}")
            return None
    
    async def confirm_energy_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """BAP: Confirm energy order"""
        try:
            context = self.config.create_context(BecknAction.CONFIRM)
            
            # Create order in database
            order_id = await self.order_service.create_energy_order(order_data)
            
            confirm_payload = {
                "context": context.dict(),
                "message": {
                    "order": await self.order_service._create_beckn_order_data(order_id, order_data)
                }
            }
            
            transaction_id = await self.order_service.create_transaction(
                context, BecknAction.CONFIRM, confirm_payload
            )
            
            response = await self.gateway_service.send_request(BecknAction.CONFIRM, confirm_payload)
            
            return {
                "order_id": order_id,
                "transaction_id": transaction_id,
                "confirmation_response": response
            }
            
        except Exception as e:
            print(f"Error in confirm_energy_order: {e}")
            return None
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Check order status through Beckn"""
        try:
            context = self.config.create_context(BecknAction.STATUS)
            
            status_payload = {
                "context": context.dict(),
                "message": {
                    "order_id": order_id
                }
            }
            
            response = await self.gateway_service.send_request(BecknAction.STATUS, status_payload)
            
            return response
            
        except Exception as e:
            print(f"Error in get_order_status: {e}")
            return None
    
    async def provide_catalog(self, search_intent: Dict[str, Any]) -> Dict[str, Any]:
        """BPP: Provide catalog in response to search"""
        try:
            # Get matching products from catalog
            filters = self._extract_filters_from_intent(search_intent)
            catalog = await self.catalog_service.get_catalog(filters)
            
            return {
                "catalog": catalog.dict()
            }
            
        except Exception as e:
            print(f"Error in provide_catalog: {e}")
            return None
    
    def _extract_filters_from_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Extract search filters from Beckn search intent"""
        filters = {}
        
        # Extract filters from intent structure
        if 'item' in intent:
            item = intent['item']
            if 'descriptor' in item and 'name' in item['descriptor']:
                name = item['descriptor']['name'].lower()
                if 'solar' in name:
                    filters['energy_source'] = 'solar'
                elif 'wind' in name:
                    filters['energy_source'] = 'wind'
        
        # Add more filter extraction logic as needed
        
        return filters
    
    async def close(self):
        """Close services"""
        await self.gateway_service.close()

# Export classes and functions
__all__ = [
    'BecknDomain', 'BecknAction', 'OrderStatus', 'EnergySourceType',
    'BecknContext', 'BecknLocation', 'BecknPrice', 'BecknQuantity', 'BecknItem', 
    'BecknProvider', 'BecknCatalog', 'BecknOrder',
    'BecknTransaction', 'BecknEnergyProduct', 'BecknEnergyOrder',
    'BecknConfigService', 'BecknCatalogService', 'BecknOrderService', 
    'BecknGatewayService', 'BecknAPIService'
]
