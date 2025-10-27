#!/usr/bin/env python3
"""
PropertyPilot AWS Amplify Deployment Script
Automated deployment of PropertyPilot real estate investment website to AWS Amplify
"""

import os
import json
import subprocess
import sys
import boto3
import time
from datetime import datetime
from botocore.exceptions import ClientError

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_prerequisites():
    """Check if all prerequisites are met"""
    print_step(1, "Checking Prerequisites")
    
    issues = []
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS CLI available")
        else:
            issues.append("AWS CLI not working")
    except FileNotFoundError:
        issues.append("AWS CLI not installed")
    
    # Check AWS credentials
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            print("✅ AWS credentials configured")
        else:
            issues.append("AWS credentials not configured")
    except Exception as e:
        issues.append(f"AWS credentials error: {e}")
    
    # Check required files
    required_files = [
        'index.html',
        'amplify.yml'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            issues.append(f"Missing required file: {file}")
    
    return issues

def create_amplify_app():
    """Create AWS Amplify application"""
    print_step(2, "Creating AWS Amplify Application")
    
    try:
        amplify_client = boto3.client('amplify')
        
        app_name = "PropertyPilot-RealEstate-Platform"
        
        # Check if app already exists
        try:
            apps = amplify_client.list_apps()
            existing_app = None
            for app in apps['apps']:
                if app['name'] == app_name:
                    existing_app = app
                    break
            
            if existing_app:
                print(f"✅ Amplify app '{app_name}' already exists")
                print(f"   App ID: {existing_app['appId']}")
                print(f"   Default Domain: {existing_app['defaultDomain']}")
                return existing_app
        except Exception as e:
            print(f"⚠️ Error checking existing apps: {e}")
        
        # Create new Amplify app
        print(f"🔨 Creating new Amplify app: {app_name}")
        
        response = amplify_client.create_app(
            name=app_name,
            description="PropertyPilot - Professional Real Estate Investment Platform powered by AI",
            platform="WEB",
            environmentVariables={
                'AMPLIFY_DIFF_DEPLOY': 'false',
                'AMPLIFY_MONOREPO_APP_ROOT': '.'
            },
            enableBranchAutoBuild=False,
            enableBranchAutoDeletion=False,
            enableBasicAuth=False,
            buildSpec="""version: 1
frontend:
  phases:
    preBuild:
      commands:
        - echo "PropertyPilot Real Estate Platform - Build Started"
    build:
      commands:
        - echo "Building PropertyPilot website"
    postBuild:
      commands:
        - echo "PropertyPilot build completed"
  artifacts:
    baseDirectory: /
    files:
      - '**/*'
  cache:
    paths: []""",
            customRules=[
                {
                    'source': '/<*>',
                    'target': '/index.html',
                    'status': '404-200'
                }
            ]
        )
        
        app = response['app']
        print(f"✅ Amplify app created successfully!")
        print(f"   App ID: {app['appId']}")
        print(f"   App ARN: {app['appArn']}")
        print(f"   Default Domain: {app['defaultDomain']}")
        
        return app
        
    except ClientError as e:
        print(f"❌ Failed to create Amplify app: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error creating Amplify app: {e}")
        return None

def create_amplify_branch(app_id):
    """Create main branch for Amplify app"""
    print_step(3, "Creating Amplify Branch")
    
    try:
        amplify_client = boto3.client('amplify')
        
        branch_name = "main"
        
        # Check if branch already exists
        try:
            branches = amplify_client.list_branches(appId=app_id)
            existing_branch = None
            for branch in branches['branches']:
                if branch['branchName'] == branch_name:
                    existing_branch = branch
                    break
            
            if existing_branch:
                print(f"✅ Branch '{branch_name}' already exists")
                return existing_branch
        except Exception as e:
            print(f"⚠️ Error checking existing branches: {e}")
        
        # Create new branch
        print(f"🌿 Creating branch: {branch_name}")
        
        response = amplify_client.create_branch(
            appId=app_id,
            branchName=branch_name,
            description="Main branch for PropertyPilot real estate investment platform",
            stage="PRODUCTION",
            enableNotification=False,
            enableAutoBuild=True,
            environmentVariables={
                'USER_BRANCH': branch_name
            }
        )
        
        branch = response['branch']
        print(f"✅ Branch created successfully!")
        print(f"   Branch Name: {branch['branchName']}")
        print(f"   Branch ARN: {branch['branchArn']}")
        
        return branch
        
    except ClientError as e:
        print(f"❌ Failed to create branch: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error creating branch: {e}")
        return None

def deploy_to_amplify(app_id, branch_name="main"):
    """Deploy website files to Amplify"""
    print_step(4, "Deploying Website to Amplify")
    
    try:
        amplify_client = boto3.client('amplify')
        
        # Create deployment
        print("📦 Creating deployment...")
        
        # Read website files
        files_to_deploy = {}
        
        # Read index.html
        if os.path.exists('index.html'):
            with open('index.html', 'r', encoding='utf-8') as f:
                files_to_deploy['index.html'] = f.read()
        
        # Read amplify.yml
        if os.path.exists('amplify.yml'):
            with open('amplify.yml', 'r', encoding='utf-8') as f:
                files_to_deploy['amplify.yml'] = f.read()
        
        # Create a zip file for deployment
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files_to_deploy.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        
        # Start deployment
        response = amplify_client.start_deployment(
            appId=app_id,
            branchName=branch_name,
            sourceUrl="",  # We'll upload files directly
            fileMap=files_to_deploy
        )
        
        job_id = response['jobSummary']['jobId']
        print(f"✅ Deployment started!")
        print(f"   Job ID: {job_id}")
        
        # Wait for deployment to complete
        print("⏳ Waiting for deployment to complete...")
        
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                job_response = amplify_client.get_job(
                    appId=app_id,
                    branchName=branch_name,
                    jobId=job_id
                )
                
                job_status = job_response['job']['summary']['status']
                
                if job_status == 'SUCCEED':
                    print("✅ Deployment completed successfully!")
                    return True
                elif job_status == 'FAILED':
                    print("❌ Deployment failed!")
                    print(f"   Error: {job_response['job']['summary'].get('statusReason', 'Unknown error')}")
                    return False
                else:
                    print(f"   Status: {job_status}...")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"⚠️ Error checking deployment status: {e}")
                time.sleep(10)
        
        print("⚠️ Deployment timeout - check Amplify console for status")
        return False
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def configure_custom_domain(app_id, domain_name=None):
    """Configure custom domain for Amplify app"""
    if not domain_name:
        return None
    
    print_step(5, f"Configuring Custom Domain: {domain_name}")
    
    try:
        amplify_client = boto3.client('amplify')
        
        response = amplify_client.create_domain_association(
            appId=app_id,
            domainName=domain_name,
            enableAutoSubDomain=True,
            subDomainSettings=[
                {
                    'prefix': '',
                    'branchName': 'main'
                },
                {
                    'prefix': 'www',
                    'branchName': 'main'
                }
            ]
        )
        
        print(f"✅ Custom domain configured!")
        print(f"   Domain: {domain_name}")
        print(f"   Status: {response['domainAssociation']['domainStatus']}")
        
        return response['domainAssociation']
        
    except ClientError as e:
        print(f"❌ Failed to configure custom domain: {e}")
        return None

def get_agentcore_endpoint():
    """Get PropertyPilot AgentCore endpoint if available"""
    try:
        # Check for deployment info
        deployment_files = [
            'agentcore_deployment_info.json',
            'website_config.json',
            'deployment_info.json'
        ]
        
        for file_path in deployment_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    
                endpoint = config.get('agentcore_endpoint') or config.get('endpoint_url')
                if endpoint:
                    return endpoint
        
        return None
        
    except Exception as e:
        print(f"⚠️ Could not get AgentCore endpoint: {e}")
        return None

def create_deployment_summary(app_info, branch_info, endpoint_url=None):
    """Create deployment summary"""
    print_step(6, "Creating Deployment Summary")
    
    app_id = app_info['appId']
    default_domain = app_info['defaultDomain']
    
    # Construct Amplify URL
    amplify_url = f"https://{branch_info['branchName']}.{app_id}.amplifyapp.com"
    
    summary = {
        "deployment_type": "AWS Amplify",
        "timestamp": datetime.now().isoformat(),
        "app_info": {
            "app_id": app_id,
            "app_name": app_info['name'],
            "app_arn": app_info['appArn'],
            "default_domain": default_domain
        },
        "branch_info": {
            "branch_name": branch_info['branchName'],
            "branch_arn": branch_info['branchArn']
        },
        "urls": {
            "amplify_url": amplify_url,
            "amplify_console": f"https://console.aws.amazon.com/amplify/home#/{app_id}"
        },
        "agentcore_endpoint": endpoint_url,
        "next_steps": [
            "Open the Amplify URL to access your PropertyPilot website",
            "Configure the AgentCore endpoint in the website interface",
            "Test real estate investment analysis features",
            "Consider setting up a custom domain",
            "Monitor usage in the Amplify console"
        ]
    }
    
    # Save summary
    with open('amplify_deployment_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Deployment summary saved to amplify_deployment_summary.json")
    
    return summary

def main():
    """Main deployment function"""
    print_header("PropertyPilot AWS Amplify Deployment")
    
    print("🎯 This script will:")
    print("   1. Check prerequisites")
    print("   2. Create AWS Amplify application")
    print("   3. Create main branch")
    print("   4. Deploy PropertyPilot website")
    print("   5. Configure domain (optional)")
    print("   6. Create deployment summary")
    
    # Step 1: Check prerequisites
    issues = check_prerequisites()
    
    if issues:
        print(f"\n❌ Prerequisites not met:")
        for issue in issues:
            print(f"   - {issue}")
        print(f"\n📋 Please fix these issues and run the script again.")
        return False
    
    print("\n✅ All prerequisites met!")
    
    # Step 2: Create Amplify app
    app_info = create_amplify_app()
    if not app_info:
        print("❌ Failed to create Amplify app. Cannot continue.")
        return False
    
    # Step 3: Create branch
    branch_info = create_amplify_branch(app_info['appId'])
    if not branch_info:
        print("❌ Failed to create branch. Cannot continue.")
        return False
    
    # Step 4: Deploy website
    deployment_success = deploy_to_amplify(app_info['appId'], branch_info['branchName'])
    if not deployment_success:
        print("❌ Deployment failed. Check Amplify console for details.")
        return False
    
    # Step 5: Optional custom domain
    custom_domain = input("\n🌐 Enter custom domain name (optional, press Enter to skip): ").strip()
    domain_info = None
    if custom_domain:
        domain_info = configure_custom_domain(app_info['appId'], custom_domain)
    
    # Get AgentCore endpoint
    endpoint_url = get_agentcore_endpoint()
    
    # Step 6: Create deployment summary
    summary = create_deployment_summary(app_info, branch_info, endpoint_url)
    
    print_header("Deployment Complete!")
    
    app_id = app_info['appId']
    amplify_url = f"https://{branch_info['branchName']}.{app_id}.amplifyapp.com"
    
    print("🎉 PropertyPilot real estate investment website deployed successfully!")
    
    print(f"\n🌐 Website URLs:")
    print(f"   Primary URL: {amplify_url}")
    if custom_domain and domain_info:
        print(f"   Custom Domain: https://{custom_domain} (configuring...)")
    
    print(f"\n🔧 Management:")
    print(f"   Amplify Console: https://console.aws.amazon.com/amplify/home#{app_id}")
    print(f"   App ID: {app_id}")
    
    if endpoint_url:
        print(f"\n🤖 AgentCore Integration:")
        print(f"   Endpoint: {endpoint_url}")
        print(f"   Status: Ready for configuration")
    else:
        print(f"\n⚠️ AgentCore Integration:")
        print(f"   No endpoint found - deploy PropertyPilot to AgentCore first")
        print(f"   Run: python build_and_deploy.py")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Open {amplify_url}")
    print(f"   2. Configure AgentCore endpoint in the website")
    print(f"   3. Test real estate investment analysis")
    print(f"   4. Share with real estate investors!")
    
    print(f"\n📁 Files created:")
    print(f"   - amplify_deployment_summary.json")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)