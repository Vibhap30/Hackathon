"""
API Router V1
PowerShare Energy Trading Platform
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users, 
    energy_trading,
    iot_devices,
    communities,
    ai_agents,
    beckn_protocol,
    blockchain,
    analytics
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(energy_trading.router, prefix="/energy", tags=["energy-trading"])
api_router.include_router(iot_devices.router, prefix="/iot", tags=["iot-devices"])
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])
api_router.include_router(ai_agents.router, prefix="/ai", tags=["ai-agents"])
api_router.include_router(beckn_protocol.router, prefix="/beckn", tags=["beckn-protocol"])
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
