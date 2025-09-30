"""
Firebase Cloud Messaging (FCM) notification sender.
Sends push notifications to mobile devices when trading signals are generated.
"""

import json
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class NotificationSender:
    def __init__(self, server_key: str, device_tokens: List[str]):
        self.server_key = server_key
        self.device_tokens = device_tokens
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        
        if not server_key:
            logging.warning("FCM server key not provided. Notifications will be logged only.")
        
        if not device_tokens:
            logging.warning("No device tokens provided. Notifications will be logged only.")
    
    def send_signal_notification(self, signal_data: Dict[str, Any]) -> bool:
        """Send a trading signal notification to all registered devices."""
        try:
            # Format the notification message
            title = f"🚨 {signal_data['signal_type'].upper()} Signal"
            body = self._format_signal_message(signal_data)
            
            # Prepare FCM payload
            notification_payload = {
                "title": title,
                "body": body,
                "icon": "ic_notification",
                "sound": "default"
            }
            
            data_payload = {
                "signal_type": signal_data['signal_type'],
                "instrument": signal_data['instrument'],
                "price": str(signal_data['price']),
                "timestamp": signal_data['timestamp'],
                "signal_strength": str(signal_data.get('signal_strength', 0))
            }
            
            success_count = 0
            
            # Send to each device token
            for token in self.device_tokens:
                if self._send_fcm_message(token, notification_payload, data_payload):
                    success_count += 1
            
            # Log the notification regardless of FCM success
            self._log_notification(signal_data, title, body)
            
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Failed to send signal notification: {e}")
            return False
    
    def send_exit_notification(self, exit_data: Dict[str, Any]) -> bool:
        """Send a trade exit notification."""
        try:
            title = f"📊 Exit Signal - {exit_data['instrument']}"
            body = self._format_exit_message(exit_data)
            
            notification_payload = {
                "title": title,
                "body": body,
                "icon": "ic_notification",
                "sound": "default"
            }
            
            data_payload = {
                "signal_type": "exit",
                "instrument": exit_data['instrument'],
                "exit_reason": exit_data.get('reason', 'unknown'),
                "timestamp": exit_data['timestamp']
            }
            
            success_count = 0
            
            for token in self.device_tokens:
                if self._send_fcm_message(token, notification_payload, data_payload):
                    success_count += 1
            
            self._log_notification(exit_data, title, body)
            
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Failed to send exit notification: {e}")
            return False
    
    def _send_fcm_message(self, device_token: str, notification: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Send FCM message to a specific device token."""
        if not self.server_key:
            return False
        
        try:
            headers = {
                'Authorization': f'key={self.server_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'to': device_token,
                'notification': notification,
                'data': data,
                'priority': 'high'
            }
            
            response = requests.post(self.fcm_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') == 1:
                    logging.info(f"FCM notification sent successfully to device")
                    return True
                else:
                    logging.warning(f"FCM notification failed: {result}")
                    return False
            else:
                logging.error(f"FCM request failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending FCM message: {e}")
            return False
    
    def _format_signal_message(self, signal_data: Dict[str, Any]) -> str:
        """Format trading signal into a readable message."""
        instrument = signal_data['instrument']
        signal_type = signal_data['signal_type'].upper()
        price = signal_data['price']
        
        message = f"{instrument} - {signal_type} at {price:.5f}"
        
        if 'sl_pips' in signal_data:
            message += f" | SL: {signal_data['sl_pips']} pips"
        
        if 'tp_pips' in signal_data:
            message += f" | TP: {signal_data['tp_pips']} pips"
        
        if 'confidence' in signal_data:
            message += f" | Confidence: {signal_data['confidence']:.1%}"
        
        return message
    
    def _format_exit_message(self, exit_data: Dict[str, Any]) -> str:
        """Format exit signal into a readable message."""
        instrument = exit_data['instrument']
        reason = exit_data.get('reason', 'Signal changed')
        
        message = f"{instrument} - {reason}"
        
        if 'current_price' in exit_data:
            message += f" at {exit_data['current_price']:.5f}"
        
        return message
    
    def _log_notification(self, signal_data: Dict[str, Any], title: str, body: str):
        """Log notification details for debugging and record keeping."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {
            "timestamp": timestamp,
            "title": title,
            "body": body,
            "signal_data": signal_data,
            "devices_targeted": len(self.device_tokens)
        }
        
        logging.info(f"NOTIFICATION SENT: {title} - {body}")
        
        # Optionally save to file for audit trail
        try:
            import os
            os.makedirs("logs", exist_ok=True)
            with open("logs/notifications.json", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logging.warning(f"Failed to log notification to file: {e}")
    
    def test_notification(self) -> bool:
        """Send a test notification to verify FCM setup."""
        test_data = {
            "signal_type": "test",
            "instrument": "EUR_USD",
            "price": 1.12345,
            "timestamp": datetime.now().isoformat(),
            "signal_strength": 1.0
        }
        
        return self.send_signal_notification(test_data)
