from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()

router = APIRouter()

class TestNotification(BaseModel):
    device_token: str
    message: str = "Test notification from Trading Signals"

@router.post("/test")
async def send_test_notification(notification: TestNotification):
    """Send test notification to verify FCM setup"""
    try:
        from ..main import get_fcm_service
        
        fcm_service = get_fcm_service()
        if not fcm_service:
            raise HTTPException(status_code=503, detail="FCM service not available")
        
        result = await fcm_service.send_test_notification(notification.device_token)
        
        return {
            "success": result["success"],
            "message": "Test notification sent" if result["success"] else "Test notification failed",
            "details": result
        }
        
    except Exception as e:
        logger.error("test_notification_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def notification_status():
    """Get notification service status"""
    try:
        from ..main import get_fcm_service, get_signal_engine
        
        fcm_service = get_fcm_service()
        signal_engine = get_signal_engine()
        
        return {
            "fcm_initialized": fcm_service._initialized if fcm_service else False,
            "registered_devices": len(signal_engine.device_tokens) if signal_engine else 0,
            "monitoring_active": signal_engine.monitoring if signal_engine else False
        }
        
    except Exception as e:
        logger.error("notification_status_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
