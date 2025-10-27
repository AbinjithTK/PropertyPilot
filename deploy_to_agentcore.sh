#!/bin/bash

# PropertyPilot Gemini AgentCore Deployment Script
echo "🚀 Deploying PropertyPilot with Google Gemini to AWS Bedrock AgentCore"
echo "=================================================================="

# Check if required tools are installed
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it with your configuration."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$AWS_REGION" ]; then
    echo "❌ AWS_REGION not set in .env file"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "   AWS Region: $AWS_REGION"
echo "   Model Provider: gemini"
echo "   Gemini Model: gemini-2.5-pro"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]; then
    echo "❌ Failed to get AWS account ID. Please check your AWS credentials."
    exit 1
fi

echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"

# Set ECR repository details
ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
REPO_NAME="propertypilot-gemini-main"
IMAGE_TAG="latest"
IMAGE_URI="$ECR_REGISTRY/$REPO_NAME:$IMAGE_TAG"

echo "📦 Docker Image URI: $IMAGE_URI"

# Step 1: Create ECR repository if it doesn't exist
echo ""
echo "1. Creating ECR repository..."
aws ecr describe-repositories --repository-names $REPO_NAME --region $AWS_REGION >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   Creating new ECR repository: $REPO_NAME"
    aws ecr create-repository \
        --repository-name $REPO_NAME \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    
    if [ $? -eq 0 ]; then
        echo "   ✅ ECR repository created successfully"
    else
        echo "   ❌ Failed to create ECR repository"
        exit 1
    fi
else
    echo "   ✅ ECR repository already exists"
fi

# Step 2: Login to ECR
echo ""
echo "2. Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
if [ $? -eq 0 ]; then
    echo "   ✅ Successfully logged into ECR"
else
    echo "   ❌ Failed to login to ECR"
    exit 1
fi

# Step 3: Build Docker image
echo ""
echo "3. Building Docker image..."
docker build -f Dockerfile.main -t $IMAGE_URI .
if [ $? -eq 0 ]; then
    echo "   ✅ Docker image built successfully"
else
    echo "   ❌ Failed to build Docker image"
    exit 1
fi

# Step 4: Push Docker image to ECR
echo ""
echo "4. Pushing Docker image to ECR..."
docker push $IMAGE_URI
if [ $? -eq 0 ]; then
    echo "   ✅ Docker image pushed successfully"
else
    echo "   ❌ Failed to push Docker image"
    exit 1
fi

# Step 5: Run Python deployment script
echo ""
echo "5. Deploying to AgentCore..."
python deploy_gemini_agentcore.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 PropertyPilot with Gemini successfully deployed to AgentCore!"
    echo "=================================================================="
    echo "Your AI-powered real estate investment system is now running on AWS!"
    echo ""
    echo "📊 Check deployment_info_gemini.json for deployment details"
    echo "🔍 Monitor your deployment in the AWS Console:"
    echo "   - Bedrock AgentCore: https://console.aws.amazon.com/bedrock/home?region=$AWS_REGION#/agentcore"
    echo "   - CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups"
    echo ""
else
    echo ""
    echo "❌ Deployment failed. Please check the logs above."
    exit 1
fi