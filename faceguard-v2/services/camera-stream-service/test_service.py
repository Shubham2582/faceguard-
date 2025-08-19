"""
Simple test script for Service C foundation
Tests basic functionality without camera dependencies
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_configuration():
    """Test configuration loading"""
    try:
        from config.settings import get_settings
        settings = get_settings()
        print(f"✅ Configuration loaded: {settings.service_name} v{settings.service_version}")
        print(f"   Port: {settings.service_port}")
        print(f"   Feature flags: analytics={settings.enable_analytics}, health_monitoring={settings.enable_health_monitoring}")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def test_domain_models():
    """Test domain models"""
    try:
        from domain.models import CameraStatus, CameraConfiguration, ServiceHealth
        print(f"✅ Domain models loaded: CameraStatus has {len(CameraStatus)} values")
        
        # Test model creation
        config = CameraConfiguration(
            camera_id="test_camera",
            source="0",
            camera_type="usb",
            name="Test Camera"
        )
        print(f"   Sample configuration: {config.name}")
        return True
    except Exception as e:
        print(f"❌ Domain models failed: {e}")
        return False

def test_basic_service_structure():
    """Test basic service structure without camera manager"""
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Test Camera Stream Service")
        print("✅ FastAPI application can be created")
        
        # Test health endpoint structure
        @app.get("/health")
        async def test_health():
            return {"status": "healthy", "service": "camera-stream-service"}
        
        print("✅ Basic endpoint structure working")
        return True
    except Exception as e:
        print(f"❌ Service structure failed: {e}")
        return False

def main():
    print("🧪 SERVICE C FOUNDATION TESTING")
    print("================================")
    print()
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("Domain Models", test_domain_models),
        ("Basic Service Structure", test_basic_service_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}:")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 PHASE 1 FOUNDATION TESTS PASSED")
        print("Service C foundation is ready for camera integration")
    else:
        print("⚠️ Some foundation tests failed")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)