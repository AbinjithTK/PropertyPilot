#!/usr/bin/env python3
"""
Test PropertyPilot API Integration
Test the complete integration from frontend to AgentCore
"""

import requests
import json
import time

def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API health...")
    
    try:
        response = requests.get(
            "https://vw4wqyl3z0.execute-api.us-east-1.amazonaws.com/health",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_api_info():
    """Test API info endpoint"""
    print("🔍 Testing API info...")
    
    try:
        response = requests.get(
            "https://vw4wqyl3z0.execute-api.us-east-1.amazonaws.com/",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_analysis_endpoint():
    """Test the main analysis endpoint"""
    print("🔍 Testing analysis endpoint...")
    
    try:
        test_payload = {
            "query": "Find investment properties in Austin, TX under $500,000",
            "location": "Austin, TX",
            "max_price": 500000,
            "property_type": "residential",
            "analysis_type": "enhanced_analysis"
        }
        
        response = requests.post(
            "https://vw4wqyl3z0.execute-api.us-east-1.amazonaws.com/api/v1/analyze",
            json=test_payload,
            timeout=60
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Analysis successful!")
                print(f"   Analysis ID: {result.get('analysis_id')}")
                print(f"   Location: {result.get('location')}")
                print(f"   Message: {result.get('message')}")
                return True
            else:
                print(f"   ❌ Analysis failed: {result.get('error')}")
        else:
            print(f"   Response: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PropertyPilot API Integration Test")
    print("=" * 50)
    
    print(f"🎯 Testing API: https://vw4wqyl3z0.execute-api.us-east-1.amazonaws.com")
    
    # Test health endpoint
    health_ok = test_api_health()
    
    # Test info endpoint  
    info_ok = test_api_info()
    
    # Test analysis endpoint
    analysis_ok = test_analysis_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Health Check: {'✅ Pass' if health_ok else '❌ Fail'}")
    print(f"   API Info: {'✅ Pass' if info_ok else '❌ Fail'}")
    print(f"   Analysis: {'✅ Pass' if analysis_ok else '❌ Fail'}")
    
    if health_ok and info_ok and analysis_ok:
        print("\n🎉 All tests passed! PropertyPilot API is working correctly!")
        print("\n🌐 Your website is ready:")
        print("   https://main.d2skoklvq312zm.amplifyapp.com")
        print("\n🏠 Real estate investors can now:")
        print("   ✅ Analyze investment properties with AI")
        print("   ✅ Get market research and trends")
        print("   ✅ Calculate ROI and cash flow")
        print("   ✅ Find investment opportunities")
    else:
        print("\n⚠️ Some tests failed. The API may need troubleshooting.")
        print("   Check AWS Lambda logs in CloudWatch for details.")
    
    return health_ok and info_ok and analysis_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)