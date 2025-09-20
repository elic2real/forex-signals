from fastapi import APIRouter
from datetime import datetime
import psutil
import os
from typing import Dict, Any

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": os.getenv("VERSION", "unknown"),
        "service": "trading-signal-alerts"
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check - ensures all dependencies are available"""
    checks = {}
    
    # Check OANDA environment variables
    checks["oanda_config"] = bool(
        os.getenv("OANDA_API_KEY") and 
        os.getenv("OANDA_ACCOUNT_ID")
    )
    
    # Check Firebase configuration
    checks["firebase_config"] = bool(
        os.getenv("FIREBASE_PROJECT_ID") and 
        os.getenv("FIREBASE_PRIVATE_KEY")
    )
    
    # System resources
    checks["cpu_available"] = psutil.cpu_percent() < 80
    checks["memory_available"] = psutil.virtual_memory().percent < 80
    
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def basic_metrics() -> Dict[str, Any]:
    """Basic metrics endpoint for monitoring"""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
        "timestamp": datetime.utcnow().isoformat()
    }
