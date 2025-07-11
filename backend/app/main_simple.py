"""
FastAPI Main Application - Simplified Version
PowerShare Energy Trading Platform - No Authentication or WebSocket
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import structlog
import uvicorn

from app.core.config import settings
from app.core.database import create_tables

# Configure structured logging
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting PowerShare API (Simplified)")
    await create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PowerShare API")

# Create FastAPI application
app = FastAPI(
    title="PowerShare API (Simplified)",
    description="Community Energy Trading Platform API - No Authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified - allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <html>
        <head>
            <title>PowerShare API (Simplified)</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2563eb; }
                .section { margin: 20px 0; }
                .link { color: #059669; text-decoration: none; }
                .link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1 class="header">⚡ PowerShare API (Simplified)</h1>
            <div class="section">
                <h2>Community Energy Trading Platform</h2>
                <p>RESTful API for decentralized energy trading - No Authentication Required</p>
            </div>
            <div class="section">
                <h3>📚 Documentation</h3>
                <ul>
                    <li><a href="/docs" class="link">Swagger UI Documentation</a></li>
                    <li><a href="/redoc" class="link">ReDoc Documentation</a></li>
                    <li><a href="/api/v1/health" class="link">Health Check</a></li>
                </ul>
            </div>
        </body>
    </html>
    """

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PowerShare API (Simplified)",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "authentication": "disabled",
        "websocket": "disabled"
    }

# Simple energy endpoints
@app.get("/api/v1/agents")
async def get_agents():
    """Get list of available AI agents"""
    return {
        "agents": [
            {
                "id": "energy-trading-agent",
                "name": "Energy Trading Agent",
                "type": "ENERGY_TRADING",
                "status": "active",
                "description": "Optimizes energy trading decisions"
            },
            {
                "id": "market-analysis-agent", 
                "name": "Market Analysis Agent",
                "type": "MARKET_ANALYSIS",
                "status": "active",
                "description": "Analyzes energy market trends"
            },
            {
                "id": "grid-management-agent",
                "name": "Grid Management Agent", 
                "type": "GRID_MANAGEMENT",
                "status": "active",
                "description": "Manages grid operations"
            }
        ]
    }

@app.get("/api/v1/energy/transactions")
async def get_energy_transactions():
    """Get energy transactions"""
    return {
        "transactions": [
            {
                "id": "txn_001",
                "buyer": "user_123",
                "seller": "user_456", 
                "amount_kwh": 25.5,
                "price_per_kwh": 0.12,
                "timestamp": "2024-01-15T10:30:00Z",
                "status": "completed"
            },
            {
                "id": "txn_002",
                "buyer": "user_789",
                "seller": "user_123",
                "amount_kwh": 15.0,
                "price_per_kwh": 0.11,
                "timestamp": "2024-01-15T11:00:00Z", 
                "status": "completed"
            }
        ]
    }

@app.post("/api/v1/tokens/collect")
async def collect_tokens():
    """Collect gamification tokens"""
    return {
        "message": "Tokens collected successfully!",
        "tokens_earned": 50,
        "total_balance": 350,
        "token_type": "energy_credits"
    }

@app.get("/api/v1/community/stats")
async def get_community_stats():
    """Get community energy statistics"""
    return {
        "total_members": 1250,
        "active_prosumers": 340,
        "total_energy_traded_kwh": 125000,
        "carbon_saved_kg": 45000,
        "average_savings_percent": 23.5
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
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
