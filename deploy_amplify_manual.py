#!/usr/bin/env python3
"""
PropertyPilot AWS Amplify Manual Deployment
Simple deployment using AWS CLI and manual file upload
"""

import os
import json
import subprocess
import sys
import boto3
import zipfile
import tempfile
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def create_deployment_package():
    """Create a deployment package with all website files"""
    print_step(1, "Creating Deployment Package")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "propertypilot-website.zip")
    
    print("📦 Packaging website files...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main files
        files_to_include = [
            'index.html',
            'amplify.yml'
        ]
        
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"   ✅ Added {file}")
            else:
                print(f"   ⚠️ Missing {file}")
    
    print(f"✅ Deployment package created: {zip_path}")
    return zip_path

def deploy_via_console_instructions():
    """Provide manual deployment instructions"""
    print_step(2, "Manual Deployment Instructions")
    
    print("🌐 Deploy PropertyPilot to AWS Amplify Console:")
    print()
    print("1. 📂 Go to AWS Amplify Console:")
    print("   https://console.aws.amazon.com/amplify/")
    print()
    print("2. 🆕 Create New App:")
    print("   - Click 'New app' → 'Host web app'")
    print("   - Choose 'Deploy without Git provider'")
    print("   - Click 'Continue'")
    print()
    print("3. 📤 Upload Files:")
    print("   - Drag and drop 'index.html' file")
    print("   - Or click 'Choose files' and select 'index.html'")
    print("   - App name: 'PropertyPilot-RealEstate-Platform'")
    print("   - Environment name: 'production'")
    print("   - Click 'Save and deploy'")
    print()
    print("4. ⏳ Wait for Deployment:")
    print("   - Deployment takes 1-2 minutes")
    print("   - You'll get a URL like: https://main.d1234567890.amplifyapp.com")
    print()
    print("5. 🎯 Configure PropertyPilot:")
    print("   - Open your Amplify URL")
    print("   - Enter your AgentCore endpoint in the configuration section")
    print("   - Start analyzing real estate investments!")
    
    return True

def create_simple_deployment_guide():
    """Create a simple deployment guide"""
    print_step(3, "Creating Deployment Guide")
    
    guide_content = """# PropertyPilot AWS Amplify Deployment Guide

## 🚀 Quick Deploy to AWS Amplify

### Step 1: Go to AWS Amplify Console
Open: https://console.aws.amazon.com/amplify/

### Step 2: Create New App
1. Click "New app" → "Host web app"
2. Choose "Deploy without Git provider"
3. Click "Continue"

### Step 3: Upload Website
1. Drag and drop the `index.html` file
2. App name: `PropertyPilot-RealEstate-Platform`
3. Environment name: `production`
4. Click "Save and deploy"

### Step 4: Wait for Deployment
- Takes 1-2 minutes
- You'll get a URL like: `https://main.d1234567890.amplifyapp.com`

### Step 5: Configure PropertyPilot
1. Open your Amplify URL
2. In the configuration section, enter your AgentCore endpoint:
   ```
   https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/your-runtime-id/invoke
   ```
3. Start analyzing real estate investments!

## 🎯 What You Get

✅ **Professional Real Estate Investment Platform**
✅ **AI-Powered Property Analysis**
✅ **Global CDN Performance**
✅ **SSL Security**
✅ **Mobile Optimized**
✅ **Auto-Scaling**

## 💰 Cost
- Small usage: ~$5-15/month
- Medium usage: ~$25-50/month
- Includes hosting, CDN, SSL, and scaling

## 🔧 Next Steps After Deployment

1. **Get AgentCore Endpoint** (if not done):
   ```bash
   python build_and_deploy.py
   python get_agentcore_endpoint.py
   ```

2. **Configure Website**:
   - Open your Amplify URL
   - Enter AgentCore endpoint
   - Test with sample queries

3. **Customize** (optional):
   - Add your branding
   - Update company information
   - Customize investment criteria

## 📞 Support
- AWS Amplify Docs: https://docs.aws.amazon.com/amplify/
- PropertyPilot Issues: GitHub repository

---

🏠 Your PropertyPilot real estate investment platform is ready to serve professional investors! 🤖💰
"""
    
    with open('AMPLIFY_DEPLOYMENT_GUIDE.md', 'w') as f:
        f.write(guide_content)
    
    print("✅ Created AMPLIFY_DEPLOYMENT_GUIDE.md")
    return True

def check_agentcore_status():
    """Check if AgentCore is deployed"""
    print_step(4, "Checking PropertyPilot AgentCore Status")
    
    # Check for deployment info files
    deployment_files = [
        'agentcore_deployment_info.json',
        'website_config.json',
        'deployment_info.json'
    ]
    
    agentcore_deployed = False
    endpoint_url = None
    
    for file_path in deployment_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    endpoint_url = config.get('agentcore_endpoint') or config.get('endpoint_url')
                    if endpoint_url:
                        agentcore_deployed = True
                        print(f"✅ AgentCore deployed: {endpoint_url}")
                        break
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
    
    if not agentcore_deployed:
        print("⚠️ PropertyPilot AgentCore not deployed yet")
        print("   Run these commands to deploy the AI backend:")
        print("   1. python build_and_deploy.py")
        print("   2. python get_agentcore_endpoint.py")
        print()
        print("   Then configure the endpoint URL in your Amplify website")
    
    return agentcore_deployed, endpoint_url

def main():
    """Main function"""
    print_header("PropertyPilot AWS Amplify Manual Deployment")
    
    print("🎯 This will help you deploy PropertyPilot to AWS Amplify manually")
    print("   (Recommended when automated deployment has issues)")
    
    # Check if required files exist
    if not os.path.exists('index.html'):
        print("❌ index.html not found!")
        print("   Make sure you're in the PropertyPilot directory")
        return False
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    # Provide manual instructions
    deploy_via_console_instructions()
    
    # Create deployment guide
    create_simple_deployment_guide()
    
    # Check AgentCore status
    agentcore_deployed, endpoint_url = check_agentcore_status()
    
    print_header("Ready for Manual Deployment!")
    
    print("📁 Files ready for deployment:")
    print("   - index.html (main website)")
    print("   - amplify.yml (build configuration)")
    print(f"   - {zip_path} (deployment package)")
    
    print("\n🌐 Deployment Options:")
    print("   1. AWS Amplify Console (recommended)")
    print("   2. Drag & drop index.html")
    print("   3. Use deployment package zip file")
    
    if agentcore_deployed:
        print(f"\n🤖 AgentCore Ready:")
        print(f"   Endpoint: {endpoint_url}")
        print(f"   Status: Ready for website configuration")
    else:
        print(f"\n⚠️ Next Steps:")
        print(f"   1. Deploy PropertyPilot AgentCore: python build_and_deploy.py")
        print(f"   2. Deploy website to Amplify (follow guide above)")
        print(f"   3. Configure AgentCore endpoint in website")
    
    print(f"\n📖 Complete Guide: AMPLIFY_DEPLOYMENT_GUIDE.md")
    
    # Ask if user wants to open Amplify console
    try:
        response = input("\n🌐 Open AWS Amplify Console now? (y/n): ").lower().strip()
        if response == 'y':
            import webbrowser
            webbrowser.open('https://console.aws.amazon.com/amplify/')
            print("✅ Opened AWS Amplify Console in your browser")
    except:
        pass
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Deployment preparation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)