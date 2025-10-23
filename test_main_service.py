"""
Test the main PropertyPilot AgentCore service
"""
import asyncio
import json
from main import invoke

async def test_main_service():
    """Test the main AgentCore service"""
    print("🏠 Testing PropertyPilot AgentCore Main Service")
    print("=" * 50)
    
    # Test payload
    test_payload = {
        "input": {
            "prompt": "Hello! I'm interested in real estate investment opportunities in Austin, TX. Can you help me analyze the market?",
            "type": "market_research",
            "location": "Austin, TX",
            "max_price": 500000
        }
    }
    
    try:
        print("📤 Sending test request...")
        print(f"Request: {json.dumps(test_payload, indent=2)}")
        
        # Call the main invoke function
        result = await invoke(test_payload)
        
        print("\n✅ SUCCESS: AgentCore service responded!")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

if __name__ == "__main__":
    asyncio.run(test_main_service())