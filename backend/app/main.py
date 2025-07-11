"""
FastAPI Main Application
PowerShare Energy Trading Platform
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import structlog
import uvicorn

from app.core.config import settings
from app.core.database import create_tables
from app.api.api_v1.api import api_router
from app.services.websocket_manager import ConnectionManager

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

# WebSocket connection manager
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting PowerShare API")
    await create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PowerShare API")

# Create FastAPI application
app = FastAPI(
    title="PowerShare API",
    description="Community Energy Trading Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <html>
        <head>
            <title>PowerShare API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2563eb; }
                .section { margin: 20px 0; }
                .link { color: #059669; text-decoration: none; }
                .link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1 class="header">⚡ PowerShare API</h1>
            <div class="section">
                <h2>Community Energy Trading Platform</h2>
                <p>RESTful API for decentralized energy trading with AI agents, blockchain integration, and Beckn Protocol support.</p>
            </div>
            <div class="section">
                <h3>📚 Documentation</h3>
                <ul>
                    <li><a href="/docs" class="link">Swagger UI Documentation</a></li>
                    <li><a href="/redoc" class="link">ReDoc Documentation</a></li>
                    <li><a href="/api/v1/health" class="link">Health Check</a></li>
                </ul>
            </div>
            <div class="section">
                <h3>🔌 Real-time Features</h3>
                <ul>
                    <li>WebSocket: <code>ws://localhost:8000/ws/[client_id]</code></li>
                    <li>Health Check: <a href="/api/v1/health" class="link">API Health</a></li>
                    <li>WebSocket Test: <a href="/api/v1/ws-test" class="link">Send Test Message</a></li>
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
        "service": "PowerShare API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication (no authentication)"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all connected clients
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client {client_id} disconnected")


@app.get("/api/v1/ws-test")
async def websocket_test():
    """Test WebSocket by sending a message to all clients"""
    await manager.broadcast("Test message from API")
    return {"message": "Test message sent to all WebSocket clients"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
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
