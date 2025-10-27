#!/usr/bin/env python3
"""
PropertyPilot Investor Website Setup
Complete setup script for deploying PropertyPilot as a real estate investment website
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🏠 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_prerequisites():
    """Check if all prerequisites are met"""
    print_step(1, "Checking Prerequisites")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    else:
        print("✅ Python version OK")
    
    # Check for required files
    required_files = [
        'main.py',
        'property_pilot_agents.py', 
        'build_and_deploy.py',
        'investor_dashboard.html',
        'simple_investor_site.html'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            issues.append(f"Missing required file: {file}")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check for required environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['GEMINI_API_KEY', 'AWS_REGION']
        for var in required_vars:
            if os.getenv(var):
                print(f"✅ {var} configured")
            else:
                issues.append(f"Missing environment variable: {var}")
    else:
        issues.append("Missing .env file - copy from .env.example")
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS CLI available")
        else:
            issues.append("AWS CLI not working")
    except FileNotFoundError:
        issues.append("AWS CLI not installed")
    
    return issues

def deploy_agentcore():
    """Deploy PropertyPilot to AgentCore"""
    print_step(2, "Deploying PropertyPilot to AWS Bedrock AgentCore")
    
    print("🚀 Starting AgentCore deployment...")
    print("   This will take 3-5 minutes...")
    
    try:
        # Run the deployment script
        result = subprocess.run([
            sys.executable, 'build_and_deploy.py'
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ AgentCore deployment successful!")
            print(result.stdout)
            return True
        else:
            print("❌ AgentCore deployment failed!")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Deployment timed out (>10 minutes)")
        return False
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def get_endpoint_info():
    """Get AgentCore endpoint information"""
    print_step(3, "Getting AgentCore Endpoint Information")
    
    try:
        # Run the endpoint script
        result = subprocess.run([
            sys.executable, 'get_agentcore_endpoint.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Endpoint information retrieved!")
            print(result.stdout)
            
            # Try to load the generated config
            if os.path.exists('website_config.json'):
                with open('website_config.json', 'r') as f:
                    config = json.load(f)
                return config.get('agentcore_endpoint')
            
        else:
            print("⚠️ Could not get endpoint automatically")
            print(result.stderr)
            
    except Exception as e:
        print(f"⚠️ Error getting endpoint: {e}")
    
    return None

def setup_website_files(endpoint_url=None):
    """Setup website files with configuration"""
    print_step(4, "Setting Up Website Files")
    
    # Create a configured version of the simple site
    if endpoint_url:
        print(f"📝 Creating configured website with endpoint: {endpoint_url}")
        
        # Read the simple site template
        with open('simple_investor_site.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace the placeholder endpoint
        html_content = html_content.replace(
            'placeholder="https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/your-runtime-id/invoke"',
            f'placeholder="{endpoint_url}" value="{endpoint_url}"'
        )
        
        # Save configured version
        with open('configured_investor_site.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Created configured_investor_site.html with your endpoint")
    
    # Create deployment package
    deployment_files = [
        'investor_dashboard.html',
        'simple_investor_site.html',
        'configured_investor_site.html' if endpoint_url else None
    ]
    
    deployment_files = [f for f in deployment_files if f and os.path.exists(f)]
    
    print(f"📦 Website files ready for deployment:")
    for file in deployment_files:
        print(f"   - {file}")
    
    return deployment_files

def create_deployment_instructions(endpoint_url, deployment_files):
    """Create deployment instructions"""
    print_step(5, "Creating Deployment Instructions")
    
    instructions = f"""
# PropertyPilot Real Estate Investment Website - Deployment Instructions

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Your PropertyPilot Configuration

**AgentCore Endpoint URL:**
```
{endpoint_url or 'Not configured - run get_agentcore_endpoint.py'}
```

## 🌐 Website Files Ready for Deployment

{chr(10).join([f'- {file}' for file in deployment_files])}

## 🚀 Quick Deployment Options

### Option 1: Netlify (Easiest - 2 minutes)
1. Go to https://netlify.com
2. Drag and drop `configured_investor_site.html` (or any website file)
3. Your site will be live instantly!

### Option 2: AWS S3 + CloudFront
```bash
# Create S3 bucket
aws s3 mb s3://propertypilot-website-$(date +%s)

# Upload website
aws s3 cp configured_investor_site.html s3://propertypilot-website-$(date +%s)/index.html --acl public-read

# Enable website hosting
aws s3 website s3://propertypilot-website-$(date +%s) --index-document index.html
```

### Option 3: Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

## 🧪 Testing Your Website

1. Open any of the website files in your browser
2. The AgentCore endpoint should be pre-configured
3. Try these test queries:
   - "Find investment properties in Austin, TX under $500,000"
   - "Analyze market conditions in Seattle, WA"
   - "What are good investment opportunities in Denver, CO?"

## 📊 Features Available

- **Enhanced Analysis**: AI + Web Research
- **Property Analysis**: ROI Calculations  
- **Market Research**: Market Conditions
- **Investment Opportunities**: Find Deals

## 🔧 Customization

Edit the HTML files to:
- Add your company branding
- Customize colors and styling
- Add additional investment criteria
- Integrate with your existing website

## 📞 Support

- Check AWS CloudWatch logs for AgentCore issues
- Test endpoint directly with curl or Postman
- Review WEBSITE_DEPLOYMENT_GUIDE.md for advanced setup

---

🎉 Your PropertyPilot real estate investment website is ready!
"""
    
    with open('DEPLOYMENT_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print("✅ Created DEPLOYMENT_INSTRUCTIONS.md")
    print("📖 Review this file for complete deployment steps")

def main():
    """Main setup function"""
    print_header("PropertyPilot Real Estate Investment Website Setup")
    
    print("🎯 This script will:")
    print("   1. Check prerequisites")
    print("   2. Deploy PropertyPilot to AWS Bedrock AgentCore") 
    print("   3. Get your AgentCore endpoint URL")
    print("   4. Configure website files")
    print("   5. Create deployment instructions")
    
    # Step 1: Check prerequisites
    issues = check_prerequisites()
    
    if issues:
        print(f"\n❌ Prerequisites not met:")
        for issue in issues:
            print(f"   - {issue}")
        print(f"\n📋 Please fix these issues and run the script again.")
        return False
    
    print("\n✅ All prerequisites met!")
    
    # Ask user if they want to proceed with deployment
    response = input("\n🤔 Deploy PropertyPilot to AgentCore now? (y/n): ").lower().strip()
    
    if response != 'y':
        print("⏸️ Skipping AgentCore deployment")
        print("   Run 'python build_and_deploy.py' manually when ready")
        endpoint_url = None
    else:
        # Step 2: Deploy to AgentCore
        if not deploy_agentcore():
            print("❌ AgentCore deployment failed. Cannot continue.")
            return False
        
        # Step 3: Get endpoint information
        endpoint_url = get_endpoint_info()
    
    # Step 4: Setup website files
    deployment_files = setup_website_files(endpoint_url)
    
    # Step 5: Create deployment instructions
    create_deployment_instructions(endpoint_url, deployment_files)
    
    print_header("Setup Complete!")
    
    if endpoint_url:
        print("🎉 PropertyPilot is ready for real estate investors!")
        print(f"\n🌐 Your AgentCore Endpoint: {endpoint_url}")
        print(f"\n📁 Website files created:")
        for file in deployment_files:
            print(f"   - {file}")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Deploy any website file to Netlify, Vercel, or AWS S3")
        print(f"   2. Test with real estate investment queries")
        print(f"   3. Customize branding and styling as needed")
        
        print(f"\n📖 Full instructions: DEPLOYMENT_INSTRUCTIONS.md")
    else:
        print("⚠️ AgentCore endpoint not configured")
        print("   Run 'python get_agentcore_endpoint.py' after deployment")
        print("   Then manually configure the endpoint in your website files")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)