"""
Analytics API Endpoints
PowerShare Energy Trading Platform
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel
import pandas as pd
from collections import defaultdict

from app.core.database import get_db
from app.models.user import User
from app.models.energy_transaction import EnergyTransaction
from app.models.iot_device import IoTDevice
from app.models.community import Community
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

# Pydantic models
class TimeSeriesData(BaseModel):
    timestamp: datetime
    value: float
    label: str

class MarketAnalytics(BaseModel):
    total_volume: float
    average_price: float
    price_trend: str
    volume_trend: str
    peak_hours: List[int]
    active_traders: int
    price_volatility: float
    market_efficiency: float

class UserAnalytics(BaseModel):
    total_trades: int
    total_volume_traded: float
    total_earnings: float
    average_trade_size: float
    success_rate: float
    energy_utilization: float
    carbon_footprint_saved: float
    ranking_percentile: float

class CommunityAnalytics(BaseModel):
    member_count: int
    total_capacity: float
    utilization_rate: float
    internal_trades: int
    external_trades: int
    energy_self_sufficiency: float
    community_score: float

class DeviceAnalytics(BaseModel):
    device_id: int
    device_name: str
    device_type: str
    total_production: float
    total_consumption: float
    efficiency_score: float
    uptime_percentage: float
    maintenance_alerts: int

class PlatformAnalytics(BaseModel):
    total_users: int
    active_users_today: int
    total_energy_traded: float
    total_transactions: int
    platform_revenue: float
    carbon_savings: float
    renewable_percentage: float
    network_growth_rate: float

class PredictiveAnalytics(BaseModel):
    prediction_type: str
    forecast_period: str
    predictions: List[TimeSeriesData]
    confidence_interval: Dict[str, float]
    key_factors: List[str]

# Helper Functions
def calculate_trend(data: List[float]) -> str:
    """Calculate trend from data points."""
    if len(data) < 2:
        return "stable"
    
    recent = sum(data[-3:]) / min(3, len(data))
    older = sum(data[:-3]) / max(1, len(data) - 3)
    
    if recent > older * 1.1:
        return "increasing"
    elif recent < older * 0.9:
        return "decreasing"
    else:
        return "stable"

def calculate_volatility(prices: List[float]) -> float:
    """Calculate price volatility."""
    if len(prices) < 2:
        return 0.0
    
    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    return variance ** 0.5

async def get_market_data(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
    """Get market data for analytics."""
    
    # Get transactions from last N days
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.count(EnergyTransaction.id).label("total_transactions"),
            func.coalesce(func.sum(EnergyTransaction.amount), 0).label("total_volume"),
            func.coalesce(func.avg(EnergyTransaction.price), 0).label("average_price"),
            func.count(func.distinct(EnergyTransaction.seller_id)).label("active_sellers"),
            func.count(func.distinct(EnergyTransaction.buyer_id)).label("active_buyers")
        )
        .where(EnergyTransaction.created_at >= start_date)
    )
    
    stats = result.first()
    
    # Get hourly transaction volumes for peak analysis
    hourly_result = await db.execute(
        select(
            func.extract('hour', EnergyTransaction.created_at).label("hour"),
            func.count(EnergyTransaction.id).label("transaction_count")
        )
        .where(EnergyTransaction.created_at >= start_date)
        .group_by(func.extract('hour', EnergyTransaction.created_at))
    )
    
    hourly_data = {int(row.hour): row.transaction_count for row in hourly_result}
    
    # Get price data for volatility calculation
    price_result = await db.execute(
        select(EnergyTransaction.price)
        .where(EnergyTransaction.created_at >= start_date)
        .order_by(EnergyTransaction.created_at)
    )
    
    prices = [float(row.price) for row in price_result]
    
    return {
        "total_transactions": stats.total_transactions or 0,
        "total_volume": float(stats.total_volume or 0),
        "average_price": float(stats.average_price or 0),
        "active_traders": (stats.active_sellers or 0) + (stats.active_buyers or 0),
        "hourly_data": hourly_data,
        "prices": prices
    }

# API Endpoints
@router.get("/market", response_model=MarketAnalytics)
async def get_market_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive market analytics."""
    
    market_data = await get_market_data(db, days)
    
    # Calculate peak hours (top 3 hours by transaction volume)
    hourly_data = market_data["hourly_data"]
    peak_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)[:3]
    peak_hours = [hour for hour, _ in peak_hours]
    
    # Calculate trends and volatility
    prices = market_data["prices"]
    volumes = [market_data["total_volume"]]  # Simplified for demo
    
    return MarketAnalytics(
        total_volume=market_data["total_volume"],
        average_price=market_data["average_price"],
        price_trend=calculate_trend(prices[-7:]) if len(prices) >= 7 else "stable",
        volume_trend=calculate_trend(volumes),
        peak_hours=peak_hours,
        active_traders=market_data["active_traders"],
        price_volatility=calculate_volatility(prices),
        market_efficiency=85.7  # Simulated metric
    )

@router.get("/user", response_model=UserAnalytics)
async def get_user_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user-specific analytics."""
    
    # Get user's transaction statistics
    result = await db.execute(
        select(
            func.count(EnergyTransaction.id).label("total_trades"),
            func.coalesce(func.sum(EnergyTransaction.amount), 0).label("total_volume"),
            func.coalesce(func.sum(EnergyTransaction.price * EnergyTransaction.amount), 0).label("total_value"),
            func.coalesce(func.avg(EnergyTransaction.amount), 0).label("avg_trade_size")
        )
        .where(
            or_(
                EnergyTransaction.seller_id == current_user.id,
                EnergyTransaction.buyer_id == current_user.id
            )
        )
    )
    
    stats = result.first()
    
    # Calculate earnings (seller transactions only)
    earnings_result = await db.execute(
        select(func.coalesce(func.sum(EnergyTransaction.price * EnergyTransaction.amount), 0))
        .where(EnergyTransaction.seller_id == current_user.id)
    )
    
    total_earnings = float(earnings_result.scalar())
    
    # Calculate energy utilization
    energy_utilization = (current_user.current_energy / max(current_user.energy_capacity, 1)) * 100
    
    # Simulate other metrics
    success_rate = 92.5  # Would calculate from successful vs failed trades
    carbon_saved = float(stats.total_volume or 0) * 0.5  # kg CO2 saved per kWh
    ranking_percentile = 78.3  # User's ranking among all users
    
    return UserAnalytics(
        total_trades=stats.total_trades or 0,
        total_volume_traded=float(stats.total_volume or 0),
        total_earnings=total_earnings,
        average_trade_size=float(stats.avg_trade_size or 0),
        success_rate=success_rate,
        energy_utilization=energy_utilization,
        carbon_footprint_saved=carbon_saved,
        ranking_percentile=ranking_percentile
    )

@router.get("/community/{community_id}", response_model=CommunityAnalytics)
async def get_community_analytics(
    community_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get community-specific analytics."""
    
    # Get community
    community_result = await db.execute(
        select(Community).where(Community.id == community_id, Community.is_active == True)
    )
    community = community_result.scalar_one_or_none()
    
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )
    
    # Check if user is member (simplified check)
    member_ids = [member.id for member in community.members] if community.members else []
    if current_user.id not in member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only community members can view analytics"
        )
    
    # Calculate community metrics
    member_count = len(community.members) if community.members else 0
    total_capacity = sum(member.energy_capacity for member in community.members) if community.members else 0
    total_current = sum(member.current_energy for member in community.members) if community.members else 0
    utilization_rate = (total_current / max(total_capacity, 1)) * 100
    
    # Get internal vs external trades (simplified for demo)
    internal_trades = 45  # Trades between community members
    external_trades = 23  # Trades with non-members
    
    energy_self_sufficiency = 73.2  # % of energy needs met internally
    community_score = 8.4  # Overall community performance score
    
    return CommunityAnalytics(
        member_count=member_count,
        total_capacity=total_capacity,
        utilization_rate=utilization_rate,
        internal_trades=internal_trades,
        external_trades=external_trades,
        energy_self_sufficiency=energy_self_sufficiency,
        community_score=community_score
    )

@router.get("/devices", response_model=List[DeviceAnalytics])
async def get_device_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for user's IoT devices."""
    
    # Get user's devices
    result = await db.execute(
        select(IoTDevice).where(IoTDevice.user_id == current_user.id, IoTDevice.is_active == True)
    )
    devices = result.scalars().all()
    
    device_analytics = []
    for device in devices:
        # Calculate device metrics (simplified for demo)
        total_production = device.energy_production * 24 * 30  # Monthly production
        total_consumption = device.energy_consumption * 24 * 30  # Monthly consumption
        efficiency_score = (total_production / max(total_consumption, 1)) * 100
        uptime_percentage = 95.5 if device.status == "operational" else 65.0
        maintenance_alerts = 2 if device.status != "operational" else 0
        
        device_analytics.append(DeviceAnalytics(
            device_id=device.id,
            device_name=device.name,
            device_type=device.device_type,
            total_production=total_production,
            total_consumption=total_consumption,
            efficiency_score=min(efficiency_score, 100),  # Cap at 100%
            uptime_percentage=uptime_percentage,
            maintenance_alerts=maintenance_alerts
        ))
    
    return device_analytics

@router.get("/platform", response_model=PlatformAnalytics)
async def get_platform_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get platform-wide analytics (admin only for some metrics)."""
    
    # Get basic platform statistics
    users_result = await db.execute(select(func.count(User.id)).where(User.is_active == True))
    total_users = users_result.scalar()
    
    # Active users today (simplified)
    today = datetime.utcnow().date()
    active_today = int(total_users * 0.15)  # Simulate 15% daily active rate
    
    # Get transaction statistics
    transactions_result = await db.execute(
        select(
            func.count(EnergyTransaction.id).label("total_transactions"),
            func.coalesce(func.sum(EnergyTransaction.amount), 0).label("total_volume"),
            func.coalesce(func.sum(EnergyTransaction.price * EnergyTransaction.amount), 0).label("total_value")
        )
    )
    
    tx_stats = transactions_result.first()
    
    # Calculate platform metrics
    platform_revenue = float(tx_stats.total_value or 0) * 0.025  # 2.5% platform fee
    carbon_savings = float(tx_stats.total_volume or 0) * 0.5  # kg CO2 saved per kWh
    renewable_percentage = 87.3  # % of energy that's renewable
    network_growth_rate = 12.5  # % monthly growth
    
    return PlatformAnalytics(
        total_users=total_users,
        active_users_today=active_today,
        total_energy_traded=float(tx_stats.total_volume or 0),
        total_transactions=tx_stats.total_transactions or 0,
        platform_revenue=platform_revenue,
        carbon_savings=carbon_savings,
        renewable_percentage=renewable_percentage,
        network_growth_rate=network_growth_rate
    )

@router.get("/predictions", response_model=PredictiveAnalytics)
async def get_predictive_analytics(
    prediction_type: str = Query(..., regex="^(price|demand|supply|renewable)$"),
    forecast_hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get predictive analytics for energy market."""
    
    # Generate time series predictions (simplified ML simulation)
    predictions = []
    base_time = datetime.utcnow()
    
    if prediction_type == "price":
        base_value = 0.25  # Base price per kWh
        for i in range(forecast_hours):
            # Simulate daily price pattern with some randomness
            time_factor = (i % 24) / 24  # Daily cycle
            price_variation = base_value * (0.8 + 0.4 * time_factor + 0.1 * (i % 3 - 1))
            
            predictions.append(TimeSeriesData(
                timestamp=base_time + timedelta(hours=i),
                value=round(price_variation, 3),
                label=f"Price +{i}h"
            ))
    
    elif prediction_type == "demand":
        base_demand = 1000  # Base demand in kWh
        for i in range(forecast_hours):
            # Simulate demand pattern
            hour_of_day = (base_time.hour + i) % 24
            demand_multiplier = 1.2 if 8 <= hour_of_day <= 20 else 0.8  # Higher during day
            demand = base_demand * demand_multiplier * (1 + 0.1 * (i % 5 - 2) / 5)
            
            predictions.append(TimeSeriesData(
                timestamp=base_time + timedelta(hours=i),
                value=round(demand, 1),
                label=f"Demand +{i}h"
            ))
    
    elif prediction_type == "supply":
        base_supply = 1200  # Base supply in kWh
        for i in range(forecast_hours):
            # Simulate supply pattern (renewable focus)
            hour_of_day = (base_time.hour + i) % 24
            renewable_factor = max(0.3, 1.0 - abs(hour_of_day - 12) / 12)  # Peak at noon
            supply = base_supply * renewable_factor * (1 + 0.05 * (i % 7 - 3) / 7)
            
            predictions.append(TimeSeriesData(
                timestamp=base_time + timedelta(hours=i),
                value=round(supply, 1),
                label=f"Supply +{i}h"
            ))
    
    elif prediction_type == "renewable":
        for i in range(forecast_hours):
            # Simulate renewable percentage
            hour_of_day = (base_time.hour + i) % 24
            renewable_pct = 60 + 30 * max(0, 1 - abs(hour_of_day - 12) / 12)  # Peak solar at noon
            
            predictions.append(TimeSeriesData(
                timestamp=base_time + timedelta(hours=i),
                value=round(renewable_pct, 1),
                label=f"Renewable% +{i}h"
            ))
    
    return PredictiveAnalytics(
        prediction_type=prediction_type,
        forecast_period=f"{forecast_hours} hours",
        predictions=predictions,
        confidence_interval={"lower": 0.15, "upper": 0.85},
        key_factors=["weather_patterns", "historical_demand", "market_trends", "seasonal_effects"]
    )

@router.get("/export/csv")
async def export_analytics_csv(
    analytics_type: str = Query(..., regex="^(transactions|users|devices|market)$"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export analytics data as CSV."""
    
    # In production, this would generate and return actual CSV data
    # For demo, return download instructions
    
    return {
        "message": f"CSV export initiated for {analytics_type} data",
        "period": f"Last {days} days",
        "download_url": f"/api/v1/analytics/download/{analytics_type}_{days}days.csv",
        "estimated_file_size": "2.5 MB",
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }

@router.get("/realtime")
async def get_realtime_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time analytics dashboard data."""
    
    # Simulate real-time metrics
    return {
        "current_price": 0.247,
        "price_change_24h": +0.012,
        "active_trades": 156,
        "total_volume_today": 2847.3,
        "renewable_percentage": 89.2,
        "network_load": 78.5,
        "carbon_saved_today": 1423.6,
        "top_communities": [
            {"name": "Green Valley", "volume": 345.7},
            {"name": "Solar Pioneers", "volume": 298.2},
            {"name": "Wind Farmers", "volume": 267.9}
        ],
        "last_updated": datetime.utcnow()
    }
