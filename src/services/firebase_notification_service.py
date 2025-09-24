"""
Firebase Admin SDK integration for sending push notifications
This will be used by the backend to send notifications to mobile devices
"""

import os
import json
import logging
from typing import Dict, List, Optional
from firebase_admin import credentials, messaging, initialize_app
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)

class FirebaseNotificationService:
    """Service for sending Firebase Cloud Messaging notifications"""
    
    def __init__(self, service_account_path: Optional[str] = None):
        """
        Initialize Firebase Admin SDK
        
        Args:
            service_account_path: Path to Firebase service account JSON file
        """
        self.app = None
        self.initialized = False
        
        try:
            # Production: Use environment variable for service account path
            if not service_account_path:
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 
                                               'config/firebase-service-account.json')
            
            if service_account_path and os.path.exists(service_account_path):
                # Initialize with service account file
                cred = credentials.Certificate(service_account_path)
                self.app = initialize_app(cred)
                self.initialized = True
                logger.info("Firebase initialized with production service account")
            else:
                # Try to initialize with default credentials or environment
                try:
                    # Production: Use Google Application Default Credentials
                    self.app = initialize_app()
                    self.initialized = True
                    logger.info("Firebase initialized with default credentials")
                except Exception as e:
                    logger.warning(f"Could not initialize Firebase: {e}")
                    logger.info("Firebase notifications will be disabled - check service account configuration")
                    
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.initialized = False
    
    def send_trading_signal_notification(
        self, 
        token: str, 
        signal_data: Dict,
        test_mode: bool = False
    ) -> bool:
        """
        Send trading signal notification to device
        
        Args:
            token: FCM device token
            signal_data: Trading signal information
            test_mode: If True, sends a test notification
            
        Returns:
            bool: True if notification sent successfully
        """
        if not self.initialized:
            logger.warning("Firebase not initialized, cannot send notification")
            return False
        
        try:
            if test_mode:
                # Send test notification
                message = messaging.Message(
                    notification=messaging.Notification(
                        title="🧪 Test Notification",
                        body="Trading Signal Alerts is working!"
                    ),
                    token=token,
                    android=messaging.AndroidConfig(
                        notification=messaging.AndroidNotification(
                            channel_id="trading_signals",
                            priority="high"
                        )
                    )
                )
            else:
                # Send actual trading signal notification
                title = f"{signal_data.get('signal_type', 'SIGNAL')}: {signal_data.get('instrument', 'Unknown')}"
                body = f"Confidence: {signal_data.get('confidence', 0)*100:.1f}%"
                
                if signal_data.get('reason'):
                    body += f" | {signal_data.get('reason')}"
                
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data={
                        'type': 'trading_signal',
                        'signal_data': json.dumps(signal_data),
                        'signal_id': signal_data.get('id', ''),
                        'instrument': signal_data.get('instrument', ''),
                        'signal_type': signal_data.get('signal_type', ''),
                        'confidence': str(signal_data.get('confidence', 0))
                    },
                    token=token,
                    android=messaging.AndroidConfig(
                        notification=messaging.AndroidNotification(
                            channel_id="trading_signals",
                            priority="high",
                            default_sound=True,
                            default_vibrate_timings=True
                        )
                    )
                )
            
            # Send the message
            response = messaging.send(message)
            logger.info(f"Successfully sent message: {response}")
            return True
            
        except FirebaseError as e:
            logger.error(f"Firebase error sending notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending notification: {e}")
            return False
    
    def send_signal_update_notification(
        self, 
        token: str, 
        signal_id: str,
        update_type: str,
        instrument: str
    ) -> bool:
        """
        Send signal update notification (take profit hit, stop loss, etc.)
        
        Args:
            token: FCM device token
            signal_id: Signal identifier
            update_type: Type of update (take_profit_hit, stop_loss_hit, expired)
            instrument: Trading instrument
            
        Returns:
            bool: True if notification sent successfully
        """
        if not self.initialized:
            logger.warning("Firebase not initialized, cannot send notification")
            return False
        
        try:
            # Determine title and body based on update type
            if update_type == "take_profit_hit":
                title = "✅ Take Profit Hit!"
                body = f"{instrument} signal closed with profit"
            elif update_type == "stop_loss_hit":
                title = "❌ Stop Loss Hit"
                body = f"{instrument} signal closed with loss"
            elif update_type == "expired":
                title = "⏰ Signal Expired"
                body = f"{instrument} signal has expired"
            else:
                title = "📊 Signal Update"
                body = f"{instrument} signal updated"
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={
                    'type': 'signal_update',
                    'signal_id': signal_id,
                    'update_type': update_type,
                    'instrument': instrument
                },
                token=token,
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        channel_id="signal_updates",
                        priority="default"
                    )
                )
            )
            
            response = messaging.send(message)
            logger.info(f"Successfully sent update notification: {response}")
            return True
            
        except FirebaseError as e:
            logger.error(f"Firebase error sending update notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending update notification: {e}")
            return False
    
    def send_bulk_notifications(
        self, 
        tokens: List[str], 
        signal_data: Dict
    ) -> Dict[str, bool]:
        """
        Send notifications to multiple devices
        
        Args:
            tokens: List of FCM device tokens
            signal_data: Trading signal information
            
        Returns:
            Dict mapping token to success status
        """
        if not self.initialized:
            logger.warning("Firebase not initialized, cannot send notifications")
            return {token: False for token in tokens}
        
        results = {}
        
        for token in tokens:
            success = self.send_trading_signal_notification(token, signal_data)
            results[token] = success
        
        success_count = sum(results.values())
        logger.info(f"Sent notifications to {success_count}/{len(tokens)} devices")
        
        return results
    
    def validate_token(self, token: str) -> bool:
        """
        Validate if FCM token is properly formatted
        
        Args:
            token: FCM device token
            
        Returns:
            bool: True if token appears valid
        """
        if not token or not isinstance(token, str):
            return False
        
        # Basic FCM token validation (tokens are typically 152+ characters)
        if len(token) < 100:
            return False
        
        # FCM tokens are alphanumeric with some special characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:')
        if not all(c in allowed_chars for c in token):
            return False
        
        return True

# Global instance
firebase_service = None

def get_firebase_service() -> FirebaseNotificationService:
    """Get global Firebase service instance"""
    global firebase_service
    if firebase_service is None:
        # Try to find service account file
        service_account_paths = [
            "firebase_service_account.json",
            "config/firebase_service_account.json",
            os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        ]
        
        service_account_path = None
        for path in service_account_paths:
            if path and os.path.exists(path):
                service_account_path = path
                break
        
        firebase_service = FirebaseNotificationService(service_account_path)
    
    return firebase_service
