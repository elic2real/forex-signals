from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import os
from typing import Dict, Any

from .api import health, signals, notifications
from .core.config import settings
from .core.logging import setup_logging
from .services.signal_engine import SignalEngine
from .services.oanda_client import OandaClient
from .services.fcm_service import FCMService

# Setup structured logging
setup_logging()
logger = structlog.get_logger()

# Global services
signal_engine: SignalEngine = None
oanda_client: OandaClient = None
fcm_service: FCMService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global signal_engine, oanda_client, fcm_service
    
    logger.info("starting_trading_signal_backend", version=settings.VERSION)
    
    # Initialize services
    oanda_client = OandaClient(
        api_key=settings.OANDA_API_KEY,
        account_id=settings.OANDA_ACCOUNT_ID,
        environment=settings.OANDA_ENV
    )
    
    fcm_service = FCMService(
        project_id=settings.FIREBASE_PROJECT_ID,
        private_key=settings.FIREBASE_PRIVATE_KEY
    )
    
    signal_engine = SignalEngine(
        oanda_client=oanda_client,
        fcm_service=fcm_service,
        config=settings.TRADING_CONFIG
    )
    
    # Start signal monitoring (background task)
    await signal_engine.start_monitoring()
    
    logger.info("trading_signal_backend_ready")
    yield
    
    # Shutdown
    logger.info("shutting_down_trading_signal_backend")
    await signal_engine.stop_monitoring()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Real-time trading signal notifications via mobile push alerts",
    lifespan=lifespan
)

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, tags=["health"])
app.include_router(signals.router, prefix="/signals", tags=["signals"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "Trading signal alerting system",
        "docs": "/docs",
        "health": "/health"
    }

# Make services available to route handlers
def get_signal_engine() -> SignalEngine:
    return signal_engine

def get_oanda_client() -> OandaClient:
    return oanda_client

def get_fcm_service() -> FCMService:
    return fcm_service
