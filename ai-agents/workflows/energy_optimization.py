"""
AI Agent Workflows for PowerShare Platform
LangGraph workflows for complex energy trading scenarios
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import structlog

from tools.platform_tools import PowerShareAPITool, WeatherTool, PriceAnalysisTool, CommunityTool

logger = structlog.get_logger()


@dataclass
class EnergyOptimizationState:
    """State for comprehensive energy optimization workflow"""
    user_id: str
    optimization_goals: List[str]  # ["cost_minimization", "sustainability", "community_engagement"]
    user_profile: Dict[str, Any] = field(default_factory=dict)
    location: Dict[str, float] = field(default_factory=dict)
    energy_usage_history: List[Dict[str, Any]] = field(default_factory=list)
    weather_forecast: Dict[str, Any] = field(default_factory=dict)
    market_analysis: Dict[str, Any] = field(default_factory=dict)
    community_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    optimization_plan: Dict[str, Any] = field(default_factory=dict)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "initializing"
    messages: List[BaseMessage] = field(default_factory=list)


class EnergyOptimizationWorkflow:
    """Comprehensive energy optimization workflow using LangGraph"""
    
    def __init__(self, api_base_url: str = "http://backend:8000"):
        # Use Azure OpenAI env variables
        import os
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        self.llm = ChatOpenAI(
            model=azure_deployment,
            api_key=azure_api_key,
            base_url=azure_endpoint,
            api_version=azure_api_version,
            temperature=0.2
        )
        # Initialize tools
        self.api_tool = PowerShareAPITool(api_base_url)
        self.weather_tool = WeatherTool()
        self.price_tool = PriceAnalysisTool()
        self.community_tool = CommunityTool(self.api_tool)
        # Build workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the comprehensive optimization workflow"""
        
        workflow = StateGraph(EnergyOptimizationState)
        
        # Add nodes
        workflow.add_node("gather_user_data", self._gather_user_data)
        workflow.add_node("analyze_energy_patterns", self._analyze_energy_patterns)
        workflow.add_node("get_weather_insights", self._get_weather_insights)
        workflow.add_node("analyze_market_conditions", self._analyze_market_conditions)
        workflow.add_node("find_communities", self._find_communities)
        workflow.add_node("generate_optimization_plan", self._generate_optimization_plan)
        workflow.add_node("create_action_items", self._create_action_items)
        
        # Define flow
        workflow.set_entry_point("gather_user_data")
        workflow.add_edge("gather_user_data", "analyze_energy_patterns")
        workflow.add_edge("analyze_energy_patterns", "get_weather_insights")
        workflow.add_edge("get_weather_insights", "analyze_market_conditions")
        workflow.add_edge("analyze_market_conditions", "find_communities")
        workflow.add_edge("find_communities", "generate_optimization_plan")
        workflow.add_edge("generate_optimization_plan", "create_action_items")
        workflow.add_edge("create_action_items", END)
        
        # Compile workflow
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    async def _gather_user_data(self, state: EnergyOptimizationState) -> EnergyOptimizationState:
        """Gather comprehensive user data"""
        try:
            logger.info(f"Gathering user data for {state.user_id}")
            
            # Get user profile
            state.user_profile = await self.api_tool.get_user_profile(state.user_id) or {}
            
            # Get energy usage history
            state.energy_usage_history = await self.api_tool.get_user_energy_history(state.user_id, days=30)
            
            # Extract location from profile
            if "location" in state.user_profile:
                state.location = state.user_profile["location"]
            
            state.status = "data_gathered"
            logger.info(f"User data gathered for {state.user_id}")
            
        except Exception as e:
            logger.error(f"Error gathering user data: {e}")
            state.status = "data_gathering_failed"
        
        return state
    
    async def _analyze_energy_patterns(self, state: EnergyOptimizationState) -> EnergyOptimizationState:
        """Analyze user's energy consumption and production patterns"""
        try:
            logger.info(f"Analyzing energy patterns for {state.user_id}")
            
            if not state.energy_usage_history:
                state.status = "insufficient_data"
                return state
            
            # Use LLM to analyze patterns
            analysis_prompt = f"""
            Analyze the following energy usage data for insights and patterns:
            
            User Profile: {json.dumps(state.user_profile, indent=2)}
            Energy Usage History (last 30 days): {json.dumps(state.energy_usage_history[-10:], indent=2)}
            
            Optimization Goals: {state.optimization_goals}
            
            Provide analysis on:
            1. Usage patterns (peak times, seasonal trends)
            2. Efficiency opportunities
            3. Renewable energy potential
            4. Cost optimization areas
            5. Sustainability improvements
            
            Respond in JSON format with detailed analysis.
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            
            # Store analysis in messages
            state.messages.extend([
                HumanMessage(content=analysis_prompt),
                response
            ])
            
            state.status = "patterns_analyzed"
            logger.info(f"Energy patterns analyzed for {state.user_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing energy patterns: {e}")
            state.status = "pattern_analysis_failed"
        
        return state
    
    async def _get_weather_insights(self, state: EnergyOptimizationState) -> EnergyOptimizationState:
        """Get weather data and renewable energy insights"""
        try:
            logger.info(f"Getting weather insights for {state.user_id}")
            
            if not state.location:
                logger.warning("No location data available for weather analysis")
                state.status = "weather_skipped"
                return state
            
            # Get weather forecast
            state.weather_forecast = await self.weather_tool.get_weather_forecast(
                state.location, days=7
            )
            
            # Calculate solar production potential if user has solar panels
            user_solar_capacity = state.user_profile.get("solar_panel_capacity_kw", 0)
            if user_solar_capacity > 0:
                solar_estimates = self.weather_tool.calculate_solar_production_estimate(
                    state.weather_forecast, user_solar_capacity
                )
                state.weather_forecast["solar_estimates"] = solar_estimates
            
            state.status = "weather_analyzed"
            logger.info(f"Weather insights gathered for {state.user_id}")
            
        except Exception as e:
            logger.error(f"Error getting weather insights: {e}")
            state.status = "weather_analysis_failed"
        
        return state
    
    async def _analyze_market_conditions(self, state: EnergyOptimizationState) -> EnergyOptimizationState:
        """Analyze current market conditions and pricing"""
        try:
            logger.info(f"Analyzing market conditions for {state.user_id}")
            
            # Get current market offers
            market_offers = await self.api_tool.get_market_offers(
                energy_type="any",
                location=state.location,
                limit=50
            )
            
            if market_offers:
                # Analyze price trends
                price_analysis = await self.price_tool.analyze_price_trends(market_offers)
                
                # Get optimal trading time prediction
                optimal_timing = await self.price_tool.predict_optimal_trading_time(
                    state.user_profile, market_offers
                )
                
                state.market_analysis = {
                    "offers": market_offers[:10],  # Store top 10 offers
                    "price_analysis": price_analysis,
                    "optimal_timing": optimal_timing,
                    "total_offers_analyzed": len(market_offers)
                }
            else:
                state.market_analysis = {
                    "offers": [],
                    "message": "No market offers available in your area"
                }
            
            state.status = "market_analyzed"
            logger.info(f"Market conditions analyzed for {state.user_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            state.status = "market_analysis_failed"
        
        return state
    
    async def _find_communities(self, state: EnergyOptimizationState) -> EnergyOptimizationState:
        """Find and recommend relevant energy communities"""
        try:
            logger.info(f"Finding communities for {state.user_id}")
            
            if not state.location:
                logger.warning("No location data for community recommendations")
                state.status = "communities_skipped"
                return state
            
            # Get community recommendations
            state.community_recommendations = await self.community_tool.recommend_communities(
                state.user_id, state.location
            )
            
            # Get stats for recommended communities
            for community in state.community_recommendations[:3]:  # Top 3
                community_stats = await self.community_tool.get_community_energy_stats(
                    community.get("community_id", "")
                )
                community["energy_stats"] = community_stats
            
            state.status = "communities_found"
            logger.info(f"Found {len(state.community_recommendations)} community recommendations")
            
        except Exception as e:
            logger.error(f"Error finding communities: {e}")
            state.status = "community_search_failed"
        
        return state
    
    async def _generate_optimization_plan(self, state: EnergyOptimizationState) -> EnergyOptimizationState:
        """Generate comprehensive energy optimization plan"""
        try:
            logger.info(f"Generating optimization plan for {state.user_id}")
            
            # Compile all data for LLM analysis
            optimization_prompt = f"""
            Create a comprehensive energy optimization plan based on the following data:
            
            User ID: {state.user_id}
            Optimization Goals: {state.optimization_goals}
            
            User Profile: {json.dumps(state.user_profile, indent=2)}
            
            Energy Usage Patterns: {len(state.energy_usage_history)} days of history available
            
            Weather Insights: {json.dumps(state.weather_forecast.get("forecast", [])[:3], indent=2)}
            
            Market Analysis: {json.dumps(state.market_analysis, indent=2)}
            
            Community Options: {len(state.community_recommendations)} communities found
            Top Community: {json.dumps(state.community_recommendations[0] if state.community_recommendations else {}, indent=2)}
            
            Generate a comprehensive optimization plan including:
            1. Short-term actions (next 7 days)
            2. Medium-term strategies (next 3 months)
            3. Long-term recommendations (next year)
            4. Cost savings estimates
            5. Sustainability impact
            6. Risk assessment
            7. Success metrics
            
            Respond in JSON format with structured recommendations.
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=optimization_prompt)])
            
            # Parse optimization plan
            try:
                # Simple parsing - in production, would use more robust JSON extraction
                plan_content = response.content
                state.optimization_plan = {
                    "generated_at": datetime.now().isoformat(),
                    "plan_summary": "Comprehensive energy optimization plan generated",
                    "confidence_score": 0.85,
                    "plan_details": plan_content,
                    "estimated_savings_monthly": self._estimate_monthly_savings(state),
                    "carbon_reduction_kg_monthly": self._estimate_carbon_reduction(state)
                }
            except Exception as parse_error:
                logger.warning(f"Failed to parse optimization plan: {parse_error}")
                state.optimization_plan = {
                    "generated_at": datetime.now().isoformat(),
                    "plan_summary": "Basic optimization plan generated",
                    "confidence_score": 0.6,
                    "plan_details": response.content
                }
            
            state.messages.extend([
                HumanMessage(content=optimization_prompt),
                response
            ])
            
            state.status = "plan_generated"
            logger.info(f"Optimization plan generated for {state.user_id}")
            
        except Exception as e:
            logger.error(f"Error generating optimization plan: {e}")
            state.status = "plan_generation_failed"
        
        return state
    
    async def _create_action_items(self, state: EnergyOptimizationState) -> EnergyOptimizationState:
        """Create specific action items from the optimization plan"""
        try:
            logger.info(f"Creating action items for {state.user_id}")
            
            action_items = []
            
            # Market-based actions
            if state.market_analysis.get("offers"):
                best_offer = state.market_analysis["offers"][0]
                action_items.append({
                    "id": "market_trade",
                    "title": "Execute Energy Trade",
                    "description": f"Consider trading with offer #{best_offer.get('offer_id')} at ${best_offer.get('price_per_kwh')}/kWh",
                    "priority": "high",
                    "timeline": "next_24_hours",
                    "type": "trading",
                    "data": best_offer
                })
            
            # Community actions
            if state.community_recommendations:
                top_community = state.community_recommendations[0]
                action_items.append({
                    "id": "join_community",
                    "title": "Join Energy Community",
                    "description": f"Join {top_community.get('name')} community for better rates and sustainability",
                    "priority": "medium",
                    "timeline": "next_week",
                    "type": "community",
                    "data": top_community
                })
            
            # Weather-based actions
            if state.weather_forecast.get("solar_estimates"):
                next_solar = state.weather_forecast["solar_estimates"][0]
                if next_solar.get("estimated_production_kwh", 0) > 10:
                    action_items.append({
                        "id": "solar_optimization",
                        "title": "Optimize Solar Production",
                        "description": f"High solar production expected tomorrow ({next_solar.get('estimated_production_kwh')} kWh)",
                        "priority": "medium",
                        "timeline": "tomorrow",
                        "type": "optimization",
                        "data": next_solar
                    })
            
            # Usage optimization actions
            if state.energy_usage_history:
                action_items.append({
                    "id": "usage_review",
                    "title": "Review Energy Usage",
                    "description": "Analyze peak usage times and identify reduction opportunities",
                    "priority": "low",
                    "timeline": "next_month",
                    "type": "analysis",
                    "data": {"avg_daily_usage": len(state.energy_usage_history)}
                })
            
            state.action_items = action_items
            state.status = "completed"
            
            logger.info(f"Created {len(action_items)} action items for {state.user_id}")
            
        except Exception as e:
            logger.error(f"Error creating action items: {e}")
            state.status = "action_creation_failed"
        
        return state
    
    def _estimate_monthly_savings(self, state: EnergyOptimizationState) -> float:
        """Estimate monthly cost savings"""
        base_savings = 0.0
        
        # Community savings
        if state.community_recommendations:
            top_community = state.community_recommendations[0]
            avg_savings = top_community.get("average_savings_percent", 0)
            base_savings += avg_savings
        
        # Market optimization savings
        if state.market_analysis.get("price_analysis"):
            volatility = state.market_analysis["price_analysis"].get("volatility", 0)
            base_savings += min(volatility * 10, 5)  # Up to 5% from timing
        
        # Solar production savings
        if state.weather_forecast.get("solar_estimates"):
            solar_potential = sum(day.get("estimated_production_kwh", 0) 
                                for day in state.weather_forecast["solar_estimates"])
            base_savings += min(solar_potential * 0.12 * 0.8, 50)  # Estimated savings
        
        return round(base_savings, 2)
    
    def _estimate_carbon_reduction(self, state: EnergyOptimizationState) -> float:
        """Estimate monthly carbon footprint reduction"""
        base_reduction = 0.0
        
        # Community renewable energy
        if state.community_recommendations:
            base_reduction += 10  # Base community benefit
        
        # Solar production
        if state.weather_forecast.get("solar_estimates"):
            solar_kwh = sum(day.get("estimated_production_kwh", 0) 
                          for day in state.weather_forecast["solar_estimates"])
            base_reduction += solar_kwh * 0.5  # ~0.5 kg CO2 per kWh
        
        return round(base_reduction, 1)
    
    async def run_optimization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete energy optimization workflow"""
        try:
            logger.info(f"Starting energy optimization for user {request['user_id']}")
            
            # Create initial state
            initial_state = EnergyOptimizationState(
                user_id=request["user_id"],
                optimization_goals=request.get("optimization_goals", ["cost_minimization"]),
                location=request.get("location", {})
            )
            
            # Run workflow
            config = {"configurable": {"thread_id": f"optimization_{request['user_id']}"}}
            
            final_state = None
            async for state in self.workflow.astream(initial_state, config):
                final_state = state
                logger.info(f"Optimization step: {list(state.keys())[0] if state else 'unknown'}")
            
            # Extract final state
            result_state = list(final_state.values())[0] if final_state else initial_state
            
            return {
                "success": True,
                "user_id": result_state.user_id,
                "status": result_state.status,
                "optimization_plan": result_state.optimization_plan,
                "action_items": result_state.action_items,
                "market_analysis": result_state.market_analysis,
                "community_recommendations": result_state.community_recommendations[:3],
                "estimated_monthly_savings": result_state.optimization_plan.get("estimated_savings_monthly", 0),
                "estimated_carbon_reduction": result_state.optimization_plan.get("carbon_reduction_kg_monthly", 0),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in energy optimization workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": request.get("user_id"),
                "status": "error"
            }
