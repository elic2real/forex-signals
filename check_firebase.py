#!/usr/bin/env python3
"""
Firebase Configuration Checker
Validates Firebase setup for Trading Signal Alerts project
"""

import os
import json
import sys
from pathlib import Path

def check_firebase_config():
    """Check if Firebase is properly configured"""
    
    print("🔥 Firebase Configuration Checker")
    print("=" * 50)
    
    # Define paths
    project_root = Path(__file__).parent
    mobile_app_path = project_root / "mobile" / "app"
    google_services_path = mobile_app_path / "google-services.json"
    
    # Check 1: google-services.json exists
    print("\n1. Checking google-services.json...")
    if google_services_path.exists():
        print("   ✅ google-services.json found")
        
        # Validate JSON structure
        try:
            with open(google_services_path, 'r') as f:
                config = json.load(f)
            
            # Check required fields
            required_fields = [
                'project_info.project_id',
                'client[0].client_info.android_client_info.package_name',
                'client[0].api_key[0].current_key'
            ]
            
            for field_path in required_fields:
                if check_nested_field(config, field_path):
                    print(f"   ✅ {field_path} present")
                else:
                    print(f"   ❌ {field_path} missing")
                    return False
            
            # Verify package name
            package_name = config['client'][0]['client_info']['android_client_info']['package_name']
            if package_name == "com.tradingsignals.alerts":
                print(f"   ✅ Package name correct: {package_name}")
            else:
                print(f"   ❌ Package name incorrect: {package_name}")
                print(f"      Expected: com.tradingsignals.alerts")
                return False
                
        except json.JSONDecodeError:
            print("   ❌ google-services.json is not valid JSON")
            return False
        except Exception as e:
            print(f"   ❌ Error reading google-services.json: {e}")
            return False
            
    else:
        print("   ❌ google-services.json not found")
        print(f"      Expected location: {google_services_path}")
        print("      Please download from Firebase Console")
        return False
    
    # Check 2: Build configuration
    print("\n2. Checking build configuration...")
    build_gradle_path = mobile_app_path / "build.gradle"
    
    if build_gradle_path.exists():
        with open(build_gradle_path, 'r') as f:
            build_content = f.read()
        
        if "com.google.gms.google-services" in build_content:
            print("   ✅ Google Services plugin configured")
        else:
            print("   ❌ Google Services plugin missing")
            return False
        
        if "firebase-messaging" in build_content:
            print("   ✅ Firebase Messaging dependency found")
        else:
            print("   ❌ Firebase Messaging dependency missing")
            return False
            
    else:
        print("   ❌ build.gradle not found")
        return False
    
    # Check 3: Android Manifest
    print("\n3. Checking Android Manifest...")
    manifest_path = mobile_app_path / "src" / "main" / "AndroidManifest.xml"
    
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        if "TradingSignalFirebaseMessagingService" in manifest_content:
            print("   ✅ Firebase Messaging Service declared")
        else:
            print("   ❌ Firebase Messaging Service not declared")
            return False
        
        if "com.google.firebase.MESSAGING_EVENT" in manifest_content:
            print("   ✅ Messaging intent filter configured")
        else:
            print("   ❌ Messaging intent filter missing")
            return False
            
    else:
        print("   ❌ AndroidManifest.xml not found")
        return False
    
    print("\n🎉 Firebase configuration looks good!")
    return True

def check_nested_field(data, field_path):
    """Check if nested field exists in data"""
    try:
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if '[' in part and ']' in part:
                # Handle array access like 'client[0]'
                key = part.split('[')[0]
                index = int(part.split('[')[1].split(']')[0])
                current = current[key][index]
            else:
                current = current[part]
        
        return True
    except (KeyError, IndexError, TypeError):
        return False

def print_setup_instructions():
    """Print Firebase setup instructions"""
    print("\n📋 Firebase Setup Instructions:")
    print("-" * 40)
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Create new project: 'Trading Signal Alerts'")
    print("3. Add Android app:")
    print("   - Package name: com.tradingsignals.alerts")
    print("   - App nickname: Trading Signal Alerts")
    print("4. Download google-services.json")
    print("5. Place file in: mobile/app/google-services.json")
    print("6. Enable Cloud Messaging in Firebase Console")
    print("\nThen run this checker again!")

if __name__ == "__main__":
    try:
        if check_firebase_config():
            print("\n✅ All Firebase checks passed!")
            sys.exit(0)
        else:
            print("\n❌ Firebase configuration issues found")
            print_setup_instructions()
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Error running Firebase checker: {e}")
        print_setup_instructions()
        sys.exit(1)
