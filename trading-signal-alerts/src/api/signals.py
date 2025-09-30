from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import structlog

from ..core.constants import ErrorCodes, HTTPStatus, ErrorMessages

logger = structlog.get_logger()

router = APIRouter()

class DeviceRegistration(BaseModel):
    device_token: str
    device_type: str = "android"  # android or ios
    app_version: str = "1.0.0"

class SignalRequest(BaseModel):
    instruments: List[str] = ["EUR_USD"]

@router.post("/register-device")
async def register_device(registration: DeviceRegistration):
    """Register a mobile device for push notifications"""
    try:
        # Validation
        if not registration.device_token or len(registration.device_token) < 10:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, 
                detail=ErrorMessages.INVALID_FCM_TOKEN
            )
        
        # Import here to avoid circular dependency
        from ..main import get_signal_engine
        
        signal_engine = get_signal_engine()
        if not signal_engine:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE, 
                detail=ErrorMessages.SERVICE_UNAVAILABLE
            )
        
        signal_engine.register_device(registration.device_token)
        
        logger.info("device_registered_via_api", 
                   device_type=registration.device_type,
                   app_version=registration.app_version)
        
        return {
            "success": True,
            "error_code": ErrorCodes.SUCCESS,
            "message": "Device registered for trading signals",
            "device_token_preview": registration.device_token[:20] + "..."
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error("device_registration_failed", error=str(e))
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=ErrorMessages.INTERNAL_ERROR
        )

@router.post("/unregister-device")
async def unregister_device(registration: DeviceRegistration):
    """Unregister a mobile device"""
    try:
        from ..main import get_signal_engine
        
        signal_engine = get_signal_engine()
        if not signal_engine:
            raise HTTPException(status_code=503, detail="Signal engine not available")
        
        signal_engine.unregister_device(registration.device_token)
        
        return {
            "success": True,
            "message": "Device unregistered"
        }
        
    except Exception as e:
        logger.error("device_unregistration_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-signals")
async def get_active_signals():
    """Get current market conditions and potential signals"""
    try:
        from ..main import get_oanda_client
        
        oanda_client = get_oanda_client()
        if not oanda_client:
            raise HTTPException(status_code=503, detail="OANDA client not available")
        
        # Get current prices for watched instruments
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
        market_data = {}
        
        for instrument in instruments:
            price = await oanda_client.get_current_price(instrument)
            spread = await oanda_client.get_spread(instrument)
            positions = await oanda_client.get_open_positions(instrument)
            
            market_data[instrument] = {
                "current_price": price,
                "spread": spread,
                "has_position": positions.get("has_position", False),
                "net_units": positions.get("net_units", 0)
            }
        
        return {
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "market_data": market_data,
            "monitoring_status": "active"
        }
        
    except Exception as e:
        logger.error("active_signals_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-signal")
async def send_test_signal(signal_request: SignalRequest):
    """Send test signal to registered devices"""
    try:
        from ..main import get_signal_engine, get_fcm_service
        
        signal_engine = get_signal_engine()
        fcm_service = get_fcm_service()
        
        if not signal_engine or not fcm_service:
            raise HTTPException(status_code=503, detail="Services not available")
        
        if not signal_engine.device_tokens:
            return {
                "success": False,
                "message": "No devices registered for notifications"
            }
        
        # Create test signal
        test_signal = {
            "signal_type": "TEST",
            "instrument": signal_request.instruments[0],
            "direction": "BUY",
            "price": 1.1000,
            "sl_pips": 15,
            "tp_pips": 30,
            "confidence": 0.8,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
        
        result = await fcm_service.send_signal_notification(
            signal_engine.device_tokens,
            test_signal
        )
        
        return {
            "success": True,
            "message": "Test signal sent",
            "fcm_result": result
        }
        
    except Exception as e:
        logger.error("test_signal_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints expected by mobile app
@router.get("/")
async def get_signals():
    """Get all trading signals - endpoint expected by mobile app"""
    # This is an alias for /active-signals to match mobile app expectations
    return await get_active_signals()

@router.get("/{signal_id}")
async def get_signal_details(signal_id: str):
    """Get details for a specific signal"""
    try:
        from ..main import get_signal_engine
        
        signal_engine = get_signal_engine()
        if not signal_engine:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=ErrorMessages.SERVICE_UNAVAILABLE
            )
        
        # For now, return a sample signal - in production this would fetch from database
        return {
            "id": signal_id,
            "instrument": "EUR_USD",
            "signal_type": "buy",
            "strength": 75,
            "price": 1.1000,
            "timestamp": "2025-09-24T14:30:00Z",
            "status": "active"
        }
        
    except Exception as e:
        logger.error("get_signal_details_failed", error=str(e), signal_id=signal_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{signal_id}/action")
async def execute_signal_action(signal_id: str, action: Dict[str, Any]):
    """Execute an action on a trading signal (buy/sell/close)"""
    try:
        logger.info("signal_action_requested", 
                   signal_id=signal_id, 
                   action=action.get("action"))
        
        # For development, just return success
        # In production, this would execute actual trades via OANDA
        return {
            "success": True,
            "message": f"Action '{action.get('action')}' executed for signal {signal_id}",
            "signal_id": signal_id
        }
        
    except Exception as e:
        logger.error("signal_action_failed", error=str(e), signal_id=signal_id)
        raise HTTPException(status_code=500, detail=str(e))
