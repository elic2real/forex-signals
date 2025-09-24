"""
Comprehensive Firebase integration test
This test verifies all Firebase components are working correctly
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from services.fcm_service import FCMService
    from services.firebase_notification_service import get_firebase_service
except ImportError:
    # Fallback imports for testing
    FCMService = None
    get_firebase_service = None

class FirebaseIntegrationTest:
    """Test Firebase configuration and functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.google_services_path = Path(__file__).parent.parent / "mobile" / "app" / "google-services.json"
        self.service_account_path = Path(__file__).parent.parent / "firebase_service_account.json"
    
    def test_google_services_config(self):
        """Test mobile app Firebase configuration"""
        print("🔍 Testing google-services.json configuration...")
        
        try:
            if not self.google_services_path.exists():
                print("❌ google-services.json not found")
                print(f"   Expected location: {self.google_services_path}")
                self.test_results["google_services"] = False
                return False
            
            with open(self.google_services_path) as f:
                config = json.load(f)
            
            # Check required fields
            required_fields = [
                "project_info.project_id",
                "client.0.client_info.mobilesdk_app_id",
                "client.0.api_key.0.current_key",
                "client.0.services.appinvite_service.other_platform_oauth_client"
            ]
            
            for field_path in required_fields:
                try:
                    current = config
                    for key in field_path.split('.'):
                        if key.isdigit():
                            current = current[int(key)]
                        else:
                            current = current[key]
                    print(f"✅ Found {field_path}")
                except (KeyError, IndexError, TypeError):
                    print(f"❌ Missing required field: {field_path}")
                    self.test_results["google_services"] = False
                    return False
            
            project_id = config["project_info"]["project_id"]
            print(f"✅ Project ID: {project_id}")
            
            self.test_results["google_services"] = True
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in google-services.json: {e}")
            self.test_results["google_services"] = False
            return False
        except Exception as e:
            print(f"❌ Error reading google-services.json: {e}")
            self.test_results["google_services"] = False
            return False
    
    def test_service_account_config(self):
        """Test backend Firebase service account configuration"""
        print("\n🔍 Testing Firebase service account configuration...")
        
        try:
            # Check if service account file exists
            if not self.service_account_path.exists():
                print("⚠️  Firebase service account file not found")
                print(f"   Expected location: {self.service_account_path}")
                print("   This is optional - you can use default credentials instead")
                self.test_results["service_account"] = "optional"
                return True
            
            with open(self.service_account_path) as f:
                service_account = json.load(f)
            
            # Check required fields for service account
            required_fields = [
                "type",
                "project_id", 
                "private_key_id",
                "private_key",
                "client_email",
                "client_id",
                "auth_uri",
                "token_uri"
            ]
            
            for field in required_fields:
                if field not in service_account:
                    print(f"❌ Missing required field in service account: {field}")
                    self.test_results["service_account"] = False
                    return False
            
            if service_account["type"] != "service_account":
                print("❌ Service account type is not 'service_account'")
                self.test_results["service_account"] = False
                return False
            
            print(f"✅ Service account project: {service_account['project_id']}")
            print(f"✅ Client email: {service_account['client_email']}")
            
            self.test_results["service_account"] = True
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in service account file: {e}")
            self.test_results["service_account"] = False
            return False
        except Exception as e:
            print(f"❌ Error reading service account file: {e}")
            self.test_results["service_account"] = False
            return False
    
    def test_firebase_admin_initialization(self):
        """Test Firebase Admin SDK initialization"""
        print("\n🔍 Testing Firebase Admin SDK initialization...")
        
        try:
            firebase_service = get_firebase_service()
            
            if firebase_service.initialized:
                print("✅ Firebase Admin SDK initialized successfully")
                self.test_results["admin_sdk"] = True
                return True
            else:
                print("❌ Firebase Admin SDK failed to initialize")
                print("   Check your service account file or default credentials")
                self.test_results["admin_sdk"] = False
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Firebase Admin SDK: {e}")
            self.test_results["admin_sdk"] = False
            return False
    
    async def test_fcm_service(self):
        """Test FCM service functionality"""
        print("\n🔍 Testing FCM service...")
        
        try:
            # Try to create FCM service with mock credentials
            # This tests the service structure without actually sending notifications
            
            # Mock project info from google-services.json
            if self.google_services_path.exists():
                with open(self.google_services_path) as f:
                    config = json.load(f)
                project_id = config["project_info"]["project_id"]
            else:
                project_id = "test-project"
            
            # Test FCM service structure
            if self.service_account_path.exists():
                fcm_service = FCMService(project_id, str(self.service_account_path))
            else:
                # Create mock service account for testing
                mock_service_account = {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key_id": "test",
                    "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
                    "client_email": f"test@{project_id}.iam.gserviceaccount.com",
                    "client_id": "test",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
                fcm_service = FCMService(project_id, json.dumps(mock_service_account))
            
            # Test that service has required methods
            required_methods = [
                "send_signal_notification",
                "send_test_notification", 
                "subscribe_to_topic"
            ]
            
            for method in required_methods:
                if hasattr(fcm_service, method):
                    print(f"✅ FCM service has {method} method")
                else:
                    print(f"❌ FCM service missing {method} method")
                    self.test_results["fcm_service"] = False
                    return False
            
            print("✅ FCM service structure is correct")
            self.test_results["fcm_service"] = True
            return True
            
        except Exception as e:
            print(f"❌ Error testing FCM service: {e}")
            self.test_results["fcm_service"] = False
            return False
    
    def test_android_manifest(self):
        """Test Android app Firebase configuration"""
        print("\n🔍 Testing Android Manifest Firebase configuration...")
        
        manifest_path = Path(__file__).parent.parent / "mobile" / "app" / "src" / "main" / "AndroidManifest.xml"
        
        try:
            if not manifest_path.exists():
                print(f"❌ AndroidManifest.xml not found at {manifest_path}")
                self.test_results["android_manifest"] = False
                return False
            
            with open(manifest_path) as f:
                manifest_content = f.read()
            
            # Check for Firebase messaging service
            if "TradingSignalFirebaseMessagingService" in manifest_content:
                print("✅ Firebase messaging service registered in manifest")
            else:
                print("❌ Firebase messaging service not found in manifest")
                self.test_results["android_manifest"] = False
                return False
            
            # Check for required permissions
            required_permissions = [
                "android.permission.INTERNET",
                "android.permission.WAKE_LOCK"
            ]
            
            for permission in required_permissions:
                if permission in manifest_content:
                    print(f"✅ Found permission: {permission}")
                else:
                    print(f"⚠️  Missing recommended permission: {permission}")
            
            self.test_results["android_manifest"] = True
            return True
            
        except Exception as e:
            print(f"❌ Error reading AndroidManifest.xml: {e}")
            self.test_results["android_manifest"] = False
            return False
    
    def test_android_build_config(self):
        """Test Android app build configuration"""
        print("\n🔍 Testing Android build configuration...")
        
        build_gradle_path = Path(__file__).parent.parent / "mobile" / "app" / "build.gradle"
        
        try:
            if not build_gradle_path.exists():
                print(f"❌ app/build.gradle not found at {build_gradle_path}")
                self.test_results["android_build"] = False
                return False
            
            with open(build_gradle_path) as f:
                build_content = f.read()
            
            # Check for Firebase dependencies
            firebase_dependencies = [
                "firebase-messaging",
                "firebase-analytics",
                "google-services"
            ]
            
            for dependency in firebase_dependencies:
                if dependency in build_content:
                    print(f"✅ Found Firebase dependency: {dependency}")
                else:
                    print(f"❌ Missing Firebase dependency: {dependency}")
                    self.test_results["android_build"] = False
                    return False
            
            # Check for google-services plugin
            if "apply plugin: 'com.google.gms.google-services'" in build_content:
                print("✅ Google services plugin applied")
            else:
                print("❌ Google services plugin not applied")
                self.test_results["android_build"] = False
                return False
            
            self.test_results["android_build"] = True
            return True
            
        except Exception as e:
            print(f"❌ Error reading build.gradle: {e}")
            self.test_results["android_build"] = False
            return False
    
    async def run_all_tests(self):
        """Run all Firebase integration tests"""
        print("🔥 Firebase Integration Test Suite")
        print("=" * 50)
        
        # Run all tests
        self.test_google_services_config()
        self.test_service_account_config()
        self.test_firebase_admin_initialization()
        await self.test_fcm_service()
        self.test_android_manifest()
        self.test_android_build_config()
        
        # Print summary
        print("\n📋 Test Results Summary")
        print("=" * 30)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        optional_tests = sum(1 for result in self.test_results.values() if result == "optional")
        failed_tests = total_tests - passed_tests - optional_tests
        
        for test_name, result in self.test_results.items():
            if result is True:
                print(f"✅ {test_name}: PASSED")
            elif result == "optional":
                print(f"⚠️  {test_name}: OPTIONAL (not required)")
            else:
                print(f"❌ {test_name}: FAILED")
        
        print(f"\n📊 Summary: {passed_tests}/{total_tests} required tests passed")
        if optional_tests > 0:
            print(f"   {optional_tests} optional tests")
        
        if failed_tests == 0 or (failed_tests == 1 and "service_account" in self.test_results and self.test_results["service_account"] == "optional"):
            print("\n🎉 Firebase integration is ready!")
            print("\n📱 Next steps:")
            print("1. Build and install the Android app")
            print("2. Run the backend server")
            print("3. Test notifications with a real device")
        else:
            print("\n❌ Firebase integration needs attention")
            print("\n🔧 To fix issues:")
            print("1. Follow FIREBASE_SETUP.md for complete setup")
            print("2. Download google-services.json from Firebase Console")
            print("3. (Optional) Create service account key for backend")

if __name__ == "__main__":
    test_suite = FirebaseIntegrationTest()
    asyncio.run(test_suite.run_all_tests())
