#!/usr/bin/env python3
"""
PropertyPilot GitHub + AWS Amplify Deployment
Deploy PropertyPilot real estate platform via GitHub integration
"""

import os
import json
import subprocess
import sys
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

def check_git_status():
    """Check Git repository status"""
    print_step(1, "Checking Git Repository Status")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not in a Git repository")
            return False
        
        print("✅ Git repository detected")
        
        # Check for remote origin
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            print(f"✅ Remote origin: {remote_url}")
            return True, remote_url
        else:
            print("⚠️ No remote origin configured")
            return True, None
            
    except FileNotFoundError:
        print("❌ Git not installed")
        return False

def setup_github_repository():
    """Set up GitHub repository"""
    print_step(2, "Setting Up GitHub Repository")
    
    print("🔧 GitHub Repository Setup Options:")
    print()
    print("Option 1: Create New Repository")
    print("   1. Go to https://github.com/new")
    print("   2. Repository name: 'propertypilot-website'")
    print("   3. Description: 'PropertyPilot - AI Real Estate Investment Platform'")
    print("   4. Make it Public")
    print("   5. Don't initialize with README (we have files)")
    print("   6. Click 'Create repository'")
    print()
    print("Option 2: Use Existing Repository")
    print("   - Make sure it's accessible and you have push permissions")
    print()
    
    repo_url = input("📝 Enter your GitHub repository URL (https://github.com/username/repo): ").strip()
    
    if not repo_url:
        print("❌ Repository URL required")
        return None
    
    # Validate URL format
    if not repo_url.startswith('https://github.com/'):
        print("❌ Please use HTTPS GitHub URL format: https://github.com/username/repo")
        return None
    
    return repo_url

def prepare_website_files():
    """Prepare website files for deployment"""
    print_step(3, "Preparing Website Files for GitHub")
    
    # Check required files
    required_files = ['index.html', 'amplify.yml']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} ready")
        else:
            missing_files.append(file)
            print(f"❌ {file} missing")
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Update index.html with AgentCore endpoint if available
    endpoint_url = get_agentcore_endpoint()
    if endpoint_url:
        print(f"🔗 Configuring AgentCore endpoint: {endpoint_url}")
        update_index_with_endpoint(endpoint_url)
    
    # Create README for GitHub
    create_github_readme()
    
    print("✅ Website files prepared for GitHub deployment")
    return True

def get_agentcore_endpoint():
    """Get AgentCore endpoint from config files"""
    try:
        config_files = [
            'website_config.json',
            'agentcore_deployment_info.json'
        ]
        
        for file_path in config_files:
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

def update_index_with_endpoint(endpoint_url):
    """Update index.html with the AgentCore endpoint"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace placeholder with actual endpoint
        updated_content = content.replace(
            'placeholder="https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/your-runtime-id/invoke"',
            f'placeholder="{endpoint_url}" value="{endpoint_url}"'
        )
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Updated index.html with AgentCore endpoint")
        
    except Exception as e:
        print(f"⚠️ Could not update index.html: {e}")

def create_github_readme():
    """Create README.md for GitHub repository"""
    readme_content = f"""# PropertyPilot - AI Real Estate Investment Platform

🏠 Professional real estate investment analysis powered by AI and deployed on AWS Amplify.

## 🚀 Live Demo

Visit the live platform: [PropertyPilot Platform](https://main.amplifyapp.com)

## 🎯 Features

- **AI-Powered Analysis** - Advanced property investment insights
- **Market Research** - Real-time market conditions and trends  
- **ROI Calculations** - Comprehensive financial analysis
- **Deal Discovery** - Find undervalued investment opportunities
- **Mobile Optimized** - Works perfectly on all devices

## 🏗️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI Backend**: AWS Bedrock AgentCore + Google Gemini 2.5 Pro
- **Hosting**: AWS Amplify with global CDN
- **Security**: SSL/TLS encryption, enterprise-grade security

## 🎨 Investment Analysis Types

1. **Enhanced Analysis** - AI + Web Research for comprehensive insights
2. **Property Analysis** - ROI calculations and financial metrics
3. **Market Research** - Market conditions and trend analysis
4. **Investment Opportunities** - Deal discovery and evaluation

## 🚀 Deployment

This website is automatically deployed to AWS Amplify from this GitHub repository.

### Local Development

1. Clone the repository
2. Open `index.html` in your browser
3. Configure AgentCore endpoint
4. Start analyzing properties!

### AWS Amplify Deployment

1. Connect this repository to AWS Amplify
2. Amplify automatically builds and deploys on every push
3. Global CDN ensures fast loading worldwide

## 🔧 Configuration

The platform connects to PropertyPilot AgentCore for AI analysis:

```
AgentCore Endpoint: https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/[runtime-id]/invoke
```

## 📊 For Real Estate Investors

Perfect for:
- **Individual Investors** - Analyze potential properties
- **Real Estate Agents** - Provide data-driven insights to clients
- **Investment Firms** - Scale property analysis operations
- **Property Managers** - Evaluate portfolio performance

## 🎯 Sample Queries

Try these investment analysis queries:
- "Find cash-flowing rental properties in Austin, TX under $500,000"
- "Analyze market conditions in Seattle, WA for multi-family investments"
- "What are the best fix-and-flip opportunities in Denver, CO?"
- "Compare rental yields between Austin and Dallas markets"

## 📱 Mobile Support

Fully responsive design optimized for:
- Desktop computers
- Tablets and iPads  
- Mobile phones
- Progressive Web App capabilities

## 🔒 Security

- SSL/TLS encryption
- Secure API communications
- No sensitive data storage
- Enterprise-grade AWS infrastructure

## 📈 Performance

- Global CDN via AWS CloudFront
- Optimized for fast loading
- Auto-scaling infrastructure
- 99.9% uptime SLA

## 🆘 Support

- **Issues**: Create an issue in this repository
- **Documentation**: See deployment guides in the repo
- **AWS Support**: Available for technical issues

---

**PropertyPilot** - Where AI meets Real Estate Investment 🏠🤖💰

*Built with AWS Bedrock AgentCore • Deployed on AWS Amplify • Powered by Google Gemini*

Last updated: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Created README.md for GitHub")

def commit_and_push_to_github(repo_url):
    """Commit and push files to GitHub"""
    print_step(4, "Committing and Pushing to GitHub")
    
    try:
        # Add remote if not exists
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"🔗 Adding remote origin: {repo_url}")
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
        
        # Add all files
        print("📁 Adding files to Git...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit
        commit_message = f"Deploy PropertyPilot Real Estate Investment Platform - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        print(f"💾 Committing: {commit_message}")
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to GitHub
        print("🚀 Pushing to GitHub...")
        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
        
        if result.returncode != 0:
            # Try master branch if main fails
            print("🔄 Trying master branch...")
            subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
        
        print("✅ Successfully pushed to GitHub!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def create_amplify_instructions(repo_url):
    """Create AWS Amplify setup instructions"""
    print_step(5, "Creating AWS Amplify Setup Instructions")
    
    # Extract username and repo name from URL
    parts = repo_url.replace('https://github.com/', '').split('/')
    username = parts[0]
    repo_name = parts[1]
    
    instructions = f"""# AWS Amplify Setup Instructions

## 🚀 Connect GitHub Repository to AWS Amplify

### Step 1: Go to AWS Amplify Console
Open: https://console.aws.amazon.com/amplify/

### Step 2: Create New App
1. Click "New app" → "Host web app"
2. Choose "GitHub" as the source
3. Click "Continue"

### Step 3: Authorize GitHub
1. Click "Authorize AWS Amplify"
2. Grant permissions to access your repositories

### Step 4: Select Repository
1. Repository: `{username}/{repo_name}`
2. Branch: `main` (or `master`)
3. Click "Next"

### Step 5: Configure Build Settings
1. App name: `PropertyPilot-RealEstate-Platform`
2. Environment name: `production`
3. Build settings should auto-detect from `amplify.yml`
4. Click "Next"

### Step 6: Review and Deploy
1. Review all settings
2. Click "Save and deploy"
3. Wait 2-3 minutes for deployment

### Step 7: Get Your URL
After deployment, you'll get a URL like:
```
https://main.d1234567890.amplifyapp.com
```

## 🎯 What Happens Next

✅ **Automatic Deployments** - Every push to GitHub triggers a new deployment
✅ **Global CDN** - Your site is served from 200+ edge locations worldwide
✅ **SSL Certificate** - Automatic HTTPS with valid SSL certificate
✅ **Custom Domain** - Add your own domain name (optional)
✅ **Branch Deployments** - Deploy different branches to different URLs

## 🔧 Post-Deployment Configuration

1. **Open Your Amplify URL**
2. **Configure AgentCore Endpoint** in the website interface
3. **Test Real Estate Analysis** with sample queries
4. **Share with Investors** - Your platform is ready!

## 📊 Monitoring

Monitor your deployment:
- **Amplify Console**: https://console.aws.amazon.com/amplify/
- **Build Logs**: Check deployment status and logs
- **Analytics**: Built-in visitor analytics
- **Performance**: Monitor load times and errors

## 🌐 Custom Domain (Optional)

To add a custom domain:
1. In Amplify Console, go to "Domain management"
2. Click "Add domain"
3. Enter your domain (e.g., propertypilot.com)
4. Follow DNS configuration steps
5. SSL certificate is automatically provisioned

## 💰 Cost Estimate

For a real estate investment platform:
- **Small usage** (< 1,000 visitors/month): ~$5-15/month
- **Medium usage** (< 10,000 visitors/month): ~$25-50/month
- **Large usage** (< 100,000 visitors/month): ~$100-200/month

Includes hosting, CDN, SSL, and auto-scaling.

## 🔄 Updates

To update your website:
1. Make changes to your files
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update PropertyPilot platform"
   git push
   ```
3. Amplify automatically deploys the changes

## 🆘 Troubleshooting

**Build Failures:**
- Check build logs in Amplify Console
- Verify `amplify.yml` configuration
- Ensure all required files are in repository

**AgentCore Connection Issues:**
- Verify endpoint URL format
- Check AWS credentials and permissions
- Test endpoint manually

---

🎉 **Your PropertyPilot real estate investment platform is ready to serve professional investors worldwide!**

Repository: {repo_url}
"""
    
    with open('AMPLIFY_SETUP_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created AMPLIFY_SETUP_INSTRUCTIONS.md")
    return f"https://console.aws.amazon.com/amplify/"

def main():
    """Main deployment function"""
    print_header("PropertyPilot GitHub + AWS Amplify Deployment")
    
    print("🎯 This will:")
    print("   1. Check Git repository status")
    print("   2. Set up GitHub repository")
    print("   3. Prepare website files")
    print("   4. Push to GitHub")
    print("   5. Create Amplify setup instructions")
    
    # Step 1: Check Git status
    git_status = check_git_status()
    if git_status is False:
        print("❌ Git setup required. Please initialize a Git repository first.")
        return False
    
    has_git, existing_remote = git_status if isinstance(git_status, tuple) else (git_status, None)
    
    # Step 2: Set up GitHub repository
    if existing_remote:
        print(f"✅ Using existing remote: {existing_remote}")
        repo_url = existing_remote
    else:
        repo_url = setup_github_repository()
        if not repo_url:
            return False
    
    # Step 3: Prepare website files
    if not prepare_website_files():
        return False
    
    # Step 4: Commit and push to GitHub
    if not commit_and_push_to_github(repo_url):
        print("❌ Failed to push to GitHub")
        return False
    
    # Step 5: Create Amplify instructions
    amplify_console_url = create_amplify_instructions(repo_url)
    
    print_header("GitHub Deployment Complete!")
    
    print("🎉 PropertyPilot successfully pushed to GitHub!")
    print(f"📁 Repository: {repo_url}")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Go to AWS Amplify Console: {amplify_console_url}")
    print(f"2. Connect your GitHub repository")
    print(f"3. Deploy to get your live URL")
    print(f"4. Configure AgentCore endpoint in the website")
    
    print(f"\n📖 Detailed Instructions: AMPLIFY_SETUP_INSTRUCTIONS.md")
    
    # Ask if user wants to open Amplify console
    try:
        response = input("\n🌐 Open AWS Amplify Console now? (y/n): ").lower().strip()
        if response == 'y':
            import webbrowser
            webbrowser.open(amplify_console_url)
            print("✅ Opened AWS Amplify Console in your browser")
    except:
        pass
    
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