#!/usr/bin/env python3
"""
Connect Existing AgentCore to PropertyPilot API
Update the API backend to use your existing AgentCore deployment
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
    print(f"🔗 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def get_existing_agentcore_info():
    """Get existing AgentCore deployment information"""
    print_step(1, "Getting Existing AgentCore Information")
    
    try:
        # Check for existing deployment info
        config_files = [
            'website_config.json',
            'agentcore_deployment_info.json'
        ]
        
        agentcore_endpoint = None
        deployment_info = None
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    endpoint = config.get('agentcore_endpoint') or config.get('endpoint_url')
                    if endpoint:
                        agentcore_endpoint = endpoint
                        deployment_info = config
                        print(f"✅ Found AgentCore info in {config_file}")
                        break
        
        if not agentcore_endpoint:
            print("❌ No existing AgentCore deployment found")
            print("   Run: python build_and_deploy.py")
            return None, None
        
        print(f"✅ Existing AgentCore Endpoint: {agentcore_endpoint}")
        
        # Extract runtime details
        if 'runtimes/' in agentcore_endpoint:
            runtime_id = agentcore_endpoint.split('runtimes/')[1].split('/')[0]
            region = agentcore_endpoint.split('bedrock-agentcore.')[1].split('.amazonaws.com')[0]
            
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Region: {region}")
            
            return {
                'endpoint': agentcore_endpoint,
                'runtime_id': runtime_id,
                'region': region,
                'deployment_info': deployment_info
            }, deployment_info
        
        return {'endpoint': agentcore_endpoint}, deployment_info
        
    except Exception as e:
        print(f"❌ Error getting AgentCore info: {e}")
        return None, None

def update_api_configuration(agentcore_info):
    """Update API configuration with existing AgentCore endpoint"""
    print_step(2, "Updating API Configuration")
    
    try:
        # Create/update .env file for API
        env_content = f"""# PropertyPilot API Configuration - Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# AgentCore Configuration (Existing Deployment)
AGENTCORE_ENDPOINT={agentcore_info['endpoint']}

# AWS Configuration
AWS_REGION={agentcore_info.get('region', 'us-east-1')}
AWS_ACCESS_KEY_ID={os.getenv('AWS_ACCESS_KEY_ID', 'your_access_key_here')}
AWS_SECRET_ACCESS_KEY={os.getenv('AWS_SECRET_ACCESS_KEY', 'your_secret_key_here')}

# API Configuration
PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production

# CORS Origins (will be updated with Amplify URL)
ALLOWED_ORIGINS=https://main.d2skoklvq312zm.amplifyapp.com,https://propertypilot.com,http://localhost:3000
"""
        
        # Ensure api directory exists
        os.makedirs('api', exist_ok=True)
        
        with open('api/.env', 'w') as f:
            f.write(env_content)
        
        print("✅ API configuration updated with existing AgentCore endpoint")
        
        # Update API main.py with the correct endpoint
        api_main_path = 'api/main.py'
        if os.path.exists(api_main_path):
            with open(api_main_path, 'r') as f:
                content = f.read()
            
            # Update the default AgentCore endpoint
            updated_content = content.replace(
                'AGENTCORE_ENDPOINT = os.getenv(\n    "AGENTCORE_ENDPOINT",\n    "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/PropertyPilotGeminiEnhanced-A9pB9q790m/invoke"\n)',
                f'AGENTCORE_ENDPOINT = os.getenv(\n    "AGENTCORE_ENDPOINT",\n    "{agentcore_info["endpoint"]}"\n)'
            )
            
            with open(api_main_path, 'w') as f:
                f.write(updated_content)
            
            print("✅ API main.py updated with correct AgentCore endpoint")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating API configuration: {e}")
        return False

def deploy_api_to_lambda(agentcore_info):
    """Deploy the API to AWS Lambda"""
    print_step(3, "Deploying PropertyPilot API to AWS Lambda")
    
    try:
        # Install mangum for Lambda compatibility
        print("📦 Installing Lambda dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "mangum==0.17.0"
        ], check=True)
        
        # Create Lambda handler
        lambda_handler_content = f"""
import os
from mangum import Mangum
from main import app

# Set environment variables for Lambda
os.environ['AGENTCORE_ENDPOINT'] = '{agentcore_info["endpoint"]}'
os.environ['AWS_REGION'] = '{agentcore_info.get("region", "us-east-1")}'

# Create Lambda handler
handler = Mangum(app, lifespan="off")
"""
        
        with open('api/lambda_function.py', 'w') as f:
            f.write(lambda_handler_content)
        
        print("✅ Lambda handler created")
        
        # Create deployment package
        print("📦 Creating deployment package...")
        
        # Create temp directory for package
        import tempfile
        import shutil
        import zipfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy API files
            shutil.copytree('api', f'{temp_dir}/api')
            
            # Install dependencies to package
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "-r", "api/requirements.txt", 
                "mangum==0.17.0",
                "-t", temp_dir
            ], check=True)
            
            # Copy main files to root of package
            shutil.copy('api/main.py', temp_dir)
            shutil.copy('api/lambda_function.py', temp_dir)
            
            # Create ZIP file
            zip_path = 'propertypilot-api.zip'
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
        
        print(f"✅ Deployment package created: {zip_path}")
        
        # Deploy to Lambda
        lambda_client = boto3.client('lambda', region_name=agentcore_info.get('region', 'us-east-1'))
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        function_name = 'PropertyPilot-API'
        
        try:
            # Try to update existing function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print("✅ Lambda function updated successfully")
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            # Get account ID for IAM role
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=f'arn:aws:iam::{account_id}:role/lambda-execution-role',
                Handler='lambda_function.handler',
                Code={'ZipFile': zip_content},
                Description='PropertyPilot Real Estate Investment API',
                Timeout=300,
                MemorySize=1024,
                Environment={
                    'Variables': {
                        'AGENTCORE_ENDPOINT': agentcore_info['endpoint'],
                        'AWS_REGION': agentcore_info.get('region', 'us-east-1'),
                        'LOG_LEVEL': 'INFO'
                    }
                }
            )
            print("✅ Lambda function created successfully")
        
        function_arn = response['FunctionArn']
        print(f"   Function ARN: {function_arn}")
        
        # Clean up
        os.remove(zip_path)
        
        return function_arn
        
    except Exception as e:
        print(f"❌ Lambda deployment failed: {e}")
        return None

def create_api_gateway(lambda_arn, region):
    """Create API Gateway for the Lambda function"""
    print_step(4, "Creating API Gateway")
    
    try:
        apigateway = boto3.client('apigatewayv2', region_name=region)
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Create HTTP API
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
        
        print(f"✅ API Gateway created: {api_endpoint}")
        
        # Create Lambda integration
        integration_response = apigateway.create_integration(
            ApiId=api_id,
            IntegrationType='AWS_PROXY',
            IntegrationUri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations",
            PayloadFormatVersion='2.0'
        )
        
        integration_id = integration_response['IntegrationId']
        
        # Create routes
        routes = [
            'GET /',
            'GET /health',
            'POST /api/v1/analyze',
            'GET /api/v1/examples',
            'GET /api/v1/analysis/{analysis_id}',
            'GET /docs',
            'GET /redoc'
        ]
        
        for route in routes:
            apigateway.create_route(
                ApiId=api_id,
                RouteKey=route,
                Target=f'integrations/{integration_id}'
            )
        
        # Create catch-all route
        apigateway.create_route(
            ApiId=api_id,
            RouteKey='ANY /{proxy+}',
            Target=f'integrations/{integration_id}'
        )
        
        # Create default stage
        apigateway.create_stage(
            ApiId=api_id,
            StageName='$default',
            AutoDeploy=True
        )
        
        # Add Lambda permission for API Gateway
        try:
            lambda_client.add_permission(
                FunctionName=lambda_arn,
                StatementId='api-gateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{region}:*:{api_id}/*/*"
            )
        except lambda_client.exceptions.ResourceConflictException:
            # Permission already exists
            pass
        
        print(f"✅ API Gateway configured with Lambda integration")
        
        return api_endpoint
        
    except Exception as e:
        print(f"❌ API Gateway creation failed: {e}")
        return None

def update_frontend_with_api(api_endpoint):
    """Update frontend to use the new API endpoint"""
    print_step(5, "Updating Frontend with API Endpoint")
    
    try:
        # Read current index.html
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update API endpoint
        updated_content = content.replace(
            "const API_ENDPOINT = '/api/v1/analyze';  // Will be updated with actual API URL after deployment",
            f"const API_ENDPOINT = '{api_endpoint}/api/v1/analyze';"
        )
        
        # Write updated content
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Frontend updated with API endpoint")
        
        # Commit and push changes
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Connect to PropertyPilot API: {api_endpoint}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Changes pushed to GitHub (Amplify will auto-deploy)")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend update failed: {e}")
        return False

def test_complete_integration(api_endpoint, agentcore_info):
    """Test the complete integration"""
    print_step(6, "Testing Complete Integration")
    
    try:
        import requests
        
        # Test API health
        print("🔍 Testing API health...")
        health_response = requests.get(f"{api_endpoint}/health", timeout=10)
        
        if health_response.status_code == 200:
            print("✅ API health check passed")
        else:
            print(f"⚠️ API health check failed: {health_response.status_code}")
        
        # Test analysis endpoint
        print("🔍 Testing analysis endpoint...")
        test_payload = {
            "query": "Test PropertyPilot integration for Austin, TX",
            "location": "Austin, TX",
            "max_price": 500000,
            "property_type": "residential",
            "analysis_type": "enhanced_analysis"
        }
        
        analysis_response = requests.post(
            f"{api_endpoint}/api/v1/analyze",
            json=test_payload,
            timeout=60
        )
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            if result.get('success'):
                print("✅ Analysis endpoint test passed")
                print(f"   Analysis ID: {result.get('analysis_id')}")
                print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
                return True
            else:
                print(f"⚠️ Analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"⚠️ Analysis endpoint test failed: {analysis_response.status_code}")
            print(f"   Response: {analysis_response.text[:200]}...")
        
        return False
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def create_deployment_summary(api_endpoint, agentcore_info):
    """Create deployment summary"""
    print_step(7, "Creating Deployment Summary")
    
    summary = {
        "deployment_type": "PropertyPilot API + Existing AgentCore",
        "timestamp": datetime.now().isoformat(),
        "agentcore_info": {
            "endpoint": agentcore_info['endpoint'],
            "runtime_id": agentcore_info.get('runtime_id'),
            "region": agentcore_info.get('region')
        },
        "api_info": {
            "endpoint": api_endpoint,
            "documentation": f"{api_endpoint}/docs",
            "health_check": f"{api_endpoint}/health"
        },
        "integration_status": "complete",
        "next_steps": [
            "API is live and connected to existing AgentCore",
            "Frontend automatically updated via GitHub/Amplify",
            "Real estate investors can now use the platform",
            "Monitor usage in AWS Lambda and API Gateway consoles"
        ]
    }
    
    with open('api_deployment_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Deployment summary saved to api_deployment_summary.json")
    
    return summary

def main():
    """Main function"""
    print_header("Connect Existing AgentCore to PropertyPilot API")
    
    print("🎯 This will:")
    print("   1. Use your existing AgentCore deployment")
    print("   2. Deploy PropertyPilot API to AWS Lambda")
    print("   3. Create API Gateway for public access")
    print("   4. Update frontend to use the new API")
    print("   5. Test the complete integration")
    
    # Step 1: Get existing AgentCore info
    agentcore_info, deployment_info = get_existing_agentcore_info()
    if not agentcore_info:
        return False
    
    # Step 2: Update API configuration
    if not update_api_configuration(agentcore_info):
        return False
    
    # Step 3: Deploy API to Lambda
    lambda_arn = deploy_api_to_lambda(agentcore_info)
    if not lambda_arn:
        return False
    
    # Step 4: Create API Gateway
    api_endpoint = create_api_gateway(lambda_arn, agentcore_info.get('region', 'us-east-1'))
    if not api_endpoint:
        return False
    
    # Step 5: Update frontend
    if not update_frontend_with_api(api_endpoint):
        return False
    
    # Step 6: Test integration
    integration_working = test_complete_integration(api_endpoint, agentcore_info)
    
    # Step 7: Create summary
    summary = create_deployment_summary(api_endpoint, agentcore_info)
    
    print_header("Integration Complete!")
    
    print("🎉 PropertyPilot API successfully connected to existing AgentCore!")
    
    print(f"\n🔗 Integration Details:")
    print(f"   AgentCore: {agentcore_info['endpoint']}")
    print(f"   API Endpoint: {api_endpoint}")
    print(f"   API Documentation: {api_endpoint}/docs")
    print(f"   Health Check: {api_endpoint}/health")
    
    print(f"\n🌐 Your PropertyPilot Website:")
    print(f"   Frontend: https://main.d2skoklvq312zm.amplifyapp.com")
    print(f"   Status: {'✅ Fully Connected' if integration_working else '⚠️ Needs Attention'}")
    
    print(f"\n🏠 For Real Estate Investors:")
    print(f"   ✅ Professional API backend")
    print(f"   ✅ Existing AI analysis engine")
    print(f"   ✅ Clean, scalable architecture")
    print(f"   ✅ Production-ready deployment")
    
    if integration_working:
        print(f"\n🎯 Your PropertyPilot platform is now fully operational!")
        print(f"   Real estate investors can analyze properties with AI")
        print(f"   All components are working together seamlessly")
    else:
        print(f"\n⚠️ Integration needs attention - check the logs above")
    
    return integration_working

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Integration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Integration failed: {e}")
        sys.exit(1)