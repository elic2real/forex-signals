"""
Development configuration for testing without Firebase
This allows us to test the system structure without real Firebase credentials
"""

import os
import json
from typing import Dict, Any

class MockFirebaseService:
    """Mock Firebase service for development testing"""
    
    def __init__(self):
        self.initialized = True
        self.project_id = "trading-signal-alerts-demo"
    
    def send_trading_signal_notification(self, token: str, signal_data: Dict, test_mode: bool = False) -> bool:
        """Mock sending trading signal notification"""
        print(f"📱 [MOCK] Would send notification to token: {token[:20]}...")
        print(f"📊 [MOCK] Signal: {signal_data.get('signal_type', 'TEST')} - {signal_data.get('instrument', 'EUR/USD')}")
        print(f"💪 [MOCK] Confidence: {signal_data.get('confidence', 0.85)*100:.1f}%")
        if test_mode:
            print("🧪 [MOCK] Test notification sent successfully!")
        return True
    
    def send_signal_update_notification(self, token: str, signal_id: str, update_type: str, instrument: str) -> bool:
        """Mock sending signal update notification"""
        print(f"📱 [MOCK] Would send {update_type} update for {instrument} (Signal ID: {signal_id})")
        return True
    
    def send_bulk_notifications(self, tokens: list, signal_data: Dict) -> Dict[str, bool]:
        """Mock sending bulk notifications"""
        print(f"📱 [MOCK] Would send notifications to {len(tokens)} devices")
        return {token: True for token in tokens}
    
    def validate_token(self, token: str) -> bool:
        """Mock token validation"""
        return len(token) > 10 if token else False

def get_development_firebase_service():
    """Get mock Firebase service for development"""
    return MockFirebaseService()

# Development configuration
DEVELOPMENT_CONFIG = {
    "firebase_enabled": False,
    "mock_notifications": True,
    "project_id": "trading-signal-alerts-demo",
    "app_id": "1:123456789012:android:abcdef1234567890"
}
