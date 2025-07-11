"""
AI Agents API Endpoints
PowerShare Energy Trading Platform
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import asyncio
import json
import httpx
from enum import Enum

from langchain_openai import ChatOpenAI

from app.core.database import get_db
from app.models.user import User
from app.models.energy_transaction import EnergyTransaction
from app.core.config import settings
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.agent_manager import AgentOrchestrator, AgentType, AgentStatus
from app.services.energy_matching import EnergyMatchingEngine, LocalityEnergyMapper
from app.services.recommendation_engine import PersonalizedRecommendationEngine

router = APIRouter()

# Initialize services using Azure OpenAI env variables
import os
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
llm = None
if azure_api_key and azure_endpoint and azure_deployment:
    llm = ChatOpenAI(
        model=azure_deployment,
        api_key=azure_api_key,
        base_url=azure_endpoint,
        api_version=azure_api_version
    )
agent_orchestrator = AgentOrchestrator(llm) if llm else None
matching_engine = EnergyMatchingEngine()
locality_mapper = LocalityEnergyMapper()

# Pydantic models
class TradingRecommendationRequest(BaseModel):
    energy_amount: float
    max_price: Optional[float] = None
    preferred_sellers: Optional[List[int]] = None
    urgency: str = "normal"  # low, normal, high
    location: Optional[Dict[str, float]] = None

class TradingRecommendation(BaseModel):
    action: str  # buy, sell, hold
    suggested_price: float
    suggested_amount: float
    confidence_score: float
    reasoning: str
    market_conditions: Dict[str, Any]
    alternative_options: List[Dict[str, Any]]

class AutoTradingConfig(BaseModel):
    enabled: bool
    max_buy_price: Optional[float] = None
    min_sell_price: Optional[float] = None
    max_transaction_amount: Optional[float] = None
    auto_sell_threshold: Optional[float] = None  # % of capacity to trigger auto-sell
    auto_buy_threshold: Optional[float] = None   # % of capacity to trigger auto-buy

class AgentQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    preferred_agents: Optional[List[str]] = None

class LocalityMapRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = 50

# Define missing enums and classes
class MatchingPriority(str, Enum):
    COST_OPTIMIZATION = "cost_optimization"
    TIME_OPTIMIZATION = "time_optimization"
    PROXIMITY = "proximity"
    RELIABILITY = "reliability"

class EnergyRequest(BaseModel):
    amount: float
    max_price: Optional[float] = None
    location: Optional[Dict[str, float]] = None
    urgency: Optional[str] = "normal"
    priority: Optional[MatchingPriority] = MatchingPriority.COST_OPTIMIZATION
    preferred_sellers: Optional[List[int]] = None

class PredictionRequest(BaseModel):
    prediction_type: str  # "price", "demand", "supply", "weather"
    timeframe: Optional[str] = "24h"  # "1h", "24h", "7d", "30d"
    location: Optional[Dict[str, float]] = None
    parameters: Optional[Dict[str, Any]] = None

class EnergyPrediction(BaseModel):
    prediction_type: str
    timeframe: str
    timestamp: datetime
    predictions: List[Dict[str, Any]]
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@router.get("/agents", response_model=List[Dict[str, Any]])
async def get_all_agents():
    """Get information about all available AI agents"""
    if not agent_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI agents service not available"
        )
    
    try:
        agents = await agent_orchestrator.get_all_agents()
        return agents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving agents: {str(e)}"
        )


@router.post("/agents/query", response_model=Dict[str, Any])
async def query_agents(
    query_request: AgentQuery
):
    """Query AI agents with natural language"""
    if not agent_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI agents service not available"
        )
    
    try:
        # Add user context to the query
        context = query_request.context or {}
        context['user_data'] = {
            'user_id': 'demo_user',
            'location': 'default_location',
            'energy_profile': {},
            'preferences': {}
        }
        
        response = await agent_orchestrator.process_user_query(
            query_request.query,
            context
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/recommendations/energy-trading")
async def get_energy_trading_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized energy trading recommendations"""
    if not agent_orchestrator:
        # Fallback to basic recommendations
        return {
            "recommendations": [
                {
                    "type": "market_opportunity",
                    "title": "Sell surplus solar energy",
                    "description": "Current market prices are favorable for selling",
                    "confidence": 0.75,
                    "action": "sell",
                    "amount": 15.5,
                    "price": 0.28
                }
            ],
            "market_summary": {
                "current_price": 0.267,
                "trend": "stable",
                "volume": "normal"
            }
        }
    
    try:
        # Get user's energy data
        user_data = {
            'user_id': current_user.id,
            'consumption_history': [],  # Would fetch from IoT devices
            'production_history': [],   # Would fetch from IoT devices
            'trading_history': []       # Would fetch from transactions
        }
        
        # Get current market data (mock for demo)
        market_data = {
            'recent_prices': [0.25, 0.26, 0.267, 0.27, 0.268],
            'recent_volumes': [1000, 1200, 1100, 1150, 1080]
        }
        
        # Query trading agent
        context = {
            'user_data': user_data,
            'market_data': market_data
        }
        
        response = await agent_orchestrator.process_user_query(
            "What are the best energy trading opportunities for me right now?",
            context
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/locality-map")
async def get_locality_energy_map(
    request: LocalityMapRequest,
    current_user: User = Depends(get_current_user)
):
    """Get energy map for a specific locality"""
    try:
        energy_map = await locality_mapper.generate_locality_map(
            center_location=(request.latitude, request.longitude),
            radius_km=request.radius_km
        )
        
        return energy_map
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating locality map: {str(e)}"
        )


@router.post("/bid-matching")
async def find_energy_matches(
    request: TradingRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Find optimal energy bid matches"""
    try:
        from app.services.energy_matching import EnergyRequest, EnergyOffer, MatchingPriority, EnergySource
        
        # Create energy request from user input
        energy_request = EnergyRequest(
            id=f"req_{current_user.id}_{datetime.utcnow().timestamp()}",
            buyer_id=str(current_user.id),
            amount_kwh=request.energy_amount,
            max_price_per_kwh=request.max_price or 0.30,
            location=request.location or (37.7749, -122.4194),  # Default to SF
            needed_by=datetime.utcnow() + timedelta(hours=24),
            priority=MatchingPriority.BALANCED,
            preferences={
                'max_distance_km': 100,
                'min_renewable_percentage': 0.5,
                'single_supplier_preference': False
            },
            urgency_factor=0.5 if request.urgency == "normal" else 0.8 if request.urgency == "high" else 0.3,
            quality_requirements={}
        )
        
        # Mock available offers (in real implementation, fetch from database)
        mock_offers = [
            EnergyOffer(
                id="offer_001",
                seller_id="seller_123",
                amount_kwh=50.0,
                price_per_kwh=0.25,
                energy_source=EnergySource.SOLAR,
                location=(37.7849, -122.4094),
                availability_start=datetime.utcnow(),
                availability_end=datetime.utcnow() + timedelta(hours=48),
                carbon_intensity=0.05,
                reliability_score=0.92,
                quality_metrics={"frequency_stability": 0.98, "voltage_quality": 0.95},
                seller_reputation=4.7,
                renewable_percentage=1.0
            ),
            EnergyOffer(
                id="offer_002",
                seller_id="seller_456",
                amount_kwh=30.0,
                price_per_kwh=0.28,
                energy_source=EnergySource.WIND,
                location=(37.7649, -122.4294),
                availability_start=datetime.utcnow(),
                availability_end=datetime.utcnow() + timedelta(hours=24),
                carbon_intensity=0.03,
                reliability_score=0.88,
                quality_metrics={"frequency_stability": 0.96, "voltage_quality": 0.93},
                seller_reputation=4.5,
                renewable_percentage=1.0
            )
        ]
        
        # Find optimal matches
        matches = await matching_engine.find_optimal_matches([energy_request], mock_offers)
        
        # Format response
        match_results = []
        for match in matches:
            match_results.append({
                "offer_id": match.offer_id,
                "amount_kwh": match.matched_amount,
                "price_per_kwh": match.final_price,
                "total_cost": match.matched_amount * match.final_price,
                "distance_km": match.distance_km,
                "carbon_impact": match.carbon_impact,
                "delivery_time_hours": match.estimated_delivery_time.total_seconds() / 3600,
                "matching_score": match.matching_score,
                "confidence": match.confidence_score,
                "reasoning": match.reasoning
            })
        
        return {
            "request_id": energy_request.id,
            "matches_found": len(match_results),
            "matches": match_results,
            "total_matched_amount": sum(m["amount_kwh"] for m in match_results),
            "average_price": sum(m["price_per_kwh"] * m["amount_kwh"] for m in match_results) / sum(m["amount_kwh"] for m in match_results) if match_results else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding matches: {str(e)}"
        )


@router.get("/agents/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get status of a specific agent"""
    if not agent_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI agents service not available"
        )
    
    try:
        agents = await agent_orchestrator.get_all_agents()
        agent = next((a for a in agents if a['id'] == agent_id), None)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        return agent
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving agent status: {str(e)}"
        )


@router.post("/demo/prosumer-scenario")
async def demo_prosumer_scenario(current_user: User = Depends(get_current_user)):
    """Demo scenario for prosumer with solar panels"""
    try:
        # Mock prosumer profile
        prosumer_data = {
            "user_type": "prosumer",
            "solar_capacity": 8.5,  # kW
            "current_production": 6.2,  # kW
            "current_consumption": 3.1,  # kW
            "surplus_available": 3.1,  # kW
            "battery_capacity": 13.5,  # kWh
            "battery_current": 8.7,  # kWh
            "location": {"lat": 37.7749, "lng": -122.4194},
            "preferences": {
                "sell_surplus": True,
                "min_sell_price": 0.22,
                "carbon_conscious": True,
                "local_trading_preference": True
            }
        }
        
        # Generate comprehensive recommendations
        recommendations = {
            "immediate_opportunities": [
                {
                    "type": "sell_surplus",
                    "title": "Sell Current Solar Surplus",
                    "description": "3.1 kW surplus available at premium rates",
                    "action": "Create sell order for 3.1 kWh",
                    "estimated_price": 0.28,
                    "estimated_revenue": 0.87,
                    "confidence": 0.92,
                    "reasoning": "High demand period with favorable pricing"
                },
                {
                    "type": "battery_optimization",
                    "title": "Optimize Battery Storage",
                    "description": "Store energy for evening peak pricing",
                    "action": "Reserve 2 kWh for evening sales",
                    "estimated_value": 1.20,
                    "confidence": 0.78,
                    "reasoning": "Evening prices typically 15-20% higher"
                }
            ],
            "market_insights": {
                "current_price": 0.267,
                "trend": "increasing",
                "peak_hours": "6-9 PM",
                "best_sell_time": "7:30 PM",
                "local_demand": "high",
                "renewable_premium": "+8%"
            },
            "energy_map": await locality_mapper.generate_locality_map(
                (prosumer_data["location"]["lat"], prosumer_data["location"]["lng"]),
                25
            )
        }
        
        return {
            "scenario": "prosumer_solar",
            "user_profile": prosumer_data,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prosumer scenario: {str(e)}"
        )


@router.post("/demo/consumer-scenario")
async def demo_consumer_scenario(current_user: User = Depends(get_current_user)):
    """Demo scenario for energy consumer"""
    try:
        # Mock consumer profile
        consumer_data = {
            "user_type": "consumer",
            "monthly_consumption": 450,  # kWh
            "current_demand": 4.2,  # kW
            "peak_demand": 7.8,  # kW
            "location": {"lat": 37.7849, "lng": -122.4094},
            "preferences": {
                "renewable_preference": 0.8,
                "cost_priority": "high",
                "reliability_requirement": "medium",
                "max_distance": 50  # km
            }
        }
        
        # Find best energy sources
        energy_request = EnergyRequest(
            id=f"demo_consumer_{current_user.id}",
            buyer_id=str(current_user.id),
            amount_kwh=4.2,
            max_price_per_kwh=0.30,
            location=(consumer_data["location"]["lat"], consumer_data["location"]["lng"]),
            needed_by=datetime.utcnow() + timedelta(hours=2),
            priority=MatchingPriority.COST_OPTIMIZATION,
            preferences=consumer_data["preferences"],
            urgency_factor=0.6,
            quality_requirements={}
        )
        
        # Mock offers
        from app.services.energy_matching import EnergyOffer, EnergySource
        mock_offers = [
            EnergyOffer(
                id="solar_coop_001",
                seller_id="solar_cooperative",
                amount_kwh=15.0,
                price_per_kwh=0.24,
                energy_source=EnergySource.SOLAR,
                location=(37.7849, -122.4094),
                availability_start=datetime.utcnow(),
                availability_end=datetime.utcnow() + timedelta(hours=6),
                carbon_intensity=0.02,
                reliability_score=0.94,
                quality_metrics={"frequency_stability": 0.98},
                seller_reputation=4.8,
                renewable_percentage=1.0
            ),
            EnergyOffer(
                id="local_grid_001",
                seller_id="local_utility",
                amount_kwh=100.0,
                price_per_kwh=0.29,
                energy_source=EnergySource.GRID,
                location=(37.7749, -122.4194),
                availability_start=datetime.utcnow(),
                availability_end=datetime.utcnow() + timedelta(hours=24),
                carbon_intensity=0.45,
                reliability_score=0.99,
                quality_metrics={"frequency_stability": 0.995},
                seller_reputation=4.2,
                renewable_percentage=0.35
            )
        ]
        
        matches = await matching_engine.find_optimal_matches([energy_request], mock_offers)
        
        recommendations = {
            "best_matches": [
                {
                    "source": match.offer_id,
                    "amount": match.matched_amount,
                    "price": match.final_price,
                    "savings": (0.30 - match.final_price) * match.matched_amount,
                    "carbon_benefit": match.carbon_impact,
                    "reasoning": match.reasoning
                } for match in matches
            ],
            "cost_analysis": {
                "total_cost": sum(m.matched_amount * m.final_price for m in matches),
                "market_average": 0.285,
                "savings_vs_market": sum((0.285 - m.final_price) * m.matched_amount for m in matches),
                "carbon_footprint": sum(m.carbon_impact for m in matches)
            },
            "recommendations": [
                "Choose solar cooperative for 70% renewable energy at lower cost",
                "Schedule high-consumption activities during low-price periods",
                "Consider demand response programs for additional savings"
            ]
        }
        
        return {
            "scenario": "consumer_optimization",
            "user_profile": consumer_data,
            "energy_matches": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating consumer scenario: {str(e)}"
        )
    timeframe: str = "1h"  # 1h, 6h, 24h, 7d
    location: Optional[str] = None

class EnergyPrediction(BaseModel):
    prediction_type: str
    timeframe: str
    predictions: List[Dict[str, Any]]
    confidence_score: float
    factors_considered: List[str]
    generated_at: datetime

class OptimizationRequest(BaseModel):
    optimization_type: str  # consumption, production, storage, trading
    constraints: Dict[str, Any] = {}
    objectives: List[str] = ["cost_minimization"]

class OptimizationResult(BaseModel):
    optimization_type: str
    recommendations: List[Dict[str, Any]]
    expected_savings: float
    implementation_complexity: str
    confidence_score: float

class EnergyOptimizationRequest(BaseModel):
    optimization_goals: List[str] = ["cost_minimization"]
    location: Optional[Dict[str, float]] = None
    preferences: Optional[Dict[str, Any]] = None

class AgentServiceResponse(BaseModel):
    success: bool
    agent_id: str
    user_id: str
    status: str
    data: Dict[str, Any] = {}
    error: Optional[str] = None
    timestamp: str

# Mock AI Agent Functions (in production, these would call actual AI services)
async def get_trading_recommendation_ai(
    user: User, 
    request: TradingRecommendationRequest,
    db: AsyncSession
) -> TradingRecommendation:
    """Generate AI-powered trading recommendations."""
    
    # Get user's current energy status
    energy_ratio = user.current_energy / max(user.energy_capacity, 1)
    
    # Simulate market analysis
    market_conditions = {
        "average_price": 0.25,
        "supply_demand_ratio": 1.2,
        "volatility": "low",
        "peak_hours": False
    }
    
    # Generate recommendation based on user's energy status
    if energy_ratio > 0.8:  # High energy, recommend selling
        action = "sell"
        suggested_price = market_conditions["average_price"] * 1.05  # Slightly above market
        suggested_amount = min(request.energy_amount, user.current_energy * 0.3)
        reasoning = "High energy levels detected. Market conditions favorable for selling."
        confidence_score = 0.85
    
    elif energy_ratio < 0.2:  # Low energy, recommend buying
        action = "buy"
        suggested_price = market_conditions["average_price"] * 0.95  # Slightly below market
        suggested_amount = min(request.energy_amount, user.energy_capacity - user.current_energy)
        reasoning = "Low energy levels detected. Recommend purchasing to meet potential demand."
        confidence_score = 0.78
    
    else:  # Moderate energy, hold or small trades
        action = "hold"
        suggested_price = market_conditions["average_price"]
        suggested_amount = request.energy_amount * 0.1
        reasoning = "Energy levels optimal. Consider small opportunistic trades only."
        confidence_score = 0.65
    
    alternative_options = [
        {
            "action": "wait",
            "reason": "Market volatility expected to decrease in 2 hours",
            "potential_savings": 0.02
        },
        {
            "action": "partial_trade",
            "reason": "Split transaction to minimize risk",
            "suggested_split": [0.6, 0.4]
        }
    ]
    
    return TradingRecommendation(
        action=action,
        suggested_price=suggested_price,
        suggested_amount=suggested_amount,
        confidence_score=confidence_score,
        reasoning=reasoning,
        market_conditions=market_conditions,
        alternative_options=alternative_options
    )

async def generate_energy_predictions(request: PredictionRequest) -> EnergyPrediction:
    """Generate AI-powered energy predictions."""
    
    predictions = []
    
    if request.prediction_type == "price":
        # Simulate price predictions
        base_price = 0.25
        for i in range(24 if request.timeframe == "24h" else 6):
            hour_price = base_price * (1 + (i % 6 - 3) * 0.1)  # Simulate daily pattern
            predictions.append({
                "time": f"+{i}h",
                "value": round(hour_price, 3),
                "unit": "$/kWh"
            })
    
    elif request.prediction_type == "demand":
        # Simulate demand predictions
        for i in range(24 if request.timeframe == "24h" else 6):
            demand = 100 + (i % 12 - 6) * 20  # Simulate daily demand pattern
            predictions.append({
                "time": f"+{i}h",
                "value": max(0, demand),
                "unit": "kWh"
            })
    
    elif request.prediction_type == "weather":
        # Simulate weather impact predictions
        weather_conditions = ["sunny", "partly_cloudy", "cloudy", "rainy"]
        for i in range(24 if request.timeframe == "24h" else 6):
            solar_efficiency = [0.9, 0.7, 0.4, 0.1][i % 4]
            predictions.append({
                "time": f"+{i}h",
                "condition": weather_conditions[i % 4],
                "solar_efficiency": solar_efficiency,
                "wind_speed": f"{5 + i % 10} mph"
            })
    
    return EnergyPrediction(
        prediction_type=request.prediction_type,
        timeframe=request.timeframe,
        predictions=predictions,
        confidence_score=0.72,
        factors_considered=["historical_data", "weather_forecast", "market_trends", "seasonal_patterns"],
        generated_at=datetime.utcnow()
    )

async def optimize_energy_usage(
    user: User, 
    request: OptimizationRequest,
    db: AsyncSession
) -> OptimizationResult:
    """Generate AI-powered optimization recommendations."""
    
    recommendations = []
    
    if request.optimization_type == "consumption":
        recommendations = [
            {
                "action": "shift_load",
                "description": "Move high-consumption activities to off-peak hours (11 PM - 6 AM)",
                "potential_savings": 15.5,
                "priority": "high"
            },
            {
                "action": "device_scheduling",
                "description": "Schedule EV charging during peak solar production hours",
                "potential_savings": 8.2,
                "priority": "medium"
            }
        ]
        expected_savings = 23.7
    
    elif request.optimization_type == "trading":
        recommendations = [
            {
                "action": "sell_excess",
                "description": "Sell excess energy during peak demand hours (6-9 PM)",
                "potential_earnings": 12.3,
                "priority": "high"
            },
            {
                "action": "buy_low",
                "description": "Purchase energy during low-price periods for storage",
                "potential_savings": 5.8,
                "priority": "medium"
            }
        ]
        expected_savings = 18.1
    
    else:  # Default generic optimization
        recommendations = [
            {
                "action": "balance_portfolio",
                "description": "Optimize energy portfolio for current market conditions",
                "potential_savings": 10.0,
                "priority": "medium"
            }
        ]
        expected_savings = 10.0
    
    return OptimizationResult(
        optimization_type=request.optimization_type,
        recommendations=recommendations,
        expected_savings=expected_savings,
        implementation_complexity="medium",
        confidence_score=0.81
    )

# AI Agents Service Client
class AIAgentsClient:
    def __init__(self):
        self.base_url = getattr(settings, 'AI_AGENTS_URL', 'http://ai-agents:8005')
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def request_energy_trading_analysis(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Request energy trading analysis from AI agents service"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/energy-trading/process",
                json={
                    "user_id": user_id,
                    **request_data
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"AI service error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to connect to AI service: {str(e)}"}
    
    async def request_optimization_analysis(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Request comprehensive energy optimization analysis"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/energy-optimization/analyze",
                json={
                    "user_id": user_id,
                    **request_data
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"AI service error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to connect to AI service: {str(e)}"}
    
    async def get_user_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get AI recommendations for user"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/energy-trading/recommendations/{user_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"AI service error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to connect to AI service: {str(e)}"}
    
    async def get_optimization_results(self, user_id: str) -> Dict[str, Any]:
        """Get optimization results for user"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/energy-optimization/results/{user_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"AI service error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to connect to AI service: {str(e)}"}
    
    async def get_action_items(self, user_id: str) -> Dict[str, Any]:
        """Get AI-generated action items for user"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/energy-optimization/action-items/{user_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"AI service error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to connect to AI service: {str(e)}"}

# Initialize AI agents client
ai_agents_client = AIAgentsClient()

# Initialize recommendation engine
recommendation_engine = None

def get_recommendation_engine(db: AsyncSession = Depends(get_db)):
    global recommendation_engine
    if recommendation_engine is None:
        recommendation_engine = PersonalizedRecommendationEngine(db)
    return recommendation_engine

# API Endpoints
@router.post("/recommendations/trading", response_model=TradingRecommendation)
async def get_trading_recommendation(
    request: TradingRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered trading recommendations."""
    
    if request.energy_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Energy amount must be positive"
        )
    
    if request.urgency not in ["low", "normal", "high"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Urgency must be one of: low, normal, high"
        )
    
    recommendation = await get_trading_recommendation_ai(current_user, request, db)
    return recommendation

@router.post("/predictions", response_model=EnergyPrediction)
async def get_energy_predictions(request: PredictionRequest):
    """Get AI-powered energy predictions."""
    
    valid_types = ["price", "demand", "supply", "weather"]
    if request.prediction_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prediction type. Must be one of: {', '.join(valid_types)}"
        )
    
    valid_timeframes = ["1h", "6h", "24h", "7d"]
    if request.timeframe not in valid_timeframes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"
        )
    
    prediction = await generate_energy_predictions(request)
    return prediction

@router.post("/optimization", response_model=OptimizationResult)
async def get_optimization_recommendations(
    request: OptimizationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered optimization recommendations."""
    
    valid_types = ["consumption", "production", "storage", "trading"]
    if request.optimization_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid optimization type. Must be one of: {', '.join(valid_types)}"
        )
    
    optimization = await optimize_energy_usage(current_user, request, db)
    return optimization

@router.get("/auto-trading/config", response_model=AutoTradingConfig)
async def get_auto_trading_config(
    current_user: User = Depends(get_current_user)
):
    """Get user's auto-trading configuration."""
    # In production, this would be stored in database
    # For demo, return default config
    return AutoTradingConfig(
        enabled=False,
        max_buy_price=0.30,
        min_sell_price=0.20,
        max_transaction_amount=50.0,
        auto_sell_threshold=80.0,
        auto_buy_threshold=20.0
    )

@router.put("/auto-trading/config")
async def update_auto_trading_config(
    config: AutoTradingConfig,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's auto-trading configuration."""
    
    # Validate configuration
    if config.max_buy_price and config.max_buy_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max buy price must be positive"
        )
    
    if config.min_sell_price and config.min_sell_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Min sell price must be positive"
        )
    
    if (config.max_buy_price and config.min_sell_price and 
        config.max_buy_price <= config.min_sell_price):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max buy price must be greater than min sell price"
        )
    
    # In production, save to database
    # For demo, just return success
    return {
        "message": "Auto-trading configuration updated successfully",
        "config": config
    }

@router.post("/auto-trading/execute")
async def execute_auto_trading(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger auto-trading execution for current user."""
    
    # In production, this would trigger the LangGraph workflow
    # For demo, simulate the process
    
    def simulate_auto_trading():
        """Background task to simulate auto-trading."""
        import time
        time.sleep(2)  # Simulate processing time
        # Would call the actual AI agent here
    
    background_tasks.add_task(simulate_auto_trading)
    
    return {
        "message": "Auto-trading execution initiated",
        "status": "processing",
        "estimated_completion": "2-5 minutes"
    }

@router.get("/analytics/performance")
async def get_ai_performance_analytics(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI agent performance analytics."""
    
    # In production, this would analyze actual AI predictions vs outcomes
    # For demo, return simulated metrics
    
    return {
        "prediction_accuracy": {
            "price_predictions": 78.5,
            "demand_predictions": 82.1,
            "weather_predictions": 89.3
        },
        "trading_performance": {
            "successful_trades": 156,
            "total_trades": 180,
            "success_rate": 86.7,
            "average_profit_margin": 12.3
        },
        "optimization_impact": {
            "energy_savings": 23.4,
            "cost_savings": 156.78,
            "efficiency_improvement": 15.2
        },
        "period": f"Last {days} days",
        "generated_at": datetime.utcnow()
    }

# AI Agents Service Integration Endpoints

@router.post("/energy-trading/analyze")
async def request_energy_trading_analysis(
    request: TradingRecommendationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request AI-powered energy trading analysis"""
    try:
        # Get user's location and preferences
        user_location = {
            "lat": getattr(current_user, 'latitude', 40.7128),
            "lng": getattr(current_user, 'longitude', -74.0060)
        }
        
        # Get current market data
        # In production, this would query actual market offers
        market_offers = await _get_current_market_offers(db)
        
        # Prepare request for AI service
        ai_request_data = {
            "energy_amount": request.energy_amount,
            "energy_type": "any",
            "max_price": request.max_price or 0.25,
            "location": user_location,
            "preferences": {
                "urgency": request.urgency,
                "preferred_sellers": request.preferred_sellers or []
            },
            "market_data": market_offers[:20]  # Send top 20 offers
        }
        
        # Request analysis from AI agents service
        result = await ai_agents_client.request_energy_trading_analysis(
            str(current_user.id), 
            ai_request_data
        )
        
        return {
            "success": result.get("success", False),
            "message": "Energy trading analysis requested successfully" if result.get("success") else "Analysis request failed",
            "analysis_id": result.get("data", {}).get("transaction_id"),
            "status": result.get("status", "unknown"),
            "estimated_completion": "2-5 minutes"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request trading analysis: {str(e)}"
        )

@router.post("/optimization/analyze")
async def request_energy_optimization(
    request: EnergyOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request comprehensive energy optimization analysis"""
    try:
        # Get user's location
        user_location = request.location or {
            "lat": getattr(current_user, 'latitude', 40.7128),
            "lng": getattr(current_user, 'longitude', -74.0060)
        }
        
        # Prepare optimization request
        optimization_data = {
            "optimization_goals": request.optimization_goals,
            "location": user_location,
            "preferences": request.preferences or {}
        }
        
        # Request comprehensive optimization analysis
        result = await ai_agents_client.request_optimization_analysis(
            str(current_user.id),
            optimization_data
        )
        
        return {
            "success": result.get("success", False),
            "message": "Energy optimization analysis started" if result.get("success") else "Analysis request failed",
            "analysis_id": result.get("data", {}).get("generated_at"),
            "status": result.get("status", "unknown"),
            "estimated_completion": "3-7 minutes"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request optimization analysis: {str(e)}"
        )

@router.get("/recommendations")
async def get_ai_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Get current AI recommendations for the user"""
    try:
        result = await ai_agents_client.get_user_recommendations(str(current_user.id))
        if result.get("success", False):
            return {
                "success": result.get("success", False),
                "recommendations": result.get("recommendations", []),
                "cached": result.get("cached", False),
                "timestamp": result.get("timestamp"),
                "message": result.get("message", "")
            }
        else:
            # Fallback: return dummy recommendations
            return {
                "success": True,
                "recommendations": [
                    {
                        "id": "rec-1",
                        "type": "energy_saving",
                        "title": "Install Smart Thermostat",
                        "description": "Installing a smart thermostat can help optimize your energy usage.",
                        "priority": "high",
                        "confidence_score": 0.92,
                        "potential_savings": 120.0
                    },
                    {
                        "id": "rec-2",
                        "type": "solar_upgrade",
                        "title": "Upgrade Solar Panel Capacity",
                        "description": "Consider upgrading your solar panel capacity for increased savings.",
                        "priority": "medium",
                        "confidence_score": 0.85,
                        "potential_savings": 300.0
                    }
                ],
                "cached": False,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "(Demo) Dummy recommendations returned."
            }
    except Exception as e:
        # Fallback: return dummy recommendations
        return {
            "success": True,
            "recommendations": [
                {
                    "id": "rec-1",
                    "type": "energy_saving",
                    "title": "Install Smart Thermostat",
                    "description": "Installing a smart thermostat can help optimize your energy usage.",
                    "priority": "high",
                    "confidence_score": 0.92,
                    "potential_savings": 120.0
                },
                {
                    "id": "rec-2",
                    "type": "solar_upgrade",
                    "title": "Upgrade Solar Panel Capacity",
                    "description": "Consider upgrading your solar panel capacity for increased savings.",
                    "priority": "medium",
                    "confidence_score": 0.85,
                    "potential_savings": 300.0
                }
            ],
            "cached": False,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "(Demo) Dummy recommendations returned due to error."
        }

@router.get("/optimization/results")
async def get_optimization_results(
    current_user: User = Depends(get_current_user)
):
    """Get latest optimization analysis results"""
    try:
        result = await ai_agents_client.get_optimization_results(str(current_user.id))
        if result.get("success", False):
            return {
                "success": result.get("success", False),
                "results": result.get("results"),
                "cached": result.get("cached", False),
                "timestamp": result.get("timestamp"),
                "message": result.get("message", "")
            }
        else:
            # Fallback: return dummy optimization results
            return {
                "success": True,
                "results": {
                    "total_savings": 420.0,
                    "optimized_load_profile": [
                        {"hour": h, "load_kwh": round(1.5 + 0.5 * (h % 4), 2)} for h in range(24)
                    ],
                    "recommendations": [
                        "Shift heavy appliance usage to off-peak hours.",
                        "Charge EV during midday solar surplus."
                    ]
                },
                "cached": False,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "(Demo) Dummy optimization results returned."
            }
    except Exception as e:
        # Fallback: return dummy optimization results
        return {
            "success": True,
            "results": {
                "total_savings": 420.0,
                "optimized_load_profile": [
                    {"hour": h, "load_kwh": round(1.5 + 0.5 * (h % 4), 2)} for h in range(24)
                ],
                "recommendations": [
                    "Shift heavy appliance usage to off-peak hours.",
                    "Charge EV during midday solar surplus."
                ]
            },
            "cached": False,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "(Demo) Dummy optimization results returned due to error."
        }

@router.get("/action-items")
async def get_ai_action_items(
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated action items for the user"""
    try:
        result = await ai_agents_client.get_action_items(str(current_user.id))
        if result.get("success", False):
            return {
                "success": result.get("success", False),
                "action_items": result.get("action_items", []),
                "count": result.get("count", 0),
                "generated_at": result.get("generated_at"),
                "timestamp": result.get("timestamp"),
                "message": result.get("message", "")
            }
        else:
            # Fallback: return dummy action items
            return {
                "success": True,
                "action_items": [
                    {
                        "id": "action-1",
                        "title": "Replace old appliances",
                        "description": "Upgrade to energy-efficient appliances to reduce consumption.",
                        "status": "pending",
                        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
                    },
                    {
                        "id": "action-2",
                        "title": "Schedule HVAC maintenance",
                        "description": "Regular maintenance improves efficiency and lowers costs.",
                        "status": "pending",
                        "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat()
                    }
                ],
                "count": 2,
                "generated_at": datetime.utcnow().isoformat(),
                "timestamp": datetime.utcnow().isoformat(),
                "message": "(Demo) Dummy action items returned."
            }
    except Exception as e:
        # Fallback: return dummy action items
        return {
            "success": True,
            "action_items": [
                {
                    "id": "action-1",
                    "title": "Replace old appliances",
                    "description": "Upgrade to energy-efficient appliances to reduce consumption.",
                    "status": "pending",
                    "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
                },
                {
                    "id": "action-2",
                    "title": "Schedule HVAC maintenance",
                    "description": "Regular maintenance improves efficiency and lowers costs.",
                    "status": "pending",
                    "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat()
                }
            ],
            "count": 2,
            "generated_at": datetime.utcnow().isoformat(),
            "timestamp": datetime.utcnow().isoformat(),
            "message": "(Demo) Dummy action items returned due to error."
        }

@router.post("/action-items/{action_id}/complete")
async def complete_action_item(
    action_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark an AI action item as completed"""
    try:
        # In production, this would update the action item status
        # For now, return success response
        
        return {
            "success": True,
            "message": f"Action item {action_id} marked as completed",
            "action_id": action_id,
            "completed_at": datetime.utcnow().isoformat(),
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete action item: {str(e)}"
        )

# Demo Endpoints

@router.get("/demo/prosumer-recommendations")
async def get_prosumer_demo_recommendations(
    current_user: User = Depends(get_current_user),
    rec_engine: PersonalizedRecommendationEngine = Depends(get_recommendation_engine)
):
    """Get demo recommendations specifically for prosumer scenario"""
    try:
        recommendations = await rec_engine.get_demo_recommendations_prosumer(current_user.id)
        
        return {
            "user_type": "prosumer",
            "user_id": current_user.id,
            "recommendations": [
                {
                    "id": rec.id,
                    "type": rec.type,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "confidence_score": rec.confidence_score,
                    "potential_savings": rec.potential_savings,
                    "implementation_effort": rec.implementation_effort,
                    "timeline": rec.timeline,
                    "reasoning": rec.reasoning,
                    "action_items": rec.action_items,
                    "data": rec.data,
                    "expires_at": rec.expires_at.isoformat()
                }
                for rec in recommendations
            ],
            "total_potential_savings": sum(rec.potential_savings for rec in recommendations),
            "high_priority_count": len([rec for rec in recommendations if rec.priority == "high"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prosumer recommendations: {str(e)}"
        )

@router.get("/demo/consumer-recommendations")
async def get_consumer_demo_recommendations(
    current_user: User = Depends(get_current_user),
    rec_engine: PersonalizedRecommendationEngine = Depends(get_recommendation_engine)
):
    """Get demo recommendations specifically for consumer scenario"""
    try:
        recommendations = await rec_engine.get_demo_recommendations_consumer(current_user.id)
        
        return {
            "user_type": "consumer", 
            "user_id": current_user.id,
            "recommendations": [
                {
                    "id": rec.id,
                    "type": rec.type,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "confidence_score": rec.confidence_score,
                    "potential_savings": rec.potential_savings,
                    "implementation_effort": rec.implementation_effort,
                    "timeline": rec.timeline,
                    "reasoning": rec.reasoning,
                    "action_items": rec.action_items,
                    "data": rec.data,
                    "expires_at": rec.expires_at.isoformat()
                }
                for rec in recommendations
            ],
            "total_potential_savings": sum(rec.potential_savings for rec in recommendations),
            "high_priority_count": len([rec for rec in recommendations if rec.priority == "high"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get consumer recommendations: {str(e)}"
        )

@router.post("/demo/personalized-recommendations")
async def get_personalized_recommendations(
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    rec_engine: PersonalizedRecommendationEngine = Depends(get_recommendation_engine)
):
    """Get comprehensive personalized recommendations for current user"""
    try:
        recommendations = await rec_engine.generate_recommendations(current_user.id, context)
        
        return {
            "user_id": current_user.id,
            "recommendations": [
                {
                    "id": rec.id,
                    "type": rec.type,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "confidence_score": rec.confidence_score,
                    "potential_savings": rec.potential_savings,
                    "implementation_effort": rec.implementation_effort,
                    "timeline": rec.timeline,
                    "reasoning": rec.reasoning,
                    "action_items": rec.action_items,
                    "data": rec.data,
                    "expires_at": rec.expires_at.isoformat()
                }
                for rec in recommendations
            ],
            "summary": {
                "total_recommendations": len(recommendations),
                "total_potential_savings": sum(rec.potential_savings for rec in recommendations),
                "by_priority": {
                    "high": len([rec for rec in recommendations if rec.priority == "high"]),
                    "medium": len([rec for rec in recommendations if rec.priority == "medium"]),
                    "low": len([rec for rec in recommendations if rec.priority == "low"])
                },
                "by_type": {
                    "trading": len([rec for rec in recommendations if rec.type == "trading"]),
                    "optimization": len([rec for rec in recommendations if rec.type == "optimization"]),
                    "community": len([rec for rec in recommendations if rec.type == "community"]),
                    "investment": len([rec for rec in recommendations if rec.type == "investment"])
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate personalized recommendations: {str(e)}"
        )

@router.get("/demo/beckn-integration-showcase")
async def showcase_beckn_integration(
    current_user: User = Depends(get_current_user)
):
    """Showcase Beckn protocol integration capabilities"""
    try:
        # Mock Beckn protocol discovery results
        beckn_networks = [
            {
                "network_id": "beckn_energy_grid_001",
                "network_name": "National Energy Grid",
                "protocol_version": "1.0",
                "offers_available": 1247,
                "avg_price_per_kwh": 0.243,
                "renewable_percentage": 0.78,
                "coverage_area": "Nationwide",
                "reliability_score": 0.96,
                "sample_offers": [
                    {
                        "offer_id": "ng_offer_001",
                        "amount_kwh": 100,
                        "price_per_kwh": 0.235,
                        "energy_source": "solar",
                        "location": "California Solar Farm Network",
                        "available_immediately": True
                    },
                    {
                        "offer_id": "ng_offer_002", 
                        "amount_kwh": 75,
                        "price_per_kwh": 0.251,
                        "energy_source": "wind",
                        "location": "Texas Wind Corridor",
                        "available_immediately": True
                    }
                ]
            },
            {
                "network_id": "beckn_community_mesh_002",
                "network_name": "Community Mesh Network",
                "protocol_version": "1.0",
                "offers_available": 342,
                "avg_price_per_kwh": 0.198,
                "renewable_percentage": 0.92,
                "coverage_area": "Regional Communities", 
                "reliability_score": 0.89,
                "sample_offers": [
                    {
                        "offer_id": "cm_offer_001",
                        "amount_kwh": 25,
                        "price_per_kwh": 0.185,
                        "energy_source": "solar",
                        "location": "LocalSolar Community Co-op",
                        "available_immediately": True
                    }
                ]
            },
            {
                "network_id": "beckn_green_alliance_003",
                "network_name": "Green Energy Alliance",
                "protocol_version": "1.0", 
                "offers_available": 889,
                "avg_price_per_kwh": 0.267,
                "renewable_percentage": 1.0,
                "coverage_area": "Multi-State Alliance",
                "reliability_score": 0.94,
                "sample_offers": [
                    {
                        "offer_id": "ga_offer_001",
                        "amount_kwh": 200,
                        "price_per_kwh": 0.259,
                        "energy_source": "hydro",
                        "location": "Pacific Northwest Hydro",
                        "available_immediately": True
                    }
                ]
            }
        ]
        
        # Calculate potential benefits
        local_platform_avg = 0.275
        beckn_avg = sum(net["avg_price_per_kwh"] for net in beckn_networks) / len(beckn_networks)
        potential_savings = (local_platform_avg - beckn_avg) * 100  # Assuming 100 kWh monthly
        
        return {
            "beckn_protocol_status": "active",
            "connected_networks": len(beckn_networks),
            "total_offers_discovered": sum(net["offers_available"] for net in beckn_networks),
            "networks": beckn_networks,
            "benefits": {
                "average_savings_per_kwh": local_platform_avg - beckn_avg,
                "potential_monthly_savings": potential_savings,
                "additional_renewable_access": "35% more renewable energy options",
                "market_liquidity_increase": "180% more trading opportunities"
            },
            "integration_features": [
                "Cross-network energy discovery",
                "Standardized transaction protocols", 
                "Automated price comparison",
                "Seamless settlement across networks",
                "Unified quality and reliability metrics"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to showcase Beckn integration: {str(e)}"
        )

# Helper functions

async def _get_current_market_offers(db: AsyncSession, limit: int = 50) -> List[Dict[str, Any]]:
    """Get current market offers for AI analysis"""
    try:
        # In production, this would query actual energy offers from database
        # For demo, return simulated offers
        offers = []
        
        for i in range(limit):
            offer = {
                "offer_id": f"offer_{i + 1}",
                "seller_id": f"seller_{(i % 10) + 1}",
                "energy_amount_kwh": 50 + (i % 100),
                "price_per_kwh": 0.08 + (i % 20) * 0.005,
                "energy_type": ["solar", "wind", "grid", "battery"][i % 4],
                "location": {
                    "lat": 40.7128 + (i % 10 - 5) * 0.1,
                    "lng": -74.0060 + (i % 10 - 5) * 0.1
                },
                "available_from": datetime.utcnow().isoformat(),
                "available_until": (datetime.utcnow().replace(hour=23, minute=59)).isoformat(),
                "seller_rating": 4.0 + (i % 10) * 0.1,
                "distance_km": (i % 25) + 1
            }
            offers.append(offer)
        
        return offers
        
    except Exception as e:
        return []
