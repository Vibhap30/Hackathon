"""
AI-Powered Bid Optimization Engine for PowerShare Platform
=========================================================

This module implements intelligent bid optimization using machine learning
and market analysis to help users maximize their energy trading profits.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class BidType(Enum):
    BUY = "buy"
    SELL = "sell"

class MarketCondition(Enum):
    OVERSUPPLY = "oversupply"
    BALANCED = "balanced"
    HIGH_DEMAND = "high_demand"
    PEAK_HOURS = "peak_hours"
    OFF_PEAK = "off_peak"

class BidStrategy(Enum):
    CONSERVATIVE = "conservative"  # Lower risk, steady returns
    MODERATE = "moderate"         # Balanced risk-reward
    AGGRESSIVE = "aggressive"     # Higher risk, higher potential returns
    SMART_AUTO = "smart_auto"    # AI decides best strategy

@dataclass
class MarketData:
    """Current market conditions and data"""
    current_price: float
    price_trend: str  # 'up', 'down', 'stable'
    demand_level: float  # 0.0 to 1.0
    supply_level: float  # 0.0 to 1.0
    renewable_percentage: float  # 0.0 to 1.0
    time_of_day: int  # 0-23 hours
    day_of_week: int  # 0-6
    weather_factor: float  # affects solar/wind generation
    grid_stability: float  # 0.0 to 1.0

@dataclass
class UserProfile:
    """User's trading profile and preferences"""
    user_id: str
    risk_tolerance: float  # 0.0 (conservative) to 1.0 (aggressive)
    preferred_strategy: BidStrategy
    energy_type_preference: str  # 'solar', 'wind', 'any'
    max_trade_amount: float
    historical_performance: Dict[str, float]
    sustainability_priority: float  # 0.0 to 1.0

@dataclass
class BidRecommendation:
    """AI-generated bid recommendation"""
    bid_price: float
    confidence_score: float  # 0.0 to 1.0
    expected_success_rate: float  # 0.0 to 1.0
    expected_profit: float
    risk_score: float  # 0.0 to 1.0
    strategy_used: BidStrategy
    reasoning: str
    alternative_bids: List[Tuple[float, float]]  # (price, confidence) alternatives

@dataclass
class OptimizationResult:
    """Result from bid optimization"""
    recommended_bid: BidRecommendation
    market_analysis: Dict[str, Any]
    timing_suggestion: str
    auto_bid_enabled: bool
    next_review_time: datetime

class MarketAnalyzer:
    """Analyzes market conditions and trends"""
    
    def __init__(self):
        self.price_history = []
        self.demand_history = []
        self.supply_history = []
    
    def analyze_market_condition(self, market_data: MarketData) -> MarketCondition:
        """Determine current market condition"""
        supply_demand_ratio = market_data.supply_level / max(market_data.demand_level, 0.1)
        
        if supply_demand_ratio > 1.3:
            return MarketCondition.OVERSUPPLY
        elif supply_demand_ratio < 0.7:
            return MarketCondition.HIGH_DEMAND
        elif 6 <= market_data.time_of_day <= 10 or 17 <= market_data.time_of_day <= 21:
            return MarketCondition.PEAK_HOURS
        elif 22 <= market_data.time_of_day or market_data.time_of_day <= 5:
            return MarketCondition.OFF_PEAK
        else:
            return MarketCondition.BALANCED
    
    def predict_price_trend(self, market_data: MarketData, 
                          historical_prices: List[float]) -> Tuple[float, str]:
        """Predict price movement in next hour"""
        if len(historical_prices) < 5:
            return market_data.current_price, "stable"
        
        # Simple trend analysis
        recent_prices = historical_prices[-5:]
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        # Factor in market conditions
        condition = self.analyze_market_condition(market_data)
        
        if condition == MarketCondition.HIGH_DEMAND:
            predicted_change = 0.05  # 5% increase
            trend = "up"
        elif condition == MarketCondition.OVERSUPPLY:
            predicted_change = -0.03  # 3% decrease
            trend = "down"
        elif condition == MarketCondition.PEAK_HOURS:
            predicted_change = 0.02  # 2% increase
            trend = "up"
        else:
            predicted_change = price_change * 0.5  # Momentum-based
            trend = "up" if predicted_change > 0.01 else "down" if predicted_change < -0.01 else "stable"
        
        predicted_price = market_data.current_price * (1 + predicted_change)
        return predicted_price, trend

class BidOptimizer:
    """AI-powered bid optimization engine"""
    
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for bid optimization"""
        # Price prediction model
        self.models['price_predictor'] = RandomForestRegressor(
            n_estimators=100, 
            random_state=42
        )
        
        # Success rate prediction model
        self.models['success_predictor'] = GradientBoostingRegressor(
            n_estimators=100,
            random_state=42
        )
        
        # Profit optimization model
        self.models['profit_optimizer'] = LinearRegression()
        
        # Feature scaler
        self.scaler = StandardScaler()
    
    def _extract_features(self, market_data: MarketData, 
                         user_profile: UserProfile) -> np.ndarray:
        """Extract features for ML models"""
        features = [
            market_data.current_price,
            market_data.demand_level,
            market_data.supply_level,
            market_data.renewable_percentage,
            market_data.time_of_day / 24.0,
            market_data.day_of_week / 7.0,
            market_data.weather_factor,
            market_data.grid_stability,
            user_profile.risk_tolerance,
            user_profile.sustainability_priority,
            user_profile.max_trade_amount
        ]
        return np.array(features).reshape(1, -1)
    
    async def optimize_bid(self, bid_type: BidType, energy_amount: float,
                          market_data: MarketData, user_profile: UserProfile,
                          historical_data: List[Dict]) -> OptimizationResult:
        """Generate optimized bid recommendation"""
        
        # Analyze market conditions
        market_condition = self.market_analyzer.analyze_market_condition(market_data)
        
        # Extract features for ML models
        features = self._extract_features(market_data, user_profile)
        
        # Generate bid recommendations based on strategy
        if user_profile.preferred_strategy == BidStrategy.SMART_AUTO:
            # Let AI choose the best strategy
            strategy = self._select_optimal_strategy(market_condition, user_profile)
        else:
            strategy = user_profile.preferred_strategy
        
        # Calculate optimal bid price
        bid_price = self._calculate_optimal_bid_price(
            bid_type, energy_amount, market_data, user_profile, strategy
        )
        
        # Calculate confidence and success rate
        confidence_score = self._calculate_confidence(
            bid_price, market_data, historical_data
        )
        success_rate = self._predict_success_rate(
            bid_price, market_data, features
        )
        
        # Calculate expected profit
        expected_profit = self._calculate_expected_profit(
            bid_type, bid_price, energy_amount, market_data
        )
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            bid_price, market_data, user_profile
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            bid_type, bid_price, market_condition, strategy
        )
        
        # Generate alternative bids
        alternative_bids = self._generate_alternatives(
            bid_price, confidence_score
        )
        
        # Create recommendation
        recommendation = BidRecommendation(
            bid_price=bid_price,
            confidence_score=confidence_score,
            expected_success_rate=success_rate,
            expected_profit=expected_profit,
            risk_score=risk_score,
            strategy_used=strategy,
            reasoning=reasoning,
            alternative_bids=alternative_bids
        )
        
        # Market analysis
        analysis = {
            "market_condition": market_condition.value,
            "price_trend": market_data.price_trend,
            "supply_demand_ratio": market_data.supply_level / max(market_data.demand_level, 0.1),
            "renewable_availability": market_data.renewable_percentage,
            "grid_stability": market_data.grid_stability
        }
        
        # Timing suggestion
        timing = self._suggest_timing(market_condition, market_data)
        
        # Auto-bid recommendation
        auto_bid = (confidence_score > 0.8 and 
                   user_profile.preferred_strategy == BidStrategy.SMART_AUTO)
        
        # Next review time
        next_review = datetime.utcnow() + timedelta(minutes=15)
        
        return OptimizationResult(
            recommended_bid=recommendation,
            market_analysis=analysis,
            timing_suggestion=timing,
            auto_bid_enabled=auto_bid,
            next_review_time=next_review
        )
    
    def _select_optimal_strategy(self, market_condition: MarketCondition,
                               user_profile: UserProfile) -> BidStrategy:
        """Select optimal strategy based on conditions"""
        if market_condition == MarketCondition.OVERSUPPLY:
            return BidStrategy.AGGRESSIVE  # Take advantage of low prices
        elif market_condition == MarketCondition.HIGH_DEMAND:
            return BidStrategy.CONSERVATIVE  # Avoid high-risk situations
        elif user_profile.risk_tolerance > 0.7:
            return BidStrategy.AGGRESSIVE
        elif user_profile.risk_tolerance < 0.3:
            return BidStrategy.CONSERVATIVE
        else:
            return BidStrategy.MODERATE
    
    def _calculate_optimal_bid_price(self, bid_type: BidType, energy_amount: float,
                                   market_data: MarketData, user_profile: UserProfile,
                                   strategy: BidStrategy) -> float:
        """Calculate optimal bid price using strategy"""
        base_price = market_data.current_price
        
        # Strategy adjustments
        if strategy == BidStrategy.CONSERVATIVE:
            if bid_type == BidType.BUY:
                price_adjustment = 0.02  # Bid 2% above market
            else:
                price_adjustment = -0.02  # Sell 2% below market
        elif strategy == BidStrategy.AGGRESSIVE:
            if bid_type == BidType.BUY:
                price_adjustment = -0.05  # Bid 5% below market
            else:
                price_adjustment = 0.05  # Sell 5% above market
        else:  # MODERATE
            if bid_type == BidType.BUY:
                price_adjustment = 0.01  # Bid 1% above market
            else:
                price_adjustment = -0.01  # Sell 1% below market
        
        # Market condition adjustments
        condition = self.market_analyzer.analyze_market_condition(market_data)
        if condition == MarketCondition.PEAK_HOURS:
            price_adjustment *= 1.5
        elif condition == MarketCondition.OFF_PEAK:
            price_adjustment *= 0.7
        
        # Sustainability bonus
        if market_data.renewable_percentage > 0.8 and user_profile.sustainability_priority > 0.7:
            if bid_type == BidType.BUY:
                price_adjustment += 0.03  # Willing to pay more for green energy
        
        optimal_price = base_price * (1 + price_adjustment)
        return round(optimal_price, 4)
    
    def _calculate_confidence(self, bid_price: float, market_data: MarketData,
                           historical_data: List[Dict]) -> float:
        """Calculate confidence score for the bid"""
        # Base confidence on market volatility
        if len(historical_data) < 10:
            return 0.6  # Medium confidence with limited data
        
        recent_prices = [data['price'] for data in historical_data[-10:]]
        price_volatility = np.std(recent_prices) / np.mean(recent_prices)
        
        # Lower volatility = higher confidence
        volatility_factor = max(0.2, 1.0 - price_volatility * 5)
        
        # Market condition factor
        condition = self.market_analyzer.analyze_market_condition(market_data)
        condition_factor = {
            MarketCondition.BALANCED: 0.9,
            MarketCondition.OVERSUPPLY: 0.8,
            MarketCondition.HIGH_DEMAND: 0.7,
            MarketCondition.PEAK_HOURS: 0.6,
            MarketCondition.OFF_PEAK: 0.8
        }.get(condition, 0.7)
        
        confidence = min(0.95, volatility_factor * condition_factor)
        return round(confidence, 3)
    
    def _predict_success_rate(self, bid_price: float, market_data: MarketData,
                            features: np.ndarray) -> float:
        """Predict probability of bid success"""
        # Simplified success rate calculation
        # In practice, this would use trained ML models
        
        price_diff = abs(bid_price - market_data.current_price) / market_data.current_price
        base_success = max(0.1, 1.0 - price_diff * 10)
        
        # Market condition adjustments
        condition = self.market_analyzer.analyze_market_condition(market_data)
        if condition == MarketCondition.BALANCED:
            base_success *= 1.1
        elif condition in [MarketCondition.PEAK_HOURS, MarketCondition.HIGH_DEMAND]:
            base_success *= 0.8
        
        return min(0.95, base_success)
    
    def _calculate_expected_profit(self, bid_type: BidType, bid_price: float,
                                 energy_amount: float, market_data: MarketData) -> float:
        """Calculate expected profit from the trade"""
        market_price = market_data.current_price
        
        if bid_type == BidType.SELL:
            profit = (bid_price - market_price) * energy_amount * 0.9  # 90% success assumption
        else:
            profit = (market_price - bid_price) * energy_amount * 0.9
        
        return round(profit, 2)
    
    def _calculate_risk_score(self, bid_price: float, market_data: MarketData,
                            user_profile: UserProfile) -> float:
        """Calculate risk score for the bid"""
        price_deviation = abs(bid_price - market_data.current_price) / market_data.current_price
        market_volatility = 1.0 - market_data.grid_stability
        
        risk_score = (price_deviation + market_volatility) / 2
        return min(1.0, risk_score)
    
    def _generate_reasoning(self, bid_type: BidType, bid_price: float,
                          market_condition: MarketCondition, strategy: BidStrategy) -> str:
        """Generate human-readable reasoning for the bid"""
        bid_action = "buying" if bid_type == BidType.BUY else "selling"
        
        reasoning = f"Recommended {bid_action} at ₹{bid_price:.4f}/kWh using {strategy.value} strategy. "
        
        condition_explanations = {
            MarketCondition.OVERSUPPLY: "Market has excess supply, favorable for buyers.",
            MarketCondition.HIGH_DEMAND: "High demand detected, good for sellers.",
            MarketCondition.PEAK_HOURS: "Peak hours - expect higher prices.",
            MarketCondition.OFF_PEAK: "Off-peak period - typically lower prices.",
            MarketCondition.BALANCED: "Balanced market conditions."
        }
        
        reasoning += condition_explanations.get(market_condition, "")
        
        return reasoning
    
    def _generate_alternatives(self, base_price: float, 
                             base_confidence: float) -> List[Tuple[float, float]]:
        """Generate alternative bid options"""
        alternatives = []
        
        # Conservative alternative (higher confidence, lower profit)
        conservative_price = base_price * 0.98
        conservative_confidence = min(0.95, base_confidence * 1.1)
        alternatives.append((conservative_price, conservative_confidence))
        
        # Aggressive alternative (lower confidence, higher profit)
        aggressive_price = base_price * 1.02
        aggressive_confidence = max(0.3, base_confidence * 0.8)
        alternatives.append((aggressive_price, aggressive_confidence))
        
        return alternatives
    
    def _suggest_timing(self, market_condition: MarketCondition,
                       market_data: MarketData) -> str:
        """Suggest optimal timing for the bid"""
        if market_condition == MarketCondition.PEAK_HOURS:
            return "Consider waiting for off-peak hours for better prices"
        elif market_condition == MarketCondition.OFF_PEAK:
            return "Good timing - off-peak hours typically offer better rates"
        elif market_data.renewable_percentage > 0.8:
            return "Excellent timing - high renewable energy availability"
        else:
            return "Current timing is suitable for trading"

class AutoBidManager:
    """Manages automated bidding based on user preferences"""
    
    def __init__(self, bid_optimizer: BidOptimizer):
        self.optimizer = bid_optimizer
        self.active_auto_bids = {}
    
    async def enable_auto_bidding(self, user_id: str, preferences: Dict):
        """Enable automated bidding for a user"""
        self.active_auto_bids[user_id] = preferences
    
    async def disable_auto_bidding(self, user_id: str):
        """Disable automated bidding for a user"""
        if user_id in self.active_auto_bids:
            del self.active_auto_bids[user_id]
    
    async def process_auto_bids(self, market_data: MarketData):
        """Process all active auto-bids"""
        for user_id, preferences in self.active_auto_bids.items():
            # This would integrate with the main trading system
            # to execute automatic bids based on user preferences
            pass

# Example usage and testing
async def main():
    """Example usage of the bid optimization system"""
    
    # Sample market data
    market_data = MarketData(
        current_price=0.08,
        price_trend="stable",
        demand_level=0.7,
        supply_level=0.6,
        renewable_percentage=0.8,
        time_of_day=14,
        day_of_week=2,
        weather_factor=0.9,
        grid_stability=0.85
    )
    
    # Sample user profile
    user_profile = UserProfile(
        user_id="user123",
        risk_tolerance=0.6,
        preferred_strategy=BidStrategy.MODERATE,
        energy_type_preference="solar",
        max_trade_amount=100.0,
        historical_performance={"avg_profit": 15.2, "success_rate": 0.78},
        sustainability_priority=0.8
    )
    
    # Initialize optimizer
    optimizer = BidOptimizer()
    
    # Get bid recommendation
    result = await optimizer.optimize_bid(
        bid_type=BidType.SELL,
        energy_amount=25.0,
        market_data=market_data,
        user_profile=user_profile,
        historical_data=[]
    )
    
    print(f"Recommended bid: ₹{result.recommended_bid.bid_price:.4f}/kWh")
    print(f"Confidence: {result.recommended_bid.confidence_score:.1%}")
    print(f"Expected profit: ₹{result.recommended_bid.expected_profit:.2f}")
    print(f"Reasoning: {result.recommended_bid.reasoning}")

if __name__ == "__main__":
    asyncio.run(main())
