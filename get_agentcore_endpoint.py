#!/usr/bin/env python3
"""
Get PropertyPilot AgentCore Endpoint
Retrieves the AgentCore runtime endpoint URL for website configuration
"""

import json
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_agentcore_endpoint():
    """Get the AgentCore endpoint URL from deployment info"""
    
    print("🔍 Looking for PropertyPilot AgentCore deployment...")
    
    # Check for deployment info file
    deployment_files = [
        'agentcore_deployment_info.json',
        'deployment_info.json',
        'agentcore_config.json'
    ]
    
    deployment_info = None
    for file_path in deployment_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    deployment_info = json.load(f)
                print(f"✅ Found deployment info in {file_path}")
                break
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
    
    if not deployment_info:
        print("❌ No deployment info found. Please deploy PropertyPilot to AgentCore first.")
        print("   Run: python build_and_deploy.py")
        return None
    
    # Extract runtime information
    runtime_arn = deployment_info.get('runtime_arn')
    region = deployment_info.get('region') or os.getenv('AWS_REGION', 'us-west-2')
    
    if not runtime_arn:
        print("❌ No runtime ARN found in deployment info")
        return None
    
    # Parse runtime ID from ARN
    # ARN format: arn:aws:bedrock-agentcore:region:account:runtime/runtime-id
    try:
        runtime_id = runtime_arn.split('/')[-1]
    except:
        print(f"❌ Could not parse runtime ID from ARN: {runtime_arn}")
        return None
    
    # Construct endpoint URL
    endpoint_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{runtime_id}/invoke"
    
    return {
        'endpoint_url': endpoint_url,
        'runtime_arn': runtime_arn,
        'runtime_id': runtime_id,
        'region': region,
        'deployment_info': deployment_info
    }

def test_agentcore_endpoint(endpoint_url):
    """Test the AgentCore endpoint"""
    
    print(f"🧪 Testing AgentCore endpoint: {endpoint_url}")
    
    try:
        import requests
        
        # Test payload
        test_payload = {
            "input": {
                "prompt": "Test PropertyPilot connection",
                "type": "property_analysis",
                "location": "Austin, TX",
                "max_price": 500000
            }
        }
        
        # Make test request
        response = requests.post(
            endpoint_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ AgentCore endpoint is working!")
            result = response.json()
            if result.get('output'):
                print(f"   Response: {result['output'].get('message', 'Success')}")
            return True
        else:
            print(f"❌ AgentCore endpoint test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except ImportError:
        print("⚠️ 'requests' library not available for testing")
        print("   Install with: pip install requests")
        return None
    except Exception as e:
        print(f"❌ AgentCore endpoint test failed: {e}")
        return False

def generate_website_config(endpoint_info):
    """Generate website configuration"""
    
    config = {
        "agentcore_endpoint": endpoint_info['endpoint_url'],
        "runtime_id": endpoint_info['runtime_id'],
        "region": endpoint_info['region'],
        "deployment_timestamp": datetime.now().isoformat(),
        "website_instructions": {
            "step_1": "Copy the agentcore_endpoint URL below",
            "step_2": "Open investor_dashboard.html in your browser",
            "step_3": "Paste the endpoint URL in the configuration section",
            "step_4": "Start analyzing real estate investments!"
        }
    }
    
    # Save configuration
    with open('website_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("💾 Website configuration saved to website_config.json")
    
    return config

def main():
    """Main function"""
    
    print("🏠 PropertyPilot AgentCore Endpoint Configuration")
    print("=" * 50)
    
    # Get endpoint information
    endpoint_info = get_agentcore_endpoint()
    
    if not endpoint_info:
        print("\n❌ Could not retrieve AgentCore endpoint information")
        print("\n📋 Next Steps:")
        print("1. Deploy PropertyPilot to AgentCore: python build_and_deploy.py")
        print("2. Run this script again to get the endpoint URL")
        return
    
    print(f"\n✅ PropertyPilot AgentCore Runtime Found!")
    print(f"   Runtime ARN: {endpoint_info['runtime_arn']}")
    print(f"   Runtime ID: {endpoint_info['runtime_id']}")
    print(f"   Region: {endpoint_info['region']}")
    
    print(f"\n🌐 AgentCore Endpoint URL:")
    print(f"   {endpoint_info['endpoint_url']}")
    
    # Test endpoint
    test_result = test_agentcore_endpoint(endpoint_info['endpoint_url'])
    
    # Generate website configuration
    config = generate_website_config(endpoint_info)
    
    print(f"\n🎯 Website Setup Instructions:")
    print(f"1. Open investor_dashboard.html in your browser")
    print(f"2. In the 'AgentCore Configuration' section, paste this URL:")
    print(f"   {endpoint_info['endpoint_url']}")
    print(f"3. Enter your investment criteria and click 'Analyze Investment Opportunity'")
    
    if test_result is True:
        print(f"\n🎉 Your PropertyPilot website is ready to use!")
    elif test_result is False:
        print(f"\n⚠️ Endpoint test failed. Check your AWS credentials and AgentCore deployment.")
    else:
        print(f"\n💡 Endpoint URL ready. Test it manually in your website.")
    
    print(f"\n📁 Files created:")
    print(f"   - website_config.json (configuration backup)")
    print(f"   - investor_dashboard.html (your website)")
    
    print(f"\n🚀 Deploy your website to:")
    print(f"   - AWS S3 + CloudFront")
    print(f"   - Netlify (drag & drop investor_dashboard.html)")
    print(f"   - Vercel")
    print(f"   - Any web hosting service")
    
    print(f"\n📖 Full deployment guide: WEBSITE_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()