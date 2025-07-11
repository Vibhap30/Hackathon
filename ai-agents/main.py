"""
PowerShare AI Agents Service
FastAPI service for managing AI agents with LangGraph workflows
"""

import os
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import structlog
from contextlib import asynccontextmanager

from agents.energy_trading_agent import EnergyTradingAgent
from workflows.energy_optimization import EnergyOptimizationWorkflow

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global agents
energy_agent = None
optimization_workflow = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global energy_agent, optimization_workflow, redis_client
    
    # Startup
    logger.info("Starting AI Agents Service")
    
    # Initialize Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url, decode_responses=True)
    
    # Initialize AI agents using Azure OpenAI env variables
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    if not azure_api_key or not azure_endpoint or not azure_deployment:
        logger.error("Azure OpenAI environment variables not set")
        raise ValueError("Azure OpenAI environment variables are required")

    api_base_url = os.getenv("API_URL", "http://backend:8000")

    # Pass env variables or let agent classes pick up from os.environ
    energy_agent = EnergyTradingAgent()
    optimization_workflow = EnergyOptimizationWorkflow()
    logger.info("AI Agents initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Agents Service")
    if redis_client:
        redis_client.close()

# Create FastAPI app
app = FastAPI(
    title="PowerShare AI Agents",
    description="AI-powered energy trading and optimization agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class EnergyTradingRequest(BaseModel):
    user_id: str
    energy_amount: float
    energy_type: str = "any"
    max_price: float
    location: Dict[str, float]  # {"lat": float, "lng": float}
    preferences: Dict[str, Any] = {}
    market_data: List[Dict[str, Any]] = []

class AgentResponse(BaseModel):
    success: bool
    agent_id: str
    user_id: str
    status: str
    data: Dict[str, Any] = {}
    error: str = None
    timestamp: str

class SessionHistoryRequest(BaseModel):
    user_id: str
    agent_type: str = "energy_trading"

class EnergyOptimizationRequest(BaseModel):
    user_id: str
    optimization_goals: List[str] = ["cost_minimization"]
    location: Dict[str, float] = {}
    preferences: Dict[str, Any] = {}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_client.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "redis": "connected",
                "energy_agent": "initialized" if energy_agent else "not_initialized",
                "optimization_workflow": "initialized" if optimization_workflow else "not_initialized"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Energy trading endpoints
@app.post("/api/v1/agents/energy-trading/process", response_model=AgentResponse)
async def process_energy_trading_request(
    request: EnergyTradingRequest,
    background_tasks: BackgroundTasks
):
    """Process an energy trading request with AI agent"""
    try:
        logger.info(f"Processing energy trading request for user {request.user_id}")
        
        # Convert request to dict
        request_dict = request.dict()
        
        # Process with AI agent
        result = await energy_agent.process_energy_request(request_dict)
        
        # Store result in Redis for later retrieval
        cache_key = f"agent_result:{request.user_id}:{result.get('transaction_id', 'latest')}"
        redis_client.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(result)
        )
        
        # Schedule background tasks
        background_tasks.add_task(
            _send_result_notification,
            request.user_id,
            result
        )
        
        return AgentResponse(
            success=result['success'],
            agent_id="energy_trading_agent",
            user_id=request.user_id,
            status=result.get('status', 'unknown'),
            data=result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing energy trading request: {e}")
        return AgentResponse(
            success=False,
            agent_id="energy_trading_agent",
            user_id=request.user_id,
            status="error",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/v1/agents/energy-trading/recommendations/{user_id}")
async def get_user_recommendations(user_id: str):
    """Get AI recommendations for a user"""
    try:
        # Get cached recommendations from Redis
        cache_key = f"recommendations:{user_id}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return {
                "success": True,
                "user_id": user_id,
                "recommendations": json.loads(cached_data),
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # If no cached data, return empty recommendations
        return {
            "success": True,
            "user_id": user_id,
            "recommendations": [],
            "cached": False,
            "message": "No recommendations available. Submit an energy request to get AI recommendations.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/session-history", response_model=Dict[str, Any])
async def get_session_history(request: SessionHistoryRequest):
    """Get conversation history for a user session"""
    try:
        logger.info(f"Getting session history for user {request.user_id}")
        
        if request.agent_type == "energy_trading":
            history = await energy_agent.get_user_session_history(request.user_id)
        else:
            history = []
        
        return {
            "success": True,
            "user_id": request.user_id,
            "agent_type": request.agent_type,
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market analysis endpoints
@app.get("/api/v1/agents/market-analysis")
async def get_market_analysis():
    """Get current market analysis from AI agents"""
    try:
        # Get cached market analysis
        cache_key = "market_analysis:latest"
        cached_analysis = redis_client.get(cache_key)
        
        if cached_analysis:
            analysis = json.loads(cached_analysis)
        else:
            # Generate new analysis (simplified)
            analysis = {
                "market_conditions": "stable",
                "average_price": 0.12,
                "price_trend": "slightly_increasing",
                "supply_demand_ratio": 1.2,
                "recommendations": [
                    "Consider immediate purchases for solar energy",
                    "Wind energy prices expected to drop next week",
                    "Peak hours show higher demand - avoid 6-8 PM"
                ],
                "last_updated": datetime.now().isoformat()
            }
            
            # Cache for 15 minutes
            redis_client.setex(cache_key, 900, json.dumps(analysis))
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent management endpoints
@app.get("/api/v1/agents/status")
async def get_agents_status():
    """Get status of all AI agents"""
    try:
        return {
            "success": True,
            "agents": {
                "energy_trading": {
                    "status": "active" if energy_agent else "inactive",
                    "description": "AI agent for energy trading optimization and recommendations"
                },
                "energy_optimization": {
                    "status": "active" if optimization_workflow else "inactive",
                    "description": "Comprehensive energy optimization workflow with market analysis, weather insights, and community recommendations"
                }
            },
            "system": {
                "redis_connected": redis_client.ping() if redis_client else False,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/reset-session/{user_id}")
async def reset_user_session(user_id: str):
    """Reset AI agent session for a user"""
    try:
        # Clear Redis cache for user
        pattern = f"*{user_id}*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        
        logger.info(f"Reset session for user {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "Session reset successfully",
            "cleared_keys": len(keys),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resetting session for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Energy optimization endpoints
@app.post("/api/v1/agents/energy-optimization/analyze", response_model=AgentResponse)
async def analyze_energy_optimization(
    request: EnergyOptimizationRequest,
    background_tasks: BackgroundTasks
):
    """Run comprehensive energy optimization analysis"""
    try:
        logger.info(f"Starting energy optimization analysis for user {request.user_id}")
        
        # Convert request to dict
        request_dict = request.dict()
        
        # Run optimization workflow
        result = await optimization_workflow.run_optimization(request_dict)
        
        # Store result in Redis
        cache_key = f"optimization_result:{request.user_id}:latest"
        redis_client.setex(
            cache_key,
            7200,  # 2 hours TTL
            json.dumps(result)
        )
        
        # Schedule background notification
        background_tasks.add_task(
            _send_optimization_notification,
            request.user_id,
            result
        )
        
        return AgentResponse(
            success=result['success'],
            agent_id="energy_optimization_workflow",
            user_id=request.user_id,
            status=result.get('status', 'unknown'),
            data=result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in energy optimization analysis: {e}")
        return AgentResponse(
            success=False,
            agent_id="energy_optimization_workflow",
            user_id=request.user_id,
            status="error",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/v1/agents/energy-optimization/results/{user_id}")
async def get_optimization_results(user_id: str):
    """Get latest optimization results for a user"""
    try:
        cache_key = f"optimization_result:{user_id}:latest"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            result = json.loads(cached_result)
            return {
                "success": True,
                "user_id": user_id,
                "results": result,
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "user_id": user_id,
            "results": None,
            "cached": False,
            "message": "No optimization results available. Run analysis first.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/energy-optimization/action-items/{user_id}")
async def get_user_action_items(user_id: str):
    """Get AI-generated action items for a user"""
    try:
        cache_key = f"optimization_result:{user_id}:latest"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            result = json.loads(cached_result)
            action_items = result.get("action_items", [])
            
            return {
                "success": True,
                "user_id": user_id,
                "action_items": action_items,
                "count": len(action_items),
                "generated_at": result.get("generated_at"),
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "user_id": user_id,
            "action_items": [],
            "count": 0,
            "message": "No action items available. Run optimization analysis first.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting action items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
async def _send_result_notification(user_id: str, result: Dict[str, Any]):
    """Send notification about agent processing result"""
    try:
        # This would integrate with the notifications microservice
        notification_data = {
            "user_id": user_id,
            "type": "agent_result",
            "title": "Energy Trading Analysis Complete",
            "message": f"Your energy trading request has been processed. Status: {result.get('status')}",
            "data": result
        }
        
        # Store notification in Redis for notifications service to pick up
        redis_client.lpush("notifications_queue", json.dumps(notification_data))
        
        logger.info(f"Queued notification for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")

async def _send_optimization_notification(user_id: str, result: Dict[str, Any]):
    """Send notification about optimization analysis result"""
    try:
        # Create detailed notification for optimization results
        savings_estimate = result.get("estimated_monthly_savings", 0)
        carbon_reduction = result.get("estimated_carbon_reduction", 0)
        action_count = len(result.get("action_items", []))
        
        notification_data = {
            "user_id": user_id,
            "type": "optimization_complete",
            "title": "Energy Optimization Analysis Complete",
            "message": f"Your personalized energy plan is ready! Potential savings: ${savings_estimate}/month, Carbon reduction: {carbon_reduction}kg/month, {action_count} action items to review.",
            "data": {
                "savings_estimate": savings_estimate,
                "carbon_reduction": carbon_reduction,
                "action_items_count": action_count,
                "status": result.get("status")
            }
        }
        
        # Store notification in Redis for notifications service
        redis_client.lpush("notifications_queue", json.dumps(notification_data))
        
        logger.info(f"Queued optimization notification for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending optimization notification: {e}")

# WebSocket support for real-time updates
@app.websocket("/ws/agents/{user_id}")
async def websocket_endpoint(websocket, user_id: str):
    """WebSocket endpoint for real-time agent updates"""
    await websocket.accept()
    
    try:
        logger.info(f"WebSocket connection established for user {user_id}")
        
        while True:
            # Listen for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            elif message.get("type") == "request_status":
                # Send current status from Redis
                cache_key = f"agent_result:{user_id}:latest"
                cached_result = redis_client.get(cache_key)
                
                if cached_result:
                    result = json.loads(cached_result)
                    await websocket.send_text(json.dumps({
                        "type": "status_update",
                        "data": result,
                        "timestamp": datetime.now().isoformat()
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "status_update",
                        "data": {"status": "no_active_requests"},
                        "timestamp": datetime.now().isoformat()
                    }))
            
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        logger.info(f"WebSocket connection closed for user {user_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )
