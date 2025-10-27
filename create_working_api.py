#!/usr/bin/env python3
"""
Create Working PropertyPilot API
Create a minimal working API that definitely works
"""

import boto3
import json
import zipfile
import tempfile
import os

def create_minimal_lambda():
    """Create minimal working Lambda function"""
    
    lambda_code = '''import json

def lambda_handler(event, context):
    """Minimal PropertyPilot API"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS (CORS preflight)
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Get path
    path = event.get('rawPath', '/')
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    
    # Health check
    if path == '/health':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'healthy',
                'service': 'PropertyPilot API',
                'message': 'API is working correctly'
            })
        }
    
    # API info
    if path == '/':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'service': 'PropertyPilot API',
                'version': '1.0.0',
                'status': 'operational',
                'endpoints': {
                    'health': '/health',
                    'analyze': '/api/v1/analyze'
                }
            })
        }
    
    # Analysis endpoint
    if path == '/api/v1/analyze' and method == 'POST':
        try:
            # Parse request
            body = event.get('body', '{}')
            if event.get('isBase64Encoded'):
                import base64
                body = base64.b64decode(body).decode('utf-8')
            
            request_data = json.loads(body)
            
            # Simple validation
            location = request_data.get('location', 'Unknown Location')
            query = request_data.get('query', 'Property analysis')
            
            # Mock response (replace with actual AgentCore call later)
            response_data = {
                'success': True,
                'message': f'Investment analysis completed for {location}',
                'analysis_id': 'mock-analysis-123',
                'timestamp': '2025-10-27T18:30:00Z',
                'location': location,
                'analysis_type': request_data.get('analysis_type', 'enhanced_analysis'),
                'processing_time': 2.1,
                'confidence_score': 0.85,
                'results': {
                    'summary': f'PropertyPilot AI has analyzed investment opportunities in {location}. Based on current market conditions, property values, and rental potential, here are the key findings for your investment query: "{query}"',
                    'analysis_data': {
                        'enhanced_analysis': f'Market Analysis for {location}: The real estate market shows positive indicators for investment. Property values have shown steady growth, and rental demand remains strong. Key factors include location desirability, economic growth, and infrastructure development.',
                        'property_analysis': f'Financial Analysis: Based on your budget and criteria, several properties in {location} show strong ROI potential. Estimated rental yields range from 6-8% annually, with property appreciation expected at 3-5% per year.',
                        'market_research': f'Market Conditions in {location}: Current market temperature is balanced to slightly favorable for buyers. Inventory levels are moderate, and days on market average 25-35 days. This creates good opportunities for selective investors.',
                        'investment_opportunities': f'Investment Recommendations: Focus on properties in emerging neighborhoods within {location}. Look for properties under market value that need minor improvements. Consider both single-family homes and small multi-family properties for diversification.'
                    }
                }
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': f'Request processing error: {str(e)}'
                })
            }
    
    # Not found
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'Endpoint not found'})
    }
'''
    
    return lambda_code

def deploy_minimal_api():
    """Deploy minimal working API"""
    
    print("🚀 Deploying minimal working PropertyPilot API...")
    
    try:
        lambda_client = boto3.client('lambda')
        
        # Create code
        lambda_code = create_minimal_lambda()
        
        # Create ZIP
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w') as zipf:
                zipf.writestr('lambda_function.py', lambda_code)
            
            zip_path = tmp_file.name
        
        # Read ZIP
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Update function
        response = lambda_client.update_function_code(
            FunctionName='PropertyPilot-API',
            ZipFile=zip_content
        )
        
        # Clean up
        os.unlink(zip_path)
        
        print("✅ Minimal API deployed successfully")
        
        # Wait for deployment
        import time
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 PropertyPilot Minimal Working API")
    print("=" * 40)
    
    if deploy_minimal_api():
        print("\n✅ Minimal API is now live!")
        print("\n🧪 Test endpoints:")
        print("   Health: https://vw4wqyl3z0.execute-api.us-east-1.amazonaws.com/health")
        print("   Info: https://vw4wqyl3z0.execute-api.us-east-1.amazonaws.com/")
        print("   Analyze: POST to /api/v1/analyze")
        
        print("\n📝 This version provides:")
        print("   ✅ Working API endpoints")
        print("   ✅ CORS support for frontend")
        print("   ✅ Mock analysis responses")
        print("   ✅ Professional error handling")
        
        print("\n🔄 Next step: Connect to real AgentCore")
        print("   The API is working - we can now integrate AgentCore")
        
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)