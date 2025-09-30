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

class DeviceRegistration(BaseModel):
    device_token: str
    device_type: str = "android"

@router.post("/register")
async def register_device_for_notifications(registration: DeviceRegistration):
    """Register device for push notifications - endpoint expected by mobile app"""
    try:
        from ..main import get_signal_engine
        
        signal_engine = get_signal_engine()
        if not signal_engine:
            raise HTTPException(status_code=503, detail="Signal engine not available")
        
        # Register the device token
        signal_engine.register_device(registration.device_token)
        
        logger.info("device_registered_for_notifications", 
                   device_type=registration.device_type)
        
        return {
            "success": True,
            "message": "Device registered for notifications",
            "device_token": registration.device_token[:20] + "..." # Partial token for security
        }
        
    except Exception as e:
        logger.error("device_registration_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
