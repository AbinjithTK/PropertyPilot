# PropertyPilot AgentCore Deployment Guide

## 🚀 Complete Guide to Deploy PropertyPilot with Google Gemini to AWS Bedrock AgentCore

This guide will walk you through deploying PropertyPilot, an AI-powered real estate investment analysis system, to AWS Bedrock AgentCore with full capabilities including memory, observability, identity management, and built-in tools.

## 📋 Prerequisites

### 1. Install Docker Desktop

**Windows:**
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Launch Docker Desktop and complete the initial setup

**Verify Installation:**
```bash
docker --version
docker run hello-world
```

### 2. Install AWS CLI

**Windows (using MSI installer):**
1. Download from: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the installer
3. Restart your terminal

**Verify Installation:**
```bash
aws --version
```

### 3. Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., `us-west-2`)
- Default output format (`json`)

### 4. Environment Variables

Ensure your `.env` file contains:
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here
AWS_REGION=us-west-2

# Optional but recommended
HASDATA_API_KEY=2e36da63-82a5-488b-ba4a-f93c79800e53
LOG_LEVEL=INFO
```

## 🏗️ AgentCore Capabilities

PropertyPilot will be deployed with these AgentCore enhancements:

### 🧠 **Memory Integration**
- **Summary Memory**: Remembers conversation context and analysis history
- **User Preference Memory**: Learns investment preferences and criteria
- **Semantic Memory**: Stores property facts and market insights
- **Retention Policies**: Configurable data retention (90-365 days)

### 📊 **Observability**
- **CloudWatch Logs**: Comprehensive logging and monitoring
- **X-Ray Tracing**: Distributed tracing for performance analysis
- **Custom Metrics**: Business metrics and KPIs
- **Dashboards**: Pre-built performance and error tracking dashboards
- **Alerts**: Automated alerts for errors, latency, and success rates

### 🔐 **Identity Management**
- **Cognito Integration**: User authentication and authorization
- **Custom Attributes**: Investment preferences, risk tolerance, timeline
- **Session Management**: Secure session handling with 45-minute timeout
- **MFA Support**: Multi-factor authentication capability

### 🛠️ **Built-in Tools**
- **Zillow Property Search**: Real property data integration
- **Market Analysis**: Demographic and trend analysis
- **ROI Calculator**: Financial modeling and calculations
- **Risk Assessor**: Investment risk evaluation
- **Web Research**: Enhanced market research capabilities

### 🌐 **API Gateways**
- **Rate Limiting**: Prevents API abuse
- **CORS Support**: Cross-origin resource sharing
- **WebSocket Support**: Real-time updates
- **Authentication**: Integrated with Cognito

## 🚀 Deployment Steps

### Step 1: Prepare the Environment

```bash
# Navigate to your PropertyPilot directory
cd /path/to/propertypilot

# Ensure all files are present
ls -la

# Verify environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Gemini API Key:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

### Step 2: Run the Deployment

```bash
# Run the comprehensive deployment script
python build_and_deploy.py
```

The script will:
1. ✅ Check all prerequisites (Docker, AWS CLI, credentials)
2. 📦 Create ECR repository with lifecycle policies
3. 🔨 Build Docker image with AgentCore enhancements
4. 📤 Push image to ECR
5. 🔐 Create IAM role with comprehensive permissions
6. 🚀 Deploy to AgentCore with full capabilities

### Step 3: Monitor Deployment

The deployment process will show progress:

```
🚀 PropertyPilot AgentCore Builder
==================================================
AWS Region: us-west-2
AWS Account: 123456789012
Image URI: 123456789012.dkr.ecr.us-west-2.amazonaws.com/propertypilot-gemini-agentcore:latest

🔍 Checking Prerequisites...
✅ Docker: Docker version 24.0.6
✅ AWS CLI: aws-cli/2.13.25
✅ Environment variables configured
✅ AWS Credentials: arn:aws:iam::123456789012:user/developer

📦 Creating ECR Repository: propertypilot-gemini-agentcore
✅ ECR repository created with lifecycle policy

🔨 Building Docker Image...
✅ Docker image built successfully

📤 Pushing to ECR...
✅ Image pushed to ECR successfully

🔐 Creating IAM Role with AgentCore Permissions...
✅ Created IAM role with comprehensive permissions

🚀 Deploying to AgentCore...
✅ AgentCore Runtime Created Successfully!
   Runtime Name: propertypilot-gemini-enhanced
   Runtime ARN: arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/propertypilot-gemini-enhanced
   Status: ACTIVE

🎉 PropertyPilot Successfully Deployed to AgentCore!
```

## 📊 Post-Deployment

### 1. Verify Deployment

Check the generated `agentcore_deployment_info.json` file:

```json
{
  "timestamp": "2025-01-27T15:30:00.000000",
  "runtime_arn": "arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/propertypilot-gemini-enhanced",
  "runtime_name": "propertypilot-gemini-enhanced",
  "status": "ACTIVE",
  "capabilities": {
    "memory": { "enabled": true },
    "observability": { "enabled": true },
    "identity": { "enabled": true }
  }
}
```

### 2. Access AWS Console

Monitor your deployment:
- **AgentCore Console**: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#logsV2:log-groups
- **ECR Repository**: https://console.aws.amazon.com/ecr/repositories

### 3. Test the Deployment

```python
import boto3
import json

# Initialize AgentCore client
client = boto3.client('bedrock-agentcore', region_name='us-west-2')

# Test payload
payload = {
    "input": {
        "prompt": "Analyze investment opportunities in Seattle, WA under $800,000",
        "type": "enhanced_analysis",
        "location": "Seattle, WA",
        "max_price": 800000
    }
}

# Invoke the agent
response = client.invoke_agent_runtime(
    agentRuntimeArn="your-runtime-arn-here",
    payload=json.dumps(payload).encode(),
    qualifier="DEFAULT"
)

# Process response
result = json.loads(response['response'].read())
print(json.dumps(result, indent=2))
```

## 🔧 Configuration Options

### Memory Configuration

Edit `agentcore_config.json` to customize memory settings:

```json
{
  "memory": {
    "strategies": [
      "summaryMemoryStrategy",
      "userPreferenceMemoryStrategy", 
      "semanticMemoryStrategy"
    ],
    "retention_policy": {
      "summary_retention_days": 90,
      "preference_retention_days": 365,
      "fact_retention_days": 180
    }
  }
}
```

### Observability Configuration

Customize monitoring and alerting:

```json
{
  "observability": {
    "alerts": {
      "high_error_rate": {
        "threshold": 5,
        "period_minutes": 5
      },
      "high_latency": {
        "threshold_ms": 10000,
        "period_minutes": 5
      }
    }
  }
}
```

### Runtime Configuration

Adjust performance settings:

```json
{
  "runtime_configuration": {
    "memory_size_mb": 4096,
    "timeout_seconds": 900,
    "concurrent_executions": 100
  }
}
```

## 🎯 Usage Examples

### Basic Property Analysis

```python
payload = {
    "input": {
        "prompt": "Find investment properties in Austin, TX under $500,000",
        "type": "property_analysis",
        "location": "Austin, TX",
        "max_price": 500000
    }
}
```

### Market Research

```python
payload = {
    "input": {
        "prompt": "Analyze the real estate market trends in Denver, CO",
        "type": "market_research",
        "location": "Denver, CO"
    }
}
```

### ROI Analysis

```python
payload = {
    "input": {
        "prompt": "Calculate ROI for a $400,000 property with $3,200 monthly rent",
        "type": "enhanced_analysis",
        "property_price": 400000,
        "monthly_rent": 3200
    }
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Docker Build Fails**
   - Ensure Docker Desktop is running
   - Check available disk space (need ~5GB)
   - Verify internet connection for package downloads

2. **ECR Push Fails**
   - Check AWS credentials: `aws sts get-caller-identity`
   - Verify ECR permissions in IAM
   - Ensure correct region configuration

3. **AgentCore Deployment Fails**
   - Check IAM role permissions
   - Verify Gemini API key is valid
   - Ensure AgentCore is available in your region

4. **Runtime Invocation Fails**
   - Check CloudWatch logs for errors
   - Verify environment variables are set correctly
   - Test Gemini API key separately

### Getting Help

- **AWS Documentation**: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html
- **Strands Agents Docs**: https://strandsagents.com/
- **PropertyPilot Issues**: Check the deployment logs and CloudWatch

## 🎉 Success!

Once deployed, you'll have a production-ready AI real estate investment system with:

- 🤖 **Google Gemini 2.5 Pro** for intelligent analysis
- 🧠 **Persistent Memory** for personalized experiences  
- 📊 **Full Observability** for monitoring and optimization
- 🔐 **Enterprise Security** with Cognito integration
- 🛠️ **Built-in Tools** for comprehensive analysis
- ⚡ **Auto-scaling** for handling variable loads
- 🌐 **API Gateway** for secure external access

Your PropertyPilot system is now ready to help investors make data-driven real estate decisions!