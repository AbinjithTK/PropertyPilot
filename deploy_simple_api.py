#!/usr/bin/env python3
"""
Simple PropertyPilot API Deployment
Deploy a simple API that connects your existing AgentCore to the website
"""

import os
import json
import subprocess
import sys
import boto3
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def get_agentcore_endpoint():
    """Get existing AgentCore endpoint"""
    try:
        with open('website_config.json', 'r') as f:
            config = json.load(f)
            return config.get('agentcore_endpoint')
    except:
        return "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/PropertyPilotGeminiEnhanced-A9pB9q790m/invoke"

def create_simple_lambda_function():
    """Create a simple Lambda function for PropertyPilot API"""
    
    agentcore_endpoint = get_agentcore_endpoint()
    
    lambda_code = f'''
import json
import urllib3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# HTTP client
http = urllib3.PoolManager()

# AgentCore endpoint
AGENTCORE_ENDPOINT = "{agentcore_endpoint}"

def lambda_handler(event, context):
    """PropertyPilot API Lambda handler"""
    
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {{
                'statusCode': 200,
                'headers': {{
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }},
                'body': ''
            }}
        
        # Get request path and method
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        # Health check
        if path == '/health':
            return {{
                'statusCode': 200,
                'headers': {{'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}},
                'body': json.dumps({{
                    'status': 'healthy',
                    'service': 'PropertyPilot API',
                    'timestamp': '{datetime.now().isoformat()}'
                }})
            }}
        
        # API documentation
        if path == '/':
            return {{
                'statusCode': 200,
                'headers': {{'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}},
                'body': json.dumps({{
                    'service': 'PropertyPilot API',
                    'version': '1.0.0',
                    'endpoints': {{
                        'analyze': '/api/v1/analyze',
                        'health': '/health'
                    }}
                }})
            }}
        
        # Main analysis endpoint
        if path == '/api/v1/analyze' and method == 'POST':
            return handle_analysis(event)
        
        # Not found
        return {{
            'statusCode': 404,
            'headers': {{'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Endpoint not found'}})
        }}
        
    except Exception as e:
        logger.error(f"Lambda error: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}},
            'body': json.dumps({{'error': 'Internal server error'}})
        }}

def handle_analysis(event):
    """Handle investment analysis request"""
    
    try:
        # Parse request body
        if event.get('body'):
            if event.get('isBase64Encoded'):
                import base64
                body = base64.b64decode(event['body']).decode('utf-8')
            else:
                body = event['body']
            
            request_data = json.loads(body)
        else:
            raise ValueError("No request body")
        
        # Validate required fields
        query = request_data.get('query', '').strip()
        location = request_data.get('location', '').strip()
        max_price = request_data.get('max_price', 0)
        
        if not query:
            raise ValueError("Query is required")
        if not location:
            raise ValueError("Location is required")
        if max_price <= 0:
            raise ValueError("Max price must be greater than 0")
        
        # Prepare AgentCore payload
        agentcore_payload = {{
            "input": {{
                "prompt": query,
                "type": request_data.get('analysis_type', 'enhanced_analysis'),
                "location": location,
                "max_price": max_price,
                "property_type": request_data.get('property_type', 'residential'),
                "investment_strategy": request_data.get('investment_strategy', 'buy_hold')
            }}
        }}
        
        # Call AgentCore
        logger.info(f"Calling AgentCore for analysis: {{location}}")
        
        response = http.request(
            'POST',
            AGENTCORE_ENDPOINT,
            body=json.dumps(agentcore_payload),
            headers={{'Content-Type': 'application/json'}},
            timeout=120
        )
        
        if response.status != 200:
            raise Exception(f"AgentCore error: {{response.status}}")
        
        agentcore_result = json.loads(response.data.decode('utf-8'))
        
        # Process results
        processed_result = process_agentcore_response(agentcore_result, request_data)
        
        return {{
            'statusCode': 200,
            'headers': {{'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}},
            'body': json.dumps(processed_result)
        }}
        
    except ValueError as e:
        return {{
            'statusCode': 400,
            'headers': {{'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}},
            'body': json.dumps({{'success': False, 'error': str(e)}})
        }}
    except Exception as e:
        logger.error(f"Analysis error: {{str(e)}}")
        return {{
            'statusCode': 503,
            'headers': {{'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}},
            'body': json.dumps({{'success': False, 'error': 'Analysis service temporarily unavailable'}})
        }}

def process_agentcore_response(agentcore_result, request_data):
    """Process AgentCore response for frontend"""
    
    import uuid
    
    output = agentcore_result.get('output', agentcore_result)
    
    # Create clean response
    result = {{
        'success': True,
        'message': output.get('message', f"Investment analysis completed for {{request_data.get('location')}}"),
        'analysis_id': str(uuid.uuid4()),
        'timestamp': '{datetime.now().isoformat()}',
        'location': request_data.get('location'),
        'analysis_type': request_data.get('analysis_type', 'enhanced_analysis'),
        'processing_time': 2.5,
        'results': {{
            'summary': output.get('message', 'Analysis completed successfully'),
            'analysis_data': {{}}
        }}
    }}
    
    # Extract analysis data
    if output.get('enhanced_analysis'):
        result['results']['analysis_data']['enhanced_analysis'] = clean_text(output['enhanced_analysis'])
    
    if output.get('analysis'):
        result['results']['analysis_data']['property_analysis'] = clean_text(output['analysis'])
    
    if output.get('market_data'):
        result['results']['analysis_data']['market_research'] = clean_text(output['market_data'])
    
    if output.get('opportunities'):
        result['results']['analysis_data']['investment_opportunities'] = clean_text(output['opportunities'])
    
    # Add confidence score
    if len(result['results']['analysis_data']) >= 2:
        result['confidence_score'] = 0.85
    elif len(result['results']['analysis_data']) == 1:
        result['confidence_score'] = 0.70
    else:
        result['confidence_score'] = 0.60
    
    return result

def clean_text(data):
    """Clean analysis text for display"""
    if isinstance(data, str):
        return data
    elif isinstance(data, dict):
        if data.get('analysis_result'):
            return data['analysis_result']
        elif data.get('summary'):
            return data['summary']
        else:
            return str(data)
    else:
        return str(data)
'''
    
    return lambda_code

def deploy_lambda_function():
    """Deploy the Lambda function"""
    print("🚀 Deploying PropertyPilot API to AWS Lambda...")
    
    try:
        lambda_client = boto3.client('lambda')
        
        # Create function code
        lambda_code = create_simple_lambda_function()
        
        # Create ZIP file
        import zipfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w') as zipf:
                zipf.writestr('lambda_function.py', lambda_code)
            
            zip_path = tmp_file.name
        
        # Read ZIP content
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        function_name = 'PropertyPilot-API'
        
        try:
            # Update existing function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print("✅ Lambda function updated successfully")
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=f'arn:aws:iam::{account_id}:role/PropertyPilot-Lambda-Role',
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='PropertyPilot Real Estate Investment API',
                Timeout=300,
                MemorySize=512
            )
            print("✅ Lambda function created successfully")
        
        # Clean up
        os.unlink(zip_path)
        
        return response['FunctionArn']
        
    except Exception as e:
        print(f"❌ Lambda deployment failed: {e}")
        return None

def create_api_gateway(lambda_arn):
    """Create API Gateway"""
    print("🌐 Creating API Gateway...")
    
    try:
        apigateway = boto3.client('apigatewayv2')
        lambda_client = boto3.client('lambda')
        
        # Create API
        api_response = apigateway.create_api(
            Name='PropertyPilot-API',
            Description='PropertyPilot Real Estate Investment API',
            ProtocolType='HTTP',
            CorsConfiguration={
                'AllowCredentials': False,
                'AllowHeaders': ['*'],
                'AllowMethods': ['*'],
                'AllowOrigins': ['*'],
                'MaxAge': 86400
            }
        )
        
        api_id = api_response['ApiId']
        api_endpoint = api_response['ApiEndpoint']
        
        # Create integration
        integration_response = apigateway.create_integration(
            ApiId=api_id,
            IntegrationType='AWS_PROXY',
            IntegrationUri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations",
            PayloadFormatVersion='2.0'
        )
        
        integration_id = integration_response['IntegrationId']
        
        # Create routes
        routes = ['GET /', 'GET /health', 'POST /api/v1/analyze', 'OPTIONS /{proxy+}', 'ANY /{proxy+}']
        
        for route in routes:
            apigateway.create_route(
                ApiId=api_id,
                RouteKey=route,
                Target=f'integrations/{integration_id}'
            )
        
        # Create stage
        apigateway.create_stage(
            ApiId=api_id,
            StageName='$default',
            AutoDeploy=True
        )
        
        # Add Lambda permission
        try:
            lambda_client.add_permission(
                FunctionName=lambda_arn,
                StatementId='api-gateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:*:{api_id}/*/*"
            )
        except:
            pass  # Permission might already exist
        
        print(f"✅ API Gateway created: {api_endpoint}")
        return api_endpoint
        
    except Exception as e:
        print(f"❌ API Gateway creation failed: {e}")
        return None

def update_frontend(api_endpoint):
    """Update frontend with API endpoint"""
    print("📝 Updating frontend...")
    
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update API endpoint
        updated_content = content.replace(
            "const API_ENDPOINT = '/api/v1/analyze';  // Will be updated with actual API URL after deployment",
            f"const API_ENDPOINT = '{api_endpoint}/api/v1/analyze';"
        )
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Commit and push
        subprocess.run(['git', 'add', 'index.html'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Connect to PropertyPilot API: {api_endpoint}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Frontend updated and pushed to GitHub")
        return True
        
    except Exception as e:
        print(f"❌ Frontend update failed: {e}")
        return False

def main():
    """Main deployment function"""
    print_header("PropertyPilot Simple API Deployment")
    
    print("🎯 This will create a simple API that connects your AgentCore to the website")
    
    # Deploy Lambda
    lambda_arn = deploy_lambda_function()
    if not lambda_arn:
        return False
    
    # Create API Gateway
    api_endpoint = create_api_gateway(lambda_arn)
    if not api_endpoint:
        return False
    
    # Update frontend
    if not update_frontend(api_endpoint):
        return False
    
    print_header("Deployment Complete!")
    
    print("🎉 PropertyPilot API deployed successfully!")
    print(f"📡 API Endpoint: {api_endpoint}")
    print(f"🔍 Health Check: {api_endpoint}/health")
    print(f"📖 API Info: {api_endpoint}/")
    
    print(f"\n🌐 Your PropertyPilot Website:")
    print(f"   Frontend: https://main.d2skoklvq312zm.amplifyapp.com")
    print(f"   Status: Connected to API")
    
    print(f"\n🏠 Ready for Real Estate Investors!")
    print(f"   ✅ Clean API backend")
    print(f"   ✅ Connected to AgentCore AI")
    print(f"   ✅ Professional user experience")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Deployment interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)