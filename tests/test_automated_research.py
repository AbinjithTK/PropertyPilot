"""
Test Suite for Automated Web Research System
Tests the enhanced PropertyPilot web research capabilities
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from automated_web_research import AutomatedWebResearcher, EnhancedWebResearchAgent


class AutomatedResearchTester:
    """Test suite for automated web research functionality"""
    
    def __init__(self):
        self.researcher = AutomatedWebResearcher()
        self.enhanced_agent = EnhancedWebResearchAgent()
        self.test_results = {}
    
    async def test_market_conditions_research(self) -> Dict[str, Any]:
        """Test automated market conditions research"""
        print("🔍 Testing Market Conditions Research")
        print("=" * 40)
        
        test_locations = [
            "Austin, TX",
            "Denver, CO", 
            "Nashville, TN",
            "Phoenix, AZ"
        ]
        
        results = {}
        
        for location in test_locations:
            print(f"\n📊 Researching market conditions for {location}...")
            
            try:
                start_time = datetime.now()
                market_data = await self.researcher.research_market_conditions(location)
                end_time = datetime.now()
                
                research_time = (end_time - start_time).total_seconds()
                
                # Analyze results
                insights_count = len(market_data.get("insights", []))
                confidence_score = market_data.get("confidence_score", 0.0)
                has_synthesis = bool(market_data.get("summary", {}))
                
                results[location] = {
                    "success": True,
                    "research_time": research_time,
                    "insights_count": insights_count,
                    "confidence_score": confidence_score,
                    "has_synthesis": has_synthesis,
                    "data_quality": self._assess_data_quality(market_data)
                }
                
                print(f"   ✅ Success: {insights_count} insights, confidence: {confidence_score:.2f}")
                print(f"   ⏱️  Research time: {research_time:.2f}s")
                
            except Exception as e:
                results[location] = {
                    "success": False,
                    "error": str(e),
                    "research_time": 0
                }
                print(f"   ❌ Failed: {str(e)}")
        
        # Calculate overall performance
        successful_tests = sum(1 for r in results.values() if r.get("success"))
        avg_research_time = sum(r.get("research_time", 0) for r in results.values()) / len(results)
        avg_confidence = sum(r.get("confidence_score", 0) for r in results.values() if r.get("success")) / max(successful_tests, 1)
        
        summary = {
            "test_type": "market_conditions_research",
            "locations_tested": len(test_locations),
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / len(test_locations)) * 100,
            "avg_research_time": avg_research_time,
            "avg_confidence_score": avg_confidence,
            "detailed_results": results
        }
        
        print(f"\n📈 Market Research Test Summary:")
        print(f"   Success Rate: {summary['success_rate']:.1f}% ({successful_tests}/{len(test_locations)})")
        print(f"   Avg Research Time: {avg_research_time:.2f}s")
        print(f"   Avg Confidence: {avg_confidence:.2f}")
        
        return summary
    
    async def test_property_specific_research(self) -> Dict[str, Any]:
        """Test property-specific research functionality"""
        print("\n🏠 Testing Property-Specific Research")
        print("=" * 40)
        
        test_properties = [
            {
                "address": "123 Main St, Austin, TX 78701",
                "property_details": {
                    "price": 450000,
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "square_feet": 1800
                }
            },
            {
                "address": "456 Oak Ave, Denver, CO 80202",
                "property_details": {
                    "price": 650000,
                    "bedrooms": 4,
                    "bathrooms": 3,
                    "square_feet": 2200
                }
            }
        ]
        
        results = {}
        
        for i, prop in enumerate(test_properties):
            address = prop["address"]
            print(f"\n🔍 Researching property: {address}...")
            
            try:
                start_time = datetime.now()
                property_data = await self.researcher.research_property_specifics(
                    address, prop["property_details"]
                )
                end_time = datetime.now()
                
                research_time = (end_time - start_time).total_seconds()
                
                # Analyze results
                has_insights = bool(property_data.get("property_insights", []))
                insights_count = len(property_data.get("property_insights", []))
                has_neighborhood_data = bool(property_data.get("neighborhood_analysis", {}))
                
                results[address] = {
                    "success": "error" not in property_data,
                    "research_time": research_time,
                    "insights_count": insights_count,
                    "has_neighborhood_data": has_neighborhood_data,
                    "data_completeness": self._assess_property_data_completeness(property_data)
                }
                
                if results[address]["success"]:
                    print(f"   ✅ Success: {insights_count} insights found")
                else:
                    print(f"   ❌ Failed: {property_data.get('error', 'Unknown error')}")
                
                print(f"   ⏱️  Research time: {research_time:.2f}s")
                
            except Exception as e:
                results[address] = {
                    "success": False,
                    "error": str(e),
                    "research_time": 0
                }
                print(f"   ❌ Exception: {str(e)}")
        
        # Calculate summary
        successful_tests = sum(1 for r in results.values() if r.get("success"))
        avg_research_time = sum(r.get("research_time", 0) for r in results.values()) / len(results)
        
        summary = {
            "test_type": "property_specific_research",
            "properties_tested": len(test_properties),
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / len(test_properties)) * 100,
            "avg_research_time": avg_research_time,
            "detailed_results": results
        }
        
        print(f"\n🏠 Property Research Test Summary:")
        print(f"   Success Rate: {summary['success_rate']:.1f}% ({successful_tests}/{len(test_properties)})")
        print(f"   Avg Research Time: {avg_research_time:.2f}s")
        
        return summary
    
    async def test_investment_opportunities_research(self) -> Dict[str, Any]:
        """Test investment opportunities research"""
        print("\n💰 Testing Investment Opportunities Research")
        print("=" * 45)
        
        test_criteria = [
            {
                "location": "Austin, TX",
                "max_price": 400000,
                "property_type": "residential",
                "min_roi": 8.0,
                "strategy": "buy and hold"
            },
            {
                "location": "Phoenix, AZ",
                "max_price": 350000,
                "property_type": "residential",
                "min_roi": 10.0,
                "strategy": "fix and flip"
            }
        ]
        
        results = {}
        
        for i, criteria in enumerate(test_criteria):
            location = criteria["location"]
            print(f"\n🎯 Researching opportunities for {location}...")
            
            try:
                start_time = datetime.now()
                opportunities = await self.researcher.research_investment_opportunities(criteria)
                end_time = datetime.now()
                
                research_time = (end_time - start_time).total_seconds()
                
                # Analyze results
                has_opportunities = bool(opportunities.get("opportunities", []))
                opportunities_count = len(opportunities.get("opportunities", []))
                has_recommendations = bool(opportunities.get("recommendations", []))
                
                results[location] = {
                    "success": "error" not in opportunities,
                    "research_time": research_time,
                    "opportunities_count": opportunities_count,
                    "has_recommendations": has_recommendations,
                    "criteria_match": self._assess_criteria_match(opportunities, criteria)
                }
                
                if results[location]["success"]:
                    print(f"   ✅ Success: {opportunities_count} opportunity sources found")
                else:
                    print(f"   ❌ Failed: {opportunities.get('error', 'Unknown error')}")
                
                print(f"   ⏱️  Research time: {research_time:.2f}s")
                
            except Exception as e:
                results[location] = {
                    "success": False,
                    "error": str(e),
                    "research_time": 0
                }
                print(f"   ❌ Exception: {str(e)}")
        
        # Calculate summary
        successful_tests = sum(1 for r in results.values() if r.get("success"))
        avg_research_time = sum(r.get("research_time", 0) for r in results.values()) / len(results)
        
        summary = {
            "test_type": "investment_opportunities_research",
            "criteria_tested": len(test_criteria),
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / len(test_criteria)) * 100,
            "avg_research_time": avg_research_time,
            "detailed_results": results
        }
        
        print(f"\n💰 Investment Opportunities Test Summary:")
        print(f"   Success Rate: {summary['success_rate']:.1f}% ({successful_tests}/{len(test_criteria)})")
        print(f"   Avg Research Time: {avg_research_time:.2f}s")
        
        return summary
    
    async def test_enhanced_analysis_integration(self) -> Dict[str, Any]:
        """Test enhanced analysis integration"""
        print("\n🚀 Testing Enhanced Analysis Integration")
        print("=" * 42)
        
        test_scenarios = [
            {
                "location": "Austin, TX",
                "max_price": 500000,
                "property_type": "residential"
            },
            {
                "location": "Denver, CO",
                "max_price": 600000,
                "property_type": "residential"
            }
        ]
        
        results = {}
        
        for scenario in test_scenarios:
            location = scenario["location"]
            print(f"\n🔄 Testing enhanced analysis for {location}...")
            
            try:
                start_time = datetime.now()
                
                # Simulate property data (normally from PropertyPilot)
                mock_property_data = {
                    "location": location,
                    "max_price": scenario["max_price"],
                    "properties": [
                        {
                            "address": f"123 Test St, {location}",
                            "price": scenario["max_price"] * 0.8,
                            "bedrooms": 3,
                            "bathrooms": 2
                        }
                    ]
                }
                
                enhanced_result = await self.enhanced_agent.enhance_property_analysis(
                    mock_property_data, location
                )
                
                end_time = datetime.now()
                research_time = (end_time - start_time).total_seconds()
                
                # Analyze integration results
                has_web_research = bool(enhanced_result.get("web_research", {}))
                has_enhanced_insights = bool(enhanced_result.get("enhanced_insights", {}))
                opportunity_score = enhanced_result.get("enhanced_insights", {}).get("opportunity_score", 0.0)
                
                results[location] = {
                    "success": True,
                    "research_time": research_time,
                    "has_web_research": has_web_research,
                    "has_enhanced_insights": has_enhanced_insights,
                    "opportunity_score": opportunity_score,
                    "integration_quality": self._assess_integration_quality(enhanced_result)
                }
                
                print(f"   ✅ Success: Opportunity score {opportunity_score:.1f}/10")
                print(f"   ⏱️  Analysis time: {research_time:.2f}s")
                
            except Exception as e:
                results[location] = {
                    "success": False,
                    "error": str(e),
                    "research_time": 0
                }
                print(f"   ❌ Exception: {str(e)}")
        
        # Calculate summary
        successful_tests = sum(1 for r in results.values() if r.get("success"))
        avg_research_time = sum(r.get("research_time", 0) for r in results.values()) / len(results)
        avg_opportunity_score = sum(r.get("opportunity_score", 0) for r in results.values() if r.get("success")) / max(successful_tests, 1)
        
        summary = {
            "test_type": "enhanced_analysis_integration",
            "scenarios_tested": len(test_scenarios),
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / len(test_scenarios)) * 100,
            "avg_research_time": avg_research_time,
            "avg_opportunity_score": avg_opportunity_score,
            "detailed_results": results
        }
        
        print(f"\n🚀 Enhanced Analysis Integration Summary:")
        print(f"   Success Rate: {summary['success_rate']:.1f}% ({successful_tests}/{len(test_scenarios)})")
        print(f"   Avg Analysis Time: {avg_research_time:.2f}s")
        print(f"   Avg Opportunity Score: {avg_opportunity_score:.1f}/10")
        
        return summary
    
    def _assess_data_quality(self, market_data: Dict) -> float:
        """Assess the quality of market research data"""
        quality_score = 0.0
        
        # Check for insights
        insights = market_data.get("insights", [])
        if insights:
            quality_score += 0.3
            if len(insights) >= 3:
                quality_score += 0.2
        
        # Check for synthesis
        summary = market_data.get("summary", {})
        if summary:
            quality_score += 0.2
            if summary.get("market_overview"):
                quality_score += 0.1
            if summary.get("price_analysis"):
                quality_score += 0.1
        
        # Check confidence score
        confidence = market_data.get("confidence_score", 0.0)
        quality_score += confidence * 0.1
        
        return min(1.0, quality_score)
    
    def _assess_property_data_completeness(self, property_data: Dict) -> float:
        """Assess completeness of property-specific data"""
        completeness = 0.0
        
        if property_data.get("property_insights"):
            completeness += 0.4
        
        if property_data.get("neighborhood_analysis"):
            completeness += 0.3
        
        if property_data.get("investment_factors"):
            completeness += 0.3
        
        return completeness
    
    def _assess_criteria_match(self, opportunities: Dict, criteria: Dict) -> float:
        """Assess how well opportunities match criteria"""
        # Basic assessment - in real implementation, would analyze content
        if opportunities.get("opportunities"):
            return 0.7  # Assume reasonable match if opportunities found
        return 0.0
    
    def _assess_integration_quality(self, enhanced_result: Dict) -> float:
        """Assess quality of enhanced analysis integration"""
        quality = 0.0
        
        if enhanced_result.get("original_analysis"):
            quality += 0.2
        
        web_research = enhanced_result.get("web_research", {})
        if web_research.get("market_conditions"):
            quality += 0.3
        if web_research.get("investment_opportunities"):
            quality += 0.2
        
        enhanced_insights = enhanced_result.get("enhanced_insights", {})
        if enhanced_insights.get("market_validation"):
            quality += 0.1
        if enhanced_insights.get("actionable_recommendations"):
            quality += 0.2
        
        return quality
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of all automated research functionality"""
        print("🧪 PropertyPilot Automated Web Research Comprehensive Test")
        print("=" * 60)
        
        comprehensive_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_results": {}
        }
        
        # Run all test categories
        print("\n🚀 Starting comprehensive automated research testing...")
        
        # Test 1: Market Conditions Research
        comprehensive_results["test_results"]["market_conditions"] = await self.test_market_conditions_research()
        
        # Test 2: Property-Specific Research
        comprehensive_results["test_results"]["property_specific"] = await self.test_property_specific_research()
        
        # Test 3: Investment Opportunities Research
        comprehensive_results["test_results"]["investment_opportunities"] = await self.test_investment_opportunities_research()
        
        # Test 4: Enhanced Analysis Integration
        comprehensive_results["test_results"]["enhanced_integration"] = await self.test_enhanced_analysis_integration()
        
        # Generate overall summary
        summary = self._generate_comprehensive_summary(comprehensive_results["test_results"])
        comprehensive_results["summary"] = summary
        
        # Save results
        with open("automated_research_test_results.json", "w") as f:
            json.dump(comprehensive_results, f, indent=2)
        
        print(f"\n📊 Comprehensive Test Results Summary:")
        print(f"=" * 45)
        for category, results in summary.items():
            status_icon = "✅" if results["passed"] else "❌"
            print(f"{status_icon} {category.replace('_', ' ').title()}: {results['success_rate']:.1f}% success")
        
        overall_score = sum(r["success_rate"] for r in summary.values()) / len(summary)
        print(f"\n🎯 Overall Automated Research Score: {overall_score:.1f}%")
        print(f"📄 Detailed results saved to: automated_research_test_results.json")
        
        return comprehensive_results
    
    def _generate_comprehensive_summary(self, test_results: Dict) -> Dict:
        """Generate comprehensive summary of all tests"""
        summary = {}
        
        for test_type, results in test_results.items():
            success_rate = results.get("success_rate", 0.0)
            summary[test_type] = {
                "passed": success_rate >= 50.0,  # 50% threshold for passing
                "success_rate": success_rate,
                "avg_time": results.get("avg_research_time", 0.0)
            }
        
        return summary


async def main():
    """Main test runner for automated research"""
    tester = AutomatedResearchTester()
    
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "market":
            await tester.test_market_conditions_research()
        elif test_type == "property":
            await tester.test_property_specific_research()
        elif test_type == "opportunities":
            await tester.test_investment_opportunities_research()
        elif test_type == "integration":
            await tester.test_enhanced_analysis_integration()
        elif test_type == "comprehensive":
            await tester.run_comprehensive_test()
        else:
            print("Usage: python test_automated_research.py [market|property|opportunities|integration|comprehensive]")
    else:
        # Run comprehensive test by default
        await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())