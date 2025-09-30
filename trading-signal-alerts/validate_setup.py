"""
Simple Firebase validation script
This script checks if our Firebase setup is working correctly
"""

import json
import os
from pathlib import Path

def check_project_structure():
    """Check if all required files and folders exist"""
    print("🔍 Checking project structure...")
    
    base_path = Path(__file__).parent
    required_paths = [
        "src/services/fcm_service.py",
        "src/services/firebase_notification_service.py", 
        "mobile/app/src/main/AndroidManifest.xml",
        "mobile/app/build.gradle",
        "mobile/app/google-services.json"
    ]
    
    all_good = True
    for path in required_paths:
        full_path = base_path / path
        if full_path.exists():
            print(f"✅ Found: {path}")
        else:
            print(f"❌ Missing: {path}")
            all_good = False
    
    return all_good

def check_google_services():
    """Check google-services.json configuration"""
    print("\n🔍 Checking google-services.json...")
    
    config_path = Path(__file__).parent / "mobile" / "app" / "google-services.json"
    
    if not config_path.exists():
        print("❌ google-services.json not found")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        # Check required fields
        project_id = config.get("project_info", {}).get("project_id")
        app_id = config.get("client", [{}])[0].get("client_info", {}).get("mobilesdk_app_id")
        package_name = config.get("client", [{}])[0].get("client_info", {}).get("android_client_info", {}).get("package_name")
        
        if project_id:
            print(f"✅ Project ID: {project_id}")
        else:
            print("❌ No project ID found")
            return False
        
        if app_id:
            print(f"✅ App ID: {app_id}")
        else:
            print("❌ No app ID found")
            return False
        
        if package_name == "com.tradingsignals.alerts":
            print(f"✅ Package name: {package_name}")
        else:
            print(f"⚠️  Package name: {package_name} (should be com.tradingsignals.alerts)")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def check_android_config():
    """Check Android app configuration"""
    print("\n🔍 Checking Android configuration...")
    
    # Check AndroidManifest.xml
    manifest_path = Path(__file__).parent / "mobile" / "app" / "src" / "main" / "AndroidManifest.xml"
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest_content = f.read()
        
        if "com.tradingsignals.alerts" in manifest_content:
            print("✅ Android package name correct")
        else:
            print("❌ Android package name mismatch")
        
        if "TradingSignalFirebaseMessagingService" in manifest_content:
            print("✅ Firebase messaging service registered")
        else:
            print("❌ Firebase messaging service not found")
    else:
        print("❌ AndroidManifest.xml not found")
        return False
    
    # Check build.gradle
    gradle_path = Path(__file__).parent / "mobile" / "app" / "build.gradle"
    if gradle_path.exists():
        with open(gradle_path) as f:
            gradle_content = f.read()
        
        if "firebase-messaging" in gradle_content:
            print("✅ Firebase messaging dependency found")
        else:
            print("❌ Firebase messaging dependency missing")
        
        if "google-services" in gradle_content:
            print("✅ Google services plugin found")
        else:
            print("❌ Google services plugin missing")
    else:
        print("❌ build.gradle not found")
        return False
    
    return True

def check_backend_services():
    """Check backend service files"""
    print("\n🔍 Checking backend services...")
    
    services_path = Path(__file__).parent / "src" / "services"
    
    # Check FCM service
    fcm_path = services_path / "fcm_service.py"
    if fcm_path.exists():
        print("✅ FCM service file exists")
        with open(fcm_path) as f:
            content = f.read()
        if "send_signal_notification" in content:
            print("✅ FCM service has signal notification method")
        else:
            print("❌ FCM service missing signal notification method")
    else:
        print("❌ FCM service file missing")
        return False
    
    # Check Firebase notification service
    firebase_path = services_path / "firebase_notification_service.py"
    if firebase_path.exists():
        print("✅ Firebase notification service exists")
    else:
        print("❌ Firebase notification service missing")
        return False
    
    return True

def test_imports():
    """Test if we can import our services"""
    print("\n🔍 Testing imports...")
    
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    try:
        from services import fcm_service
        print("✅ Can import FCM service")
    except ImportError as e:
        print(f"❌ Cannot import FCM service: {e}")
        return False
    
    try:
        from services import firebase_notification_service
        print("✅ Can import Firebase notification service")
    except ImportError as e:
        print(f"❌ Cannot import Firebase notification service: {e}")
        return False
    
    return True

def main():
    """Run all validation checks"""
    print("🔥 Firebase Setup Validation")
    print("=" * 40)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Google Services Config", check_google_services),
        ("Android Configuration", check_android_config),
        ("Backend Services", check_backend_services),
        ("Import Tests", test_imports)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results[name] = False
    
    # Summary
    print("\n📋 Validation Summary")
    print("=" * 25)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, passed_check in results.items():
        status = "✅ PASSED" if passed_check else "❌ FAILED"
        print(f"{status} {name}")
    
    print(f"\n📊 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All validations passed!")
        print("\n📱 Your Firebase setup is ready for testing!")
        print("\n🚀 Next steps:")
        print("1. Build the Android app")
        print("2. Start the backend server")
        print("3. Test notifications")
    else:
        print("\n⚠️  Some validations failed")
        print("Check the issues above and fix them")
    
    return passed == total

if __name__ == "__main__":
    main()
