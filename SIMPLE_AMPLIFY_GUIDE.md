# PropertyPilot AWS Amplify Deployment Guide

## Quick Deploy to AWS Amplify

### Step 1: Go to AWS Amplify Console
Open: https://console.aws.amazon.com/amplify/

### Step 2: Create New App
1. Click "New app" -> "Host web app"
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
   https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/PropertyPilotGeminiEnhanced-A9pB9q790m/invoke
   ```
3. Start analyzing real estate investments!

## What You Get

- Professional Real Estate Investment Platform
- AI-Powered Property Analysis
- Global CDN Performance
- SSL Security
- Mobile Optimized
- Auto-Scaling

## Cost
- Small usage: ~$5-15/month
- Medium usage: ~$25-50/month
- Includes hosting, CDN, SSL, and scaling

## Next Steps After Deployment

1. Open your Amplify URL
2. Enter AgentCore endpoint in configuration
3. Test with sample queries like:
   - "Find investment properties in Austin, TX under $500,000"
   - "Analyze market conditions in Seattle, WA"
   - "What are good investment opportunities in Denver, CO?"

Your PropertyPilot real estate investment platform is ready to serve professional investors!