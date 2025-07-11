"""
Energy Trading Agent
PowerShare AI Agents with LangGraph
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
from dataclasses import dataclass

import os
import base64
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import structlog

logger = structlog.get_logger()


@dataclass
class EnergyTradingState:
    """State for energy trading workflow"""
    user_id: str
    energy_amount: float
    energy_type: str
    max_price: float
    location: Dict[str, float]  # lat, lng
    preferences: Dict[str, Any]
    market_data: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    selected_offer: Optional[Dict[str, Any]] = None
    transaction_id: Optional[str] = None
    status: str = "analyzing"
    messages: List[BaseMessage] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []


class DummyWeatherProvider:
    """Provides dummy weather data for the prototype."""
    @staticmethod
    def get_current_weather(location: Dict[str, float]) -> Dict[str, Any]:
        # In a real system, fetch from weather API
        return {
            "summary": "Sunny",
            "temperature_c": 32,
            "solar_output": "high",
            "wind_speed_kmh": 10,
            "forecast": "Clear skies, high solar generation expected"
        }


class EnergyMarketAnalyzer:
    """Analyzes energy market conditions and offers using Azure OpenAI"""
    def __init__(self):
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )
        self.deployment = deployment

    async def analyze_market(self, state: EnergyTradingState) -> EnergyTradingState:
        """Analyze current market conditions using Azure OpenAI"""
        try:
            logger.info(f"Analyzing market for user {state.user_id}")
            # Enhanced prompt with all parameters
            market_prompt = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are an AI energy trading assistant. "
                                "Analyze the following scenario and provide JSON analysis with: "
                                "1. Market conditions (supply/demand), 2. Price trends, 3. Best available offers, 4. Timing recommendations. "
                                "Consider user preferences, weather, and all provided parameters."
                            )
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"User ID: {state.user_id}\n"
                                f"Energy needed: {state.energy_amount} kWh\n"
                                f"Energy type: {state.energy_type}\n"
                                f"Max price: ${state.max_price}/kWh\n"
                                f"Location: {state.location}\n"
                                f"Preferences: {json.dumps(state.preferences)}\n"
                                f"Weather: [dummy: sunny, 32C, high solar output]\n"
                                f"Market offers: {json.dumps(state.market_data, indent=2)}"
                            )
                        }
                    ]
                }
            ]
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=market_prompt,
                max_tokens=1200,
                temperature=0.6,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False
            )
            response_content = completion.choices[0].message.content if completion.choices else "{}"
            # Parse LLM response and update state
            state.messages.append(HumanMessage(content=str(market_prompt)))
            state.messages.append(AIMessage(content=response_content))
            # Filter and rank offers based on analysis (dummy logic for now)
            filtered_offers = self._filter_offers(state.market_data, state)
            state.market_data = filtered_offers
            state.status = "offers_analyzed"
            logger.info(f"Market analysis complete. Found {len(filtered_offers)} suitable offers")
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            state.status = "analysis_failed"
        return state
    
    def _filter_offers(self, offers: List[Dict], state: EnergyTradingState) -> List[Dict]:
        """Filter offers based on user preferences"""
        filtered = []
        
        for offer in offers:
            # Price filter
            if offer.get('price_per_kwh', 0) > state.max_price:
                continue
            
            # Energy type filter
            if state.energy_type != 'any' and offer.get('energy_type') != state.energy_type:
                continue
            
            # Quantity filter
            if offer.get('energy_amount_kwh', 0) < state.energy_amount:
                continue
            
            # Calculate distance (simplified)
            offer_location = offer.get('location', {})
            if offer_location:
                distance = self._calculate_distance(state.location, offer_location)
                offer['distance_km'] = distance
                
                # Distance filter (within 50km)
                if distance > 50:
                    continue
            
            filtered.append(offer)
        
        # Sort by best value (price, distance, energy type match)
        return sorted(filtered, key=lambda x: (
            x.get('price_per_kwh', 999),
            x.get('distance_km', 999),
            0 if x.get('energy_type') == state.energy_type else 1
        ))
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Simple distance calculation (in reality, use proper geo-distance)"""
        lat_diff = abs(loc1.get('lat', 0) - loc2.get('lat', 0))
        lng_diff = abs(loc1.get('lng', 0) - loc2.get('lng', 0))
        return (lat_diff + lng_diff) * 111  # Rough km conversion


class RecommendationEngine:
    """Generates personalized energy trading recommendations"""
    
    def __init__(self, azure_client=None):
        self.client = azure_client
    
    async def generate_recommendations(self, state: EnergyTradingState) -> EnergyTradingState:
        """Generate trading recommendations"""
        try:
            logger.info(f"Generating recommendations for user {state.user_id}")
            
            recommendation_prompt = f"""
            Based on the market analysis, generate personalized trading recommendations for:
            
            User Requirements:
            - Energy needed: {state.energy_amount} kWh
            - Energy type: {state.energy_type}
            - Max price: ${state.max_price}/kWh
            - User preferences: {state.preferences}
            
            Available Offers:
            {json.dumps(state.market_data[:5], indent=2)}  # Top 5 offers
            
            Generate 3 trading recommendations with:
            1. Recommended offer details
            2. Reasoning for recommendation
            3. Potential savings/benefits
            4. Risk assessment
            5. Optimal timing
            
            Respond in JSON format with recommendations array.
            """
            
            response = await self.client.ainvoke([HumanMessage(content=recommendation_prompt)])
            
            # Parse recommendations from LLM response
            try:
                recommendations_text = response.content
                # Extract JSON from response (simplified parsing)
                recommendations = self._parse_recommendations(recommendations_text, state.market_data[:3])
                state.recommendations = recommendations
            except Exception as parse_error:
                logger.warning(f"Failed to parse LLM recommendations: {parse_error}")
                # Fallback to rule-based recommendations
                state.recommendations = self._generate_fallback_recommendations(state.market_data[:3])
            
            state.messages.append(HumanMessage(content=recommendation_prompt))
            state.messages.append(response)
            state.status = "recommendations_ready"
            
            logger.info(f"Generated {len(state.recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            state.status = "recommendation_failed"
        
        return state
    
    def _parse_recommendations(self, llm_text: str, offers: List[Dict]) -> List[Dict]:
        """Parse LLM recommendations (simplified)"""
        recommendations = []
        
        for i, offer in enumerate(offers):
            recommendation = {
                "offer_id": offer.get('offer_id', f"offer_{i}"),
                "offer": offer,
                "reasoning": f"Good match for your requirements with competitive pricing",
                "savings_estimate": round((0.15 - offer.get('price_per_kwh', 0.12)) * offer.get('energy_amount_kwh', 0), 2),
                "risk_level": "low",
                "timing_recommendation": "immediate",
                "confidence_score": 0.85 - (i * 0.1)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_fallback_recommendations(self, offers: List[Dict]) -> List[Dict]:
        """Generate rule-based recommendations as fallback"""
        recommendations = []
        
        for i, offer in enumerate(offers):
            recommendation = {
                "offer_id": offer.get('offer_id', f"offer_{i}"),
                "offer": offer,
                "reasoning": "Rule-based recommendation based on price and distance",
                "savings_estimate": round((0.15 - offer.get('price_per_kwh', 0.12)) * offer.get('energy_amount_kwh', 0), 2),
                "risk_level": "low" if i == 0 else "medium",
                "timing_recommendation": "immediate" if i == 0 else "consider_timing",
                "confidence_score": 0.75 - (i * 0.15)
            }
            recommendations.append(recommendation)
        
        return recommendations


class AutoTrader:
    """Handles automated trading decisions and execution"""
    
    def __init__(self, azure_client=None, api_client=None):
        self.client = azure_client
        self.api_client = api_client
    
    async def execute_trade(self, state: EnergyTradingState) -> EnergyTradingState:
        """Execute the selected trade"""
        try:
            if not state.selected_offer:
                # Auto-select best recommendation if user hasn't chosen
                if state.recommendations:
                    state.selected_offer = state.recommendations[0]['offer']
                else:
                    state.status = "no_suitable_offers"
                    return state
            
            logger.info(f"Executing trade for user {state.user_id}")
            
            # Simulate trade execution (would call actual API)
            trade_result = await self._execute_trade_api(state.selected_offer, state)
            
            if trade_result.get('success'):
                state.transaction_id = trade_result.get('transaction_id')
                state.status = "trade_executed"
                logger.info(f"Trade executed successfully: {state.transaction_id}")
            else:
                state.status = "trade_failed"
                logger.error(f"Trade execution failed: {trade_result.get('error')}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            state.status = "trade_error"
        
        return state
    
    async def _execute_trade_api(self, offer: Dict, state: EnergyTradingState) -> Dict:
        """Simulate API call to execute trade"""
        # In real implementation, this would call the actual energy trading API
        await asyncio.sleep(0.1)  # Simulate API delay
        
        return {
            'success': True,
            'transaction_id': f"tx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{state.user_id[:8]}",
            'offer_id': offer.get('offer_id'),
            'amount': offer.get('energy_amount_kwh'),
            'price': offer.get('price_per_kwh'),
            'total_cost': offer.get('energy_amount_kwh', 0) * offer.get('price_per_kwh', 0)
        }


class EnergyTradingAgent:
    """Main energy trading agent using LangGraph workflow"""
    
    def __init__(self, openai_api_key: str):
        endpoint = os.getenv("ENDPOINT_URL", "https://sunai.openai.azure.com/")
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version="2025-01-01-preview",
        )
        
        self.market_analyzer = EnergyMarketAnalyzer()
        self.recommendation_engine = RecommendationEngine()
        self.auto_trader = AutoTrader()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for energy trading"""
        
        # Define the workflow graph
        workflow = StateGraph(EnergyTradingState)
        
        # Add nodes
        workflow.add_node("analyze_market", self.market_analyzer.analyze_market)
        workflow.add_node("generate_recommendations", self.recommendation_engine.generate_recommendations)
        workflow.add_node("execute_trade", self.auto_trader.execute_trade)
        
        # Define the flow
        workflow.set_entry_point("analyze_market")
        
        workflow.add_edge("analyze_market", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "execute_trade")
        workflow.add_edge("execute_trade", END)
        
        # Compile the workflow
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        
        return app
    
    async def process_energy_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an energy trading request"""
        try:
            logger.info(f"Processing energy request: {request}")
            
            # Create initial state
            initial_state = EnergyTradingState(
                user_id=request['user_id'],
                energy_amount=request['energy_amount'],
                energy_type=request.get('energy_type', 'any'),
                max_price=request['max_price'],
                location=request['location'],
                preferences=request.get('preferences', {}),
                market_data=request.get('market_data', []),
                messages=[]
            )
            
            # Run the workflow
            config = {"configurable": {"thread_id": f"user_{request['user_id']}"}}
            
            final_state = None
            async for state in self.workflow.astream(initial_state, config):
                final_state = state
                logger.info(f"Workflow step completed: {state}")
            
            # Extract the final state
            result_state = list(final_state.values())[0] if final_state else initial_state
            
            # Return results
            return {
                'success': True,
                'user_id': result_state.user_id,
                'status': result_state.status,
                'recommendations': result_state.recommendations,
                'selected_offer': result_state.selected_offer,
                'transaction_id': result_state.transaction_id,
                'message_count': len(result_state.messages)
            }
            
        except Exception as e:
            logger.error(f"Error processing energy request: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_id': request.get('user_id'),
                'status': 'error'
            }
    
    async def get_user_session_history(self, user_id: str) -> List[Dict]:
        """Get conversation history for a user"""
        config = {"configurable": {"thread_id": f"user_{user_id}"}}
        
        try:
            # Get checkpoint data
            checkpoint = self.workflow.get_state(config)
            if checkpoint and checkpoint.values:
                state = list(checkpoint.values.values())[0]
                return [
                    {
                        'role': 'human' if isinstance(msg, HumanMessage) else 'ai',
                        'content': msg.content,
                        'timestamp': datetime.now().isoformat()
                    }
                    for msg in state.messages
                ]
        except Exception as e:
            logger.error(f"Error retrieving session history: {e}")
        
        return []
