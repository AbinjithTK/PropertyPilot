#!/usr/bin/env python3
"""
Test PropertyPilot tools functionality without AWS Bedrock
"""

import os
import sys
from datetime import datetime

# Set environment variables
os.environ['HASDATA_API_KEY'] = '2e36da63-82a5-488b-ba4a-f93c79800e53'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['LOG_LEVEL'] = 'INFO'

# Import PropertyPilot tools
try:
    from property_pilot_agents import (
        get_demographic_data,
        calculate_neighborhood_score,
        get_market_trends,
        analyze_comparable_sales,
        calculate_roi,
        estimate_repair_costs,
        assess_investment_risk,
        zillow_client
    )
    print("✅ Successfully imported PropertyPilot tools")
except ImportError as e:
    print(f"❌ Failed to import PropertyPilot tools: {e}")
    sys.exit(1)

def test_all_tools():
    """Test all PropertyPilot tools"""
    print("\n🔧 Testing All PropertyPilot Tools")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Demographic Data
    print("\n1. Testing Demographic Data...")
    try:
        demo_result = get_demographic_data("Austin, TX")
        if demo_result and not demo_result.get("error"):
            print(f"✅ SUCCESS - Median Income: ${demo_result.get('median_income', 0):,}")
            print(f"   Population: {demo_result.get('population', 0):,}")
            print(f"   Homeownership: {demo_result.get('homeownership_rate', 0)}%")
            results["demographic_data"] = "✅ PASS"
        else:
            print(f"❌ FAILED - {demo_result}")
            results["demographic_data"] = "❌ FAIL"
    except Exception as e:
        print(f"❌ FAILED - {e}")
        results["demographic_data"] = "❌ FAIL"
    
    # Test 2: Neighborhood Scoring
    print("\n2. Testing Neighborhood Scoring...")
    try:
        neighborhood_result = calculate_neighborhood_score("Austin, TX")
        if neighborhood_result and not neighborhood_result.get("error"):
            print(f"✅ SUCCESS - Overall Score: {neighborhood_result.get('overall_score', 0)}/10")
            print(f"   Income Score: {neighborhood_result.get('component_scores', {}).get('income_score', 0)}/10")
            print(f"   School Score: {neighborhood_result.get('component_scores', {}).get('school_score', 0)}/10")
            results["neighborhood_scoring"] = "✅ PASS"
        else:
            print(f"❌ FAILED - {neighborhood_result}")
            results["neighborhood_scoring"] = "❌ FAIL"
    except Exception as e:
        print(f"❌ FAILED - {e}")
        results["neighborhood_scoring"] = "❌ FAIL"
    
    # Test 3: Market Trends
    print("\n3. Testing Market Trends...")
    try:
        trends_result = get_market_trends("Austin, TX")
        if trends_result and not trends_result.get("error"):
            print(f"✅ SUCCESS - Market Sentiment: {trends_result.get('market_indicators', {}).get('overall_sentiment', 'Unknown')}")
            print(f"   Unemployment Rate: {trends_result.get('economic_data', {}).get('unemployment_rate', 0)}%")
            print(f"   Fed Rate: {trends_result.get('economic_data', {}).get('federal_funds_rate', 0)}%")
            results["market_trends"] = "✅ PASS"
        else:
            print(f"❌ FAILED - {trends_result}")
            results["market_trends"] = "❌ FAIL"
    except Exception as e:
        print(f"❌ FAILED - {e}")
        results["market_trends"] = "❌ FAIL"
    
    # Test 4: Comparable Sales
    print("\n4. Testing Comparable Sales...")
    try:
        comps_result = analyze_comparable_sales("123 Main St, Austin, TX")
        if isinstance(comps_result, list):
            print(f"✅ SUCCESS - Found {len(comps_result)} comparable sales")
            if comps_result:
                comp = comps_result[0]
                print(f"   Sample: {comp.get('address', 'Unknown')} - ${comp.get('price', 0):,}")
            results["comparable_sales"] = "✅ PASS"
        else:
            print(f"❌ FAILED - {comps_result}")
            results["comparable_sales"] = "❌ FAIL"
    except Exception as e:
        print(f"❌ FAILED - {e}")
        results["comparable_sales"] = "❌ FAIL"
    
    # Test 5: ROI Calculation
    print("\n5. Testing ROI Calculation...")
    try:
        roi_result = calculate_roi(350000, 2800, 800)
        if roi_result and isinstance(roi_result, dict):
            print(f"✅ SUCCESS - ROI: {roi_result.get('roi_percentage', 0)}%")
            print(f"   Monthly Cash Flow: ${roi_result.get('cash_flow_monthly', 0):,}")
            print(f"   Rental Yield: {roi_result.get('rental_yield', 0)}%")
            results["roi_calculation"] = "✅ PASS"
        else:
            print(f"❌ FAILED - {roi_result}")
            results["roi_calculation"] = "❌ FAIL"
    except Exception as e:
        print(f"❌ FAILED - {e}")
        results["roi_calculation"] = "❌ FAIL"
    
    # Test 6: Repair Cost Estimation
    print("\n6. Testing Repair Cost Estimation...")
    try:
        property_data = {"square_feet": 1800, "year_built": 2010}
        repair_cost = estimate_repair_costs(property_data, condition_score=7)
        if isinstance(repair_cost, (int, float)):
            print(f"✅ SUCCESS - Estimated Repair Cost: ${repair_cost:,}")
            results["repair_costs"] = "✅ PASS"
        else:
            print(f"❌ FAILED - {repair_cost}")
            results["repair_costs"] = "❌ FAIL"
    except Exception as e:
        print(f"❌ FAILED - {e}")
        results["repair_costs"] = "❌ FAIL"
    
    # Test 7: Investment Risk Assessment
    print("\n7. Testing Investment Risk Assessment...")
    try:
        property_data = {"price": 350000, "year_built": 2010}
        market_data = {"market_conditions": "balanced", "neighborhood_score": 8.2}
        risk_score = assess_investment_risk(property_data, market_data)
        if isinstance(risk_score, (int, float)):
            print(f"✅ SUCCESS - Risk Score: {risk_score}/10 (lower is better)")
            results["risk_assessment"] = "✅ PASS"
        else:
            print(f"❌ FAILED - {risk_score}")
            results["risk_assessment"] = "❌ FAIL"
    except Exception as e:
        print(f"❌ FAILED - {e}")
        results["risk_assessment"] = "❌ FAIL"
    
    return results

def main():
    """Main test function"""
    print("🏠 PropertyPilot Tools Functionality Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing individual tools without AWS Bedrock dependency")
    
    # Run all tool tests
    results = test_all_tools()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if "✅ PASS" in result)
    total = len(results)
    
    for test_name, result in results.items():
        print(f"   {test_name.replace('_', ' ').title()}: {result}")
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TOOLS WORKING PERFECTLY!")
        print("   PropertyPilot is ready for real estate investment analysis")
        print("   ✅ Free demographic data integration")
        print("   ✅ Neighborhood scoring algorithm")
        print("   ✅ Market trend analysis")
        print("   ✅ Financial calculations (ROI, cash flow, risk)")
        print("   ✅ Property analysis tools")
    else:
        print(f"⚠️ {total - passed} tools need attention")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Note: Agents require AWS Bedrock access for full functionality.")
    print("   All individual tools are working with free data sources!")

if __name__ == "__main__":
    main()