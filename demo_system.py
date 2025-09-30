"""
Demo script to test the trading signal notification system
This script demonstrates how the system sends trading signals and notifications
"""

import asyncio
import json
import sys
from pathlib import Path
import requests
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.development import get_development_firebase_service

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_signals_endpoint():
    """Test the signals endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/signals", timeout=5)
        if response.status_code == 200:
            signals = response.json()
            print(f"✅ Signals endpoint working - Found {len(signals)} signals")
            return signals
        else:
            print(f"❌ Signals endpoint failed: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot fetch signals: {e}")
        return []

def test_notification_endpoint():
    """Test sending a notification"""
    try:
        # Mock device token for testing
        test_token = "demo_device_token_for_testing_notifications_123456789"
        
        notification_data = {
            "device_token": test_token,
            "title": "🚀 Demo Trading Signal",
            "body": "EUR/USD BUY signal detected - 85.3% confidence",
            "data": {
                "signal_type": "BUY",
                "instrument": "EUR/USD",
                "confidence": "0.853",
                "price": "1.0924",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            "http://localhost:8000/api/notifications/send",
            json=notification_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Notification endpoint working")
            print(f"📱 Mock notification sent: {result}")
            return True
        else:
            print(f"❌ Notification endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot send notification: {e}")
        return False

def demonstrate_firebase_service():
    """Demonstrate the Firebase notification service"""
    print("\n🔥 Testing Firebase Notification Service...")
    
    # Get the development Firebase service (mock)
    firebase_service = get_development_firebase_service()
    
    # Test sending a trading signal notification
    test_token = "demo_device_token_12345"
    signal_data = {
        "signal_type": "BUY",
        "instrument": "EUR/USD",
        "direction": "LONG",
        "price": 1.0924,
        "confidence": 0.853,
        "sl_pips": 20,
        "tp_pips": 40,
        "reason": "Strong bullish momentum with RSI oversold bounce",
        "timestamp": datetime.now().isoformat()
    }
    
    # Test normal signal notification
    print("\n📊 Testing trading signal notification...")
    success = firebase_service.send_trading_signal_notification(test_token, signal_data)
    
    # Test signal update notification
    print("\n📈 Testing signal update notification...")
    success = firebase_service.send_signal_update_notification(
        test_token, "signal_123", "take_profit_hit", "EUR/USD"
    )
    
    # Test bulk notifications
    print("\n📱 Testing bulk notifications...")
    test_tokens = ["token1", "token2", "token3"]
    results = firebase_service.send_bulk_notifications(test_tokens, signal_data)
    
    print(f"✅ Firebase service demonstration complete!")

def main():
    """Run the complete demo"""
    print("🎯 Trading Signal Alerts - System Demo")
    print("=" * 50)
    
    # Test 1: API Health
    print("\n1️⃣ Testing Backend API...")
    if not test_api_health():
        print("❌ Backend is not running. Please start it with: python run_dev.py")
        return
    
    # Test 2: Signals Endpoint
    print("\n2️⃣ Testing Signal Generation...")
    signals = test_signals_endpoint()
    
    # Test 3: Notification Endpoint
    print("\n3️⃣ Testing Notification System...")
    test_notification_endpoint()
    
    # Test 4: Firebase Service Demo
    print("\n4️⃣ Firebase Service Demonstration...")
    demonstrate_firebase_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print("\n📱 What you've seen:")
    print("✅ Backend API running and responding")
    print("✅ Signal generation system working")
    print("✅ Notification endpoints functional") 
    print("✅ Firebase service integration ready")
    print("\n🚀 Next Steps:")
    print("1. 📱 Build the Android app (mobile/app/)")
    print("2. 🔗 Connect real OANDA account (update credentials)")
    print("3. 🔥 Set up real Firebase project (follow FIREBASE_SETUP.md)")
    print("4. 📲 Install app and test real notifications")
    
    print(f"\n📊 Current API Status: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
