#!/usr/bin/env python3
"""
Test the deployed PropertyPilot AgentCore service
"""

import boto3
import json
import time
from datetime import datetime

def test_deployed_service():
    """Test the deployed PropertyPilot AgentCore service"""
    print("🧪 Testing Deployed PropertyPilot AgentCore Service")
    print("=" * 60)
    
    # Load deployment info
    try:
        with open('agentcore_deployment_info.json', 'r') as f:
            deployment_info = json.load(f)
        
        runtime_arn = deployment_info['runtime_arn']
        print(f"Runtime ARN: {runtime_arn}")
        print(f"Status: {deployment_info['status']}")
        
    except FileNotFoundError:
        print("❌ Deployment info file not found. Please run deployment first.")
        return False
    except Exception as e:
        print(f"❌ Failed to load deployment info: {e}")
        return False
    
    # Initialize AgentCore client
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        print("✅ AgentCore client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AgentCore client: {e}")
        return False
    
    # Wait for runtime to be active
    print("\n⏳ Waiting for runtime to be active...")
    max_wait_time = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # Check runtime status
            response = client.get_agent_runtime(agentRuntimeArn=runtime_arn)
            status = response['status']
            print(f"   Current status: {status}")
            
            if status == 'ACTIVE':
                print("✅ Runtime is now active!")
                break
            elif status in ['FAILED', 'STOPPED']:
                print(f"❌ Runtime failed with status: {status}")
                return False
            else:
                print(f"   Waiting... ({int(time.time() - start_time)}s elapsed)")
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ Failed to check runtime status: {e}")
            return False
    else:
        print("❌ Timeout waiting for runtime to become active")
        return False
    
    # Test the service
    print("\n🧪 Testing PropertyPilot functionality...")
    
    test_cases = [
        {
            "name": "Basic Property Analysis",
            "payload": {
                "input": {
                    "prompt": "Hello! Can you help me analyze real estate investments in Austin, TX?",
                    "type": "general",
                    "location": "Austin, TX"
                }
            }
        },
        {
            "name": "Market Research",
            "payload": {
                "input": {
                    "prompt": "Analyze the real estate market trends in Seattle, WA",
                    "type": "market_research",
                    "location": "Seattle, WA"
                }
            }
        },
        {
            "name": "ROI Calculation",
            "payload": {
                "input": {
                    "prompt": "Calculate ROI for a $400,000 property with $3,200 monthly rent",
                    "type": "enhanced_analysis",
                    "property_price": 400000,
                    "monthly_rent": 3200
                }
            }
        }
    ]
    
    successful_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}...")
        
        try:
            # Generate unique session ID
            session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
            
            # Invoke the agent
            response = client.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_case['payload']).encode(),
                qualifier="DEFAULT"
            )
            
            # Process response
            response_body = response['response'].read()
            result = json.loads(response_body)
            
            print(f"   ✅ {test_case['name']} - SUCCESS")
            print(f"   Response: {str(result)[:200]}...")
            successful_tests += 1
            
        except Exception as e:
            print(f"   ❌ {test_case['name']} - FAILED: {e}")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {successful_tests}/{len(test_cases)}")
    print(f"Success rate: {successful_tests/len(test_cases)*100:.1f}%")
    
    if successful_tests == len(test_cases):
        print("\n🎉 All tests passed! PropertyPilot is fully operational on AgentCore!")
        print("Your AI-powered real estate investment system is ready for production use!")
        return True
    else:
        print(f"\n⚠️ {len(test_cases) - successful_tests} test(s) failed.")
        print("The service may still be initializing or there may be configuration issues.")
        return False

if __name__ == "__main__":
    success = test_deployed_service()
    if success:
        print("\n🚀 PropertyPilot AgentCore deployment verified!")
    else:
        print("\n❌ Deployment verification failed. Check the logs above.")