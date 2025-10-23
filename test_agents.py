"""
PropertyPilot Agent Testing Suite
Test the multi-agent system locally and on AWS Bedrock AgentCore
"""

import asyncio
import json
import os
from typing import Dict, Any
from property_pilot_agents import PropertyPilotSystem
from bedrock_deployment import BedrockDeploymentManager
import boto3


class PropertyPilotTester:
    """Test suite for PropertyPilot agents"""
    
    def __init__(self):
        self.property_pilot = PropertyPilotSystem()
        self.deployment_manager = BedrockDeploymentManager()
    
    async def test_local_agents(self):
        """Test all agents locally"""
        print("🧪 Testing PropertyPilot Agents Locally")
        print("=" * 40)
        
        # Test Property Scout
        print("\n1. Testing Property Scout Agent...")
        scout_result = self.property_pilot.property_scout(
            "Find 3-bedroom single-family homes under $350,000 in Austin, Texas"
        )
        print(f"✅ Property Scout Result:\n{scout_result.message[:200]}...")
        
        # Test Market Analyzer
        print("\n2. Testing Market Analyzer Agent...")
        market_result = self.property_pilot.market_analyzer(
            "Analyze the real estate market conditions in Austin, TX for investment opportunities"
        )
        print(f"✅ Market Analyzer Result:\n{market_result.message[:200]}...")
        
        # Test Deal Evaluator
        print("\n3. Testing Deal Evaluator Agent...")
        deal_result = self.property_pilot.deal_evaluator(
            "Evaluate a $300,000 property with potential $2,500 monthly rent and $500 monthly expenses"
        )
        print(f"✅ Deal Evaluator Result:\n{deal_result.message[:200]}...")
        
        # Test Investment Manager
        print("\n4. Testing Investment Manager Agent...")
        manager_result = self.property_pilot.investment_manager(
            "Coordinate a complete investment analysis for properties in Austin, TX under $400,000"
        )
        print(f"✅ Investment Manager Result:\n{manager_result.message[:200]}...")
        
        # Test Full Multi-Agent Analysis
        print("\n5. Testing Complete Multi-Agent Analysis...")
        full_result = await self.property_pilot.analyze_property_investment(
            location="Austin, TX",
            max_price=400000
        )
        print(f"✅ Full Analysis Complete!")
        print(f"   Location: {full_result['location']}")
        print(f"   Max Price: ${full_result['max_price']:,}")
        print(f"   Analysis: {full_result['analysis_result'][:300]}...")
    
    def test_bedrock_agents(self, deployed_agents_file: str = "deployed_agents.json"):
        """Test deployed Bedrock agents"""
        print("\n🚀 Testing PropertyPilot Agents on AWS Bedrock AgentCore")
        print("=" * 55)
        
        # Load deployed agent ARNs
        try:
            with open(deployed_agents_file, 'r') as f:
                deployed_agents = json.load(f)
        except FileNotFoundError:
            print(f"❌ Deployed agents file not found: {deployed_agents_file}")
            print("   Run deployment first: ./deploy.sh")
            return
        
        if not deployed_agents:
            print("❌ No deployed agents found")
            return
        
        print(f"Found {len(deployed_agents)} deployed agents:")
        for name, arn in deployed_agents.items():
            print(f"   {name}: {arn}")
        
        # Test each deployed agent
        session_id = "propertypilot-test-session-" + "1" * 20  # Must be 33+ chars
        
        test_cases = {
            "PropertyScout": {
                "prompt": "Find investment properties in Dallas, TX under $300,000",
                "description": "Property discovery and data collection"
            },
            "MarketAnalyzer": {
                "prompt": "Analyze market conditions in Dallas, TX for real estate investment",
                "description": "Market research and valuation"
            },
            "DealEvaluator": {
                "prompt": "Evaluate ROI for a $250,000 property with $2,200 monthly rent potential",
                "description": "Financial analysis and ROI calculations"
            },
            "InvestmentManager": {
                "prompt": "Coordinate investment analysis for Dallas, TX properties",
                "location": "Dallas, TX",
                "max_price": 350000,
                "description": "Multi-agent orchestration"
            },
            "PropertyPilotMain": {
                "prompt": "Complete investment analysis for Houston, TX",
                "location": "Houston, TX", 
                "max_price": 400000,
                "description": "Full system analysis"
            }
        }
        
        results = {}
        
        for agent_name, test_case in test_cases.items():
            if agent_name in deployed_agents:
                print(f"\n🧪 Testing {agent_name} ({test_case['description']})...")
                
                try:
                    result = self.deployment_manager.invoke_agent(
                        deployed_agents[agent_name],
                        session_id,
                        test_case
                    )
                    
                    if "error" in result:
                        print(f"❌ {agent_name} failed: {result['error']}")
                    else:
                        print(f"✅ {agent_name} success!")
                        if "message" in result:
                            print(f"   Response: {result['message'][:150]}...")
                        elif "result" in result:
                            print(f"   Analysis: {str(result['result'])[:150]}...")
                    
                    results[agent_name] = result
                    
                except Exception as e:
                    print(f"❌ {agent_name} error: {str(e)}")
                    results[agent_name] = {"error": str(e)}
            else:
                print(f"⚠️  {agent_name} not found in deployed agents")
        
        # Save test results
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Test results saved to: test_results.json")
        
        # Summary
        successful_tests = sum(1 for r in results.values() if "error" not in r)
        total_tests = len(results)
        
        print(f"\n📈 Test Summary: {successful_tests}/{total_tests} agents passed")
        
        if successful_tests == total_tests:
            print("🎉 All agents are working correctly!")
        else:
            print("⚠️  Some agents need attention. Check the logs above.")
    
    def run_performance_test(self):
        """Run performance tests on the agents"""
        print("\n⚡ Running Performance Tests")
        print("=" * 30)
        
        import time
        
        test_prompts = [
            "Find properties in Austin, TX",
            "Analyze market in Dallas, TX", 
            "Evaluate $300k property deal",
            "Generate investment report"
        ]
        
        agents = [
            ("PropertyScout", self.property_pilot.property_scout),
            ("MarketAnalyzer", self.property_pilot.market_analyzer),
            ("DealEvaluator", self.property_pilot.deal_evaluator),
            ("InvestmentManager", self.property_pilot.investment_manager)
        ]
        
        performance_results = {}
        
        for agent_name, agent in agents:
            print(f"\n🏃 Testing {agent_name} performance...")
            
            times = []
            for i, prompt in enumerate(test_prompts):
                start_time = time.time()
                try:
                    result = agent(prompt)
                    end_time = time.time()
                    response_time = end_time - start_time
                    times.append(response_time)
                    print(f"   Test {i+1}: {response_time:.2f}s")
                except Exception as e:
                    print(f"   Test {i+1}: Failed - {str(e)}")
                    times.append(None)
            
            valid_times = [t for t in times if t is not None]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
                performance_results[agent_name] = {
                    "average_response_time": round(avg_time, 2),
                    "successful_tests": len(valid_times),
                    "total_tests": len(times)
                }
                print(f"   Average: {avg_time:.2f}s ({len(valid_times)}/{len(times)} successful)")
            else:
                performance_results[agent_name] = {
                    "average_response_time": None,
                    "successful_tests": 0,
                    "total_tests": len(times)
                }
                print(f"   All tests failed")
        
        # Save performance results
        with open("performance_results.json", "w") as f:
            json.dump(performance_results, f, indent=2)
        
        print(f"\n📊 Performance results saved to: performance_results.json")


async def main():
    """Main test runner"""
    tester = PropertyPilotTester()
    
    print("🏠 PropertyPilot Agent Testing Suite")
    print("=" * 40)
    
    # Check if we should test local or deployed agents
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "bedrock":
        # Test deployed Bedrock agents
        tester.test_bedrock_agents()
    elif len(sys.argv) > 1 and sys.argv[1] == "performance":
        # Run performance tests
        tester.run_performance_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "all":
        # Run all tests
        await tester.test_local_agents()
        tester.test_bedrock_agents()
        tester.run_performance_test()
    else:
        # Test local agents by default
        await tester.test_local_agents()
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    asyncio.run(main())