"""
Enhanced RBAC API Endpoints for PowerShare Platform
===================================================

This module provides FastAPI endpoints with comprehensive role-based access control,
role-specific dashboards, and advanced user management features.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.rbac.models import User, UserRole, Permission, RolePermission
from app.gamification.models import GamificationService, TokenBalance
from app.services.bid_optimizer import BidOptimizer, MarketData, UserProfile, BidType
from app.beckn.beckn_service import BecknEnergyService
from app.quantum.quantum_engine import QuantumDemonstration

router = APIRouter()
security = HTTPBearer()

# Pydantic Models for API
class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserRegistrationRequest(BaseModel):
    username: str
    email: str
    password: str
    role_type: str = Field(..., description="prosumer, consumer, community_manager, grid_operator, regulator")
    profile_data: Dict[str, Any] = {}

class DashboardResponse(BaseModel):
    user_info: Dict[str, Any]
    role_permissions: List[str]
    dashboard_config: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]
    notifications: List[Dict[str, Any]]
    quick_stats: Dict[str, Any]

class BidOptimizationRequest(BaseModel):
    bid_type: str = Field(..., description="buy or sell")
    energy_amount: float
    user_preferences: Dict[str, Any]
    market_conditions: Dict[str, Any]

class EnergySearchRequest(BaseModel):
    energy_type: Optional[str] = None
    location: Dict[str, float] = Field(..., description="lat, lng")
    radius: float = 50.0
    capacity_range: Dict[str, float] = Field(default={"min": 0, "max": 1000})
    price_range: Dict[str, float] = Field(default={"min": 0, "max": 20})
    renewable_min: float = 0.0

class TokenTransferRequest(BaseModel):
    recipient_user_id: str
    token_type: str = Field(..., description="PWC, EC, CT, CC")
    amount: float
    description: str = ""

# Authentication and Authorization
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                    db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
        user_permissions = db.query(Permission.name).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(RolePermission.role_id == current_user.role_id).all()
        
        user_permission_names = [p.name for p in user_permissions]
        
        if permission not in user_permission_names:
            raise HTTPException(
                status_code=403, 
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_checker

def require_role(role_type: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.role_type != role_type:
            raise HTTPException(
                status_code=403, 
                detail=f"Role '{role_type}' required"
            )
        return current_user
    return role_checker

# Dashboard Endpoints
@router.get("/dashboard/prosumer", response_model=DashboardResponse)
async def get_prosumer_dashboard(
    current_user: User = Depends(require_role("prosumer")),
    db: Session = Depends(get_db)
):
    """Get prosumer-specific dashboard data"""
    
    gamification_service = GamificationService(db)
    token_balance = await gamification_service.get_user_token_balance(str(current_user.id))
    
    # Mock energy production data
    energy_stats = {
        "total_generated_today": 45.2,
        "total_generated_month": 1250.8,
        "current_output": 8.5,
        "capacity_utilization": 0.68,
        "energy_sold_today": 32.1,
        "energy_sold_month": 890.5,
        "revenue_today": 166.92,
        "revenue_month": 4625.60,
        "carbon_offset_today": 22.6,
        "carbon_offset_month": 625.4
    }
    
    recent_activities = [
        {
            "id": "1",
            "type": "energy_sold",
            "description": "Sold 15.5 kWh to nearby consumer",
            "amount": 80.60,
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "status": "completed"
        },
        {
            "id": "2",
            "type": "achievement_earned",
            "description": "Earned 'Green Pioneer' achievement",
            "tokens_earned": {"EC": 25, "PWC": 50},
            "timestamp": datetime.utcnow() - timedelta(hours=5),
            "status": "new"
        },
        {
            "id": "3",
            "type": "bid_optimized",
            "description": "AI optimized your selling price to ₹5.20/kWh",
            "estimated_profit": 12.30,
            "timestamp": datetime.utcnow() - timedelta(hours=8),
            "status": "active"
        }
    ]
    
    notifications = [
        {
            "id": "1",
            "type": "price_alert",
            "title": "Energy prices trending up",
            "message": "Consider selling excess energy now for 15% better rates",
            "priority": "medium",
            "timestamp": datetime.utcnow() - timedelta(minutes=30)
        },
        {
            "id": "2",
            "type": "weather_forecast",
            "title": "Sunny weather ahead",
            "message": "Expect 20% higher solar generation tomorrow",
            "priority": "low",
            "timestamp": datetime.utcnow() - timedelta(hours=1)
        }
    ]
    
    return DashboardResponse(
        user_info={
            "id": str(current_user.id),
            "username": current_user.username,
            "role": current_user.role.role_type,
            "profile": current_user.profile_data
        },
        role_permissions=["energy_sell", "view_analytics", "bid_optimization", "community_interact"],
        dashboard_config={
            "layout": "prosumer_grid",
            "widgets": ["energy_production", "sales_analytics", "market_prices", "weather_forecast", "achievements"],
            "auto_refresh": 30,
            "theme": "green"
        },
        recent_activities=recent_activities,
        notifications=notifications,
        quick_stats={
            "energy_stats": energy_stats,
            "token_balance": token_balance.to_dict(),
            "market_position": "top_15_percent",
            "reputation_score": 4.8,
            "active_bids": 3,
            "completed_trades_today": 5
        }
    )

@router.get("/dashboard/consumer", response_model=DashboardResponse)
async def get_consumer_dashboard(
    current_user: User = Depends(require_role("consumer")),
    db: Session = Depends(get_db)
):
    """Get consumer-specific dashboard data"""
    
    gamification_service = GamificationService(db)
    token_balance = await gamification_service.get_user_token_balance(str(current_user.id))
    
    # Mock energy consumption data
    consumption_stats = {
        "total_consumed_today": 28.5,
        "total_consumed_month": 785.2,
        "current_consumption": 3.2,
        "efficiency_score": 0.82,
        "energy_bought_today": 25.0,
        "energy_bought_month": 650.8,
        "cost_today": 130.00,
        "cost_month": 3380.16,
        "savings_today": 18.50,
        "savings_month": 485.20,
        "renewable_percentage": 75.0
    }
    
    recent_activities = [
        {
            "id": "1",
            "type": "energy_purchased",
            "description": "Bought 12.0 kWh of solar energy",
            "amount": -62.40,
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "status": "completed"
        },
        {
            "id": "2",
            "type": "efficiency_improvement",
            "description": "Your energy efficiency improved by 5%",
            "tokens_earned": {"EC": 15, "CT": 10},
            "timestamp": datetime.utcnow() - timedelta(hours=6),
            "status": "new"
        },
        {
            "id": "3",
            "type": "cost_saving",
            "description": "Saved ₹25.60 by choosing renewable energy",
            "savings": 25.60,
            "timestamp": datetime.utcnow() - timedelta(hours=12),
            "status": "completed"
        }
    ]
    
    notifications = [
        {
            "id": "1",
            "type": "price_alert",
            "title": "Low-cost renewable energy available",
            "message": "Solar energy available at ₹4.80/kWh from nearby prosumers",
            "priority": "high",
            "timestamp": datetime.utcnow() - timedelta(minutes=15)
        },
        {
            "id": "2",
            "type": "usage_tip",
            "title": "Peak hours starting soon",
            "message": "Consider reducing usage between 6-9 PM to save costs",
            "priority": "medium",
            "timestamp": datetime.utcnow() - timedelta(hours=2)
        }
    ]
    
    return DashboardResponse(
        user_info={
            "id": str(current_user.id),
            "username": current_user.username,
            "role": current_user.role.role_type,
            "profile": current_user.profile_data
        },
        role_permissions=["energy_buy", "view_consumption", "efficiency_tracking", "community_interact"],
        dashboard_config={
            "layout": "consumer_grid",
            "widgets": ["energy_consumption", "cost_analytics", "efficiency_meter", "renewable_tracker", "savings_summary"],
            "auto_refresh": 30,
            "theme": "blue"
        },
        recent_activities=recent_activities,
        notifications=notifications,
        quick_stats={
            "consumption_stats": consumption_stats,
            "token_balance": token_balance.to_dict(),
            "efficiency_rank": "top_25_percent",
            "reputation_score": 4.6,
            "active_requests": 2,
            "completed_purchases_today": 4
        }
    )

@router.get("/dashboard/community_manager", response_model=DashboardResponse)
async def get_community_manager_dashboard(
    current_user: User = Depends(require_role("community_manager")),
    db: Session = Depends(get_db)
):
    """Get community manager dashboard data"""
    
    # Mock community statistics
    community_stats = {
        "total_members": 245,
        "active_members_today": 128,
        "total_energy_traded_today": 1250.5,
        "total_energy_traded_month": 35420.8,
        "average_price": 5.45,
        "renewable_percentage": 78.5,
        "grid_stability": 0.94,
        "community_savings": 15680.50,
        "carbon_offset": 2340.6,
        "dispute_resolution_rate": 0.98
    }
    
    recent_activities = [
        {
            "id": "1",
            "type": "dispute_resolved",
            "description": "Resolved pricing dispute between User123 and User456",
            "resolution_time": "2 hours",
            "timestamp": datetime.utcnow() - timedelta(hours=3),
            "status": "completed"
        },
        {
            "id": "2",
            "type": "community_milestone",
            "description": "Community reached 1000 kWh renewable energy milestone",
            "achievement": "Green Community Badge",
            "timestamp": datetime.utcnow() - timedelta(hours=8),
            "status": "celebrated"
        },
        {
            "id": "3",
            "type": "new_member",
            "description": "5 new members joined the community today",
            "growth_rate": "12%",
            "timestamp": datetime.utcnow() - timedelta(hours=10),
            "status": "growth"
        }
    ]
    
    return DashboardResponse(
        user_info={
            "id": str(current_user.id),
            "username": current_user.username,
            "role": current_user.role.role_type,
            "profile": current_user.profile_data
        },
        role_permissions=["community_manage", "dispute_resolution", "member_management", "analytics_full", "policy_set"],
        dashboard_config={
            "layout": "manager_grid",
            "widgets": ["community_overview", "member_activity", "trading_analytics", "dispute_tracking", "growth_metrics"],
            "auto_refresh": 15,
            "theme": "purple"
        },
        recent_activities=recent_activities,
        notifications=[],
        quick_stats={
            "community_stats": community_stats,
            "pending_disputes": 2,
            "approval_requests": 5,
            "active_policies": 8,
            "community_health_score": 0.92
        }
    )

@router.get("/dashboard/grid_operator", response_model=DashboardResponse)
async def get_grid_operator_dashboard(
    current_user: User = Depends(require_role("grid_operator")),
    db: Session = Depends(get_db)
):
    """Get grid operator dashboard data"""
    
    # Mock grid statistics
    grid_stats = {
        "grid_stability": 0.96,
        "total_load": 2450.8,
        "renewable_contribution": 68.5,
        "peak_demand_forecast": 2890.0,
        "energy_storage_level": 0.78,
        "transmission_efficiency": 0.94,
        "grid_frequency": 49.98,
        "voltage_stability": 0.97,
        "outage_incidents": 0,
        "maintenance_alerts": 3
    }
    
    recent_activities = [
        {
            "id": "1",
            "type": "load_balancing",
            "description": "Automatically balanced load across 5 substations",
            "affected_capacity": "150 MW",
            "timestamp": datetime.utcnow() - timedelta(minutes=45),
            "status": "completed"
        },
        {
            "id": "2",
            "type": "renewable_integration",
            "description": "Integrated 25 MW of solar power from community sources",
            "efficiency_gain": "8%",
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "status": "active"
        },
        {
            "id": "3",
            "type": "predictive_maintenance",
            "description": "Scheduled maintenance for Transformer T-245",
            "estimated_downtime": "2 hours",
            "timestamp": datetime.utcnow() - timedelta(hours=4),
            "status": "scheduled"
        }
    ]
    
    return DashboardResponse(
        user_info={
            "id": str(current_user.id),
            "username": current_user.username,
            "role": current_user.role.role_type,
            "profile": current_user.profile_data
        },
        role_permissions=["grid_monitor", "load_balance", "system_control", "emergency_response", "maintenance_schedule"],
        dashboard_config={
            "layout": "operator_grid",
            "widgets": ["grid_status", "load_monitoring", "renewable_integration", "fault_detection", "demand_forecast"],
            "auto_refresh": 5,  # More frequent updates for grid operations
            "theme": "orange"
        },
        recent_activities=recent_activities,
        notifications=[],
        quick_stats={
            "grid_stats": grid_stats,
            "active_alerts": 3,
            "systems_operational": 98.5,
            "emergency_response_ready": True,
            "maintenance_due": 2
        }
    )

# Bid Optimization Endpoints
@router.post("/bid/optimize")
async def optimize_bid(
    request: BidOptimizationRequest,
    current_user: User = Depends(require_permission("bid_optimization")),
    db: Session = Depends(get_db)
):
    """Get AI-powered bid optimization recommendations"""
    
    try:
        # Initialize bid optimizer
        optimizer = BidOptimizer()
        
        # Create market data from request
        market_data = MarketData(
            current_price=request.market_conditions.get("current_price", 6.0),
            price_trend=request.market_conditions.get("price_trend", "stable"),
            demand_level=request.market_conditions.get("demand_level", 0.7),
            supply_level=request.market_conditions.get("supply_level", 0.6),
            renewable_percentage=request.market_conditions.get("renewable_percentage", 0.8),
            time_of_day=datetime.utcnow().hour,
            day_of_week=datetime.utcnow().weekday(),
            weather_factor=request.market_conditions.get("weather_factor", 0.9),
            grid_stability=request.market_conditions.get("grid_stability", 0.85)
        )
        
        # Create user profile
        user_profile = UserProfile(
            user_id=str(current_user.id),
            risk_tolerance=request.user_preferences.get("risk_tolerance", 0.6),
            preferred_strategy=request.user_preferences.get("strategy", "moderate"),
            energy_type_preference=request.user_preferences.get("energy_type", "any"),
            max_trade_amount=request.user_preferences.get("max_trade_amount", 100.0),
            historical_performance=request.user_preferences.get("historical_performance", {}),
            sustainability_priority=request.user_preferences.get("sustainability_priority", 0.8)
        )
        
        # Get optimization result
        result = await optimizer.optimize_bid(
            bid_type=BidType(request.bid_type),
            energy_amount=request.energy_amount,
            market_data=market_data,
            user_profile=user_profile,
            historical_data=[]
        )
        
        return {
            "success": True,
            "optimization_result": {
                "recommended_bid": {
                    "price": result.recommended_bid.bid_price,
                    "confidence": result.recommended_bid.confidence_score,
                    "success_rate": result.recommended_bid.expected_success_rate,
                    "expected_profit": result.recommended_bid.expected_profit,
                    "risk_score": result.recommended_bid.risk_score,
                    "strategy": result.recommended_bid.strategy_used.value,
                    "reasoning": result.recommended_bid.reasoning,
                    "alternatives": result.recommended_bid.alternative_bids
                },
                "market_analysis": result.market_analysis,
                "timing_suggestion": result.timing_suggestion,
                "auto_bid_enabled": result.auto_bid_enabled,
                "next_review": result.next_review_time.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bid optimization failed: {str(e)}")

# Token Management Endpoints
@router.get("/tokens/balance")
async def get_token_balance(
    current_user: User = Depends(require_permission("view_tokens")),
    db: Session = Depends(get_db)
):
    """Get user's token balance"""
    
    gamification_service = GamificationService(db)
    balance = await gamification_service.get_user_token_balance(str(current_user.id))
    
    return {
        "success": True,
        "balance": balance.to_dict(),
        "last_updated": datetime.utcnow().isoformat()
    }

@router.post("/tokens/transfer")
async def transfer_tokens(
    request: TokenTransferRequest,
    current_user: User = Depends(require_permission("transfer_tokens")),
    db: Session = Depends(get_db)
):
    """Transfer tokens to another user"""
    
    try:
        gamification_service = GamificationService(db)
        
        # Get current balance
        current_balance = await gamification_service.get_user_token_balance(str(current_user.id))
        
        # Check if user has sufficient balance
        token_field_map = {
            "PWC": current_balance.power_coin,
            "EC": current_balance.energy_credit,
            "CT": current_balance.community_token,
            "CC": current_balance.carbon_credit
        }
        
        current_amount = token_field_map.get(request.token_type, 0)
        if current_amount < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient token balance")
        
        # TODO: Implement actual token transfer logic
        # This would involve blockchain transactions in a real implementation
        
        return {
            "success": True,
            "transaction_id": str(uuid.uuid4()),
            "message": f"Transferred {request.amount} {request.token_type} tokens to user {request.recipient_user_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token transfer failed: {str(e)}")

# Beckn Protocol Endpoints
@router.post("/beckn/search")
async def search_energy_beckn(
    request: EnergySearchRequest,
    current_user: User = Depends(require_permission("energy_search")),
    beckn_service: BecknEnergyService = Depends()  # Would be injected
):
    """Search for energy using Beckn protocol"""
    
    try:
        search_params = {
            "energy_type": request.energy_type,
            "lat": request.location["lat"],
            "lng": request.location["lng"],
            "radius": request.radius,
            "min_capacity": request.capacity_range["min"],
            "max_capacity": request.capacity_range["max"],
            "min_price": request.price_range["min"],
            "max_price": request.price_range["max"],
            "min_renewable": request.renewable_min
        }
        
        providers = await beckn_service.search_energy(search_params)
        
        return {
            "success": True,
            "providers_found": len(providers),
            "providers": [
                {
                    "id": provider.id,
                    "name": provider.descriptor["name"],
                    "rating": provider.rating,
                    "items": [
                        {
                            "id": item.id,
                            "name": item.descriptor["name"],
                            "price": item.price["value"],
                            "currency": item.price["currency"]
                        }
                        for item in provider.items or []
                    ]
                }
                for provider in providers
            ],
            "search_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beckn energy search failed: {str(e)}")

# Quantum Computing Demonstration Endpoint
@router.get("/quantum/demo")
async def quantum_demonstration(
    current_user: User = Depends(require_permission("view_quantum_demo"))
):
    """Demonstrate quantum computing capabilities (future scope)"""
    
    try:
        demo_result = await QuantumDemonstration.demonstrate_quantum_advantage()
        
        return {
            "success": True,
            "quantum_demonstration": demo_result,
            "note": "This is a demonstration of future quantum computing capabilities for energy optimization",
            "status": "future_scope",
            "estimated_implementation": "2025 Q3"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "note": "Quantum computing features are in development and not yet integrated with frontend",
            "fallback_message": "Classical optimization algorithms are currently being used"
        }

# User Management Endpoints
@router.post("/auth/register")
async def register_user(
    request: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Register new user with specific role"""
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == request.username) | (User.email == request.email)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Get role
        role = db.query(UserRole).filter(UserRole.role_type == request.role_type).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role type")
        
        # Create new user
        new_user = User(
            username=request.username,
            email=request.email,
            password_hash=request.password,  # In real implementation, hash the password
            role_id=role.id,
            profile_data=request.profile_data,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Initialize gamification profile
        gamification_service = GamificationService(db)
        await gamification_service.get_user_token_balance(str(new_user.id))  # Creates initial balance
        
        return {
            "success": True,
            "user_id": str(new_user.id),
            "message": f"User registered successfully with role: {request.role_type}",
            "dashboard_url": f"/dashboard/{request.role_type}"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/analytics/role-specific")
async def get_role_specific_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    time_range: str = Query("7d", description="1d, 7d, 30d, 90d")
):
    """Get analytics data specific to user's role"""
    
    role_type = current_user.role.role_type
    
    # Mock analytics data based on role
    if role_type == "prosumer":
        analytics = {
            "energy_production": {
                "total_generated": 1250.8,
                "revenue_earned": 6487.20,
                "efficiency_score": 0.89,
                "carbon_offset": 625.4
            },
            "trading_performance": {
                "total_trades": 156,
                "success_rate": 0.94,
                "avg_profit_per_trade": 18.45,
                "best_price_achieved": 7.85
            },
            "market_insights": {
                "optimal_trading_hours": ["10:00-12:00", "14:00-16:00"],
                "price_trends": "increasing",
                "demand_forecast": "high"
            }
        }
    elif role_type == "consumer":
        analytics = {
            "energy_consumption": {
                "total_consumed": 785.2,
                "cost_incurred": 3380.16,
                "efficiency_improvement": 0.15,
                "renewable_percentage": 75.0
            },
            "savings_analysis": {
                "total_saved": 485.20,
                "best_deals_found": 23,
                "avg_price_paid": 4.65,
                "cost_reduction": 0.12
            },
            "usage_patterns": {
                "peak_hours": ["08:00-10:00", "18:00-20:00"],
                "efficiency_tips": ["Use solar during midday", "Avoid peak hours"],
                "next_optimization": "Switch to time-of-use pricing"
            }
        }
    else:
        analytics = {
            "system_metrics": {
                "total_users": 245,
                "active_trades": 1250,
                "grid_stability": 0.96,
                "renewable_integration": 0.785
            }
        }
    
    return {
        "success": True,
        "role": role_type,
        "time_range": time_range,
        "analytics": analytics,
        "generated_at": datetime.utcnow().isoformat()
    }
