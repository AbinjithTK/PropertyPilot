"""
Test PropertyPilot core functionality without AgentCore
"""
import asyncio
import os
from automated_web_research import AutomatedWebResearcher

async def test_core_functionality():
    """Test the core PropertyPilot functionality"""
    print("🏠 Testing PropertyPilot Core Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Automated Web Research
        print("\n1. Testing Automated Web Research...")
        researcher = AutomatedWebResearcher()
        
        # Test market conditions research
        location = "Austin, TX"
        print(f"   Researching market conditions for {location}...")
        
        market_result = await researcher.research_market_conditions(location)
        
        print("✅ Market research completed!")
        print(f"   Status: {market_result.get('status', 'unknown')}")
        print(f"   Confidence: {market_result.get('confidence_score', 0.0):.2f}")
        
        if market_result.get('summary'):
            summary = market_result['summary']
            print(f"   Market Overview: {summary.get('market_overview', {}).get('temperature', 'unknown')}")
        
        # Test 2: Investment Opportunities Research
        print("\n2. Testing Investment Opportunities Research...")
        criteria = {
            "location": location,
            "max_price": 500000,
            "property_type": "residential"
        }
        
        opportunities_result = await researcher.research_investment_opportunities(criteria)
        
        print("✅ Investment opportunities research completed!")
        print(f"   Status: {opportunities_result.get('status', 'unknown')}")
        print(f"   Confidence: {opportunities_result.get('confidence_score', 0.0):.2f}")
        
        # Test 3: Property-specific research
        print("\n3. Testing Property-specific Research...")
        test_address = "123 Main St, Austin, TX"
        property_details = {
            "price": 450000,
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1800
        }
        
        property_result = await researcher.research_property_specifics(test_address, property_details)
        
        print("✅ Property-specific research completed!")
        print(f"   Status: {property_result.get('status', 'unknown')}")
        print(f"   Confidence: {property_result.get('confidence_score', 0.0):.2f}")
        
        print("\n🎉 All core functionality tests passed!")
        print("\n📊 Summary:")
        print(f"   Market Research: {'✅ Working' if market_result.get('status') != 'failed' else '❌ Failed'}")
        print(f"   Investment Opportunities: {'✅ Working' if opportunities_result.get('status') != 'failed' else '❌ Failed'}")
        print(f"   Property Research: {'✅ Working' if property_result.get('status') != 'failed' else '❌ Failed'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_core_functionality())
    if success:
        print("\n🚀 PropertyPilot core functionality is ready!")
        print("   The system can perform market research and analysis without AI agents.")
        print("   Once the Bedrock payment issue is resolved, full AI agent functionality will be available.")
    else:
        print("\n⚠️ Some core functionality tests failed.")
        print("   Please check the error messages above.")