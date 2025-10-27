#!/usr/bin/env python3
"""
Fix AgentCore Connection for PropertyPilot
Create a working connection to AgentCore runtime
"""

import boto3
import json
import requests
import os
from datetime import datetime

def test_agentcore_direct():
    """Test direct connection to AgentCore"""
    
    runtime_id = "PropertyPilotGeminiEnhanced-A9pB9q790m"
    region = "us-east-1"
    
    print(f"🧪 Testing AgentCore Runtime: {runtime_id}")
    
    # Try different endpoint formats
    endpoints_to_try = [
        f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{runtime_id}/invoke",
        f"https://bedrock-agentcore.{region}.amazonaws.com/runtime/{runtime_id}/invoke",
        f"https://{runtime_id}.bedrock-agentcore.{region}.amazonaws.com/invoke"
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            # Test with AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials:
                # Use boto3 to make authenticated request
                client = boto3.client('bedrock-agentcore', region_name=region)
                
                # Try to invoke the runtime
                try:
                    response = client.invoke_agent_runtime(
                        agentRuntimeArn=f"arn:aws:bedrock-agentcore:{region}:476114109859:runtime/{runtime_id}",
                        payload=json.dumps({
                            "input": {
                                "prompt": "test connection",
                                "type": "enhanced_analysis",
                                "location": "Austin, TX",
                                "max_price": 500000
                            }
                        }).encode(),
                        qualifier="DEFAULT"
                    )
                    
                    print("✅ AgentCore connection successful!")
                    print(f"   Response status: {response['ResponseMetadata']['HTTPStatusCode']}")
                    
                    # Read response
                    response_body = response['response'].read()
                    result = json.loads(response_body)
                    print(f"   Response preview: {str(result)[:200]}...")
                    
                    return endpoint, True
                    
                except Exception as e:
                    print(f"❌ AgentCore invoke failed: {e}")
            
            # Try direct HTTP request
            test_payload = {
                "input": {
                    "prompt": "test connection",
                    "type": "enhanced_analysis", 
                    "location": "Austin, TX",
                    "max_price": 500000
                }
            }
            
            response = requests.post(
                endpoint,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"   HTTP Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ Direct HTTP connection successful!")
                return endpoint, True
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    
    return None, False

def create_working_proxy():
    """Create a simple proxy that works with AgentCore"""
    
    print("\n🔧 Creating AgentCore proxy solution...")
    
    proxy_code = f'''#!/usr/bin/env python3
"""
PropertyPilot AgentCore Proxy
Simple proxy server to connect website to AgentCore
"""

import json
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# AgentCore configuration
RUNTIME_ID = "PropertyPilotGeminiEnhanced-A9pB9q790m"
REGION = "us-east-1"
RUNTIME_ARN = f"arn:aws:bedrock-agentcore:{{REGION}}:476114109859:runtime/{{RUNTIME_ID}}"

# Initialize AgentCore client
agentcore_client = boto3.client('bedrock-agentcore', region_name=REGION)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({{"status": "healthy", "service": "PropertyPilot Proxy"}})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Proxy endpoint for PropertyPilot analysis"""
    
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('input'):
            return jsonify({{"error": "Invalid request format"}}), 400
        
        # Call AgentCore
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=RUNTIME_ARN,
            payload=json.dumps(data).encode(),
            qualifier="DEFAULT"
        )
        
        # Read and return response
        response_body = response['response'].read()
        result = json.loads(response_body)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

if __name__ == '__main__':
    print("🚀 Starting PropertyPilot AgentCore Proxy...")
    print("   Proxy: http://localhost:5000")
    print("   Health: http://localhost:5000/health")
    print("   Analyze: http://localhost:5000/analyze")
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    
    with open('agentcore_proxy.py', 'w') as f:
        f.write(proxy_code)
    
    print("✅ Created agentcore_proxy.py")
    
    # Create requirements for proxy
    proxy_requirements = """flask==2.3.3
flask-cors==4.0.0
boto3==1.34.0
"""
    
    with open('proxy_requirements.txt', 'w') as f:
        f.write(proxy_requirements)
    
    print("✅ Created proxy_requirements.txt")
    
    return True

def update_website_for_proxy():
    """Update website to use local proxy"""
    
    print("\n📝 Updating website to use AgentCore proxy...")
    
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update endpoint to use local proxy
        updated_content = content.replace(
            "const AGENTCORE_ENDPOINT = 'https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/PropertyPilotGeminiEnhanced-A9pB9q790m/invoke';",
            "const AGENTCORE_ENDPOINT = 'http://localhost:5000/analyze';"
        )
        
        # Update connection test
        updated_content = updated_content.replace(
            """// Simple test to see if we can reach the endpoint
                const response = await fetch(AGENTCORE_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        input: {
                            prompt: "test connection",
                            type: "enhanced_analysis",
                            location: "test",
                            max_price: 100000
                        }
                    })
                });""",
            """// Test proxy connection
                const response = await fetch('http://localhost:5000/health', {
                    method: 'GET'
                });"""
        )
        
        with open('index_with_proxy.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Created index_with_proxy.html for local testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update website: {e}")
        return False

def create_simple_test():
    """Create a simple test script"""
    
    test_code = f'''#!/usr/bin/env python3
"""
Test PropertyPilot AgentCore Connection
"""

import boto3
import json

def test_agentcore():
    """Test AgentCore connection"""
    
    print("🧪 Testing PropertyPilot AgentCore...")
    
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        payload = {{
            "input": {{
                "prompt": "Find investment properties in Austin, TX under $500,000",
                "type": "enhanced_analysis",
                "location": "Austin, TX",
                "max_price": 500000,
                "property_type": "residential"
            }}
        }}
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn="arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/PropertyPilotGeminiEnhanced-A9pB9q790m",
            payload=json.dumps(payload).encode(),
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        result = json.loads(response_body)
        
        print("✅ AgentCore test successful!")
        print(f"Response: {{str(result)[:500]}}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCore test failed: {{e}}")
        return False

if __name__ == "__main__":
    test_agentcore()
'''
    
    with open('test_agentcore_direct.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Created test_agentcore_direct.py")

def main():
    """Main function"""
    
    print("🔧 PropertyPilot AgentCore Connection Fix")
    print("=" * 50)
    
    # Test current connection
    endpoint, working = test_agentcore_direct()
    
    if working:
        print(f"\n✅ AgentCore is working at: {endpoint}")
        print("   The issue might be CORS restrictions for browser connections")
    else:
        print("\n❌ AgentCore connection issues detected")
    
    # Create proxy solution
    create_working_proxy()
    
    # Update website
    update_website_for_proxy()
    
    # Create test script
    create_simple_test()
    
    print("\n🎯 Solutions Created:")
    print("   1. agentcore_proxy.py - Local proxy server")
    print("   2. index_with_proxy.html - Website for local testing")
    print("   3. test_agentcore_direct.py - Direct AgentCore test")
    
    print("\n🚀 To fix the connection:")
    print("   Option 1 - Local Testing:")
    print("     1. pip install -r proxy_requirements.txt")
    print("     2. python agentcore_proxy.py")
    print("     3. Open index_with_proxy.html in browser")
    
    print("\n   Option 2 - Test AgentCore Directly:")
    print("     1. python test_agentcore_direct.py")
    
    print("\n   Option 3 - Deploy Proxy to AWS Lambda:")
    print("     1. Convert proxy to Lambda function")
    print("     2. Update website to use Lambda endpoint")
    
    return True

if __name__ == "__main__":
    main()