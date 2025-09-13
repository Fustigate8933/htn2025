#!/usr/bin/env python3
"""
Test script to verify the frontend-backend integration
"""

import requests
import json
import sys

def test_backend_health():
    """Test if backend is running and accessible"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running:")
        print("   cd backend && python main.py")
        return False

def test_batch_endpoint():
    """Test if batch generation endpoint is accessible"""
    try:
        response = requests.get("http://localhost:8000/batch/batch-videos/test")
        if response.status_code == 200:
            print("✅ Batch generation endpoint is accessible")
            data = response.json()
            print(f"   Response: {data.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Batch generation endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to batch endpoint")
        return False

def test_frontend_health():
    """Test if frontend is running and accessible"""
    try:
        response = requests.get("http://localhost:3000/api/health")
        if response.status_code == 200:
            print("✅ Frontend API health check passed")
            return True
        else:
            print(f"❌ Frontend API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to frontend. Make sure it's running:")
        print("   npm run dev")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_health()
    batch_ok = test_batch_endpoint()
    
    # Test frontend
    frontend_ok = test_frontend_health()
    
    print("\n📊 Integration Test Summary")
    print("=" * 50)
    print(f"Backend Health: {'✅ PASSED' if backend_ok else '❌ FAILED'}")
    print(f"Batch Endpoint: {'✅ PASSED' if batch_ok else '❌ FAILED'}")
    print(f"Frontend Health: {'✅ PASSED' if frontend_ok else '❌ FAILED'}")
    
    if backend_ok and batch_ok and frontend_ok:
        print("\n🎉 All integration tests passed!")
        print("\n📋 Next steps:")
        print("1. Upload PPT, face video, and voice files in the frontend")
        print("2. Click 'Generate Content' to start the generation process")
        print("3. The system will:")
        print("   - Extract slides from PPT")
        print("   - Generate scripts for each slide")
        print("   - Create avatar videos using batch generation")
        print("   - Navigate to presentation mode")
        print("4. Use the presentation controls to switch between avatar and human mode")
    else:
        print("\n❌ Some integration tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        if not backend_ok:
            print("- Start the backend: cd backend && python main.py")
        if not frontend_ok:
            print("- Start the frontend: npm run dev")
        if not batch_ok:
            print("- Check that batch_generate route is properly included in main.py")
    
    return backend_ok and batch_ok and frontend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

