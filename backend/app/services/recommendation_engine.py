"""
Personalized Recommendation Engine for PowerShare Platform
=========================================================

This service provides comprehensive AI-powered recommendations for:
- Energy trading opportunities
- Optimal consumption patterns
- Community interactions
- Investment strategies
- Sustainability improvements
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import logging

from app.models.user import User
from app.models.energy_transaction import EnergyTransaction
from app.models.iot_device import IoTDevice
from app.models.community import Community

logger = logging.getLogger(__name__)

@dataclass
class Recommendation:
    id: str
    type: str  # 'trading', 'optimization', 'community', 'investment'
    title: str
    description: str
    priority: str  # 'high', 'medium', 'low'
    confidence_score: float
    potential_savings: float
    implementation_effort: str  # 'easy', 'medium', 'complex'
    timeline: str
    reasoning: str
    action_items: List[str]
    data: Dict[str, Any]
    expires_at: datetime

@dataclass
class UserProfile:
    user_id: int
    energy_usage_pattern: Dict[str, float]
    trading_history: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    location: Optional[Tuple[float, float]]
    consumption_predictions: Dict[str, float]
    production_capacity: Dict[str, float]
    sustainability_score: float
    risk_tolerance: str

@dataclass
class MarketConditions:
    current_price: float
    price_trend: str
    volatility: float
    supply_demand_ratio: float
    renewable_percentage: float
    peak_hours: List[int]
    forecast_24h: List[float]

class PersonalizedRecommendationEngine:
    """AI-powered recommendation engine for personalized energy insights"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.recommendation_weights = {
            'trading': 0.3,
            'optimization': 0.4,
            'community': 0.2,
            'investment': 0.1
        }
    
    async def generate_recommendations(self, user_id: int, context: Optional[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate comprehensive personalized recommendations"""
        try:
            # Get user profile and market data
            user_profile = await self._build_user_profile(user_id)
            market_conditions = await self._get_market_conditions()
            
            # Generate recommendations from different engines
            recommendations = []
            
            # Trading recommendations
            trading_recs = await self._generate_trading_recommendations(user_profile, market_conditions)
            recommendations.extend(trading_recs)
            
            # Optimization recommendations
            optimization_recs = await self._generate_optimization_recommendations(user_profile)
            recommendations.extend(optimization_recs)
            
            # Community recommendations
            community_recs = await self._generate_community_recommendations(user_profile)
            recommendations.extend(community_recs)
            
            # Investment recommendations
            investment_recs = await self._generate_investment_recommendations(user_profile, market_conditions)
            recommendations.extend(investment_recs)
            
            # Sort by priority and confidence
            recommendations.sort(key=lambda x: (
                {'high': 3, 'medium': 2, 'low': 1}[x.priority],
                x.confidence_score
            ), reverse=True)
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return []
    
    async def _build_user_profile(self, user_id: int) -> UserProfile:
        """
        Build comprehensive user profile for recommendations.
        For prototype: All data is dummy or file-based. SQLAlchemy queries are commented out.
        """
        try:
            # --- SQLAlchemy code commented for prototype ---
            # user = self.db.query(User).filter(User.id == user_id).first()
            # if not user:
            #     raise ValueError(f"User {user_id} not found")
            # preferences = getattr(user, 'preferences', {})
            # location = getattr(user, 'location', None)
            # risk_tolerance = getattr(user, 'risk_tolerance', 'medium')
            # ----------------------------------------------
            # Dummy user data for prototype
            preferences = {"demo": True}
            location = (37.7749, -122.4194)
            risk_tolerance = 'medium'
            # Get energy usage patterns
            usage_pattern = await self._analyze_usage_patterns(user_id)
            # Get trading history
            trading_history = await self._get_trading_history(user_id)
            # Get IoT device data for production capacity
            production_capacity = await self._get_production_capacity(user_id)
            # Calculate sustainability score
            sustainability_score = await self._calculate_sustainability_score(user_id)
            return UserProfile(
                user_id=user_id,
                energy_usage_pattern=usage_pattern,
                trading_history=trading_history,
                preferences=preferences,
                location=location,
                consumption_predictions=await self._predict_consumption(user_id, usage_pattern),
                production_capacity=production_capacity,
                sustainability_score=sustainability_score,
                risk_tolerance=risk_tolerance
            )
        except Exception as e:
            logger.error(f"Error building user profile: {e}")
            return UserProfile(
                user_id=user_id,
                energy_usage_pattern={},
                trading_history=[],
                preferences={},
                location=None,
                consumption_predictions={},
                production_capacity={},
                sustainability_score=0.5,
                risk_tolerance='medium'
            )
    
    async def _analyze_usage_patterns(self, user_id: int) -> Dict[str, float]:
        """Analyze user's energy usage patterns"""
        # Mock implementation - in real system, would analyze historical IoT data
        return {
            'avg_daily_consumption': 25.5,
            'peak_usage_hour': 19.0,
            'weekend_vs_weekday_ratio': 0.85,
            'seasonal_variation': 0.15,
            'efficiency_trend': 0.05  # Improving efficiency by 5%
        }
    
    async def _get_trading_history(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user's trading history.
        For prototype: Returns dummy trading history. SQLAlchemy code is commented out.
        """
        try:
            # --- SQLAlchemy code commented for prototype ---
            # transactions = self.db.query(EnergyTransaction).filter(
            #     EnergyTransaction.buyer_id == user_id or EnergyTransaction.seller_id == user_id
            # ).order_by(EnergyTransaction.created_at.desc()).limit(50).all()
            # return [ ... ]
            # ----------------------------------------------
            # Dummy trading history
            return [
                {
                    'amount': 10.0,
                    'price': 0.25,
                    'type': 'buy',
                    'timestamp': datetime.now().isoformat(),
                    'profit_loss': -2.5
                },
                {
                    'amount': 8.0,
                    'price': 0.28,
                    'type': 'sell',
                    'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                    'profit_loss': 2.24
                }
            ]
        except Exception as e:
            logger.error(f"Error getting trading history: {e}")
            return []
    
    async def _get_production_capacity(self, user_id: int) -> Dict[str, float]:
        """
        Get user's energy production capacity from IoT devices.
        For prototype: Returns dummy device data. SQLAlchemy code is commented out.
        """
        try:
            # --- SQLAlchemy code commented for prototype ---
            # devices = self.db.query(IoTDevice).filter(
            #     IoTDevice.user_id == user_id,
            #     IoTDevice.device_type.in_(['solar_panel', 'wind_turbine', 'battery'])
            # ).all()
            # capacity = {'solar': 0.0, 'wind': 0.0, 'storage': 0.0}
            # for device in devices:
            #     ...
            # return capacity
            # ----------------------------------------------
            # Dummy device data
            return {'solar': 5.0, 'wind': 0.0, 'storage': 10.0}
        except Exception as e:
            logger.error(f"Error getting production capacity: {e}")
            return {'solar': 0.0, 'wind': 0.0, 'storage': 0.0}
    
    async def _calculate_sustainability_score(self, user_id: int) -> float:
        """
        Calculate user's sustainability score (0-1).
        For prototype: Returns dummy score. SQLAlchemy code is commented out.
        """
        try:
            # --- SQLAlchemy code commented for prototype ---
            # base_score = 0.5
            # devices = self.db.query(IoTDevice).filter(IoTDevice.user_id == user_id).all()
            # renewable_bonus = min(0.3, len([d for d in devices if d.device_type in ['solar_panel', 'wind_turbine']]) * 0.1)
            # transactions = self.db.query(EnergyTransaction).filter(
            #     EnergyTransaction.buyer_id == user_id
            # ).limit(20).all()
            # renewable_trading_bonus = ...
            # return min(1.0, base_score + renewable_bonus + renewable_trading_bonus)
            # ----------------------------------------------
            # Dummy sustainability score
            return 0.75
        except Exception as e:
            logger.error(f"Error calculating sustainability score: {e}")
            return 0.5
    
    async def _predict_consumption(self, user_id: int, usage_pattern: Dict[str, float]) -> Dict[str, float]:
        """Predict future energy consumption"""
        base_consumption = usage_pattern.get('avg_daily_consumption', 25.0)
        
        return {
            'next_24h': base_consumption * (1 + np.random.normal(0, 0.1)),
            'next_week': base_consumption * 7 * (1 + usage_pattern.get('seasonal_variation', 0.1)),
            'next_month': base_consumption * 30 * (1 + usage_pattern.get('seasonal_variation', 0.1))
        }
    
    async def _get_market_conditions(self) -> MarketConditions:
        """Get current market conditions"""
        # Mock market data - in real system, would fetch from market APIs
        return MarketConditions(
            current_price=0.267,
            price_trend='stable',
            volatility=0.15,
            supply_demand_ratio=1.05,
            renewable_percentage=0.65,
            peak_hours=[8, 9, 18, 19, 20],
            forecast_24h=[0.25, 0.23, 0.22, 0.24, 0.26, 0.28, 0.30, 0.32, 0.28, 0.25, 0.24, 0.26,
                         0.27, 0.26, 0.25, 0.24, 0.26, 0.29, 0.32, 0.35, 0.33, 0.30, 0.28, 0.26]
        )
    
    async def _generate_trading_recommendations(self, profile: UserProfile, market: MarketConditions) -> List[Recommendation]:
        """Generate trading-specific recommendations"""
        recommendations = []
        
        # Price-based trading opportunity
        if market.current_price < 0.25 and profile.consumption_predictions['next_24h'] > 20:
            recommendations.append(Recommendation(
                id=f"trading_buy_{int(datetime.now().timestamp())}",
                type="trading",
                title="Favorable Buying Opportunity",
                description=f"Current energy price ({market.current_price:.3f} $/kWh) is 12% below average. Consider purchasing energy for the next 24 hours.",
                priority="high",
                confidence_score=0.87,
                potential_savings=profile.consumption_predictions['next_24h'] * (0.267 - market.current_price),
                implementation_effort="easy",
                timeline="Next 2 hours",
                reasoning=f"Market analysis shows current price is in bottom 15% of historical range. Your predicted consumption of {profile.consumption_predictions['next_24h']:.1f} kWh makes this a high-value opportunity.",
                action_items=[
                    "Place buy order for predicted consumption amount",
                    "Set price limit at current market rate + 5%",
                    "Monitor price movements for next 2 hours"
                ],
                data={
                    "recommended_amount": profile.consumption_predictions['next_24h'],
                    "max_price": market.current_price * 1.05,
                    "market_trend": market.price_trend
                },
                expires_at=datetime.now() + timedelta(hours=2)
            ))
        
        # Selling opportunity for producers
        if profile.production_capacity['solar'] > 0 and market.current_price > 0.28:
            excess_production = profile.production_capacity['solar'] * 6 - profile.consumption_predictions['next_24h']  # 6 hours of peak sun
            if excess_production > 0:
                recommendations.append(Recommendation(
                    id=f"trading_sell_{int(datetime.now().timestamp())}",
                    type="trading",
                    title="High-Value Selling Opportunity",
                    description=f"Energy prices are 15% above average. Sell your excess solar production for maximum profit.",
                    priority="high",
                    confidence_score=0.82,
                    potential_savings=excess_production * (market.current_price - 0.24),
                    implementation_effort="easy",
                    timeline="Next 4 hours",
                    reasoning=f"Your solar capacity can produce {profile.production_capacity['solar'] * 6:.1f} kWh during peak hours, with {excess_production:.1f} kWh excess after consumption.",
                    action_items=[
                        f"List {excess_production:.1f} kWh for sale",
                        "Set minimum price at current rate",
                        "Schedule for peak production hours (10 AM - 4 PM)"
                    ],
                    data={
                        "recommended_amount": excess_production,
                        "min_price": market.current_price,
                        "production_window": "10:00-16:00"
                    },
                    expires_at=datetime.now() + timedelta(hours=4)
                ))
        
        return recommendations
    
    async def _generate_optimization_recommendations(self, profile: UserProfile) -> List[Recommendation]:
        """Generate energy optimization recommendations"""
        recommendations = []
        
        # Peak hour shifting
        if profile.energy_usage_pattern.get('peak_usage_hour', 19) in [18, 19, 20]:
            recommendations.append(Recommendation(
                id=f"optimization_peak_{int(datetime.now().timestamp())}",
                type="optimization",
                title="Shift Energy Usage to Off-Peak Hours",
                description="Moving 30% of your energy usage from peak hours (6-8 PM) to off-peak can save 15-20% on energy costs.",
                priority="medium",
                confidence_score=0.91,
                potential_savings=profile.energy_usage_pattern.get('avg_daily_consumption', 25) * 0.3 * 0.08 * 30,  # Monthly savings
                implementation_effort="medium",
                timeline="Implement over 2 weeks",
                reasoning="Your usage pattern shows high consumption during peak pricing hours. Smart scheduling can maintain comfort while reducing costs.",
                action_items=[
                    "Install smart timers for major appliances",
                    "Set dishwasher and washing machine to run at 10 PM",
                    "Pre-cool/heat home during off-peak hours",
                    "Use smart thermostat scheduling"
                ],
                data={
                    "current_peak_usage": profile.energy_usage_pattern.get('peak_usage_hour', 19),
                    "optimal_usage_hours": [22, 23, 6, 7],
                    "shiftable_load_percentage": 0.3
                },
                expires_at=datetime.now() + timedelta(days=7)
            ))
        
        # Efficiency improvements
        if profile.sustainability_score < 0.7:
            recommendations.append(Recommendation(
                id=f"optimization_efficiency_{int(datetime.now().timestamp())}",
                type="optimization",
                title="Energy Efficiency Upgrades",
                description="LED lighting and smart power strips can reduce consumption by 8-12% with minimal investment.",
                priority="medium",
                confidence_score=0.85,
                potential_savings=profile.energy_usage_pattern.get('avg_daily_consumption', 25) * 0.10 * 0.267 * 30,  # Monthly savings
                implementation_effort="easy",
                timeline="Complete in 1 weekend",
                reasoning="Analysis shows efficiency opportunities in lighting and standby power consumption.",
                action_items=[
                    "Replace incandescent bulbs with LED",
                    "Install smart power strips for electronics",
                    "Seal air leaks around windows and doors",
                    "Upgrade to ENERGY STAR appliances when replacing"
                ],
                data={
                    "efficiency_potential": 0.10,
                    "investment_required": 150,
                    "payback_period_months": 8
                },
                expires_at=datetime.now() + timedelta(days=30)
            ))
        
        return recommendations
    
    async def _generate_community_recommendations(self, profile: UserProfile) -> List[Recommendation]:
        """Generate community-related recommendations"""
        recommendations = []
        
        # Community solar opportunity
        if profile.production_capacity['solar'] == 0 and profile.location:
            recommendations.append(Recommendation(
                id=f"community_solar_{int(datetime.now().timestamp())}",
                type="community",
                title="Join Local Community Solar Program",
                description="Access solar energy benefits without rooftop installation. Save 10-15% on electricity bills.",
                priority="medium",
                confidence_score=0.78,
                potential_savings=profile.energy_usage_pattern.get('avg_daily_consumption', 25) * 0.12 * 0.267 * 30,
                implementation_effort="easy",
                timeline="Available now",
                reasoning="No solar installation detected. Community solar programs provide renewable energy access for non-homeowners or unsuitable rooftops.",
                action_items=[
                    "Research local community solar projects",
                    "Compare subscription rates with current utility",
                    "Sign up for available capacity",
                    "Monitor monthly savings"
                ],
                data={
                    "estimated_savings_percentage": 0.12,
                    "typical_contract_length": "12-24 months",
                    "programs_in_area": 3
                },
                expires_at=datetime.now() + timedelta(days=14)
            ))
        
        # Energy sharing group
        recommendations.append(Recommendation(
            id=f"community_sharing_{int(datetime.now().timestamp())}",
            type="community",
            title="Form Neighborhood Energy Sharing Group",
            description="Coordinate with neighbors for bulk energy purchases and shared storage. Reduce costs by 15-25%.",
            priority="low",
            confidence_score=0.72,
            potential_savings=profile.energy_usage_pattern.get('avg_daily_consumption', 25) * 0.20 * 0.267 * 30,
            implementation_effort="complex",
            timeline="3-6 months to organize",
            reasoning="Community coordination can leverage economies of scale and mutual support for energy independence.",
            action_items=[
                "Identify interested neighbors",
                "Research legal frameworks for energy sharing",
                "Organize informational meeting",
                "Develop cost-sharing agreement"
            ],
            data={
                "group_size_optimal": "8-12 households",
                "shared_storage_capacity": "50-100 kWh",
                "coordination_effort": "monthly meetings"
            },
            expires_at=datetime.now() + timedelta(days=60)
        ))
        
        return recommendations
    
    async def _generate_investment_recommendations(self, profile: UserProfile, market: MarketConditions) -> List[Recommendation]:
        """Generate investment-related recommendations"""
        recommendations = []
        
        # Solar investment opportunity
        if profile.production_capacity['solar'] == 0 and profile.location:
            annual_consumption = profile.energy_usage_pattern.get('avg_daily_consumption', 25) * 365
            solar_potential = annual_consumption * 0.8  # Assume 80% solar offset potential
            
            recommendations.append(Recommendation(
                id=f"investment_solar_{int(datetime.now().timestamp())}",
                type="investment",
                title="Rooftop Solar Installation",
                description=f"Install {solar_potential/1500:.1f}kW solar system. Break-even in 6-8 years, 20+ year lifespan.",
                priority="low",
                confidence_score=0.83,
                potential_savings=annual_consumption * 0.8 * 0.267 * 15,  # 15-year savings
                implementation_effort="complex",
                timeline="3-6 months project",
                reasoning=f"Your annual consumption of {annual_consumption:.0f} kWh makes solar financially attractive with current incentives.",
                action_items=[
                    "Get solar potential assessment",
                    "Obtain quotes from 3+ installers",
                    "Research federal and state incentives",
                    "Consider financing options"
                ],
                data={
                    "estimated_system_size": solar_potential/1500,
                    "estimated_cost": solar_potential/1500 * 3000,
                    "annual_savings": annual_consumption * 0.8 * 0.267,
                    "payback_period_years": 7.2
                },
                expires_at=datetime.now() + timedelta(days=90)
            ))
        
        # Battery storage
        if profile.production_capacity['solar'] > 0 and profile.production_capacity['storage'] == 0:
            recommendations.append(Recommendation(
                id=f"investment_battery_{int(datetime.now().timestamp())}",
                type="investment",
                title="Add Battery Storage System",
                description="Store excess solar production for peak-hour use. Increase solar value by 30-40%.",
                priority="low",
                confidence_score=0.76,
                potential_savings=profile.production_capacity['solar'] * 4 * 0.08 * 365,  # 4 hours storage, 8 cent arbitrage
                implementation_effort="medium",
                timeline="1-2 months",
                reasoning="Existing solar system can benefit from storage to maximize value and provide backup power.",
                action_items=[
                    "Size storage system for 4-6 hours of evening usage",
                    "Research battery technologies and warranties",
                    "Check utility time-of-use rates",
                    "Consider backup power needs"
                ],
                data={
                    "recommended_capacity": profile.energy_usage_pattern.get('avg_daily_consumption', 25) * 0.25,
                    "estimated_cost": profile.energy_usage_pattern.get('avg_daily_consumption', 25) * 0.25 * 800,
                    "value_increase_percentage": 0.35
                },
                expires_at=datetime.now() + timedelta(days=45)
            ))
        
        return recommendations
    
    async def get_demo_recommendations_prosumer(self, user_id: int) -> List[Recommendation]:
        """Get demo recommendations specifically for prosumer scenario"""
        return [
            Recommendation(
                id="demo_prosumer_sell",
                type="trading",
                title="🌞 Sell Excess Solar Production",
                description="Current market price $0.29/kWh is 15% above average. Your solar panels will produce 35 kWh excess today.",
                priority="high",
                confidence_score=0.92,
                potential_savings=35 * 0.05,
                implementation_effort="easy",
                timeline="Next 3 hours",
                reasoning="Weather forecast shows peak solar conditions coinciding with high demand period. Energy trading agent recommends immediate listing.",
                action_items=[
                    "List 35 kWh for sale at $0.28/kWh minimum",
                    "Schedule delivery for 11 AM - 3 PM peak production",
                    "Set automatic price adjustment based on market conditions"
                ],
                data={"amount": 35, "min_price": 0.28, "market_premium": 0.15},
                expires_at=datetime.now() + timedelta(hours=3)
            ),
            Recommendation(
                id="demo_prosumer_community",
                type="community",
                title="🏘️ Neighbor Energy Sharing Opportunity",
                description="3 neighbors need 45 kWh combined during your peak production hours. Direct sales save 20% in fees.",
                priority="medium",
                confidence_score=0.85,
                potential_savings=45 * 0.03,
                implementation_effort="easy",
                timeline="Today",
                reasoning="Community coordination agent identified local demand matching your production schedule. Direct peer-to-peer sales reduce platform fees.",
                action_items=[
                    "Accept neighbor requests for energy sharing",
                    "Set up automatic supply for regular customers",
                    "Join neighborhood energy cooperative"
                ],
                data={"neighbors": 3, "amount": 45, "fee_savings": 0.03},
                expires_at=datetime.now() + timedelta(hours=8)
            ),
            Recommendation(
                id="demo_prosumer_optimization",
                type="optimization",
                title="⚡ Battery Charging Strategy",
                description="Charge battery at 2 AM (lowest rates $0.18/kWh), sell stored energy at 7 PM peak ($0.32/kWh).",
                priority="medium",
                confidence_score=0.89,
                potential_savings=15 * 0.14,
                implementation_effort="easy",
                timeline="Ongoing daily",
                reasoning="Optimization agent analyzed 30-day price patterns. Time-shifted arbitrage provides consistent daily profit opportunities.",
                action_items=[
                    "Configure smart battery schedule",
                    "Set buy threshold at $0.20/kWh",
                    "Set sell threshold at $0.30/kWh"
                ],
                data={"arbitrage_profit": 0.14, "daily_amount": 15, "automation": True},
                expires_at=datetime.now() + timedelta(days=1)
            )
        ]
    
    async def get_demo_recommendations_consumer(self, user_id: int) -> List[Recommendation]:
        """Get demo recommendations specifically for consumer scenario"""
        return [
            Recommendation(
                id="demo_consumer_buy",
                type="trading",
                title="💰 Cheap Energy Alert",
                description="Solar energy available at $0.22/kWh (18% below grid rate). Pre-purchase 50 kWh for the week.",
                priority="high",
                confidence_score=0.88,
                potential_savings=50 * 0.045,
                implementation_effort="easy",
                timeline="Next 2 hours",
                reasoning="Market analysis agent detected oversupply from local solar farms. Energy trading agent recommends bulk purchase for weekly consumption.",
                action_items=[
                    "Place buy order for 50 kWh",
                    "Set delivery schedule for off-peak hours",
                    "Enable auto-purchase for similar opportunities"
                ],
                data={"amount": 50, "price": 0.22, "savings_vs_grid": 0.045},
                expires_at=datetime.now() + timedelta(hours=2)
            ),
            Recommendation(
                id="demo_consumer_schedule",
                type="optimization",
                title="🕐 Smart Usage Scheduling",
                description="Shift dishwasher and laundry to 11 PM-6 AM. Save $18/month with 25% rate reduction during off-peak hours.",
                priority="medium",
                confidence_score=0.91,
                potential_savings=18.0,
                implementation_effort="easy",
                timeline="Start tonight",
                reasoning="Optimization agent analyzed your usage patterns. Large appliances during off-peak hours maximize savings without lifestyle impact.",
                action_items=[
                    "Program dishwasher delay timer for 11 PM",
                    "Set laundry schedule for early morning",
                    "Install smart timers for water heater"
                ],
                data={"monthly_savings": 18, "off_peak_hours": "23:00-06:00", "rate_reduction": 0.25},
                expires_at=datetime.now() + timedelta(days=1)
            ),
            Recommendation(
                id="demo_consumer_community",
                type="community",
                title="🤝 Join Bulk Buying Group",
                description="GreenVille Energy Cooperative has 2 spots open. Members save average 12% through group purchasing power.",
                priority="medium",
                confidence_score=0.79,
                potential_savings=35.0,
                implementation_effort="medium",
                timeline="1 week to join",
                reasoning="Community agent found local energy cooperative with strong track record. Group purchasing leverages collective demand for better rates.",
                action_items=[
                    "Attend Tuesday info session at Community Center",
                    "Review cooperative agreement and fees",
                    "Commit to 12-month minimum membership"
                ],
                data={"group_size": 47, "avg_savings_pct": 0.12, "monthly_savings": 35},
                expires_at=datetime.now() + timedelta(days=7)
            ),
            Recommendation(
                id="demo_consumer_beckn",
                type="trading",
                title="🌐 Cross-Network Energy Discovery",
                description="Beckn protocol found renewable energy offers from 3 external networks. Best price: $0.21/kWh from WindShare Network.",
                priority="high",
                confidence_score=0.84,
                potential_savings=40 * 0.06,
                implementation_effort="easy",
                timeline="Available now",
                reasoning="Beckn integration agent discovered cheaper renewable energy from partner networks. Cross-platform trading expands your options significantly.",
                action_items=[
                    "Verify WindShare Network credentials",
                    "Place order for 40 kWh renewable energy",
                    "Set up recurring purchases from best networks"
                ],
                data={"networks_found": 3, "best_price": 0.21, "amount": 40, "source": "wind"},
                expires_at=datetime.now() + timedelta(hours=4)
            )
        ]
