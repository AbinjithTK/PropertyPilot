#!/usr/bin/env python3
"""
Test PropertyPilot AgentCore Connection
"""

import boto3
import json

def test_agentcore():
    """Test AgentCore connection"""
    
    print("Testing PropertyPilot AgentCore...")
    
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        payload = {
            "input": {
                "prompt": "Find investment properties in Austin, TX under $500,000",
                "type": "enhanced_analysis",
                "location": "Austin, TX",
                "max_price": 500000,
                "property_type": "residential"
            }
        }
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn="arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/PropertyPilotGeminiEnhanced-X7HpvF97L6",
            payload=json.dumps(payload).encode(),
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        result = json.loads(response_body)
        
        print("SUCCESS! AgentCore test successful!")
        print(f"Response: {str(result)[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"FAILED: AgentCore test failed: {e}")
        return False

if __name__ == "__main__":
    test_agentcore()