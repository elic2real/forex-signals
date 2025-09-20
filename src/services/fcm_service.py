"""Firebase Cloud Messaging service for push notifications"""

import structlog
import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Any, Optional
import json
import os

logger = structlog.get_logger()

class FCMService:
    def __init__(self, project_id: str, private_key: str):
        self.project_id = project_id
        self.private_key = private_key
        self._initialized = False
        self._init_firebase()
    
    def _init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                # Create credentials from private key
                if self.private_key.startswith('{'):
                    # JSON string
                    cred_dict = json.loads(self.private_key)
                else:
                    # File path
                    cred_dict = json.load(open(self.private_key))
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred, {
                    'projectId': self.project_id,
                })
            
            self._initialized = True
            logger.info("firebase_initialized", project_id=self.project_id)
            
        except Exception as e:
            logger.error("firebase_init_failed", error=str(e))
            self._initialized = False
    
    async def send_signal_notification(
        self, 
        device_tokens: List[str], 
        signal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send trading signal notification to mobile devices"""
        
        if not self._initialized:
            logger.error("fcm_not_initialized")
            return {"success": False, "error": "FCM not initialized"}
        
        try:
            # Create notification message
            title = f"{signal_data['signal_type']} Signal"
            body = f"{signal_data['instrument']}: {signal_data['direction']} at {signal_data['price']}"
            
            # Create FCM message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={
                    "signal_type": signal_data['signal_type'],
                    "instrument": signal_data['instrument'],
                    "direction": signal_data['direction'],
                    "price": str(signal_data['price']),
                    "timestamp": signal_data['timestamp'],
                    "sl_pips": str(signal_data.get('sl_pips', '')),
                    "tp_pips": str(signal_data.get('tp_pips', '')),
                    "confidence": str(signal_data.get('confidence', 0.0))
                },
                tokens=device_tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_signal',
                        color='#2196F3',
                        sound='signal_sound',
                        channel_id='trading_signals'
                    )
                )
            )
            
            # Send message
            response = messaging.send_multicast(message)
            
            success_count = response.success_count
            failure_count = response.failure_count
            
            logger.info(
                "signal_notification_sent",
                success_count=success_count,
                failure_count=failure_count,
                signal_type=signal_data['signal_type'],
                instrument=signal_data['instrument']
            )
            
            return {
                "success": True,
                "success_count": success_count,
                "failure_count": failure_count,
                "responses": response.responses
            }
            
        except Exception as e:
            logger.error("signal_notification_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def send_test_notification(self, device_token: str) -> Dict[str, Any]:
        """Send test notification to verify FCM setup"""
        
        if not self._initialized:
            return {"success": False, "error": "FCM not initialized"}
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Trading Signals Test",
                    body="Your notification setup is working!"
                ),
                data={
                    "test": "true",
                    "timestamp": str(int(__import__('time').time()))
                },
                token=device_token
            )
            
            response = messaging.send(message)
            
            logger.info("test_notification_sent", message_id=response)
            
            return {
                "success": True,
                "message_id": response
            }
            
        except Exception as e:
            logger.error("test_notification_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def subscribe_to_topic(self, device_tokens: List[str], topic: str) -> Dict[str, Any]:
        """Subscribe devices to a topic for broadcast notifications"""
        
        if not self._initialized:
            return {"success": False, "error": "FCM not initialized"}
        
        try:
            response = messaging.subscribe_to_topic(device_tokens, topic)
            
            logger.info(
                "devices_subscribed_to_topic",
                topic=topic,
                success_count=response.success_count,
                failure_count=response.failure_count
            )
            
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
            
        except Exception as e:
            logger.error("topic_subscription_failed", error=str(e))
            return {"success": False, "error": str(e)}
