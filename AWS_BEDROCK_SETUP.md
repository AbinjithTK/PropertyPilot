# AWS Bedrock Setup Guide for PropertyPilot

## 🚀 **Quick Setup Steps**

### 1. **Configure AWS Credentials**

**Option A: Using AWS CLI (Recommended)**
```bash
# Install AWS CLI if not already installed
# Configure your credentials
aws configure

# Enter your credentials when prompted:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]  
# Default region name: us-east-1
# Default output format: json
```

**Option B: Using Environment Variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your AWS credentials
AWS_ACCESS_KEY_ID=your_actual_access_key_id
AWS_SECRET_ACCESS_KEY=your_actual_secret_access_key
AWS_REGION=us-east-1
```

### 2. **Enable Bedrock Models**

You need to enable Claude models in AWS Bedrock console:

1. **Go to AWS Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. **Navigate to**: Model access (left sidebar)
3. **Click**: "Manage model access" 
4. **Enable these models**:
   - ✅ **Claude 3.5 Sonnet** (anthropic.claude-3-5-sonnet-20241022-v2:0)
   - ✅ **Claude 3 Haiku** (anthropic.claude-3-haiku-20240307-v1:0)
   - ✅ **Claude 3 Opus** (anthropic.claude-3-opus-20240229-v1:0)

5. **Click**: "Request model access" for each
6. **Wait**: 2-5 minutes for approval (usually instant)

### 3. **Test AWS Bedrock Connection**

```bash
# Test your AWS connection
python -c "
import boto3
try:
    client = boto3.client('bedrock', region_name='us-east-1')
    models = client.list_foundation_models()
    print('✅ AWS Bedrock connection successful!')
    print(f'Available models: {len(models[\"modelSummaries\"])}')
except Exception as e:
    print(f'❌ AWS Bedrock connection failed: {e}')
"
```

### 4. **Test PropertyPilot Agents**

```bash
# Run the agent functionality test
python test_agents_functionality.py
```

## 🔑 **Required AWS Permissions**

Your AWS user/role needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/PropertyPilot-*"
        }
    ]
}
```

## 🏠 **PropertyPilot Configuration**

### **Strands Agents Model Configuration**

PropertyPilot uses Strands Agents which automatically configures Bedrock. The agents will use:

- **Default Model**: Claude 3.5 Sonnet (best performance)
- **Fallback Model**: Claude 3 Haiku (faster, cheaper)
- **Region**: us-east-1 (or your configured region)

### **Model Selection Priority**
1. **Claude 3.5 Sonnet** - Best for complex analysis
2. **Claude 3 Haiku** - Fast responses for simple tasks
3. **Claude 3 Opus** - Most capable for difficult reasoning

## 🧪 **Testing Your Setup**

### **1. Test Individual Tools (No AWS Required)**
```bash
python test_tools_only.py
```
Expected: ✅ All 7 tools should pass

### **2. Test Full Agent System (Requires AWS)**
```bash
python test_agents_functionality.py
```
Expected: ✅ All agents should respond successfully

### **3. Test Complete Analysis**
```bash
python -c "
import asyncio
from property_pilot_agents import PropertyPilotSystem

async def test():
    pp = PropertyPilotSystem()
    result = await pp.analyze_property_investment('Austin, TX', 400000)
    print('✅ PropertyPilot Analysis Complete!')
    print(f'Result: {result[\"analysis_result\"][:200]}...')

asyncio.run(test())
"
```

## 💰 **AWS Bedrock Costs**

### **Claude Model Pricing (us-east-1)**
- **Claude 3.5 Sonnet**: $3.00 per 1M input tokens, $15.00 per 1M output tokens
- **Claude 3 Haiku**: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- **Claude 3 Opus**: $15.00 per 1M input tokens, $75.00 per 1M output tokens

### **Typical PropertyPilot Usage**
- **Property Analysis**: ~2,000 tokens ($0.01-0.05 per analysis)
- **Market Research**: ~3,000 tokens ($0.02-0.08 per research)
- **Complete Investment Analysis**: ~5,000 tokens ($0.03-0.12 per analysis)

### **Monthly Estimates**
- **Light Usage** (10 analyses/month): $1-5/month
- **Regular Usage** (50 analyses/month): $5-25/month  
- **Heavy Usage** (200 analyses/month): $20-100/month

## 🔧 **Troubleshooting**

### **Common Issues**

**❌ "AccessDeniedException: Model access is denied"**
- **Solution**: Enable Claude models in Bedrock console (Step 2 above)
- **Wait**: 2-5 minutes after requesting access

**❌ "INVALID_PAYMENT_INSTRUMENT"**
- **Solution**: Add valid payment method to AWS account
- **Go to**: AWS Billing Console → Payment methods

**❌ "NoCredentialsError"**
- **Solution**: Configure AWS credentials (Step 1 above)
- **Check**: `aws sts get-caller-identity` works

**❌ "Region not supported"**
- **Solution**: Use supported regions: us-east-1, us-west-2, eu-west-1
- **Update**: AWS_REGION in .env file

### **Debug Commands**

```bash
# Check AWS credentials
aws sts get-caller-identity

# List available Bedrock models
aws bedrock list-foundation-models --region us-east-1

# Test Bedrock access
aws bedrock invoke-model \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"messages":[{"role":"user","content":"Hello"}],"max_tokens":100}' \
  --cli-binary-format raw-in-base64-out \
  --region us-east-1 \
  response.json && cat response.json
```

## 🎯 **Next Steps**

1. **✅ Configure AWS credentials** (Step 1)
2. **✅ Enable Bedrock models** (Step 2)  
3. **✅ Test connection** (Step 3)
4. **✅ Run PropertyPilot tests** (Step 4)
5. **🚀 Start analyzing properties!**

Once configured, PropertyPilot will provide:
- **Intelligent property analysis** using Claude AI
- **Market research** with real demographic data
- **Investment recommendations** based on comprehensive analysis
- **Multi-agent collaboration** for thorough evaluation

Your PropertyPilot system will be production-ready with professional-grade AI analysis capabilities! 🏠🤖