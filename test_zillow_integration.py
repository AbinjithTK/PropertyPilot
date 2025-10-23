#!/usr/bin/env python3
"""
Test script for Zillow API integration using HasData service
"""

import os
import json
import asyncio
from property_pilot_agents import PropertyPilotSystem, zillow_client

async def test_zillow_integration():
    """Test the Zillow API integration"""
    print("🏠 Testing PropertyPilot Zillow API Integration")
    print("=" * 50)
    
    # Test 1: Search for properties
    print("\n1. Testing property search...")
    try:
        properties = zillow_client.search_properties("Austin, TX", max_price=500000)
        print(f"✅ Found {len(properties)} properties in Austin, TX")
        
        if properties:
            sample_property = properties[0]
            print(f"   Sample property: {sample_property.get('address', 'Unknown')}")
            print(f"   Price: ${sample_property.get('price', 0):,}")
            print(f"   Bedrooms: {sample_property.get('bedrooms', 0)}")
            print(f"   Square feet: {sample_property.get('livingArea', 0):,}")
    except Exception as e:
        print(f"❌ Property search failed: {e}")
    
    # Test 2: Get property details (using a sample Zillow URL)
    print("\n2. Testing property details...")
    sample_zillow_url = "https://www.zillow.com/homedetails/301-E-79th-St-APT-23S-New-York-NY-10075/31543731_zpid/"
    
    try:
        details = zillow_client.get_property_details(sample_zillow_url)
        if details and not details.get("error"):
            print(f"✅ Successfully fetched property details")
            print(f"   Address: {details.get('address', 'Unknown')}")
            print(f"   Price: ${details.get('price', 0):,}")
            print(f"   Zestimate: ${details.get('zestimate', 0):,}")
            print(f"   Rent Estimate: ${details.get('rentZestimate', 0):,}/month")
        else:
            print(f"⚠️ Property details fetch returned: {details}")
    except Exception as e:
        print(f"❌ Property details failed: {e}")
    
    # Test 3: PropertyPilot agent integration
    print("\n3. Testing PropertyPilot agent integration...")
    try:
        property_pilot = PropertyPilotSystem()
        
        # Test Property Scout agent
        scout_result = property_pilot.property_scout(
            "Find investment properties in Austin, TX under $400,000 using the Zillow API"
        )
        print(f"✅ Property Scout agent response:")
        print(f"   {scout_result.message[:200]}...")
        
    except Exception as e:
        print(f"❌ PropertyPilot agent test failed: {e}")
    
    # Test 4: Investment analysis
    print("\n4. Testing investment analysis...")
    try:
        from property_pilot_agents import analyze_zillow_investment_opportunity
        
        # This would normally use a real Zillow URL
        analysis = analyze_zillow_investment_opportunity(sample_zillow_url, target_roi=8.0)
        
        if analysis and not analysis.get("error"):
            print(f"✅ Investment analysis completed")
            if "investment_metrics" in analysis:
                metrics = analysis["investment_metrics"]
                print(f"   ROI: {metrics.get('roi_percentage', 0)}%")
                print(f"   Monthly Cash Flow: ${metrics.get('monthly_cash_flow', 0):,}")
                print(f"   Recommendation: {analysis.get('recommendation', 'N/A')}")
        else:
            print(f"⚠️ Investment analysis returned: {analysis}")
            
    except Exception as e:
        print(f"❌ Investment analysis failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Zillow API integration test completed!")
    print("\nNote: Some tests may show sample data if the HasData API")
    print("is not accessible or returns errors. This is expected behavior.")

if __name__ == "__main__":
    asyncio.run(test_zillow_integration())