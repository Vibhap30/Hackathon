"""
AI Agent Tools for PowerShare Platform
Various tools that agents can use to interact with the platform
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
import structlog

logger = structlog.get_logger()


class PowerShareAPITool:
    """Tool for interacting with PowerShare backend API"""
    
    def __init__(self, api_base_url: str = "http://backend:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_market_offers(self, 
                               energy_type: str = "any",
                               max_price: float = None,
                               location: Dict[str, float] = None,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """Get current market offers"""
        try:
            params = {
                "limit": limit,
                "energy_type": energy_type
            }
            
            if max_price:
                params["max_price"] = max_price
            
            if location:
                params["lat"] = location.get("lat")
                params["lng"] = location.get("lng")
                params["radius"] = 50  # 50km radius
            
            response = await self.client.get(
                f"{self.api_base_url}/api/v1/energy-trading/offers",
                params=params
            )
            
            if response.status_code == 200:
                return response.json().get("offers", [])
            else:
                logger.error(f"Failed to get market offers: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting market offers: {e}")
            return []
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile and preferences"""
        try:
            response = await self.client.get(
                f"{self.api_base_url}/api/v1/users/{user_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user profile: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def get_user_energy_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's energy consumption/production history"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            response = await self.client.get(
                f"{self.api_base_url}/api/v1/analytics/energy-usage/{user_id}",
                params=params
            )
            
            if response.status_code == 200:
                return response.json().get("usage_data", [])
            else:
                logger.error(f"Failed to get energy history: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting energy history: {e}")
            return []
    
    async def submit_energy_offer(self, offer_data: Dict[str, Any]) -> Optional[str]:
        """Submit an energy offer to the marketplace"""
        try:
            response = await self.client.post(
                f"{self.api_base_url}/api/v1/energy-trading/offers",
                json=offer_data
            )
            
            if response.status_code == 201:
                result = response.json()
                return result.get("offer_id")
            else:
                logger.error(f"Failed to submit offer: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting offer: {e}")
            return None
    
    async def execute_trade(self, trade_data: Dict[str, Any]) -> Optional[str]:
        """Execute a trade transaction"""
        try:
            response = await self.client.post(
                f"{self.api_base_url}/api/v1/energy-trading/execute",
                json=trade_data
            )
            
            if response.status_code == 201:
                result = response.json()
                return result.get("transaction_id")
            else:
                logger.error(f"Failed to execute trade: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return None


class WeatherTool:
    """Tool for getting weather data (affects renewable energy predictions)"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    async def get_weather_forecast(self, 
                                  location: Dict[str, float],
                                  days: int = 7) -> Dict[str, Any]:
        """Get weather forecast for location"""
        cache_key = f"weather_{location.get('lat')}_{location.get('lng')}_{days}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            # Simulate weather API call (in production, use real weather API)
            await asyncio.sleep(0.1)
            
            forecast = {
                "location": location,
                "forecast": []
            }
            
            for i in range(days):
                date = datetime.now() + timedelta(days=i)
                day_forecast = {
                    "date": date.isoformat(),
                    "temperature_c": 20 + (i * 2) % 15,  # Mock temperature
                    "humidity": 60 + (i * 5) % 40,
                    "wind_speed_kmh": 10 + (i * 3) % 20,
                    "solar_irradiance": 800 + (i * 50) % 400,  # W/m²
                    "precipitation_mm": 0 if i % 3 != 0 else 5,
                    "cloud_cover_percent": 20 + (i * 10) % 60
                }
                forecast["forecast"].append(day_forecast)
            
            # Cache the result
            self.cache[cache_key] = (forecast, datetime.now().timestamp())
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            return {"location": location, "forecast": []}
    
    def calculate_solar_production_estimate(self, 
                                          weather_data: Dict[str, Any],
                                          panel_capacity_kw: float) -> List[Dict[str, Any]]:
        """Calculate estimated solar energy production based on weather"""
        estimates = []
        
        for day in weather_data.get("forecast", []):
            # Simple solar production calculation
            irradiance = day.get("solar_irradiance", 0)
            cloud_cover = day.get("cloud_cover_percent", 0)
            
            # Efficiency factors
            irradiance_factor = irradiance / 1000  # Peak sun irradiance
            cloud_factor = 1 - (cloud_cover / 100)
            
            # Daily production estimate (kWh)
            daily_production = panel_capacity_kw * 8 * irradiance_factor * cloud_factor
            
            estimates.append({
                "date": day.get("date"),
                "estimated_production_kwh": round(daily_production, 2),
                "confidence": 0.8 if cloud_cover < 50 else 0.6,
                "weather_factors": {
                    "solar_irradiance": irradiance,
                    "cloud_cover": cloud_cover
                }
            })
        
        return estimates


class PriceAnalysisTool:
    """Tool for analyzing energy prices and market trends"""
    
    def __init__(self):
        self.price_history = []
    
    async def analyze_price_trends(self, 
                                  market_data: List[Dict[str, Any]],
                                  time_period: str = "24h") -> Dict[str, Any]:
        """Analyze current price trends"""
        try:
            if not market_data:
                return {"trend": "unknown", "confidence": 0.0}
            
            prices = [offer.get("price_per_kwh", 0) for offer in market_data]
            
            if not prices:
                return {"trend": "unknown", "confidence": 0.0}
            
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            price_volatility = (max_price - min_price) / avg_price if avg_price > 0 else 0
            
            # Simple trend analysis
            recent_prices = prices[-10:] if len(prices) >= 10 else prices
            if len(recent_prices) >= 3:
                trend_direction = "increasing" if recent_prices[-1] > recent_prices[0] else "decreasing"
                if abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] < 0.05:
                    trend_direction = "stable"
            else:
                trend_direction = "stable"
            
            analysis = {
                "trend": trend_direction,
                "average_price": round(avg_price, 4),
                "min_price": round(min_price, 4),
                "max_price": round(max_price, 4),
                "volatility": round(price_volatility, 2),
                "confidence": 0.75,
                "sample_size": len(prices),
                "analysis_time": datetime.now().isoformat(),
                "recommendations": self._generate_price_recommendations(
                    trend_direction, avg_price, price_volatility
                )
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing price trends: {e}")
            return {"trend": "unknown", "confidence": 0.0, "error": str(e)}
    
    def _generate_price_recommendations(self, 
                                       trend: str, 
                                       avg_price: float, 
                                       volatility: float) -> List[str]:
        """Generate trading recommendations based on price analysis"""
        recommendations = []
        
        if trend == "decreasing":
            recommendations.append("Prices are trending down - consider waiting for better rates")
            recommendations.append("Good time to be a buyer in the market")
        elif trend == "increasing":
            recommendations.append("Prices are rising - consider buying soon")
            recommendations.append("Sellers may want to list energy now")
        else:
            recommendations.append("Stable market conditions - good time for both buying and selling")
        
        if volatility > 0.2:
            recommendations.append("High volatility detected - monitor market closely")
        elif volatility < 0.05:
            recommendations.append("Low volatility - predictable pricing environment")
        
        if avg_price < 0.10:
            recommendations.append("Below-average prices - good buying opportunity")
        elif avg_price > 0.15:
            recommendations.append("Above-average prices - consider energy conservation")
        
        return recommendations
    
    async def predict_optimal_trading_time(self, 
                                         user_preferences: Dict[str, Any],
                                         market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict optimal time to trade based on patterns"""
        try:
            # Simple prediction based on current data
            current_hour = datetime.now().hour
            
            # Peak hours typically have higher prices
            if 17 <= current_hour <= 20:  # Evening peak
                recommendation = "off_peak_hours"
                reason = "Current time is peak hours - prices typically higher"
                optimal_time = "late_night_or_early_morning"
            elif 6 <= current_hour <= 9:  # Morning peak
                recommendation = "off_peak_hours"
                reason = "Morning peak hours - consider waiting"
                optimal_time = "midday_or_late_night"
            else:
                recommendation = "good_time"
                reason = "Off-peak hours - generally good pricing"
                optimal_time = "now"
            
            return {
                "recommendation": recommendation,
                "reason": reason,
                "optimal_time": optimal_time,
                "current_hour": current_hour,
                "confidence": 0.7,
                "next_check": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting optimal trading time: {e}")
            return {
                "recommendation": "unknown",
                "reason": f"Analysis error: {e}",
                "confidence": 0.0
            }


class CommunityTool:
    """Tool for community-related operations"""
    
    def __init__(self, api_tool: PowerShareAPITool):
        self.api_tool = api_tool
    
    async def get_community_energy_stats(self, community_id: str) -> Dict[str, Any]:
        """Get energy statistics for a community"""
        try:
            response = await self.api_tool.client.get(
                f"{self.api_tool.api_base_url}/api/v1/communities/{community_id}/energy-stats"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get community stats: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting community stats: {e}")
            return {}
    
    async def recommend_communities(self, 
                                  user_id: str,
                                  location: Dict[str, float]) -> List[Dict[str, Any]]:
        """Recommend communities for a user"""
        try:
            params = {
                "lat": location.get("lat"),
                "lng": location.get("lng"),
                "radius": 25  # 25km radius
            }
            
            response = await self.api_tool.client.get(
                f"{self.api_tool.api_base_url}/api/v1/communities/nearby",
                params=params
            )
            
            if response.status_code == 200:
                communities = response.json().get("communities", [])
                
                # Add recommendation scoring
                for community in communities:
                    community["recommendation_score"] = self._calculate_community_score(community)
                    community["recommendation_reason"] = self._get_recommendation_reason(community)
                
                # Sort by recommendation score
                communities.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
                
                return communities[:5]  # Top 5 recommendations
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error recommending communities: {e}")
            return []
    
    def _calculate_community_score(self, community: Dict[str, Any]) -> float:
        """Calculate recommendation score for a community"""
        score = 0.0
        
        # Member count factor
        member_count = community.get("member_count", 0)
        if member_count > 50:
            score += 0.3
        elif member_count > 20:
            score += 0.2
        elif member_count > 5:
            score += 0.1
        
        # Activity factor
        if community.get("active_trades_count", 0) > 10:
            score += 0.2
        
        # Energy diversity
        energy_types = community.get("supported_energy_types", [])
        score += min(len(energy_types) * 0.1, 0.3)
        
        # Average savings
        avg_savings = community.get("average_savings_percent", 0)
        if avg_savings > 15:
            score += 0.2
        elif avg_savings > 10:
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_recommendation_reason(self, community: Dict[str, Any]) -> str:
        """Get reason for recommending this community"""
        reasons = []
        
        member_count = community.get("member_count", 0)
        if member_count > 50:
            reasons.append("large active community")
        
        avg_savings = community.get("average_savings_percent", 0)
        if avg_savings > 15:
            reasons.append("high average savings")
        
        energy_types = community.get("supported_energy_types", [])
        if len(energy_types) >= 3:
            reasons.append("diverse energy options")
        
        if not reasons:
            reasons.append("nearby community with potential")
        
        return "Good fit: " + ", ".join(reasons)
