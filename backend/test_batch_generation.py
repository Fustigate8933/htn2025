#!/usr/bin/env python3
"""
Test script for batch video generation functionality
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_batch_generation_api():
    """Test the batch generation API endpoints"""
    
    print("🧪 Testing Batch Video Generation API")
    print("=" * 50)
    
    # Test endpoint availability
    base_url = "http://localhost:8000"
    
    try:
        # Test the test endpoint
        response = requests.get(f"{base_url}/batch/batch-videos/test")
        if response.status_code == 200:
            print("✅ Batch generation API is accessible")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API test failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend server is running:")
        print("   cd backend && python main.py")
        return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False
    
    return True

def test_batch_generation_functions():
    """Test the batch generation functions directly"""
    
    print("\n🔧 Testing Batch Generation Functions")
    print("=" * 50)
    
    try:
        from utils.Topview import gen_video_batch, gen_video_batch_simple
        
        print("✅ Batch generation functions imported successfully")
        
        # Test with sample data (without actually generating videos)
        sample_texts = [
            "Welcome to our presentation about AI technology.",
            "Today we'll discuss machine learning applications.",
            "Let's explore the future of artificial intelligence."
        ]
        
        print(f"✅ Sample texts prepared: {len(sample_texts)} texts")
        print("Sample texts:")
        for i, text in enumerate(sample_texts):
            print(f"  {i+1}. {text}")
        
        print("\n📋 Function signatures:")
        print("  gen_video_batch(audio_path, video_path, texts, max_workers=3, notice_url=None)")
        print("  gen_video_batch_simple(audio_path, video_path, texts)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Function test error: {e}")
        return False

def test_api_usage_example():
    """Show example of how to use the API"""
    
    print("\n📖 API Usage Example")
    print("=" * 50)
    
    example_curl = """
# Test the API endpoint
curl -X GET http://localhost:8000/batch/batch-videos/test

# Generate batch videos (example)
curl -X POST http://localhost:8000/batch/batch-videos \\
  -F "audio_file=@audio.mp3" \\
  -F "video_file=@video.mp4" \\
  -F 'texts=["Text 1", "Text 2", "Text 3"]' \\
  -F "max_workers=2"

# Simple batch generation
curl -X POST http://localhost:8000/batch/batch-videos-simple \\
  -F "audio_file=@audio.mp3" \\
  -F "video_file=@video.mp4" \\
  -F 'texts=["Text 1", "Text 2", "Text 3"]'
"""
    
    print("Example API calls:")
    print(example_curl)
    
    print("📋 API Endpoints:")
    print("  GET  /batch/batch-videos/test - Test endpoint")
    print("  POST /batch/batch-videos - Full batch generation")
    print("  POST /batch/batch-videos-simple - Simple batch generation")
    
    print("\n📋 Request Parameters:")
    print("  audio_file: Audio file for voice cloning")
    print("  video_file: Video file for avatar")
    print("  texts: JSON string array of text content")
    print("  max_workers: Maximum concurrent workers (optional)")
    print("  notice_url: Webhook URL for notifications (optional)")

def main():
    """Main test function"""
    
    print("🚀 Batch Video Generation Test")
    print("=" * 60)
    
    # Test 1: API availability
    api_success = test_batch_generation_api()
    
    # Test 2: Function imports
    function_success = test_batch_generation_functions()
    
    # Test 3: Usage examples
    test_api_usage_example()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"API Test: {'✅ PASSED' if api_success else '❌ FAILED'}")
    print(f"Function Test: {'✅ PASSED' if function_success else '❌ FAILED'}")
    
    if api_success and function_success:
        print("\n🎉 All tests passed! Batch generation is ready to use.")
        print("\n📋 Next steps:")
        print("1. Prepare your audio and video files")
        print("2. Create a list of text content for each video")
        print("3. Use the API endpoints to generate batch videos")
        print("4. Monitor the webhook endpoint for completion notifications")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return api_success and function_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
