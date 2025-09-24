from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
signal_engine: SignalEngine | None = None
oanda_client: OandaClient | None = None
fcm_service: FCMService | None = None

# Simplified startup - initialize on first request instead of startup
def initialize_services():
    global signal_engine, oanda_client, fcm_service
    
    if signal_engine is None:
        logger.info("initializing_services")
        
        # Initialize services with error handling - use test/development mode
        try:
            # For development, use test configurations that won't fail
            oanda_client = OandaClient(
                api_key=settings.OANDA_API_KEY or "test_key",
                account_id=settings.OANDA_ACCOUNT_ID or "test_account",
                environment=settings.OANDA_ENV or "practice"
            )
            
            fcm_service = FCMService(
                project_id=settings.FIREBASE_PROJECT_ID or "test_project",
                private_key=settings.FIREBASE_PRIVATE_KEY or "test_key"
            )
            
            signal_engine = SignalEngine(
                oanda_client=oanda_client,
                fcm_service=fcm_service,
                config=settings.TRADING_CONFIG
            )
            
            logger.info("services_initialized_successfully")
        except Exception as e:
            logger.error("service_initialization_failed", error=str(e))
            # Don't raise for development - allow health check to work
            logger.warning("running_in_development_mode_without_full_services")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Real-time trading signal notifications via mobile push alerts"
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
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "Trading signal alerting system",
        "docs": "/docs",
        "health": "/health"
    }

# Make services available to route handlers - initialize on first access
def get_signal_engine() -> SignalEngine:
    initialize_services()
    if signal_engine is None:
        raise HTTPException(status_code=503, detail="Signal engine not available in development mode")
    return signal_engine

def get_oanda_client() -> OandaClient:
    initialize_services()
    if oanda_client is None:
        raise HTTPException(status_code=503, detail="OANDA client not available in development mode")
    return oanda_client

def get_fcm_service() -> FCMService:
    initialize_services()
    if fcm_service is None:
        raise HTTPException(status_code=503, detail="FCM service not available in development mode")
    return fcm_service
