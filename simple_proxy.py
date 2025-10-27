#!/usr/bin/env python3
"""
Simple PropertyPilot Proxy Server
Connects website to AgentCore with proper authentication
"""

import json
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# AgentCore configuration
RUNTIME_ID = "PropertyPilotGeminiEnhanced-X7HpvF97L6"
REGION = "us-east-1"
RUNTIME_ARN = f"arn:aws:bedrock-agentcore:{REGION}:476114109859:runtime/{RUNTIME_ID}"

# Initialize AgentCore client
agentcore_client = boto3.client('bedrock-agentcore', region_name=REGION)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PropertyPilot Proxy"})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Proxy endpoint for PropertyPilot analysis"""
    
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('input'):
            return jsonify({"error": "Invalid request format"}), 400
        
        print(f"Received analysis request: {data}")
        
        # Call AgentCore with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = agentcore_client.invoke_agent_runtime(
                    agentRuntimeArn=RUNTIME_ARN,
                    payload=json.dumps(data).encode(),
                    qualifier="DEFAULT"
                )
                
                # Read and return response
                response_body = response['response'].read()
                result = json.loads(response_body)
                
                print(f"AgentCore response received successfully")
                return jsonify(result)
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    raise e
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    """Test AgentCore connection"""
    
    try:
        test_payload = {
            "input": {
                "prompt": "Test PropertyPilot connection",
                "type": "enhanced_analysis",
                "location": "Austin, TX",
                "max_price": 500000
            }
        }
        
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=RUNTIME_ARN,
            payload=json.dumps(test_payload).encode(),
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        result = json.loads(response_body)
        
        return jsonify({
            "status": "success",
            "message": "AgentCore connection working",
            "test_result": str(result)[:200] + "..."
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"AgentCore connection failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("🚀 Starting PropertyPilot AgentCore Proxy...")
    print(f"   Runtime ID: {RUNTIME_ID}")
    print(f"   Runtime ARN: {RUNTIME_ARN}")
    print("   Proxy: http://localhost:5000")
    print("   Health: http://localhost:5000/health")
    print("   Test: http://localhost:5000/test")
    print("   Analyze: http://localhost:5000/analyze")
    app.run(host='0.0.0.0', port=5000, debug=True)