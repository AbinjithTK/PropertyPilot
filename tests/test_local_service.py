import requests
import json

def test_propertypilot_local():
    """Test PropertyPilot running locally"""
    print("🏠 Testing PropertyPilot Local Service")
    print("=" * 50)
    
    # Test the /invocations endpoint
    url = "http://localhost:8080/invocations"
    
    # Test payload
    payload = {
        "input": {
            "prompt": "Hello! I'm interested in real estate investment opportunities in Austin, TX. Can you help me analyze the market?",
            "location": "Austin, TX",
            "max_price": 500000,
            "type": "market_research"
        }
    }
    
    try:
        print("📤 Sending request to PropertyPilot...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: PropertyPilot responded!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to PropertyPilot service")
        print("   Make sure the service is running on port 8080")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_propertypilot_local()
    if success:
        print("\n🎉 PropertyPilot is working locally!")
    else:
        print("\n⚠️ PropertyPilot test failed")