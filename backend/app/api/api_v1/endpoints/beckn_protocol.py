"""
Beckn Protocol API Endpoints
PowerShare Energy Trading Platform
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid
import json
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.energy_transaction import EnergyTransaction
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

# Beckn Protocol Models
class BecknContext(BaseModel):
    domain: str = "energy"
    country: str = "IND"
    city: str = "*"
    action: str
    version: str = "1.0.0"
    bap_id: str = settings.BECKN_SUBSCRIBER_ID
    bap_uri: str = settings.BECKN_SUBSCRIBER_URL
    transaction_id: str
    message_id: str
    timestamp: datetime

class BecknItem(BaseModel):
    id: str
    descriptor: Dict[str, str]
    price: Dict[str, Any]
    quantity: Dict[str, Any]
    category_id: str
    location_id: Optional[str] = None
    time: Optional[Dict[str, str]] = None

class BecknProvider(BaseModel):
    id: str
    descriptor: Dict[str, str]
    categories: List[Dict[str, Any]]
    items: List[BecknItem]
    locations: List[Dict[str, Any]]

class BecknCatalog(BaseModel):
    providers: List[BecknProvider]

class BecknIntent(BaseModel):
    item: Optional[Dict[str, Any]] = None
    provider: Optional[Dict[str, str]] = None
    fulfillment: Optional[Dict[str, Any]] = None
    payment: Optional[Dict[str, str]] = None

class BecknMessage(BaseModel):
    intent: Optional[BecknIntent] = None
    catalog: Optional[BecknCatalog] = None
    order: Optional[Dict[str, Any]] = None

class BecknRequest(BaseModel):
    context: BecknContext
    message: BecknMessage

class BecknResponse(BaseModel):
    context: BecknContext
    message: Optional[BecknMessage] = None
    error: Optional[Dict[str, str]] = None

class EnergySearchRequest(BaseModel):
    energy_type: str = "renewable"  # renewable, solar, wind, etc.
    amount: float
    max_price: Optional[float] = None
    location: Optional[str] = None
    delivery_time: Optional[str] = None

class EnergyOrderRequest(BaseModel):
    provider_id: str
    item_id: str
    quantity: float
    price: float
    delivery_location: Optional[str] = None

# Helper Functions
def generate_transaction_id() -> str:
    """Generate unique transaction ID."""
    return str(uuid.uuid4())

def generate_message_id() -> str:
    """Generate unique message ID."""
    return str(uuid.uuid4())

def create_beckn_context(action: str) -> BecknContext:
    """Create Beckn context for API calls."""
    return BecknContext(
        action=action,
        transaction_id=generate_transaction_id(),
        message_id=generate_message_id(),
        timestamp=datetime.utcnow()
    )

async def send_beckn_request(endpoint: str, request: BecknRequest) -> BecknResponse:
    """Send request to Beckn gateway (mock for demo)."""
    
    # In production, this would send actual HTTP requests to Beckn gateway
    # For demo, we simulate responses
    
    if request.context.action == "search":
        # Simulate search response with energy providers
        providers = [
            BecknProvider(
                id="provider_solar_farm_1",
                descriptor={
                    "name": "Green Energy Solar Farm",
                    "short_desc": "Clean solar energy provider",
                    "long_desc": "Leading solar energy provider with 500MW capacity"
                },
                categories=[
                    {
                        "id": "renewable_energy",
                        "descriptor": {"name": "Renewable Energy"}
                    }
                ],
                items=[
                    BecknItem(
                        id="solar_energy_1",
                        descriptor={
                            "name": "Solar Energy Package",
                            "short_desc": "Clean solar energy",
                            "long_desc": "100% clean solar energy from certified farms"
                        },
                        price={
                            "currency": "INR",
                            "value": "4.50",
                            "maximum_value": "5.00"
                        },
                        quantity={
                            "available": {"count": 1000},
                            "maximum": {"count": 1000}
                        },
                        category_id="renewable_energy",
                        time={
                            "range": {
                                "start": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                                "end": (datetime.utcnow() + timedelta(hours=24)).isoformat()
                            }
                        }
                    )
                ],
                locations=[
                    {
                        "id": "loc_solar_farm_1",
                        "descriptor": {"name": "Main Solar Farm"},
                        "gps": "12.9716,77.5946",
                        "city": {"name": "Bangalore"}
                    }
                ]
            ),
            BecknProvider(
                id="provider_wind_farm_1",
                descriptor={
                    "name": "Wind Power Solutions",
                    "short_desc": "Wind energy provider",
                    "long_desc": "Sustainable wind energy with 300MW capacity"
                },
                categories=[
                    {
                        "id": "renewable_energy",
                        "descriptor": {"name": "Renewable Energy"}
                    }
                ],
                items=[
                    BecknItem(
                        id="wind_energy_1",
                        descriptor={
                            "name": "Wind Energy Package",
                            "short_desc": "Clean wind energy",
                            "long_desc": "100% clean wind energy from coastal farms"
                        },
                        price={
                            "currency": "INR",
                            "value": "4.20",
                            "maximum_value": "4.80"
                        },
                        quantity={
                            "available": {"count": 800},
                            "maximum": {"count": 800}
                        },
                        category_id="renewable_energy"
                    )
                ],
                locations=[
                    {
                        "id": "loc_wind_farm_1",
                        "descriptor": {"name": "Coastal Wind Farm"},
                        "gps": "13.0827,80.2707",
                        "city": {"name": "Chennai"}
                    }
                ]
            )
        ]
        
        return BecknResponse(
            context=request.context,
            message=BecknMessage(
                catalog=BecknCatalog(providers=providers)
            )
        )
    
    elif request.context.action == "select":
        # Simulate select response
        return BecknResponse(
            context=request.context,
            message=BecknMessage(
                order={
                    "id": generate_transaction_id(),
                    "state": "Created",
                    "items": [request.message.intent.item] if request.message.intent and request.message.intent.item else [],
                    "provider": request.message.intent.provider if request.message.intent and request.message.intent.provider else {},
                    "quote": {
                        "price": {"currency": "INR", "value": "450.00"},
                        "breakup": [
                            {"title": "Energy Cost", "price": {"currency": "INR", "value": "400.00"}},
                            {"title": "Transmission Fee", "price": {"currency": "INR", "value": "30.00"}},
                            {"title": "Service Fee", "price": {"currency": "INR", "value": "20.00"}}
                        ]
                    }
                }
            )
        )
    
    else:
        # Default response for other actions
        return BecknResponse(
            context=request.context,
            message=BecknMessage(
                order={"id": generate_transaction_id(), "state": "Accepted"}
            )
        )

# API Endpoints
@router.post("/search", response_model=BecknResponse)
async def search_energy_providers(
    search_request: EnergySearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search for energy providers using Beckn protocol."""
    
    if search_request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Energy amount must be positive"
        )
    
    # Create Beckn search intent
    intent = BecknIntent(
        item={
            "descriptor": {"name": search_request.energy_type},
            "quantity": {"count": search_request.amount}
        }
    )
    
    if search_request.max_price:
        intent.item["price"] = {"maximum_value": str(search_request.max_price)}
    
    if search_request.location:
        intent.fulfillment = {"end": {"location": {"city": {"name": search_request.location}}}}
    
    # Create Beckn request
    beckn_request = BecknRequest(
        context=create_beckn_context("search"),
        message=BecknMessage(intent=intent)
    )
    
    # Send to Beckn gateway
    try:
        response = await send_beckn_request("/search", beckn_request)
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beckn search failed: {str(e)}"
        )

@router.post("/select", response_model=BecknResponse)
async def select_energy_offer(
    provider_id: str,
    item_id: str,
    quantity: float,
    current_user: User = Depends(get_current_user)
):
    """Select specific energy offer using Beckn protocol."""
    
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be positive"
        )
    
    # Create Beckn select intent
    intent = BecknIntent(
        provider={"id": provider_id},
        item={"id": item_id, "quantity": {"count": quantity}}
    )
    
    # Create Beckn request
    beckn_request = BecknRequest(
        context=create_beckn_context("select"),
        message=BecknMessage(intent=intent)
    )
    
    # Send to Beckn gateway
    try:
        response = await send_beckn_request("/select", beckn_request)
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beckn select failed: {str(e)}"
        )

@router.post("/init", response_model=BecknResponse)
async def initialize_energy_order(
    order_request: EnergyOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize energy order using Beckn protocol."""
    
    if order_request.quantity <= 0 or order_request.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity and price must be positive"
        )
    
    # Create Beckn init order
    order = {
        "id": generate_transaction_id(),
        "provider": {"id": order_request.provider_id},
        "items": [
            {
                "id": order_request.item_id,
                "quantity": {"count": order_request.quantity}
            }
        ],
        "billing": {
            "name": current_user.full_name,
            "email": current_user.email
        },
        "payment": {
            "type": "ON-FULFILLMENT",
            "collected_by": "BAP"
        }
    }
    
    if order_request.delivery_location:
        order["fulfillment"] = {
            "end": {"location": {"city": {"name": order_request.delivery_location}}}
        }
    
    # Create Beckn request
    beckn_request = BecknRequest(
        context=create_beckn_context("init"),
        message=BecknMessage(order=order)
    )
    
    # Send to Beckn gateway
    try:
        response = await send_beckn_request("/init", beckn_request)
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beckn init failed: {str(e)}"
        )

@router.post("/confirm", response_model=BecknResponse)
async def confirm_energy_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm energy order using Beckn protocol."""
    
    # Create Beckn confirm order
    order = {
        "id": order_id,
        "state": "Created",
        "payment": {
            "status": "PAID",
            "collected_by": "BAP"
        }
    }
    
    # Create Beckn request
    beckn_request = BecknRequest(
        context=create_beckn_context("confirm"),
        message=BecknMessage(order=order)
    )
    
    # Send to Beckn gateway
    try:
        response = await send_beckn_request("/confirm", beckn_request)
        
        # Create local transaction record
        if response.message and response.message.order:
            transaction = EnergyTransaction(
                seller_id=1,  # Would get from provider mapping
                buyer_id=current_user.id,
                amount=100.0,  # Would get from order details
                price=4.50,    # Would get from order quote
                status="confirmed",
                transaction_type="beckn_order",
                beckn_order_id=order_id
            )
            
            db.add(transaction)
            await db.commit()
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beckn confirm failed: {str(e)}"
        )

@router.post("/cancel")
async def cancel_energy_order(
    order_id: str,
    cancellation_reason: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel energy order using Beckn protocol."""
    
    # Create Beckn cancel request
    beckn_request = BecknRequest(
        context=create_beckn_context("cancel"),
        message=BecknMessage(
            order={
                "id": order_id,
                "cancellation": {
                    "cancelled_by": current_user.email,
                    "reason": {"id": "buyer_cancellation", "descriptor": {"name": cancellation_reason}}
                }
            }
        )
    )
    
    # Send to Beckn gateway
    try:
        response = await send_beckn_request("/cancel", beckn_request)
        return {"message": "Order cancellation initiated", "order_id": order_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beckn cancel failed: {str(e)}"
        )

@router.get("/status/{order_id}", response_model=BecknResponse)
async def get_order_status(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get order status using Beckn protocol."""
    
    # Create Beckn status request
    beckn_request = BecknRequest(
        context=create_beckn_context("status"),
        message=BecknMessage(
            order={"id": order_id}
        )
    )
    
    # Send to Beckn gateway
    try:
        response = await send_beckn_request("/status", beckn_request)
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beckn status failed: {str(e)}"
        )

@router.get("/registry")
async def get_beckn_registry():
    """Get Beckn registry information."""
    
    return {
        "subscriber_id": settings.BECKN_SUBSCRIBER_ID,
        "subscriber_url": settings.BECKN_SUBSCRIBER_URL,
        "domain": "energy",
        "supported_actions": [
            "search", "select", "init", "confirm", "status", "track", "cancel", "update"
        ],
        "api_version": "1.0.0",
        "registry_url": settings.BECKN_GATEWAY_URL,
        "status": "active"
    }

@router.post("/webhook")
async def beckn_webhook(
    webhook_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Handle Beckn protocol webhooks."""
    
    # In production, this would handle various Beckn callbacks
    # For demo, just log and acknowledge
    
    action = webhook_data.get("context", {}).get("action", "unknown")
    order_id = webhook_data.get("message", {}).get("order", {}).get("id")
    
    # Handle different webhook types
    if action == "on_status":
        # Update order status in database
        pass
    elif action == "on_track":
        # Update delivery tracking info
        pass
    elif action == "on_cancel":
        # Handle order cancellation
        pass
    
    return {
        "message": "Webhook received",
        "action": action,
        "order_id": order_id,
        "timestamp": datetime.utcnow()
    }
