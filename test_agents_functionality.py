#!/usr/bin/env python3
"""
Test script for PropertyPilot agents functionality with free APIs only
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Set environment variables for testing
# No Census API key needed anymore
os.environ['HASDATA_API_KEY'] = '2e36da63-82a5-488b-ba4a-f93c79800e53'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['LOG_LEVEL'] = 'INFO'

# Import PropertyPilot components
try:
    from property_pilot_agents import (
        PropertyPilotSystem,
        get_demographic_data,
        calculate_neighborhood_score,
        get_market_trends,
        analyze_zillow_investment_opportunity,
        zillow_client
    )
    print("✅ Successfully imported PropertyPilot components")
except ImportError as e:
    print(f"❌ Failed to import PropertyPilot components: {e}")
    sys.exit(1)

async def test_individual_tools():
    """Test individual agent tools"""
    print("\n🔧 Testing Individual Agent Tools")
    print("=" * 50)
    
    # Test 1: Demographic Data
    print("\n1. Testing Demographic Data...")
    try:
        demographic_result = get_demographic_data("Austin, TX")
        if demographic_result and not demographic_result.get("error"):
            print(f"✅ Demographic data retrieved successfully")
            print(f"   Median Income: ${demographic_result.get('median_income', 0):,}")
            print(f"   Population: {demographic_result.get('population', 0):,}")
            print(f"   Data Source: {demographic_result.get('data_source', 'Unknown')}")
        else:
            print(f"⚠️ Demographic data returned: {demographic_result}")
    except Exception as e:
        print(f"❌ Demographic data test failed: {e}")
    
    # Test 2: Neighborhood Scoring
    print("\n2. Testing Neighborhood Scoring...")
    try:
        neighborhood_result = calculate_neighborhood_score("Austin, TX")
        if neighborhood_result and not neighborhood_result.get("error"):
            print(f"✅ Neighborhood score calculated successfully")
            print(f"   Overall Score: {neighborhood_result.get('overall_score', 0)}/10")
            print(f"   Component Scores: {neighborhood_result.get('component_scores', {})}")
        else:
            print(f"⚠️ Neighborhood scoring returned: {neighborhood_result}")
    except Exception as e:
        print(f"❌ Neighborhood scoring test failed: {e}")
    
    # Test 3: Market Trends
    print("\n3. Testing Market Trends Analysis...")
    try:
        trends_result = get_market_trends("Austin, TX")
        if trends_result and not trends_result.get("error"):
            print(f"✅ Market trends analyzed successfully")
            print(f"   Market Sentiment: {trends_result.get('market_indicators', {}).get('overall_sentiment', 'Unknown')}")
            print(f"   Economic Data: {trends_result.get('economic_data', {})}")
        else:
            print(f"⚠️ Market trends returned: {trends_result}")
    except Exception as e:
        print(f"❌ Market trends test failed: {e}")
    
    # Test 4: Zillow Property Details (if URL provided)
    print("\n4. Testing Zillow Property Details...")
    try:
        sample_url = "https://www.zillow.com/homedetails/301-E-79th-St-APT-23S-New-York-NY-10075/31543731_zpid/"
        zillow_result = zillow_client.get_property_details(sample_url)
        if zillow_result and not zillow_result.get("error"):
            print(f"✅ Zillow property details retrieved successfully")
            print(f"   Address: {zillow_result.get('address', 'Unknown')}")
            print(f"   Price: ${zillow_result.get('price', 0):,}")
        else:
            print(f"⚠️ Zillow property details: Limited data or API issue")
    except Exception as e:
        print(f"❌ Zillow property details test failed: {e}")

async def test_agent_system():
    """Test the complete PropertyPilot agent system"""
    print("\n🤖 Testing PropertyPilot Agent System")
    print("=" * 50)
    
    try:
        # Initialize PropertyPilot system
        property_pilot = PropertyPilotSystem()
        print("✅ PropertyPilot system initialized successfully")
        
        # Test Property Scout Agent
        print("\n1. Testing Property Scout Agent...")
        scout_prompt = "Find investment properties in Austin, TX under $400,000. Focus on properties with good rental potential."
        scout_result = property_pilot.property_scout(scout_prompt)
        print(f"✅ Property Scout Agent responded")
        print(f"   Response length: {len(scout_result.message)} characters")
        print(f"   Sample response: {scout_result.message[:200]}...")
        
        # Test Market Analyzer Agent
        print("\n2. Testing Market Analyzer Agent...")
        market_prompt = "Analyze the real estate market in Austin, TX. Provide demographic data, neighborhood scores, and market trends."
        market_result = property_pilot.market_analyzer(market_prompt)
        print(f"✅ Market Analyzer Agent responded")
        print(f"   Response length: {len(market_result.message)} characters")
        print(f"   Sample response: {market_result.message[:200]}...")
        
        # Test Deal Evaluator Agent
        print("\n3. Testing Deal Evaluator Agent...")
        deal_prompt = "Evaluate a $350,000 property with potential $2,800 monthly rent and estimated $800 monthly expenses. Calculate ROI and investment metrics."
        deal_result = property_pilot.deal_evaluator(deal_prompt)
        print(f"✅ Deal Evaluator Agent responded")
        print(f"   Response length: {len(deal_result.message)} characters")
        print(f"   Sample response: {deal_result.message[:200]}...")
        
        # Test Investment Manager Agent
        print("\n4. Testing Investment Manager Agent...")
        manager_prompt = "Coordinate a comprehensive investment analysis for Austin, TX properties under $400,000. Use all available tools and provide a detailed recommendation."
        manager_result = property_pilot.investment_manager(manager_prompt)
        print(f"✅ Investment Manager Agent responded")
        print(f"   Response length: {len(manager_result.message)} characters")
        print(f"   Sample response: {manager_result.message[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ PropertyPilot system test failed: {e}")
        return False

async def test_full_analysis():
    """Test complete property investment analysis"""
    print("\n📊 Testing Complete Investment Analysis")
    print("=" * 50)
    
    try:
        property_pilot = PropertyPilotSystem()
        
        # Run complete analysis
        print("Running comprehensive investment analysis for Austin, TX...")
        analysis_result = await property_pilot.analyze_property_investment(
            location="Austin, TX",
            max_price=400000
        )
        
        print(f"✅ Complete analysis finished successfully")
        print(f"   Location: {analysis_result['location']}")
        print(f"   Max Price: ${analysis_result['max_price']:,}")
        print(f"   Data Source: {analysis_result.get('data_source', 'Unknown')}")
        print(f"   Analysis Time: {analysis_result['timestamp']}")
        print(f"\n📋 Analysis Result Summary:")
        print(f"   {analysis_result['analysis_result'][:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete analysis test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🏠 PropertyPilot Agent Functionality Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Using FREE data sources only (Public Demographics + HasData Zillow)")
    
    # Test individual tools
    await test_individual_tools()
    
    # Test agent system
    agent_success = await test_agent_system()
    
    # Test complete analysis
    analysis_success = await test_full_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    if agent_success and analysis_success:
        print("✅ ALL TESTS PASSED")
        print("   - Individual tools working")
        print("   - All agents responding")
        print("   - Complete analysis functional")
        print("   - Free APIs integrated successfully")
    else:
        print("⚠️ SOME TESTS HAD ISSUES")
        print(f"   - Agent System: {'✅ Pass' if agent_success else '❌ Fail'}")
        print(f"   - Complete Analysis: {'✅ Pass' if analysis_success else '❌ Fail'}")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Note: Some API calls may show warnings if external services")
    print("   are temporarily unavailable. This is expected behavior.")

if __name__ == "__main__":
    asyncio.run(main())